from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import settings
from app.models import InboundEvent, OutboundMessage, Task


def store_inbound(db: Session, *, channel, external_id, sender, destination, payload) -> str | None:
    existing = db.scalar(select(InboundEvent).where(
        InboundEvent.channel == channel, InboundEvent.external_id == external_id))
    if existing:
        return None
    event = InboundEvent(channel=channel, external_id=external_id,
                         sender=sender, destination=destination, payload=payload)
    db.add(event)
    db.commit()
    return event.id


def queue_message(db: Session, channel: str, destination: str, subject: str,
                  body: str, key: str):
    if db.scalar(select(OutboundMessage.id).where(OutboundMessage.dedupe_key == key)):
        return
    db.add(OutboundMessage(channel=channel, destination=destination,
                           subject=subject, body=body, dedupe_key=key))


def notify_owner(db: Session, subject: str, body: str, key: str):
    # Configured channels receive the same notification. No unverified targets.
    targets = [('telegram', settings.telegram_chat_id),
               ('discord', settings.discord_channel_id),
               ('email', settings.email_owner)]
    for channel, dest in targets:
        if dest:
            queue_message(db, channel, dest, subject, body, f'{key}:{channel}')


def render_tasks(db: Session, limit: int = 10) -> str:
    tasks = db.scalars(select(Task).where(Task.status.in_(['open', 'queued', 'running']))
                       .order_by(Task.priority, Task.created_at).limit(limit)).all()
    if not tasks:
        return 'No outstanding tasks.'
    return '\n'.join(f'{t.id[:8]}  P{t.priority}  [{t.status}] {t.title}' for t in tasks)


def create_task(db: Session, title: str, description: str, priority: int = 3,
                kind='human', assigned_agent='none', origin_event_id=None,
                due_at=None) -> Task:
    task = Task(title=title[:255], description=description,
                priority=min(max(priority, 1), 5), kind=kind,
                assigned_agent=assigned_agent, origin_event_id=origin_event_id,
                due_at=due_at, status='queued' if kind == 'agent' else 'open')
    db.add(task)
    db.flush()
    return task
