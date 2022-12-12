from typing import Any, List, Optional, Sequence, TypedDict, Unpack
from codeable_models.cassociation import CAssociation
from codeable_models.cobject import CObject
from codeable_models.clink import CLink
from codeable_models.cbundle import CBundle
from codeable_models.cclass import CClass
from codeable_models.cexception import CException
from codeable_models.cmetaclass import CMetaclass
from codeable_models.cnamedelement import CNamedElement, CNamedElementKwargs
from codeable_models.cstereotype import CStereotype
from codeable_models.internal.commons import ListOrSingle, set_keyword_args, check_named_element_is_not_deleted

class CBundlableKwargs(CNamedElementKwargs, total=False):
    bundles: ListOrSingle[CBundle]

class CBundlable(CNamedElement):
    def __init__(self, name: Optional[str], **kwargs: Unpack[CBundlableKwargs]):
        """``CBundlable`` is a superclass for all elements in Codeable Models that can be placed in a
        :py:class:`.CBundle`, which is used for grouping elements. Elements that can be bundled are
        :py:class:`.CClass`, :py:class:`.CObject`, etc.
        The class is usually not used directly but via its bundable subclasses.

        **Superclasses:**  :py:class:`.CNamedElement`

        Args:
           name (str): An optional name.
           **kwargs: Accepts keyword args defined as ``legal_keyword_args`` by subclasses.

        ``CBundlable`` is superclass of all classes that can be placed in a :py:class:`.CBundle` as shown in the
        figure below. Please note that bundles can be placed in bundles in order to model composite structures.

        .. image:: ../images/bundles_model.png
        """
        self.bundles_: List[CBundle] = []
        super().__init__(name, **kwargs)

    def _init_keyword_args(self, legal_keyword_args: Optional[List[str]]=None, **kwargs: dict[str, Any]):
        if legal_keyword_args is None:
            legal_keyword_args = []
        legal_keyword_args.append("bundles")
        super()._init_keyword_args(legal_keyword_args, **kwargs)

    @property
    def bundles(self):
        """ListOrSingle[CBundle]: Property that gets or sets the list of bundles this bundable element is part of.
        For the setter, ``None`` or ``[]`` can be used to remove the element from all bundles.
        In the setter, a single parameter of type :py:class:`.CBundle` will set this single bundle as the only
        bundle of the element. A list of bundles (i.e., list elements of
        type :py:class:`.CBundle`) will set the whole list."""
        return list(self.bundles_)

    @bundles.setter
    def bundles(self, bundles: Optional[ListOrSingle[CBundle]]):
        if bundles is None:
            bundles = []
        for b in self.bundles_:
            b.remove(self)
        self.bundles_ = []
        if isinstance(bundles, CBundle):
            bundles = [bundles]
        for b in bundles:
            check_named_element_is_not_deleted(b)
            if b in self.bundles_:
                raise CException(f"'{b.name!s}' is already a bundle of '{self.name!s}'")
            self.bundles_.append(b)
            b.elements_.append(self)

    def delete(self):
        """
        Delete the element and remove the element from all bundles it is part of.
        Calls ``delete()`` on superclass.

        Returns:
            None
        """
        if self.is_deleted:
            return
        bundles_to_delete = list(self.bundles_)
        for b in bundles_to_delete:
            b.remove(self)
        self.bundles_ = []
        super().delete()

    def get_connected_elements(self, **kwargs: dict[str, Any]) -> List["CBundlable"]:
        """Get all elements this element is connected to.

        Args:
            **kwargs: Configuration parameters for the method

        Returns:
            List[CBundlable]: List of connected elements.

        Per default associations and inheritance relations are included.
        Use the following ``**kwargs`` to specify which connections are included.

        - ``add_bundles`` (bool):
            Default value: False. If set to True, relations to
            bundles are included in the returned list.
        - ``process_bundles`` (bool):
            Default value: False. If set to True, elements in
            connected bundles will be processed and all elements in the bundle will be
            added recursively (i.e. their connections will be processed, too) to the returned list.
        - ``stop_elements_inclusive`` (list of CNamedElements):
            Default value: []. If set, searching will be
            stopped whenever an element on the list in encountered. The stop element will be added to the result.
        - ``stop_elements_exclusive`` (list of CNamedElements):
            Default value: []. If set, searching will be
            stopped whenever an element on the list in encountered. The stop element will not be added to the result.
        - ``add_stereotypes`` (bool):
            Default value: False. If set to True, relations to stereotypes are included
            in the returned list. The option is only applicable on :py:class:`.CMetaclass`,
            :py:class:`.CBundle`, or :py:class:`.CStereotype`.
        - ``process_stereotypes`` (bool):
            Default value: False. If set to True, relations to stereotypes will be
            processed and all elements connected to the stereotype will be added recursively
            (i.e. their connections will be processed, too) to the returned list.
            The option is only applicable on :py:class:`.CMetaclass`,
            :py:class:`.CBundle`, or :py:class:`.CStereotype`.
        - ``add_associations`` (bool):
            Default value: False. If set to True, relations to associations
            (i.e., the association objects) are included
            in the returned list.
            The option is only applicable on :py:class:`.CMetaclass`,
            :py:class:`.CClass`, or :py:class:`.CAssociation`.
        - ``add_links`` (bool):
            Default value: False. If set to True, relations to links
            (i.e., the link objects) are included
            in the returned list. The option is only applicable on :py:class:`.CObject` and  :py:class:`CLink`.
        """
        context = ConnectedElementsContext()

        allowed_keyword_args = ["add_bundles", "process_bundles", "stop_elements_inclusive",
                                "stop_elements_exclusive"]
        if isinstance(self, CMetaclass) or isinstance(self, CBundle) or isinstance(self, CStereotype):
            allowed_keyword_args = ["add_stereotypes", "process_stereotypes"] + allowed_keyword_args
        if isinstance(self, CMetaclass) or isinstance(self, CClass) or isinstance(self, CAssociation):
            allowed_keyword_args = ["add_associations"] + allowed_keyword_args
        if isinstance(self, CObject) or isinstance(self, CLink):
            allowed_keyword_args = ["add_links"] + allowed_keyword_args

        set_keyword_args(context, allowed_keyword_args, **kwargs)

        if self in context.stop_elements_exclusive:
            return []
        context.elements.append(self)
        self.compute_connected_(context)
        if not context.add_bundles:
            context.elements = [elt for elt in context.elements if not isinstance(elt, CBundle)]
        if not context.add_stereotypes:
            context.elements = [elt for elt in context.elements if not isinstance(elt, CStereotype)]
        if not context.add_associations:
            context.elements = [elt for elt in context.elements if not isinstance(elt, CAssociation)]
        if not context.add_links:
            context.elements = [elt for elt in context.elements if not isinstance(elt, CLink)]
        return context.elements

    @staticmethod
    def append_connected_(context: "ConnectedElementsContext", connected: Sequence["CBundlable"]):
        for c in connected:
            if c not in context.elements:
                context.elements.append(c)
                if c not in context.all_stop_elements:
                    c.compute_connected_(context)

    def compute_connected_(self, context: "ConnectedElementsContext"):
        connected: List[CBundlable] = []
        for bundle in self.bundles_:
            if bundle not in context.stop_elements_exclusive:
                connected.append(bundle)
        self.append_connected_(context, connected)


class ConnectedElementsContext(object):
    def __init__(self):
        self.elements: List[CBundlable] = []
        self.add_bundles = False
        self.add_associations = False
        self.add_links = False
        self.add_stereotypes = False
        self.process_bundles = False
        self.process_stereotypes = False
        self._stop_elements_inclusive: List[CBundlable] = []
        self._stop_elements_exclusive: List[CBundlable] = []
        self.all_stop_elements = []

    @property
    def stop_elements_inclusive(self):
        return list(self._stop_elements_inclusive)

    @stop_elements_inclusive.setter
    def stop_elements_inclusive(self, stop_elements_inclusive: List[CBundlable]):
        if isinstance(stop_elements_inclusive, CBundlable):
            stop_elements_inclusive = [stop_elements_inclusive]
        self._stop_elements_inclusive = stop_elements_inclusive
        self.all_stop_elements = self._stop_elements_inclusive + self._stop_elements_exclusive

    @property
    def stop_elements_exclusive(self):
        return list(self._stop_elements_exclusive)

    @stop_elements_exclusive.setter
    def stop_elements_exclusive(self, stop_elements_exclusive: List[CBundlable]):
        if isinstance(stop_elements_exclusive, CBundlable):
            stop_elements_exclusive = [stop_elements_exclusive]
        self._stop_elements_exclusive = stop_elements_exclusive
        self.all_stop_elements = self._stop_elements_inclusive + self._stop_elements_exclusive
