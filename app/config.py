from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    database_url: str = 'postgresql+psycopg://nexus:nexus@db:5432/nexus'
    redis_url: str = 'redis://redis:6379/0'
    openai_api_key: str = ''
    nexus_admin_token: str = ''
    timezone: str = 'Europe/London'
    telegram_bot_token: str = ''
    telegram_webhook_secret: str = ''
    telegram_owner_user_id: str = ''
    telegram_chat_id: str = ''
    discord_bot_token: str = ''
    discord_public_key: str = ''
    discord_owner_user_id: str = ''
    discord_channel_id: str = ''
    resend_api_key: str = ''
    resend_webhook_secret: str = ''
    email_owner: str = ''
    email_from: str = ''

settings = Settings()
