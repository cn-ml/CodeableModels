import nose
from nose.tools import ok_, eq_

from codeable_models import CBundle, CStereotype, CMetaclass, CClass, CException, CEnum
from tests.testing_commons import exception_expected_


class TestBundlesOfStereotypes:
    def setup(self):
        self.mcl = CMetaclass("MCL")
        self.b1 = CBundle("B1")
        self.b2 = CBundle("B2")
        self.m1 = CMetaclass("M1")
        self.m2 = CMetaclass("M2")
        self.a = self.m1.association(self.m2, name="A", multiplicity="1", role_name="m1",
                                     source_multiplicity="*", source_role_name="m2")

    def test_stereotype_name_fail(self):
        try:
            # noinspection PyTypeChecker
            CStereotype(self.b1)
            exception_expected_()
        except CException as e:
            ok_(e.value.startswith("is not a name string: '"))
            ok_(e.value.endswith(" B1'"))

    def test_stereotype_defined_bundles(self):
        eq_(set(self.b1.get_elements(type=CStereotype)), set())
        s1 = CStereotype("s1", bundles=self.b1)
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1})
        s2 = CStereotype("s2", bundles=[self.b1])
        s3 = CStereotype("s3", bundles=[self.b1, self.b2])
        cl = CClass(self.mcl, "C", bundles=self.b1)
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1, s2, s3})
        eq_(set(self.b1.elements), {s1, s2, s3, cl})
        eq_(set(self.b2.get_elements(type=CStereotype)), {s3})
        eq_(set(self.b2.elements), {s3})

    def test_bundle_defined_stereotype(self):
        s1 = CStereotype("s1")
        s2 = CStereotype("s2")
        s3 = CStereotype("s3")
        eq_(set(self.b1.get_elements(type=CStereotype)), set())
        b1 = CBundle("B1", elements=[s1, s2, s3])
        eq_(set(b1.elements), {s1, s2, s3})
        cl = CClass(self.mcl, "C", bundles=b1)
        eq_(set(b1.elements), {s1, s2, s3, cl})
        eq_(set(b1.get_elements(type=CStereotype)), {s1, s2, s3})
        b2 = CBundle("B2")
        b2.elements = [s2, s3]
        eq_(set(b2.get_elements(type=CStereotype)), {s2, s3})
        eq_(set(s1.bundles), {b1})
        eq_(set(s2.bundles), {b1, b2})
        eq_(set(s3.bundles), {b1, b2})

    def test_get_stereotypes_by_name(self):
        eq_(set(self.b1.get_elements(type=CStereotype, name="s1")), set())
        s1 = CStereotype("s1", bundles=self.b1)
        c1 = CClass(self.mcl, "C1", bundles=self.b1)
        eq_(self.b1.get_elements(type=CClass), [c1])
        eq_(set(self.b1.get_elements(type=CStereotype, name="s1")), {s1})
        s2 = CStereotype("s1", bundles=self.b1)
        eq_(set(self.b1.get_elements(type=CStereotype, name="s1")), {s1, s2})
        ok_(s1 != s2)
        s3 = CStereotype("s1", bundles=self.b1)
        eq_(set(self.b1.get_elements(type=CStereotype, name="s1")), {s1, s2, s3})
        eq_(self.b1.get_element(type=CStereotype, name="s1"), s1)

    def test_get_stereotype_elements_by_name(self):
        eq_(set(self.b1.get_elements(name="s1")), set())
        s1 = CStereotype("s1", bundles=self.b1)
        eq_(set(self.b1.get_elements(name="s1")), {s1})
        c1 = CClass(self.mcl, "s1", bundles=self.b1)
        eq_(set(self.b1.get_elements(name="s1")), {s1, c1})
        s2 = CStereotype("s1", bundles=self.b1)
        eq_(set(self.b1.get_elements(name="s1")), {s1, c1, s2})
        ok_(s1 != s2)
        s3 = CStereotype("s1", bundles=self.b1)
        eq_(set(self.b1.get_elements(name="s1")), {s1, c1, s2, s3})
        eq_(self.b1.get_element(name="s1"), s1)

    def test_stereotype_defined_bundle_change(self):
        s1 = CStereotype("s1", bundles=self.b1)
        s2 = CStereotype("s2", bundles=self.b1)
        s3 = CStereotype("s3", bundles=self.b1)
        cl1 = CClass(self.mcl, "C1", bundles=self.b1)
        cl2 = CClass(self.mcl, "C2", bundles=self.b1)
        b = CBundle()
        s2.bundles = b
        s3.bundles = None
        cl2.bundles = b
        eq_(set(self.b1.elements), {cl1, s1})
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1})
        eq_(set(b.elements), {s2, cl2})
        eq_(set(b.get_elements(type=CStereotype)), {s2})
        eq_(s1.bundles, [self.b1])
        eq_(s2.bundles, [b])
        eq_(s3.bundles, [])

    def test_bundle_delete_stereotype_metaclass(self):
        s1 = CStereotype("s1", bundles=self.b1, extended=self.mcl)
        eq_(s1.extended, [self.mcl])
        s2 = CStereotype("s2", bundles=self.b1)
        s3 = CStereotype("s3", bundles=self.b1)
        self.b1.delete()
        eq_(set(self.b1.elements), set())
        eq_(s1.bundles, [])
        eq_(s1.extended, [self.mcl])
        eq_(s2.bundles, [])
        eq_(s3.bundles, [])

    def test_bundle_delete_stereotype_association(self):
        s1 = CStereotype("s1", bundles=self.b1, extended=self.a)
        eq_(s1.extended, [self.a])
        s2 = CStereotype("s2", bundles=self.b1)
        s3 = CStereotype("s3", bundles=self.b1)
        self.b1.delete()
        eq_(set(self.b1.elements), set())
        eq_(s1.bundles, [])
        eq_(s1.extended, [self.a])
        eq_(s2.bundles, [])
        eq_(s3.bundles, [])

    def test_creation_of_unnamed_stereotype_in_bundle(self):
        cl = CClass(self.mcl)
        s1 = CStereotype()
        s2 = CStereotype()
        s3 = CStereotype("x")
        self.b1.elements = [s1, s2, s3, cl]
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1, s2, s3})
        eq_(self.b1.get_element(name=None), s1)
        eq_(set(self.b1.get_elements(type=CStereotype, name=None)), {s1, s2})
        eq_(self.b1.get_element(name=None), s1)
        eq_(set(self.b1.get_elements(name=None)), {s1, s2, cl})

    def test_remove_stereotype_from_bundle(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        s1 = CStereotype("s1", bundles=b1)
        try:
            # noinspection PyTypeChecker
            b1.remove(None)
            exception_expected_()
        except CException as e:
            eq_("'None' is not an element of the bundle", e.value)
        try:
            b1.remove(CEnum("A"))
            exception_expected_()
        except CException as e:
            eq_("'A' is not an element of the bundle", e.value)
        try:
            b2.remove(s1)
            exception_expected_()
        except CException as e:
            eq_("'s1' is not an element of the bundle", e.value)
        b1.remove(s1)
        eq_(set(b1.get_elements(type=CStereotype)), set())

        s1 = CStereotype("s1", bundles=b1)
        s2 = CStereotype("s1", bundles=b1)
        s3 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, bundles=b1, extended=self.mcl)
        s4 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, bundles=b1, extended=self.a)

        b1.remove(s1)
        try:
            b1.remove(CStereotype("s2", bundles=b2))
            exception_expected_()
        except CException as e:
            eq_("'s2' is not an element of the bundle", e.value)
        try:
            b1.remove(s1)
            exception_expected_()
        except CException as e:
            eq_("'s1' is not an element of the bundle", e.value)

        eq_(set(b1.get_elements(type=CStereotype)), {s2, s3, s4})
        b1.remove(s3)
        b1.remove(s4)
        eq_(set(b1.get_elements(type=CStereotype)), {s2})

        eq_(s3.superclasses, [s2])
        eq_(s2.subclasses, [s3, s4])
        eq_(s3.attribute_names, ["i"])
        eq_(s3.extended, [self.mcl])
        eq_(s3.name, "s1")
        eq_(s3.bundles, [])
        eq_(s4.superclasses, [s2])
        eq_(s4.attribute_names, ["i"])
        eq_(s4.extended, [self.a])
        eq_(s4.name, "s1")
        eq_(s4.bundles, [])

    def test_delete_stereotype_from_bundle(self):
        b1 = CBundle("B1")
        s1 = CStereotype("s1", bundles=b1)
        s1.delete()
        eq_(set(b1.get_elements(type=CStereotype)), set())

        s1 = CStereotype("s1", bundles=b1)
        s2 = CStereotype("s1", bundles=b1)
        s3 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, bundles=b1, extended=self.mcl)
        s4 = CStereotype("s1", superclasses=s2, attributes={"i": 1}, bundles=b1, extended=self.a)

        s1.delete()
        eq_(set(b1.get_elements(type=CStereotype)), {s2, s3, s4})
        s3.delete()
        s4.delete()
        eq_(set(b1.get_elements(type=CStereotype)), {s2})

        eq_(s3.superclasses, [])
        eq_(s2.subclasses, [])
        eq_(s3.attributes, [])
        eq_(s3.attribute_names, [])
        eq_(s3.extended, [])
        eq_(s3.name, None)
        eq_(s3.bundles, [])

        eq_(s4.superclasses, [])
        eq_(s4.attributes, [])
        eq_(s4.attribute_names, [])
        eq_(s4.extended, [])
        eq_(s4.name, None)
        eq_(s4.bundles, [])

    def test_remove_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        s1 = CStereotype("s1", bundles=[b1, b2])
        b1.remove(s1)
        eq_(set(b1.get_elements(type=CStereotype)), set())
        eq_(set(b2.get_elements(type=CStereotype)), {s1})
        eq_(set(s1.bundles), {b2})

    def test_delete_bundle_from_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        s1 = CStereotype("s1", bundles=[b1, b2])
        b1.delete()
        eq_(set(b1.get_elements(type=CStereotype)), set())
        eq_(set(b2.get_elements(type=CStereotype)), {s1})
        eq_(set(s1.bundles), {b2})

    def test_delete_stereotype_having_two_bundles(self):
        b1 = CBundle("B1")
        b2 = CBundle("B2")
        s1 = CStereotype("s1", bundles=[b1, b2])
        s2 = CStereotype("s2", bundles=[b2])
        s1.delete()
        eq_(set(b1.get_elements(type=CStereotype)), set())
        eq_(set(b2.get_elements(type=CStereotype)), {s2})
        eq_(set(s1.bundles), set())
        eq_(set(s2.bundles), {b2})

    def test_stereotype_remove_stereotype_or_metaclass(self):
        mcl = CMetaclass("MCL1")
        s1 = CStereotype("S1", extended=[mcl])
        s2 = CStereotype("S2", extended=[mcl])
        s3 = CStereotype("S3", extended=[mcl])
        s4 = CStereotype("S4", extended=[mcl])
        self.b1.elements = [mcl, s1, s2, s3, s4]
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1, s2, s3, s4})
        s2.delete()
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1, s3, s4})
        eq_(set(s2.extended), set())
        eq_(set(s1.extended), {mcl})
        mcl.delete()
        eq_(set(mcl.stereotypes), set())
        eq_(set(s1.extended), set())
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1, s3, s4})

    def test_double_assignment_stereotype_extension_metaclass(self):
        try:
            CStereotype("S1", bundles=self.b1, extended=[self.mcl, self.mcl])
            exception_expected_()
        except CException as e:
            eq_("'MCL' is already extended by stereotype 'S1'", e.value)
        s1 = self.b1.get_element(type=CStereotype, name="S1")
        eq_(s1.name, "S1")
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1})
        eq_(s1.bundles, [self.b1])
        eq_(self.mcl.stereotypes, [s1])

    def test_double_assignment_stereotype_extension_association(self):
        try:
            CStereotype("S1", bundles=self.b1, extended=[self.a, self.a])
            exception_expected_()
        except CException as e:
            eq_("'A' is already extended by stereotype 'S1'", e.value)
        s1 = self.b1.get_element(type=CStereotype, name="S1")
        eq_(s1.name, "S1")
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1})
        eq_(s1.bundles, [self.b1])
        eq_(self.a.stereotypes, [s1])

    def test_double_assignment_metaclass_stereotype(self):
        try:
            s1 = CStereotype("S1", bundles=self.b1)
            self.mcl.stereotypes = [s1, s1]
            exception_expected_()
        except CException as e:
            eq_("'S1' is already a stereotype of 'MCL'", e.value)
        s1 = self.b1.get_element(type=CStereotype, name="S1")
        eq_(s1.name, "S1")
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1})

    def test_double_assignment_association_stereotype(self):
        try:
            s1 = CStereotype("S1", bundles=self.b1)
            self.a.stereotypes = [s1, s1]
            exception_expected_()
        except CException as e:
            eq_("'S1' is already a stereotype of 'A'", e.value)
        s1 = self.b1.get_element(type=CStereotype, name="S1")
        eq_(s1.name, "S1")
        eq_(set(self.b1.get_elements(type=CStereotype)), {s1})

    def test_bundle_that_is_deleted(self):
        b1 = CBundle("B1")
        b1.delete()
        try:
            CStereotype("S1", bundles=b1)
            exception_expected_()
        except CException as e:
            eq_(e.value, "cannot access named element that has been deleted")

    def test_set_bundle_to_none(self):
        s = CStereotype("S1", bundles=None)
        eq_(s.bundles, [])
        eq_(s.name, "S1")


if __name__ == "__main__":
    nose.main()
