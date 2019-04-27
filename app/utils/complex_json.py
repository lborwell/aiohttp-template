import json
from uuid import UUID
from datetime import datetime


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID) or isinstance(obj, datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

    @classmethod
    def dumps(cls, obj):
        return json.dumps(obj, cls=cls)