from typing import TYPE_CHECKING, List, Optional, Dict
from driconfig import DriConfig
from pydantic import BaseModel, BaseSettings, Field, validator
from os.path import split


class ConfigConfig(BaseSettings):
    path: str = "config.yaml"
    env_prefix: str = "TM_"

    class Config:
        env_prefix = "CONFIG_"


class EndpointConfig(BaseModel):
    endpoint: str
    headers: Dict[str, str] = Field(default_factory=dict)


class Settings(DriConfig):
    class Config:
        config_folder = split(ConfigConfig().path)[0]
        config_file_name = split(ConfigConfig().path)[1]
        env_prefix = ConfigConfig().env_prefix

    endpoints: Dict[str, EndpointConfig]

    @validator("endpoints")
    def validate_endpoints(
        cls, v: Dict[str, EndpointConfig]
    ) -> Dict[str, EndpointConfig]:
        if not "default" in v:
            raise ValueError("No default endpoint defined")
        return v
