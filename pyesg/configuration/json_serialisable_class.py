import json

from collections import OrderedDict
from typing import Dict


class JSONSerialisableClass:
    """
    Base class for encoding and decoding JSON objects representing the pyESG configuration.
    """
    _serialisable_lists = {}  # type: Dict[str, JSONSerialisableClass]
    _serialisable_attrs = {}  # type: Dict[str, JSONSerialisableClass]
    _validation_schema = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return json.dumps(self._encode_json(), indent=4)

    def _encode_json(self)->dict:
        json_obj = {}
        for key, value in self.__dict__.items():
            if isinstance(value, JSONSerialisableClass):
                json_obj[key] = value._encode_json()
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], JSONSerialisableClass):
                json_obj[key] = [item._encode_json() for item in value]
            else:
                json_obj[key] = value
        return OrderedDict(sorted(json_obj.items()))

    @classmethod
    def _decode_json(cls, json_obj: dict):
        instance = cls()
        for key, value in json_obj.items():
            if key in cls._serialisable_lists:
                class_type = cls._serialisable_lists[key]
                set_value = [class_type._decode_json(item) for item in value]
            elif key in cls._serialisable_attrs:
                class_type = cls._serialisable_attrs[key]
                set_value = class_type._decode_json(value)
            else:
                set_value = value
            instance.__setattr__(key, set_value)
        return instance


def _has_parameters(Cls):
    """
    A decorator for any class which has parameters which creates an add_parameter method for the class.
    Args:
        Cls: The class with parameters

    Returns:
        An augmented class version of the original class which has an add_parameter method.

    """
    class AugmentedCls(Cls):
        def add_parameter(self, id: str, value: str):
            if hasattr(self.parameters, id):
                raise ValueError("Object already has a parameter {id}".format(id=id))
            setattr(self.parameters, id, value)
    return AugmentedCls
