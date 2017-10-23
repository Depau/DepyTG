import warnings

from depytg.errors import NotImplementedWarning
from depytg.types import *

from typing import GenericMeta, Sequence, Mapping, _ForwardRef, Union, Any


def is_union(some_type: Any) -> bool:
    """
    Apparently there's no way to know if some type is a Union other than checking
    the memory location of its type. Thanks Python <3
    :param some_type: The type you're checking
    :return: True if it is a Union
    """

    # Yeah. Thanks Python.
    return isinstance(some_type, type(Union)) or \
           id(type(some_type)) == id(type(Union)) or \
           str(type(some_type)) == "typing.Union"


def depyfy(obj: Any, otype: Union[type, GenericMeta]) -> Any:
    """
    Walks into a generic object 'obj' and converts it to a DepyTG typechecked
    object, if possible.
    Please note that only JSON-serializable objects are
    supported: other objects will be returned without conversion.
    Moreover, forward references are not supported and objects whose type
    specified as such will not be converted. To avoid passing unwanted forward references,
    please use 'typing.get_type_hints' instead of finding them manually.
    :param obj: The object to convert
    :param otype: The expected type for the object
    :return: The converted object
    """

    if isinstance(otype, Sequence):
        return depyfy_sequence(obj, otype)
    elif isinstance(otype, Mapping):
        return depyfy_mapping(obj, otype)
    elif is_union(otype):
        return depyfy_union(obj, otype)
    elif (type(otype) == type and issubclass(otype, TelegramObjectBase)) or \
            isinstance(otype, TelegramObjectBase):
        return depyfy_tobject(obj, otype)
    else:
        return obj


def depyfy_sequence(seq: Sequence, seq_type: GenericMeta) -> Sequence:
    subtype = seq_type.__args__[0]
    newseq = []

    if isinstance(subtype, _ForwardRef):
        warnings.warn("Not depyfying sequence whose argument is a forward reference", NotImplementedWarning)
        return seq
    elif isinstance(subtype, Sequence):
        for i in seq:
            newseq.append(depyfy_sequence(i, subtype))
    elif isinstance(subtype, Mapping):
        for i in seq:
            newseq.append(depyfy_mapping(i, subtype))
    elif (type(subtype) == type and issubclass(subtype, TelegramObjectBase)) or \
            isinstance(subtype, TelegramObjectBase):
        for i in seq:
            newseq.append(depyfy_tobject(i, subtype))
    else:
        # Subtype is a regular Python object. This is not a typechecker, skip loop
        return seq

    # Cast back to original type
    return type(seq)(newseq)


def depyfy_mapping(mapp: Mapping, map_type: GenericMeta) -> Mapping:
    keytype, valtype = map_type.__args__
    newmap = {}

    k_is_fref = isinstance(keytype, _ForwardRef)
    v_is_fref = isinstance(valtype, _ForwardRef)

    # Skip loop if everything is a forward reference
    if k_is_fref or v_is_fref:
        warnings.warn("Not depyfying mapping whose {} defined as _ForwardRef"
                      .format(k_is_fref and not v_is_fref and "key is" or \
                              v_is_fref and not k_is_fref and "value is" or \
                              k_is_fref and v_is_fref and "key and value are"),
                      NotImplementedWarning)
        return mapp

    # Skip loop if both keys and values are regular Python objects
    if not (isinstance(keytype, GenericMeta) or
                ((type(keytype) == type and issubclass(keytype, TelegramObjectBase)) or
                     isinstance(keytype, TelegramObjectBase)) or
                isinstance(valtype, GenericMeta) or
                        type(valtype) == type and issubclass(valtype, GenericMeta)):
        return mapp

    # Either key or value needs to be depyfied
    for k, v in mapp.items():
        newkey, newval = k, v

        if k_is_fref:
            pass
        elif isinstance(keytype, Sequence):
            newkey = depyfy_sequence(k, keytype)
        elif isinstance(keytype, Mapping):
            newkey = depyfy_mapping(k, keytype)
        elif (type(keytype) == type and issubclass(keytype, TelegramObjectBase)) or \
                isinstance(keytype, TelegramObjectBase):
            newkey = depyfy_tobject(k, keytype)

        if v_is_fref:
            pass
        elif isinstance(valtype, Sequence):
            newval = depyfy_sequence(v, valtype)
        elif isinstance(valtype, Mapping):
            newval = depyfy_mapping(v, valtype)
        elif (type(valtype) == type and issubclass(valtype, TelegramObjectBase)) or \
                isinstance(valtype, TelegramObjectBase):
            newval = depyfy_tobject(v, valtype)

        newmap[newkey] = newval

    # Cast back to original type
    return type(mapp)(newmap)


def depyfy_union(obj: Any, union: GenericMeta) -> Any:
    given_t = type(obj)

    # If the object is a regular Python object and its type is specified
    # in the Union, it's good to go
    if given_t in union.__args__:
        return obj

    # Not a regular type, one first shot looking for TelegramObjectBase
    if given_t == dict and Mapping not in union.__args__:
        # Try to convert it to every TelegramObjectBase subclass specified
        # in the Union. Return the first one that succeeds
        for t in union.__args__:
            if not (isinstance(t, TelegramObjectBase) or (type(t) == type and issubclass(t, TelegramObjectBase))):
                continue
            try:
                return depyfy_tobject(obj, t)
            except Exception:
                import traceback;
                traceback.print_exc()

    # Maybe it's a GenericMeta. Check for Sequence and Mapping
    for t in union.__args__:
        try:
            if isinstance(t, Sequence):
                return depyfy_sequence(obj, t)
        except Exception:
            import traceback;
            traceback.print_exc()

        try:
            if isinstance(t, Mapping):
                return depyfy_mapping(obj, t)
        except Exception:
            import traceback;
            traceback.print_exc()

    # The object is nothing we can convert. Return it with a warning
    warnings.warn("Could not match object '{}' of type {} with anything in {}".format(obj, given_t, union))
    return obj


def depyfy_tobject(tobj: Union[TelegramObjectBase, dict, str], otype: type) -> TelegramObjectBase:
    if type(tobj) == otype:
        return tobj
    elif type(tobj) in (str, dict):
        return otype.from_json(tobj)
    return tobj
