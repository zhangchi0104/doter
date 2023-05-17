from asyncio import subprocess
from typing import Any, Callable, Generic, List, Optional, TypeVar
import logging
from doter.exceptions import SubprocessError
import inspect


def copysig(from_func, *args_to_remove):
    def wrap(func):
        #add and remove parameters
        oldsig = inspect.signature(from_func)
        oldsig = _remove_args(oldsig, args_to_remove)
        newsig = _add_args(oldsig, func)

        #write some code for a function that we can exec
        #the function will have the correct signature and forward its arguments to the real function
        code = '''
def {name}{signature}:
    {func}({args})
'''.format(name=func.__name__,
           signature=newsig,
           func='_' + func.__name__,
           args=_forward_args(oldsig, newsig))
        globs = {'_' + func.__name__: func}
        exec(code, globs)
        newfunc = globs[func.__name__]

        #copy as many attributes as possible
        newfunc.__doc__ = func.__doc__
        newfunc.__module__ = func.__module__
        #~ newfunc.__closure__= func.__closure__
        #~ newfunc.__code__.co_filename= func.__code__.co_filename
        #~ newfunc.__code__.co_firstlineno= func.__code__.co_firstlineno
        return newfunc

    return wrap


def _collectargs(sig):
    """
    Writes code that gathers all parameters into "self" (if present), "args" and "kwargs"
    """
    arglist = list(sig.parameters.values())

    #check if the first parameter is "self"
    selfarg = ''
    if arglist:
        arg = arglist[0]
        if arg.name == 'self':
            selfarg = 'self, '
            del arglist[0]

    #all named parameters will be passed as kwargs. args is only used for varargs.
    args = 'tuple(), '
    kwargs = ''
    kwarg = ''
    for arg in arglist:
        if arg.kind in (arg.POSITIONAL_ONLY, arg.POSITIONAL_OR_KEYWORD,
                        arg.KEYWORD_ONLY):
            kwargs += '("{0}",{0}), '.format(arg.name)
        elif arg.kind == arg.VAR_POSITIONAL:
            #~ assert not args
            args = arg.name + ', '
        elif arg.kind == arg.VAR_KEYWORD:
            assert not kwarg
            kwarg = 'list({}.items())+'.format(arg.name)
        else:
            assert False, arg.kind
    kwargs = 'dict({}[{}])'.format(kwarg, kwargs[:-2])

    return '{}{}{}'.format(selfarg, args, kwargs)


def _forward_args(args_to_collect, sig):
    collect = _collectargs(args_to_collect)

    collected = {arg.name for arg in args_to_collect.parameters.values()}
    args = ''
    for arg in sig.parameters.values():
        if arg.name in collected:
            continue

        if arg.kind == arg.VAR_POSITIONAL:
            args += '*{}, '.format(arg.name)
        elif arg.kind == arg.VAR_KEYWORD:
            args += '**{}, '.format(arg.name)
        else:
            args += '{0}={0}, '.format(arg.name)
    args = args[:-2]

    code = '{}, {}'.format(collect, args) if args else collect
    return code


def _remove_args(signature, args_to_remove):
    """
    Removes named parameters from a signature.
    """
    args_to_remove = set(args_to_remove)
    varargs_removed = False
    args = []
    for arg in signature.parameters.values():
        if arg.name in args_to_remove:
            if arg.kind == arg.VAR_POSITIONAL:
                varargs_removed = True
            continue

        if varargs_removed and arg.kind == arg.KEYWORD_ONLY:  #if varargs have been removed, there are no more keyword-only parameters
            arg = arg.replace(kind=arg.POSITIONAL_OR_KEYWORD)

        args.append(arg)

    return signature.replace(parameters=args)


def _add_args(sig, func):
    """
    Merges a signature and a function into a signature that accepts ALL the parameters.
    """
    funcsig = inspect.signature(func)

    #find out where we want to insert the new parameters
    #parameters with a default value will be inserted before *args (if any)
    #if parameters with a default value exist, parameters with no default value will be inserted as keyword-only AFTER *args
    vararg = None
    kwarg = None
    insert_index_default = None
    insert_index_nodefault = None
    default_found = False
    args = list(sig.parameters.values())
    for index, arg in enumerate(args):
        if arg.kind == arg.VAR_POSITIONAL:
            vararg = arg
            insert_index_default = index
            if default_found:
                insert_index_nodefault = index + 1
            else:
                insert_index_nodefault = index
        elif arg.kind == arg.VAR_KEYWORD:
            kwarg = arg
            if insert_index_default is None:
                insert_index_default = insert_index_nodefault = index
        else:
            if arg.default != arg.empty:
                default_found = True

    if insert_index_default is None:
        insert_index_default = insert_index_nodefault = len(args)

    #find the new parameters
    #skip the first two parameters (args and kwargs)
    newargs = list(funcsig.parameters.values())
    if not newargs:
        raise Exception(
            'The decorated function must accept at least 2 parameters')
    #if the first parameter is called "self", ignore the first 3 parameters
    if newargs[0].name == 'self':
        del newargs[0]
    if len(newargs) < 2:
        raise Exception(
            'The decorated function must accept at least 2 parameters')
    newargs = newargs[2:]

    #add the new parameters
    if newargs:
        new_vararg = None
        for arg in newargs:
            if arg.kind == arg.VAR_POSITIONAL:
                if vararg is None:
                    new_vararg = arg
                else:
                    raise Exception(
                        'Cannot add varargs to a function that already has varargs'
                    )
            elif arg.kind == arg.VAR_KEYWORD:
                if kwarg is None:
                    args.append(arg)
                else:
                    raise Exception(
                        'Cannot add kwargs to a function that already has kwargs'
                    )
            else:
                #we can insert it as a positional parameter if it has a default value OR no other parameter has a default value
                if arg.default != arg.empty or not default_found:
                    #do NOT change the parameter kind here. Leave it as it was, so that the order of varargs and keyword-only parameters is preserved.
                    args.insert(insert_index_default, arg)
                    insert_index_nodefault += 1
                    insert_index_default += 1
                else:
                    arg = arg.replace(kind=arg.KEYWORD_ONLY)
                    args.insert(insert_index_nodefault, arg)
                    if insert_index_default == insert_index_nodefault:
                        insert_index_default += 1
                    insert_index_nodefault += 1

        #if varargs need to be added, insert them before keyword-only arguments
        if new_vararg is not None:
            for i, arg in enumerate(args):
                if arg.kind not in (arg.POSITIONAL_ONLY,
                                    arg.POSITIONAL_OR_KEYWORD):
                    break
            else:
                i += 1
            args.insert(i, new_vararg)

    return inspect.Signature(args, return_annotation=funcsig.return_annotation)


F = TypeVar('F', bound=Callable[..., Any])


class LoggerMixin(object):
    def __init__(self):
        self._logger = logging.getLogger(__file__)

    def info(self, *args, **kwargs):
        self._logger.info(*args, **kwargs)

    def error(self, *args, **kwargs):
        self._logger.error(*args, **kwargs)

    def warn(self, *args, **kwargs):
        self._logger.warn(*args, **kwargs)

    def debug(self, *args, **kwargs):
        self._logger.debug(*args, **kwargs)


async def sh(cmd: str):
    proc = await subprocess.create_subprocess_shell(
        cmd,
        stderr=subprocess.PIPE,
        shell=True,
    )
    _, stderr = await proc.communicate()
    retcode = proc.returncode
    if retcode != 0:
        raise SubprocessError(cmd, retcode, stderr)
