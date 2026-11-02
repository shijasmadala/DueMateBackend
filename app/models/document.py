from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A document with an expiry date, owned by a single user."""

    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_user_id_expiry_date", "user_id", "expiry_date"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    document_type: Mapped[str] = mapped_column(String(80), nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        server_default=text("true"),
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="documents")
    reminder_preferences: Mapped[list["ReminderPreference"]] = relationship(
        back_populates="document"
    )
    reminder_deliveries: Mapped[list["ReminderDelivery"]] = relationship(
        back_populates="document"
    )
