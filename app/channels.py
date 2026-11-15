import httpx
from app.config import settings

async def send(channel: str, destination: str, subject: str, body: str):
    async with httpx.AsyncClient(timeout=25) as client:
        if channel == 'telegram':
            if not settings.telegram_bot_token:
                raise RuntimeError('Telegram token not configured')
            response = await client.post(
                f'https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage',
                json={'chat_id': destination, 'text': body[:4000]},
            )
        elif channel == 'discord':
            if not settings.discord_bot_token:
                raise RuntimeError('Discord bot token not configured')
            response = await client.post(
                f'https://discord.com/api/v10/channels/{destination}/messages',
                headers={'Authorization': f'Bot {settings.discord_bot_token}'},
                json={'content': body[:1900], 'allowed_mentions': {'parse': []}},
            )
        elif channel == 'email':
            if not settings.resend_api_key or not settings.email_from:
                raise RuntimeError('Email sender not configured')
            response = await client.post(
                'https://api.resend.com/emails',
                headers={'Authorization': f'Bearer {settings.resend_api_key}'},
                json={'from': settings.email_from, 'to': [destination],
                      'subject': subject, 'text': body},
            )
        else:
            raise ValueError(f'Unknown channel: {channel}')
        response.raise_for_status()
        return response.json()

async def get_received_email(email_id: str) -> str:
    async with httpx.AsyncClient(timeout=25) as client:
        response = await client.get(
            f'https://api.resend.com/emails/receiving/{email_id}',
            headers={'Authorization': f'Bearer {settings.resend_api_key}'},
        )
        response.raise_for_status()
        message = response.json()
        return (message.get('text') or '[No plain-text body available]')[:12000]
