from typing import List, Optional
from codeable_models.cassociation import CAssociation
from codeable_models.cbundlable import CBundlable
from codeable_models.cclass import CClass
from codeable_models.clink import CLink
from codeable_models.cexception import CException
from codeable_models.cmetaclass import CMetaclass
from codeable_models.cstereotype import CStereotype
from codeable_models.internal.commons import check_is_cstereotype, check_named_element_is_not_deleted

CElementType = CClass | CLink | CAssociation

class CStereotypesHolder:
    def __init__(self, element: CElementType | CMetaclass):
        self.stereotypes_: List[CStereotype] = []
        self.element = element

    @property
    def stereotypes(self):
        return list(self.stereotypes_)

    @stereotypes.setter
    def stereotypes(self, elements: Optional[List[CStereotype] | CStereotype]):
        self._set_stereotypes(elements)

    # methods to be overridden in subclass
    def _remove_from_stereotype(self):
        for s in self.stereotypes_:
            s.extended_.remove(self.element)

    def _append_to_stereotype(self, stereotype: CStereotype):
        stereotype.extended_.append(self.element)

    def _check_stereotype_can_be_added(self, stereotype: CStereotype):
        if stereotype in self.stereotypes_:
            raise CException(f"'{stereotype.name!s}' is already a stereotype of '{self.element.name!s}'")

    def _init_extended_element(self, stereotype: CStereotype):
        pass

    # template method
    def _set_stereotypes(self, elements: Optional[List[CStereotype] | CStereotype]):
        if elements is None:
            elements = []
        self._remove_from_stereotype()
        self.stereotypes_ = []
        if isinstance(elements, CStereotype):
            elements = [elements]
        for s in elements:
            check_is_cstereotype(s)
            if s is not None:
                check_named_element_is_not_deleted(s)
                self._check_stereotype_can_be_added(s)
                self.stereotypes_.append(s)
                # noinspection PyTypeChecker
                self._append_to_stereotype(s)
                self._init_extended_element(s)


class CStereotypeInstancesHolder(CStereotypesHolder):
    def __init__(self, element: CElementType):
        super().__init__(element)

    def _set_all_default_tagged_values_of_stereotype(self, stereotype):
        for a in stereotype.attributes:
            if a.default is not None:
                self.element.set_tagged_value(a.name, a.default, stereotype)

    def _get_stereotype_instance_path_superclasses(self, stereotype: CStereotype):
        stereotype_path = [stereotype]
        for superclass in stereotype.superclasses:
            for superclassStereotype in self._get_stereotype_instance_path_superclasses(superclass):
                if superclassStereotype not in stereotype_path:
                    stereotype_path.append(superclassStereotype)
        return stereotype_path

    def get_stereotype_instance_path(self):
        stereotype_path: List[CStereotype] = []
        for stereotypeOfThisElement in self.stereotypes:
            for stereotype in self._get_stereotype_instance_path_superclasses(stereotypeOfThisElement):
                if stereotype not in stereotype_path:
                    stereotype_path.append(stereotype)
        return stereotype_path

    def _remove_from_stereotype(self):
        for s in self.stereotypes_:
            s.extended_instances_.remove(self.element)

    def _append_to_stereotype(self, stereotype):
        stereotype.extended_instances_.append(self.element)

    def _get_element_name_string(self):
        if isinstance(self.element, CClass):
            return f"'{self.element.name!s}'"
        elif isinstance(self.element, CLink):
            return f"link from '{self.element.source!s}' to '{self.element.target!s}'"
        elif isinstance(self.element, CAssociation):
            return f"association from '{self.element.source!s}' to '{self.element.target!s}'"
        raise CException(f"unexpected element type: {self.element!r}")

    def _check_stereotype_can_be_added(self, stereotype):
        if stereotype in self.stereotypes_:
            raise CException(
                f"'{stereotype.name!s}' is already a stereotype instance on {self._get_element_name_string()!s}")
        if not stereotype.is_element_extended_by_stereotype_(self.element):
            raise CException(f"stereotype '{stereotype!s}' cannot be added to " +
                             f"{self._get_element_name_string()!s}: no extension by this stereotype found")

    def _init_extended_element(self, stereotype):
        self._set_all_default_tagged_values_of_stereotype(stereotype)
        for sc in stereotype.all_superclasses:
            self._set_all_default_tagged_values_of_stereotype(sc)
