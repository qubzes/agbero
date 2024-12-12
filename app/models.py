from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database import Base
from app.schemas import Sender


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime, server_default=func.now())

    @classmethod
    def get(cls, db, id):
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def list(cls, db, sort_by=None, sort_order="asc", **kwargs):
        query = db.query(cls)
        for key, value in kwargs.items():
            query = query.filter(getattr(cls, key) == value)

        if sort_by and hasattr(cls, sort_by):
            order_col = getattr(cls, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(order_col.desc())
            else:
                query = query.order_by(order_col.asc())

        return query.all()

    def save(self, db):
        if not self.id:
            db.add(self)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db):
        db.delete(self)
        db.commit()
        return True


class Thread(BaseModel):
    __tablename__ = "threads"
    messages = relationship("Message", back_populates="thread")


class Message(BaseModel):
    __tablename__ = "messages"
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id"))
    sender = Column(Enum(Sender), nullable=False)
    content = Column(Text)
    thread = relationship("Thread", back_populates="messages")
