import inspect
import json
import warnings
from typing import TypeVar, Union, Sequence, Any, Generator, Tuple, Type, Optional
from inspect import _empty

unacceptable_names = (
    "from", "import", "for", "class", "def", "return", "yield", "with", "global", "print", "del", "is", "not", "while",
    "try", "except", "finally", "if", "elif", "else", "or", "and")

T = TypeVar("T")


def shadow(name: str) -> str:
    if name in unacceptable_names:
        return name + "_"
    return name


def unshadow(name: str) -> str:
    if name[:-1] in unacceptable_names:
        return name[:-1]
    return name


class NotImplementedWarning(Warning, NotImplementedError):
    pass


class TelegramObjectBase(dict):
    """
    Base class for Telegram API objects. It should not be used directly.
    """

    __fields = []

    def __init__(self):
        super().__init__()

        self.__fields.extend([i for i, _ in self._get_fields(required=None)])

    @classmethod
    def _get_fields(cls, required: Optional[bool]) -> Generator[Tuple[str, Any], None, None]:
        s = inspect.signature(cls.__init__)
        for name, p in s.parameters.items():
            if name == "self":
                continue
            if (required or required is None) and p.default == _empty:
                yield name, Any if p.annotation == _empty else p.annotation
            if not required and p.default != _empty:
                yield name, Any if p.annotation == _empty else p.annotation

    @classmethod
    def _get_required(cls) -> Generator[Tuple[str, Any], None, None]:
        """
        A generator yielding required fields based on the constructor's signature.
        :return: A sequence of (field_name, type) tuples
        """
        for n, t in cls._get_fields(required=True):
            yield n, t

    @classmethod
    def _get_optional(cls) -> Generator[Tuple[str, Any], None, None]:
        """
        A generator yielding optional fields based on the constructor's signature.
        :return: A sequence of (field_name, type) tuples
        """
        for n, t in cls._get_fields(required=False):
            yield n, t

    @classmethod
    def _get_field_type(cls, name: str) -> Optional[Type]:
        s = inspect.signature(cls.__init__)
        a = s.parameters[name].annotation
        return a if a != _empty else None

    @classmethod
    def _is_required(cls, name: str) -> bool:
        return inspect.signature(cls.__init__).parameters[name].default == _empty

    @classmethod
    def _is_optional(cls, name: str) -> bool:
        return not cls._is_required(name)

    @classmethod
    def from_json(cls, j: str) -> 'TelegramObjectBase':
        """
        Converts a Telegram object JSON to a native object.
        :param j: The source JSON
        :return: A TelegramObjectBase instance representing the object
        """
        return cls.from_dict(json.loads(j))

    @classmethod
    def from_dict(cls, d: dict) -> 'TelegramObjectBase':
        """
        Converts a Telegram object dict to a native object.
        :param d: The source dict
        :return: A TelegramObjectBase subclass instance representing the object
        """

        # Check if all required fields are specified
        # (KwArgs /\ Required) = Required
        required = set([i for i, _ in cls._get_required()])
        given = set(d)
        if given.intersection(required) != required:
            # missing = Required \ (KwArgs /\ Required)
            missing = required.difference(given.intersection(required))
            raise TypeError("Not a valid '{}' object. Missing {} required fields: {}"
                            .format(cls.__name__, len(missing), missing))

        args = (cls._depyfy(shadow(i), d[i]) for i, _ in cls._get_required())
        kwargs = {shadow(i): cls._depyfy(shadow(i), d[i]) for i in given.difference(required)}

        return cls(*args, **kwargs)

    @classmethod
    def _depyfy(cls, name: str, value: T, field_type: Type = None) -> Union[T, 'TelegramObjectBase', None]:
        """
        Converts a generic object compatible with Telegram's API to an object
        that is native to this library. If the object is already of the right
        type, nothing is done.
        :param name: The name of the field
        :param value: The given object
        :param field_type: The default type for that value, or None to retrieve it automatically
        :return: A TelegramObjectBase subclass instance that represents the object
        """

        if field_type is None:
            field_type = cls._get_field_type(name)

        try:
            # Check if type is a string; in that case, replace it with the right
            # type from depytg.types
            if isinstance(field_type, str):
                import depytg.types
                field_type = getattr(depytg.types, field_type)

            # If the field is optional, the value can be None
            if cls._is_optional(name) and value is None:
                return None
            # If the field is a Telegram object and the given object is a 'dict',
            # convert it to a native object of that type
            if type(value) == dict and issubclass(field_type, TelegramObjectBase):
                return field_type.from_dict(value)
            # If the given object is of the right type, do nothing
            if isinstance(value, field_type):
                return value
        # There has been some mess with parameterized generics and convertion
        # is not implemented
        except TypeError:
            warnings.warn(
                "Could not convert field '{name}' of '{object}' from '{t1}' to '{t2}' because of poor implementation.",
                NotImplementedWarning)
            return value

        # If the given object is of an incompatible type, raise an exception
        raise TypeError("Incompatible type for field '{}' of type '{}': '{}'"
                        .format(name, field_type.__name__, type(value).__name__))

    def __getattr__(self, item):
        try:
            return super(TelegramObjectBase, self).__getattribute__(item)
        except AttributeError:
            if unshadow(item) in self:
                return self[unshadow(item)]
            if self._is_optional(item):
                return None
            else:
                raise

    def __setattr__(self, item, value):
        try:
            if self._is_required(item):
                self[unshadow(item)] = value
                return
        except AttributeError:
            pass
        try:
            if self._is_optional(item):
                # Avoid setting None defaults when not explicitly provided
                if unshadow(item) not in self and value is None:
                    pass
                else:
                    self[unshadow(item)] = self._depyfy(item, value)
                return
        except AttributeError:
            pass
        warnings.warn(
            "'{}' object has no attribute '{}', but you are trying to set it. It will be set as a Python attribute and will not appear in the ."
            .format(self.__class__.__name__, unshadow(item)), RuntimeWarning)
        return super().__setattr__(item, value)

    def __delattr__(self, item):
        required = False
        try:
            required = self._is_required(item)
        except AttributeError:
            pass

        if required:
            raise AttributeError(
                "Field '{}' of object '{}' is required and can't be deleted."
                    .format(unshadow(item), self.__class__.__name__))

        if unshadow(item) in self:
            self.pop(unshadow(item))
        else:
            return super().__delattr__(item)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, dict(self))

    def __dir__(self):
        return dir(type(self)) + self.__fields
