from typing import TypedDict, List, Dict


class ConfigItem(TypedDict, total=False):
    src: str
    dst: str
    before_setup: List[str]
    after_steup: List[str]


class GlobalHooks(TypedDict, total=False):
    before_setup: List[str]
    after_setup: List[str]


Dotfiles = Dict[str, ConfigItem]


class ConfigYaml(TypedDict, total=False):
    hooks: GlobalHooks
    files: Dotfiles
