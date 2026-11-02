from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import PaymentItemType, Recurrence


class PaymentItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A subscription or bill that belongs to a single user."""

    __tablename__ = "payment_items"
    __table_args__ = (
        CheckConstraint(
            "item_type IN ('subscription', 'bill')",
            name="item_type_valid",
        ),
        CheckConstraint(
            "recurrence IN ('monthly', 'yearly', 'one_time')",
            name="recurrence_valid",
        ),
        CheckConstraint("amount >= 0", name="amount_non_negative"),
        Index("ix_payment_items_user_id_next_due_date", "user_id", "next_due_date"),
        Index("ix_payment_items_user_id_item_type", "user_id", "item_type"),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="INR")
    recurrence: Mapped[str] = mapped_column(String(20), nullable=False)
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        server_default=text("true"),
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="payment_items")
    payment_records: Mapped[list["PaymentRecord"]] = relationship(
        back_populates="payment_item"
    )
    reminder_preferences: Mapped[list["ReminderPreference"]] = relationship(
        back_populates="payment_item"
    )
    reminder_deliveries: Mapped[list["ReminderDelivery"]] = relationship(
        back_populates="payment_item"
    )

    def typed_item_type(self) -> PaymentItemType:
        return PaymentItemType(self.item_type)

    def typed_recurrence(self) -> Recurrence:
        return Recurrence(self.recurrence)
