from pydantic import BaseModel
from os import PathLike
from typing import Union, List, Dict


class ConfigItem(BaseModel):
    mappings: Dict[str, str]
    before: Union[List[str], None]
    after: Union[List[str], None]


class ConfigFile(BaseModel):
    version: int
    items: Dict[str, ConfigItem]

    def to_file(self, path: PathLike):
        self.dict()
        return FileExistsError()

    @classmethod
    def from_file(cls, path: PathLike):
        from yaml import safe_load
        f = open(path, 'r')
        values = safe_load(f)
        f.close()
        return ConfigFile(**values)
