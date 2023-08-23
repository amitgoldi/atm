from pydantic import BaseSettings


class MongoDbSettings(BaseSettings):
    database: str = "atm"
    uri: str = "mongodb://localhost:27017/atm"

    class Config:
        env_prefix = "MONGODB_"
