from dataclasses import dataclass
from datetime import timedelta


@dataclass()
class LogTrigger(object):
    sid: int
    delay: timedelta
    name: str


class CustomEnum(object):

    def __contains__(self, item):
        return item.name in self.keys

    @classmethod
    @property
    def keys(cls):
        return [attr for attr in dir(cls) if
                attr.isupper() and (not attr.endswith("__") and not attr.startswith("__"))]


class StateLoggingTriggersByTime(CustomEnum):
    TEST = LogTrigger(-1, timedelta(seconds=10), "TEST")
    EVERY_MINUTE = LogTrigger(0, timedelta(minutes=1), "EVERY_MINUTE")
    EVERY_FIVE_MINUTES = LogTrigger(1, timedelta(minutes=5), "EVERY_FIVE_MINUTES")
    EVERY_FIFTEEN_MINUTES = LogTrigger(2, timedelta(minutes=15), "EVERY_FIFTEEN_MINUTES")
    EVERY_THIRTY_MINUTES = LogTrigger(3, timedelta(minutes=30), "EVERY_FIFTEEN_MINUTES")
    EVERY_HOUR = LogTrigger(4, timedelta(hours=1), "EVERY_HOUR")
    EVERY_TWELVE_HOUR = LogTrigger(5, timedelta(hours=12), "EVERY_TWELVE_HOUR")
    DAILY = LogTrigger(6, timedelta(days=1), "DAILY")
    WEEKLY = LogTrigger(7, timedelta(weeks=1), "WEEKLY")
    MONTHLY = LogTrigger(8, timedelta(days=30), "MONTHLY")
    ANNUALLY = LogTrigger(9, timedelta(weeks=52), "ANNUALLY")


class StateLoggingTriggersBySignal(CustomEnum):
    BEFORE_SHUTDOWN = LogTrigger(10, timedelta(seconds=0), "BEFORE_SHUTDOWN")
    BANDWIDTH_LIMIT_USAGE_EXCEED = LogTrigger(11, timedelta(seconds=0), "BANDWIDTH_LIMIT_USAGE_EXCEED")


class StateLoggingTriggers(
    StateLoggingTriggersByTime,
    StateLoggingTriggersBySignal
):
    pass
