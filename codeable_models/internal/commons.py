from typing import Any, List
from codeable_models import *

def set_keyword_args(obj: object, allowed_values: List[str], **kwargs: dict[str, Any]):
    for key in kwargs:
        if key in allowed_values:
            setattr(obj, key, kwargs[key])
        else:
            raise CException(f"unknown keyword argument '{key!s}', should be one of: {allowed_values!s}")


def get_attribute_type(attr: object):
    if isinstance(attr, str):
        return str
    elif isinstance(attr, bool):
        return bool
    elif isinstance(attr, int):
        return int
    elif isinstance(attr, float):
        return float
    elif isinstance(attr, list):
        return list[Any]
    elif isinstance(attr, CObject):
        check_named_element_is_not_deleted(attr)
        return attr.classifier
    elif isinstance(attr, CClass):
        check_named_element_is_not_deleted(attr)
        return attr.metaclass
    return None


def is_known_attribute_type(test_type):
    if isinstance(test_type, CNamedElement):
        return False
    return test_type == str or test_type == bool or test_type == int or test_type == float or test_type == list


def check_is_cmetaclass(elt: object):
    if not isinstance(elt, CMetaclass):
        raise CException(f"'{elt!s}' is not a metaclass")


def check_is_cclassifier(elt: object):
    if not isinstance(elt, CClassifier):
        raise CException(f"'{elt!s}' is not a classifier")


def check_is_cclass(elt: object):
    if not isinstance(elt, CClass):
        raise CException(f"'{elt!s}' is not a class")


def check_is_cstereotype(elt: object):
    if not isinstance(elt, CStereotype):
        raise CException(f"'{elt!s}' is not a stereotype")


def check_is_cobject(elt: object):
    if not isinstance(elt, CObject):
        raise CException(f"'{elt!s}' is not an object")


def check_is_cbundle(elt: object):
    if not isinstance(elt, CBundle):
        raise CException(f"'{elt!s}' is not a bundle")


def check_is_cassociation(elt: object):
    if not isinstance(elt, CAssociation):
        raise CException(f"'{elt!s}' is not a association")


def check_named_element_is_not_deleted(named_element: CNamedElement):
    if named_element.is_deleted:
        raise CException(f"cannot access named element that has been deleted")


# get the common (top level) classifier in a list of objects
def get_common_classifier(objects):
    common_classifier = None
    for o in objects:
        if o is None or not isinstance(o, CObject):
            raise CException(f"not an object: '{o!s}'")
        if common_classifier is None:
            common_classifier = o.classifier
        else:
            object_classifiers = {o.classifier}.union(o.classifier.all_superclasses)
            common_classifier_found = False
            if common_classifier in object_classifiers:
                common_classifier_found = True
            if not common_classifier_found and common_classifier in o.classifier.all_subclasses:
                common_classifier = o.classifier
                common_classifier_found = True
            if not common_classifier_found:
                for cl in common_classifier.all_superclasses:
                    if cl in object_classifiers:
                        common_classifier = cl
                        common_classifier_found = True
                        break
            if not common_classifier_found:
                if isinstance(o, CLink):
                    raise CException(f"the link's association is missing a compatible classifier")
                else:
                    raise CException(f"object '{o!s}' has an incompatible classifier")
    return common_classifier


def check_is_common_classifier(classifier, objects):
    for o in objects:
        if not o.instance_of(classifier):
            raise CException(f"object '{o!s}' not compatible with classifier '{classifier!s}'")


def _remove_superclasses_and_duplicates(classes):
    result = []
    while len(classes) > 0:
        current_class = classes.pop(0)
        append = True
        for cl in classes:
            if cl == current_class or cl in current_class.all_subclasses:
                append = False
                break
        if append:
            for cl in result:
                if cl == current_class or cl in current_class.all_subclasses:
                    append = False
                    break
        if append:
            result.append(current_class)
    return result


def update_common_metaclasses(common_metaclasses, new_metaclasses):
    updated_common_metaclasses = []
    for metaclass in new_metaclasses:
        metaclasses = metaclass.class_path
        for cmc in common_metaclasses:
            for mc in metaclasses:
                if cmc == mc:
                    updated_common_metaclasses.append(cmc)
    if len(updated_common_metaclasses) == 0:
        return []
    return updated_common_metaclasses


def get_common_metaclasses(classes_or_links):
    common_metaclasses = None
    for classifier in classes_or_links:
        if isinstance(classifier, CLink):
            link_classifiers = [link_cl for link_cl in classifier.association.all_superclasses if
                                isinstance(link_cl, CMetaclass)]
            if not link_classifiers:
                raise CException(f"the metaclass link's association is missing a compatible classifier")
            if common_metaclasses is None:
                common_metaclasses = link_classifiers
            else:
                common_metaclasses = update_common_metaclasses(common_metaclasses, link_classifiers)
                if len(common_metaclasses) == 0:
                    break
        elif classifier is None or not isinstance(classifier, CClass):
            raise CException(f"not a class or link: '{classifier!s}'")
        else:
            if common_metaclasses is None:
                common_metaclasses = classifier.metaclass.class_path
            else:
                common_metaclasses = update_common_metaclasses(common_metaclasses, [classifier.metaclass])
                if len(common_metaclasses) == 0:
                    break
    if common_metaclasses is None:
        return [None]
    if len(common_metaclasses) == 0:
        raise CException(f"no common metaclass for classes or links found")
    # if some superclasses and their subclasses are in the list, take only the subclasses 
    # and remove duplicates form the list
    common_metaclasses = _remove_superclasses_and_duplicates(common_metaclasses)
    return common_metaclasses


def get_links(linked_elements):
    result = []
    for linked_ in linked_elements:
        linked = linked_
        if not isinstance(linked, CObject) and not isinstance(linked, CLink):
            if isinstance(linked, CClass):
                linked_ = linked.class_object
            else:
                raise CException(f"'{linked!s}' is not an object, class, or link")
        result.extend(linked_.links)
    return result
