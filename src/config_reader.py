from dataclasses import dataclass
import json

@dataclass
class DatabaseConfig:
    connection_string: str

@dataclass
class WorksnapsConfig:
    api_url: str

@dataclass
class TelegramConfig:
    token: str

@dataclass
class RedisConfig:
    host: str
    port: int

@dataclass
class Config:
    database: DatabaseConfig
    telegram: TelegramConfig
    worksnaps: WorksnapsConfig
    redis: RedisConfig

    @staticmethod
    def from_json_file(config_path: str):
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
        return Config(
            database=DatabaseConfig(**config_data['database']),
            telegram=TelegramConfig(**config_data['telegram']),
            worksnaps=WorksnapsConfig(**config_data['worksnaps']),
            redis=RedisConfig(**config_data['redis'])
        )

config_path = './config.json'
config = Config.from_json_file(config_path)
