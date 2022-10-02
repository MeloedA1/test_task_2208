from pydantic import BaseSettings


class Settings(BaseSettings):
    pg_user: str = 'meloed'
    pg_password: str = 'OPmcGLVkDCM!'
    pg_host: str = 'postgres_db'
    pg_db: str = 'test_task'
    tg_token: str = ''
    tg_chat_id: str = ''


cfg = Settings()

