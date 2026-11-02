from enum import StrEnum


class PaymentItemType(StrEnum):
    SUBSCRIPTION = "subscription"
    BILL = "bill"


class Recurrence(StrEnum):
    MONTHLY = "monthly"
    YEARLY = "yearly"
    ONE_TIME = "one_time"


class DevicePlatform(StrEnum):
    ANDROID = "android"
    IOS = "ios"


class ReminderChannel(StrEnum):
    PUSH = "push"


class ReminderDeliveryStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"
