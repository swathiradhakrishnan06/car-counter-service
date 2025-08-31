from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_host: str
    database_port: int
    database_password: str
    database_name: str
    database_user: str

    class Config:
        env_file = ".env.example"


settings = Settings()
