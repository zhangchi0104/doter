from dataclasses import dataclass
from typing import Dict, List, Union
import yaml


@dataclass
class ConfigItem:
    files: Dict[str, str]
    pre_hooks: List[str]
    post_hooks: List[str]
    clean_hooks: Union[List[str], None]


@dataclass
class Dotfile:
    items: Dict[str, ConfigItem]
    all_items: List[str]
    _raw: dict


def parse_config(path: str):
    f = open(path, 'r')
    dotfile = yaml.load(f, Loader=yaml.Loader)
    all_items = dotfile.get('all', None)
    if all_items is None:
        all_items = list(dotfile['config'].keys())
    items = {}
    f.close()
    for key, item in dotfile['config'].items():
        config_item = ConfigItem(files=item.get('files', dict()),
                                 pre_hooks=item.get('before_setup', []),
                                 post_hooks=item.get('after_setup', []),
                                 clean_hooks=item.get('clean_hooks', []))
        items[key] = config_item
    return Dotfile(items=items, all_items=all_items, _raw=dotfile)
