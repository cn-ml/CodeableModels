from enum import Enum
from optparse import Option
from typing import Dict, Optional, Sequence, TypeVar
from codeable_models.internal.commons import *
from codeable_models.internal.stereotype_holders import CElementType


class VarValueKind(Enum):
    ATTRIBUTE_VALUE = 1
    TAGGED_VALUE = 2
    DEFAULT_VALUE = 3

T = TypeVar("T")

def _get_var_unknown_exception(value_kind: VarValueKind, entity: object, var_name: str):
    if value_kind == VarValueKind.TAGGED_VALUE:
        value_kind_str = "tagged value"
    elif value_kind == VarValueKind.ATTRIBUTE_VALUE or value_kind == VarValueKind.DEFAULT_VALUE:
        value_kind_str = "attribute"
    else:
        raise CException("unknown variable kind")

    if value_kind == VarValueKind.DEFAULT_VALUE:
        return CException(
            f"{value_kind_str!s} '{var_name!s}' unknown for metaclasses extended by stereotype '{entity!s}'")
    if isinstance(entity, CLink):
        return CException(f"{value_kind_str!s} '{var_name!s}' unknown")
    return CException(f"{value_kind_str!s} '{var_name!s}' unknown for '{entity!s}'")


def _get_and_check_var_classifier(_self: CNamedElement, class_path: Sequence[CClassifier], var_name: str, value_kind: VarValueKind, classifier: Optional[CClassifier]=None) -> CAttribute:
    if classifier is None:
        # search on a class path
        for cl in class_path:
            if cl.get_attribute(var_name) is not None:
                return _get_and_check_var_classifier(_self, class_path, var_name, value_kind, cl)
        raise _get_var_unknown_exception(value_kind, _self, var_name)
    else:
        # check only on specified classifier
        attribute = classifier.get_attribute(var_name)
        if attribute is None:
            raise _get_var_unknown_exception(value_kind, classifier, var_name)
        attribute.check_attribute_type_is_not_deleted()
        return attribute


def delete_var_value(_self: CNamedElement, class_path: Sequence[CClassifier], values_dict: Dict[Any, Any], var_name: str, value_kind: VarValueKind, classifier: Optional[CClassifier]=None):
    if _self.is_deleted:
        raise CException(f"can't delete '{var_name!s}' on deleted element")
    attribute = _get_and_check_var_classifier(_self, class_path, var_name, value_kind, classifier)
    try:
        values_of_classifier = values_dict[attribute.classifier]
    except KeyError:
        return None
    try:
        value = values_of_classifier[var_name]
        del values_of_classifier[var_name]
        return value
    except KeyError:
        return None


def set_var_value(_self: CNamedElement, class_path: Sequence[CClassifier], values_dict: Dict[CClassifier, Dict[str, T]], var_name: str, value: T, value_kind: VarValueKind, classifier: Optional[CClassifier]=None):
    if _self.is_deleted:
        raise CException(f"can't set '{var_name!s}' on deleted element")
    attribute = _get_and_check_var_classifier(_self, class_path, var_name, value_kind, classifier)
    attribute.check_attribute_value_type_(var_name, value)
    try:
        values_dict[attribute.classifier].update({var_name: value})
    except KeyError:
        values_dict[attribute.classifier] = {var_name: value}


def get_var_value(_self: CNamedElement, class_path: Sequence[CClassifier], values_dict: Dict[CClassifier, Dict[str, T]], var_name: str, value_kind: VarValueKind, classifier: Optional[CClassifier]=None) -> Optional[T]:
    if _self.is_deleted:
        raise CException(f"can't get '{var_name!s}' on deleted element")
    attribute = _get_and_check_var_classifier(_self, class_path, var_name, value_kind, classifier)
    if attribute.classifier is None:
        raise Exception("Attribute has no classifier!")
    return values_dict.get(attribute.classifier, {}).get(var_name, None)

def get_var_values(class_path: Sequence[CClassifier], values_dict: Dict[CClassifier, Dict[str, T]]):
    result: Dict[Any, Any] = {}
    for cl in class_path:
        if cl in values_dict:
            for attrName in values_dict[cl]:
                if attrName not in result:
                    result[attrName] = values_dict[cl][attrName]
    return result


def set_var_values(_self: CNamedElement, new_values: Optional[Dict[str, Any]], values_kind: VarValueKind):
    if new_values is None:
        new_values = {}
    if not isinstance(new_values, dict):
        if values_kind == VarValueKind.TAGGED_VALUE:
            value_kind_str = "tagged values"
        elif values_kind == VarValueKind.ATTRIBUTE_VALUE:
            value_kind_str = "attribute values"
        elif values_kind == VarValueKind.DEFAULT_VALUE:
            value_kind_str = "default values"
        else:
            raise CException("unknown variable kind")
        raise CException(f"malformed {value_kind_str!s} description: '{new_values!s}'")
    for valueName, value in new_values.items():
        if values_kind == VarValueKind.ATTRIBUTE_VALUE:
            _self.set_value(valueName, value)
        elif values_kind == VarValueKind.TAGGED_VALUE:
            _self.set_tagged_value(valueName, value)
        elif values_kind == VarValueKind.DEFAULT_VALUE:
            _self.set_default_value(valueName, value)
        else:
            raise CException("unknown variable kind")
