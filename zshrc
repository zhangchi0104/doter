# load antigen
ANTIGEN_PATH="$HOME/antigen.zsh"
source $ANTIGEN_PATH
MINICONDA_PREFIX="$HOME/miniconda3"
if [ $(uname -s) = 'Darwin' ]; then
	source ~/.bash_profile
fi 
# =====Antigen Configs=======
antigen use oh-my-zsh
antigen bundle git
antigen bundle pip
antigen bundle lein
antigen bundle command-not-found
antigen bundle docker
antigen bundle zsh-users/zsh-syntax-highlighting
antigen bundle esc/conda-zsh-completion
antigen apply

#####################################################
#													#
#						ALIAS						#
#													#	
#####################################################

alias watch-temp='sudo powermetrics --samplers smc |grep -i "CPU die temperature"'
alias ea='conda activate'
alias ipy=ipython 
alias dc='docker-compose'
alias e='nvim'
export EDITOR=nvim
if [ -e fuck ]; then
  eval $(thefuck --alias)
fi
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init --path)"
  eval "$(pyenv init -)"
fi
eval "$(starship init zsh)"
# eval "$(lua $HOME/github.com/z.lua/z.lua --init zsh)"

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('$MINICONDA_PREFIX/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "$MINICONDA_PREFIX/etc/profile.d/conda.sh" ]; then
        . "$MINICONDA_PREFIX/etc/profile.d/conda.sh"
    else
        export PATH="$MINICONDA_PREFIX/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 
export PATH=$HOME/.yarn/bin:$PATH
