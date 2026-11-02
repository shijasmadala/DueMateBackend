"""Create the initial DueMate tables.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-25

This is the first revision, so down_revision is None.
upgrade() creates tables. downgrade() drops them in reverse order.
This file is a draft until you run: alembic upgrade head
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("timezone", sa.String(length=64), server_default="UTC", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "payment_items",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("item_type", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="INR", nullable=False),
        sa.Column("recurrence", sa.String(length=20), nullable=False),
        sa.Column("next_due_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "item_type IN ('subscription', 'bill')",
            name="ck_payment_items_item_type_valid",
        ),
        sa.CheckConstraint(
            "recurrence IN ('monthly', 'yearly', 'one_time')",
            name="ck_payment_items_recurrence_valid",
        ),
        sa.CheckConstraint("amount >= 0", name="ck_payment_items_amount_non_negative"),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_payment_items_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_payment_items"),
    )
    op.create_index("ix_payment_items_user_id", "payment_items", ["user_id"])
    op.create_index(
        "ix_payment_items_user_id_item_type",
        "payment_items",
        ["user_id", "item_type"],
    )
    op.create_index(
        "ix_payment_items_user_id_next_due_date",
        "payment_items",
        ["user_id", "next_due_date"],
    )

    op.create_table(
        "documents",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("document_type", sa.String(length=80), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_documents_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])
    op.create_index(
        "ix_documents_user_id_expiry_date",
        "documents",
        ["user_id", "expiry_date"],
    )

    op.create_table(
        "payment_records",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("payment_item_id", sa.Uuid(), nullable=False),
        sa.Column("amount_paid", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="INR", nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount_paid >= 0",
            name="ck_payment_records_amount_paid_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["payment_item_id"],
            ["payment_items.id"],
            name="fk_payment_records_payment_item_id_payment_items",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_payment_records_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_payment_records"),
    )
    op.create_index("ix_payment_records_user_id", "payment_records", ["user_id"])
    op.create_index(
        "ix_payment_records_payment_item_id",
        "payment_records",
        ["payment_item_id"],
    )
    op.create_index(
        "ix_payment_records_user_id_paid_at",
        "payment_records",
        ["user_id", "paid_at"],
    )

    op.create_table(
        "reminder_preferences",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("payment_item_id", sa.Uuid(), nullable=True),
        sa.Column("document_id", sa.Uuid(), nullable=True),
        sa.Column("days_before", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "remind_at",
            sa.Time(),
            server_default=sa.text("'09:00:00'"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(length=20), server_default="push", nullable=False),
        sa.Column(
            "is_enabled",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(payment_item_id IS NOT NULL AND document_id IS NULL) OR "
            "(payment_item_id IS NULL AND document_id IS NOT NULL)",
            name="ck_reminder_preferences_exactly_one_target",
        ),
        sa.CheckConstraint(
            "days_before >= 0",
            name="ck_reminder_preferences_days_before_non_negative",
        ),
        sa.CheckConstraint(
            "channel IN ('push')",
            name="ck_reminder_preferences_channel_valid",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name="fk_reminder_preferences_document_id_documents",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["payment_item_id"],
            ["payment_items.id"],
            name="fk_reminder_preferences_payment_item_id_payment_items",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_reminder_preferences_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reminder_preferences"),
        sa.UniqueConstraint(
            "document_id",
            "days_before",
            "channel",
            name="uq_reminder_preferences_document_offset_channel",
        ),
        sa.UniqueConstraint(
            "payment_item_id",
            "days_before",
            "channel",
            name="uq_reminder_preferences_item_offset_channel",
        ),
    )
    op.create_index("ix_reminder_preferences_user_id", "reminder_preferences", ["user_id"])
    op.create_index(
        "ix_reminder_preferences_payment_item_id",
        "reminder_preferences",
        ["payment_item_id"],
    )
    op.create_index(
        "ix_reminder_preferences_document_id",
        "reminder_preferences",
        ["document_id"],
    )
    op.create_index(
        "ix_reminder_preferences_user_id_enabled",
        "reminder_preferences",
        ["user_id", "is_enabled"],
    )

    op.create_table(
        "device_tokens",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token", sa.String(length=512), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "platform IN ('android', 'ios')",
            name="ck_device_tokens_platform_valid",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_device_tokens_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_device_tokens"),
        sa.UniqueConstraint("user_id", "token", name="uq_device_tokens_user_id_token"),
    )
    op.create_index("ix_device_tokens_user_id", "device_tokens", ["user_id"])

    op.create_table(
        "reminder_deliveries",
        sa.Column(
            "id",
            sa.Uuid(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("reminder_preference_id", sa.Uuid(), nullable=False),
        sa.Column("payment_item_id", sa.Uuid(), nullable=True),
        sa.Column("document_id", sa.Uuid(), nullable=True),
        sa.Column("target_event_date", sa.Date(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(payment_item_id IS NOT NULL AND document_id IS NULL) OR "
            "(payment_item_id IS NULL AND document_id IS NOT NULL)",
            name="ck_reminder_deliveries_exactly_one_target",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'sent', 'failed', 'cancelled')",
            name="ck_reminder_deliveries_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name="fk_reminder_deliveries_document_id_documents",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["payment_item_id"],
            ["payment_items.id"],
            name="fk_reminder_deliveries_payment_item_id_payment_items",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reminder_preference_id"],
            ["reminder_preferences.id"],
            name="fk_reminder_deliveries_pref_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_reminder_deliveries_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_reminder_deliveries"),
        sa.UniqueConstraint(
            "reminder_preference_id",
            "target_event_date",
            name="uq_reminder_deliveries_preference_event",
        ),
    )
    op.create_index("ix_reminder_deliveries_user_id", "reminder_deliveries", ["user_id"])
    op.create_index(
        "ix_reminder_deliveries_reminder_preference_id",
        "reminder_deliveries",
        ["reminder_preference_id"],
    )
    op.create_index(
        "ix_reminder_deliveries_payment_item_id",
        "reminder_deliveries",
        ["payment_item_id"],
    )
    op.create_index(
        "ix_reminder_deliveries_document_id",
        "reminder_deliveries",
        ["document_id"],
    )
    op.create_index(
        "ix_reminder_deliveries_status_scheduled_for",
        "reminder_deliveries",
        ["status", "scheduled_for"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_reminder_deliveries_status_scheduled_for",
        table_name="reminder_deliveries",
    )
    op.drop_index("ix_reminder_deliveries_document_id", table_name="reminder_deliveries")
    op.drop_index(
        "ix_reminder_deliveries_payment_item_id",
        table_name="reminder_deliveries",
    )
    op.drop_index(
        "ix_reminder_deliveries_reminder_preference_id",
        table_name="reminder_deliveries",
    )
    op.drop_index("ix_reminder_deliveries_user_id", table_name="reminder_deliveries")
    op.drop_table("reminder_deliveries")

    op.drop_index("ix_device_tokens_user_id", table_name="device_tokens")
    op.drop_table("device_tokens")

    op.drop_index(
        "ix_reminder_preferences_user_id_enabled",
        table_name="reminder_preferences",
    )
    op.drop_index("ix_reminder_preferences_document_id", table_name="reminder_preferences")
    op.drop_index(
        "ix_reminder_preferences_payment_item_id",
        table_name="reminder_preferences",
    )
    op.drop_index("ix_reminder_preferences_user_id", table_name="reminder_preferences")
    op.drop_table("reminder_preferences")

    op.drop_index("ix_payment_records_user_id_paid_at", table_name="payment_records")
    op.drop_index("ix_payment_records_payment_item_id", table_name="payment_records")
    op.drop_index("ix_payment_records_user_id", table_name="payment_records")
    op.drop_table("payment_records")

    op.drop_index("ix_documents_user_id_expiry_date", table_name="documents")
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_table("documents")

    op.drop_index("ix_payment_items_user_id_next_due_date", table_name="payment_items")
    op.drop_index("ix_payment_items_user_id_item_type", table_name="payment_items")
    op.drop_index("ix_payment_items_user_id", table_name="payment_items")
    op.drop_table("payment_items")

    op.drop_table("users")
