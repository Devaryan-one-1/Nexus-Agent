from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def now():
    return datetime.now(timezone.utc)

def uid():
    return str(uuid4())

class Base(DeclarativeBase):
    pass

class InboundEvent(Base):
    __tablename__ = 'inbound_events'
    __table_args__ = (UniqueConstraint('channel', 'external_id'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    channel: Mapped[str] = mapped_column(String(20))
    external_id: Mapped[str] = mapped_column(String(128))
    sender: Mapped[str] = mapped_column(String(255))
    destination: Mapped[str] = mapped_column(String(255))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default='received')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(32), default='open')
    priority: Mapped[int] = mapped_column(Integer, default=3)
    kind: Mapped[str] = mapped_column(String(32), default='human')
    assigned_agent: Mapped[str] = mapped_column(String(40), default='none')
    origin_event_id: Mapped[str | None] = mapped_column(ForeignKey('inbound_events.id'), nullable=True)
    result: Mapped[str] = mapped_column(Text, default='')
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class OutboundMessage(Base):
    __tablename__ = 'outbound_messages'
    __table_args__ = (UniqueConstraint('dedupe_key'),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    dedupe_key: Mapped[str] = mapped_column(String(255))
    channel: Mapped[str] = mapped_column(String(20))
    destination: Mapped[str] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255), default='NEXUS update')
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default='queued')
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
