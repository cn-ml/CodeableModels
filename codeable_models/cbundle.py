from typing import Any, Dict, List, Optional, TypedDict, Unpack
from codeable_models import CBundlable
from codeable_models.cbundlable import ConnectedElementsContext
from codeable_models.cexception import CException
from codeable_models.cnamedelement import CNamedElement
from codeable_models.internal.commons import check_named_element_is_not_deleted


class CBundle(CBundlable):
    def __init__(self, name: Optional[str]=None, **kwargs: dict[str, Any]):
        """
        ``CBundle`` is used to manage bundles, i.e., groups of modelling elements in Codeable Models.

        **Superclasses:**  :py:class:`.CBundlable`

        Args:
           name (str): An optional name.
           **kwargs: Pass in any kwargs acceptable to superclasses. In addition, ``CBundle`` accepts:
                ``elements``.

                - The ``elements`` kwarg accepts a list of elements (same format as the ``elements`` property).

        All kinds of modelling elements in Codeable Models that inherit from :py:class:`.CBundlable`
        can be placed in a bundle, including bundles themselves.
        Thus bundles can be composed recursively in order to model composite structures. The relations of
        ``CBundle`` are shown in the figure below.

        .. image:: ../images/bundles_model.png

        For example, the following code creates the bundle of classes used to generate the figure above::

            bundles_model = CBundle("bundles_model", elements=[cbundlable, cbundle, cenum,
                                    cobject, cclassifier, cclass, cmetaclass, cstereotype, cassociation, clink])

        """
        self.elements_: List[CBundlable] = []
        super().__init__(name, **kwargs)

    def _init_keyword_args(self, legal_keyword_args: Optional[List[str]]=None, **kwargs: dict[str, Any]):
        if legal_keyword_args is None:
            legal_keyword_args = []
        legal_keyword_args.append("elements")
        super()._init_keyword_args(legal_keyword_args, **kwargs)

    def add(self, elt: CBundlable):
        """
        Add an element to the bundle.

        Args:
            elt (CBundlable): Element to add to the bundle

        Returns:
            None

        """
        if elt in self.elements_:
            raise CException(f"element '{elt!s}' cannot be added to bundle: element is already in bundle")
        self.elements_.append(elt)
        elt.bundles_.append(self)

    def remove(self, element: CBundlable):
        """
        Remove an element from the bundle.

        Args:
            element (CBundlable): Element to remove from the bundle.

        Returns:
            None

        """
        if (element is None or
                (self not in element.bundles)):
            raise CException(f"'{element!s}' is not an element of the bundle")
        self.elements_.remove(element)
        element.bundles_.remove(self)

    def delete(self):
        """
        Delete the bundle. Delete all elements from the bundle.
        Calls ``delete()`` on superclass.

        Returns:
            None
        """
        if self.is_deleted:
            return
        elements_to_delete = list(self.elements_)
        for e in elements_to_delete:
            e.bundles_.remove(self)
        self.elements_ = []
        super().delete()

    @property
    def elements(self):
        """List[CBundlable]: Getter and setter for the elements of the bundle.
        """
        return list(self.elements_)

    @elements.setter
    def elements(self, elements: List[CBundlable] | CBundlable):
        if elements is None:
            elements = []
        for e in self.elements_:
            e.bundles = None
        self.elements_ = []
        if isinstance(elements, CNamedElement):
            elements = [elements]
        for e in elements:
            if e is not None:
                check_named_element_is_not_deleted(e)
            else:
                raise CException(f"'None' cannot be an element of bundle")
            if e not in self.elements_:
                # if it is already in the bundle, do not add it twice
                self.elements_.append(e)
                # noinspection PyUnresolvedReferences
                e.bundles_.append(self)

    class GetElementsArgs(TypedDict, total=False):
        name: str
        type: type

    def get_elements(self, **kwargs: Unpack[GetElementsArgs]):
        """
        Get specific elements from the bundle. Per default returns all elements.

        Args:
            **kwargs: Used to specify in more detail which elements to get from the bundle. Accepts the
                following arguments:

                - ``type``: Return only elements which are instances of the specified type.
                - ``name``: Return only elements with the specified name.

        Returns:
            List[CBundlable]: List of elements.

        """
        type_ = kwargs.get("type")
        name = kwargs.get("name")
        # use this as name can also be provided as None
        name_specified = name is not None
        elements: List[CBundlable] = []
        for elt in self.elements_:
            append = True
            if name_specified and elt.name != name:
                append = False
            # noinspection PyTypeHints
            if type_ is not None and not isinstance(elt, type_):
                append = False
            if append:
                elements.append(elt)
        return elements

    def get_element(self, **kwargs: GetElementsArgs):
        """
          Get a specific element from the bundle. Returns the first found element, if more than one are found.
          Returns ``None`` if none is found.

          Args:
              **kwargs: Used to specify in more detail which elements to get from the bundle. Accepts the
                arguments acceptable to ``get_elements()``.

          Returns:
              CBundlable: The element of the bundle.

          """
        elements = self.get_elements(**kwargs)
        return next(iter(elements), None)

    def compute_connected_(self, context: ConnectedElementsContext):
        super().compute_connected_(context)
        if not context.process_bundles:
            return
        connected: List[CBundlable] = []
        for element in self.elements_:
            if element not in context.stop_elements_exclusive:
                connected.append(element)
        self.append_connected_(context, connected)


class CPackage(CBundle):
    def __init__(self, name: Optional[str]=None, **kwargs: Dict[str, Any]):
        """
        Simple class to designate bundles as packages.

        **Superclasses:**  :py:class:`.CBundle`
        """
        super().__init__(name, **kwargs)


class CLayer(CBundle):
    def __init__(self, name: Optional[str]=None, **kwargs: Dict[str, Any]):
        """
        Simple class to designate bundles as layers, and manage sub-/super-layer relations.

        **Superclasses:**  :py:class:`.CBundle`

        Args:
           name (str): An optional name.
           **kwargs: Pass in any kwargs acceptable to superclasses. In addition, ``CLayer`` accepts:
                ``sub_layer`` and ``super_layer``.

                - The ``sub_layer`` kwarg accepts a ``CLayer`` as a sub layer (same as the same-named property).
                - The ``super_layer`` kwarg accepts a ``CLayer`` as a super layer (same as the same-named property).

        """
        self._sub_layer: Optional["CLayer"] = None
        self._super_layer: Optional["CLayer"] = None
        super().__init__(name, **kwargs)

    def _init_keyword_args(self, legal_keyword_args: Optional[List[str]]=None, **kwargs: Dict[str, Any]):
        if legal_keyword_args is None:
            legal_keyword_args = []
        legal_keyword_args.append("sub_layer")
        legal_keyword_args.append("super_layer")
        super()._init_keyword_args(legal_keyword_args, **kwargs)

    @property
    def sub_layer(self: "CLayer"):
        """CLayer: Accepts a ``CLayer`` as a sub layer.
        """
        return self._sub_layer

    @sub_layer.setter
    def sub_layer(self, layer: "CLayer"):
        if self._sub_layer is not None:
            self._sub_layer._super_layer = None
        self._sub_layer = layer
        if layer is not None:
            if layer._super_layer is not None:
                layer._super_layer._sub_layer = None
            layer._super_layer = self

    @property
    def super_layer(self):
        """CLayer: Accepts a ``CLayer`` as a super layer.
        """
        return self._super_layer

    @super_layer.setter
    def super_layer(self, layer: "CLayer"):
        if self._super_layer is not None:
            self._super_layer._sub_layer = None
        self._super_layer = layer
        if layer is not None:
            if layer._sub_layer is not None:
                layer._sub_layer._super_layer = None
            layer._sub_layer = self
