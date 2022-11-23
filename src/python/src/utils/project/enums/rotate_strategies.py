import json


class RotateStrategies(object):
    NO_ROTATE = 0
    FORCE_ROTATE = 1
    ON_BAD_HTTP_STATUS_ROTATE = 2
    DEFAULT = NO_ROTATE

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            attr: getattr(self, attr) for attr in RotateStrategies.__dict__ if attr.isupper()
        }
