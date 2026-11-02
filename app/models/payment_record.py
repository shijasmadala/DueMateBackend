from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PaymentRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A historical payment against a payment item."""

    __tablename__ = "payment_records"
    __table_args__ = (
        CheckConstraint("amount_paid >= 0", name="amount_paid_non_negative"),
        Index("ix_payment_records_user_id_paid_at", "user_id", "paid_at"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_item_id: Mapped[UUID] = mapped_column(
        ForeignKey("payment_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="INR")
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="payment_records")
    payment_item: Mapped["PaymentItem"] = relationship(back_populates="payment_records")
