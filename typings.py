from typing import Dict, List, TypedDict, Union

ArgList = List[str]


class DotFileConfig(TypedDict):
    src: str
    dst: str
    before_setup: Union[List[str], None]
    after_setup: Union[List[str], None]
    force_override: bool
    deps: Union[List[str], None]
    use_file: str


class ConfigFile(TypedDict):
    hooks: List[str]
    files: Dict[str, DotFileConfig]


class DepTree(TypedDict):
    value: DotFileConfig
    children: Union[List[DotFileConfig], None]
