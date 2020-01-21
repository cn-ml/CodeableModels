import re

import nose
from nose.tools import ok_, eq_

from codeable_models import CMetaclass, CStereotype, CClass, CObject, CException
from tests.testing_commons import exception_expected_


class TestClassInheritance:
    def setup(self):
        self.mcl = CMetaclass("MCL")

    def test_class_no_inheritance(self):
        t = CClass(self.mcl, "T")
        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), set())
        eq_(set(t.all_superclasses), set())
        eq_(set(t.all_subclasses), set())

    def test_class_superclasses_empty_input(self):
        m1 = CClass(self.mcl, "M1", superclasses=[])
        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), set())

    def test_class_superclasses_none_input(self):
        m1 = CClass(self.mcl, "M1", superclasses=None)
        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), set())

    def test_class_simple_inheritance(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=t)
        m2 = CClass(self.mcl, "M2", superclasses=t)
        b1 = CClass(self.mcl, "B1", superclasses=m1)
        b2 = CClass(self.mcl, "B2", superclasses=m1)
        b3 = CClass(self.mcl, "B3", superclasses=t)

        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), {m1, m2, b3})
        eq_(set(t.all_superclasses), set())
        eq_(set(t.all_subclasses), {m1, m2, b1, b2, b3})

        eq_(set(m1.superclasses), {t})
        eq_(set(m1.subclasses), {b1, b2})
        eq_(set(m1.all_superclasses), {t})
        eq_(set(m1.all_subclasses), {b1, b2})

        eq_(set(m2.superclasses), {t})
        eq_(set(m2.subclasses), set())
        eq_(set(m2.all_superclasses), {t})
        eq_(set(m2.all_subclasses), set())

        eq_(set(b1.superclasses), {m1})
        eq_(set(b1.subclasses), set())
        eq_(set(b1.all_superclasses), {t, m1})
        eq_(set(b1.all_subclasses), set())

        eq_(set(b2.superclasses), {m1})
        eq_(set(b2.subclasses), set())
        eq_(set(b2.all_superclasses), {t, m1})
        eq_(set(b2.all_subclasses), set())

        eq_(set(b3.superclasses), {t})
        eq_(set(b3.subclasses), set())
        eq_(set(b3.all_superclasses), {t})
        eq_(set(b3.all_subclasses), set())

    def test_class_inheritance_double_assignment(self):
        t = CClass(self.mcl, "T")
        try:
            CClass(self.mcl, "C1", superclasses=[t, t])
            exception_expected_()
        except CException as e:
            eq_("'T' is already a superclass of 'C1'", e.value)
        c1 = self.mcl.get_class("C1")
        eq_(c1.metaclass, self.mcl)
        eq_(c1.name, "C1")
        eq_(t.name, "T")
        eq_(set(c1.superclasses), {t})

    def test_class_inheritance_delete_top_class(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t])

        t.delete()

        eq_(t.name, None)
        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), set())
        eq_(set(t.all_superclasses), set())
        eq_(set(t.all_subclasses), set())

        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), {b1, b2})
        eq_(set(m1.all_superclasses), set())
        eq_(set(m1.all_subclasses), {b1, b2})

        eq_(set(m2.superclasses), set())
        eq_(set(m2.subclasses), set())
        eq_(set(m2.all_superclasses), set())
        eq_(set(m2.all_subclasses), set())

        eq_(set(b1.superclasses), {m1})
        eq_(set(b1.subclasses), set())
        eq_(set(b1.all_superclasses), {m1})
        eq_(set(b1.all_subclasses), set())

        eq_(set(b2.superclasses), {m1})
        eq_(set(b2.subclasses), set())
        eq_(set(b2.all_superclasses), {m1})
        eq_(set(b2.all_subclasses), set())

        eq_(set(b3.superclasses), set())
        eq_(set(b3.subclasses), set())
        eq_(set(b3.all_superclasses), set())
        eq_(set(b3.all_subclasses), set())

    def test_class_inheritance_delete_inner_class(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t])

        m1.delete()

        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), {m2, b3})
        eq_(set(t.all_superclasses), set())
        eq_(set(t.all_subclasses), {m2, b3})

        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), set())
        eq_(set(m1.all_superclasses), set())
        eq_(set(m1.all_subclasses), set())

        eq_(set(m2.superclasses), {t})
        eq_(set(m2.subclasses), set())
        eq_(set(m2.all_superclasses), {t})
        eq_(set(m2.all_subclasses), set())

        eq_(set(b1.superclasses), set())
        eq_(set(b1.subclasses), set())
        eq_(set(b1.all_superclasses), set())
        eq_(set(b1.all_subclasses), set())

        eq_(set(b2.superclasses), set())
        eq_(set(b2.subclasses), set())
        eq_(set(b2.all_superclasses), set())
        eq_(set(b2.all_subclasses), set())

        eq_(set(b3.superclasses), {t})
        eq_(set(b3.subclasses), set())
        eq_(set(b3.all_superclasses), {t})
        eq_(set(b3.all_subclasses), set())

    def test_class_superclasses_reassignment(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t])

        m1.superclasses = []
        b1.superclasses = []
        b2.superclasses = []

        eq_(set(t.superclasses), set())
        eq_(set(t.subclasses), {m2, b3})
        eq_(set(t.all_superclasses), set())
        eq_(set(t.all_subclasses), {m2, b3})

        eq_(set(m1.superclasses), set())
        eq_(set(m1.subclasses), set())
        eq_(set(m1.all_superclasses), set())
        eq_(set(m1.all_subclasses), set())

        eq_(set(m2.superclasses), {t})
        eq_(set(m2.subclasses), set())
        eq_(set(m2.all_superclasses), {t})
        eq_(set(m2.all_subclasses), set())

        eq_(set(b1.superclasses), set())
        eq_(set(b1.subclasses), set())
        eq_(set(b1.all_superclasses), set())
        eq_(set(b1.all_subclasses), set())

        eq_(set(b2.superclasses), set())
        eq_(set(b2.subclasses), set())
        eq_(set(b2.all_superclasses), set())
        eq_(set(b2.all_subclasses), set())

        eq_(set(b3.superclasses), {t})
        eq_(set(b3.subclasses), set())
        eq_(set(b3.all_superclasses), {t})
        eq_(set(b3.all_subclasses), set())

    def test_class_multiple_inheritance(self):
        t1 = CClass(self.mcl, "T1")
        t2 = CClass(self.mcl, "T2")
        t3 = CClass(self.mcl, "T3")
        m1 = CClass(self.mcl, "M1", superclasses=[t1, t3])
        m2 = CClass(self.mcl, "M2", superclasses=[t2, t3])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1, m2])
        b3 = CClass(self.mcl, "B3", superclasses=[m2, m1])

        eq_(set(t1.superclasses), set())
        eq_(set(t1.subclasses), {m1})
        eq_(set(t1.all_superclasses), set())
        eq_(set(t1.all_subclasses), {m1, b1, b2, b3})

        eq_(set(t2.superclasses), set())
        eq_(set(t2.subclasses), {m2})
        eq_(set(t2.all_superclasses), set())
        eq_(set(t2.all_subclasses), {m2, b3, b2})

        eq_(set(t3.superclasses), set())
        eq_(set(t3.subclasses), {m2, m1})
        eq_(set(t3.all_superclasses), set())
        eq_(set(t3.all_subclasses), {m2, m1, b1, b2, b3})

        eq_(set(m1.superclasses), {t1, t3})
        eq_(set(m1.subclasses), {b1, b2, b3})
        eq_(set(m1.all_superclasses), {t1, t3})
        eq_(set(m1.all_subclasses), {b1, b2, b3})

        eq_(set(m2.superclasses), {t2, t3})
        eq_(set(m2.subclasses), {b2, b3})
        eq_(set(m2.all_superclasses), {t2, t3})
        eq_(set(m2.all_subclasses), {b2, b3})

        eq_(set(b1.superclasses), {m1})
        eq_(set(b1.subclasses), set())
        eq_(set(b1.all_superclasses), {m1, t1, t3})
        eq_(set(b1.all_subclasses), set())

        eq_(set(b2.superclasses), {m1, m2})
        eq_(set(b2.subclasses), set())
        eq_(set(b2.all_superclasses), {m1, m2, t1, t2, t3})
        eq_(set(b2.all_subclasses), set())

        eq_(set(b3.superclasses), {m1, m2})
        eq_(set(b3.subclasses), set())
        eq_(set(b3.all_superclasses), {m1, m2, t1, t2, t3})
        eq_(set(b3.all_subclasses), set())

    def test_class_as_wrong_type_of_superclass(self):
        t = CClass(self.mcl, "C")
        try:
            CMetaclass("M", superclasses=[t])
            exception_expected_()
        except CException as e:
            ok_(re.match("^cannot add superclass 'C' to 'M': not of type([_ <a-zA-Z.']+)CMetaclass'>$", e.value))
        try:
            CStereotype("S", superclasses=[t])
            exception_expected_()
        except CException as e:
            ok_(re.match("^cannot add superclass 'C' to 'S': not of type([_ <a-zA-Z.']+)CStereotype'>$", e.value))

    def test_class_path_no_inheritance(self):
        t = CClass(self.mcl)
        eq_(set(t.class_path), {t})

    def test_class_path_simple_inheritance(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1])
        b2 = CClass(self.mcl, "B2", superclasses=[m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t])
        eq_(b1.class_path, [b1, m1, t])
        eq_(b2.class_path, [b2, m1, t])
        eq_(b3.class_path, [b3, t])
        eq_(m1.class_path, [m1, t])
        eq_(m2.class_path, [m2, t])
        eq_(t.class_path, [t])

    def test_class_path_multiple_inheritance(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1, m2])
        b2 = CClass(self.mcl, "B2", superclasses=[t, m1])
        b3 = CClass(self.mcl, "B3", superclasses=[t, m1, m2])
        eq_(b1.class_path, [b1, m1, t, m2])
        eq_(b2.class_path, [b2, t, m1])
        eq_(b3.class_path, [b3, t, m1, m2])
        eq_(m1.class_path, [m1, t])
        eq_(m2.class_path, [m2, t])
        eq_(t.class_path, [t])

    def test_class_instance_of(self):
        a = CClass(self.mcl)
        b = CClass(self.mcl, superclasses=[a])
        c = CClass(self.mcl)
        o = CObject(b, "o")

        eq_(o.instance_of(a), True)
        eq_(o.instance_of(b), True)
        eq_(o.instance_of(c), False)

        try:
            o.instance_of(o)
            exception_expected_()
        except CException as e:
            eq_("'o' is not a class", e.value)

        o.delete()
        eq_(o.instance_of(a), False)

    def test_class_get_all_instances(self):
        t = CClass(self.mcl, "T")
        m1 = CClass(self.mcl, "M1", superclasses=[t])
        m2 = CClass(self.mcl, "M2", superclasses=[t])
        b1 = CClass(self.mcl, "B1", superclasses=[m1, m2])
        to1 = CObject(t)
        to2 = CObject(t)
        m1o1 = CObject(m1)
        m1o2 = CObject(m1)
        m2o = CObject(m2)
        b1o1 = CObject(b1)
        b1o2 = CObject(b1)

        eq_(set(t.objects), {to1, to2})
        eq_(set(t.all_objects), {to1, to2, m1o1, m1o2, b1o1, b1o2, m2o})
        eq_(set(m1.objects), {m1o1, m1o2})
        eq_(set(m1.all_objects), {m1o1, m1o2, b1o1, b1o2})
        eq_(set(m2.objects), {m2o})
        eq_(set(m2.all_objects), {m2o, b1o1, b1o2})
        eq_(set(b1.objects), {b1o1, b1o2})
        eq_(set(b1.all_objects), {b1o1, b1o2})

    def test_class_has_superclass_has_subclass(self):
        c1 = CClass(self.mcl, "C1")
        c2 = CClass(self.mcl, "C2", superclasses=[c1])
        c3 = CClass(self.mcl, "C3", superclasses=[c2])
        c4 = CClass(self.mcl, "C4", superclasses=[c2])
        c5 = CClass(self.mcl, "C5", superclasses=[])

        eq_(c1.has_superclass(c2), False)
        eq_(c5.has_superclass(c2), False)
        eq_(c1.has_superclass(None), False)
        eq_(c5.has_superclass(None), False)
        eq_(c2.has_superclass(c1), True)
        eq_(c3.has_superclass(c2), True)
        eq_(c3.has_superclass(c2), True)
        eq_(c4.has_superclass(c2), True)
        eq_(c3.has_subclass(c2), False)
        eq_(c3.has_subclass(None), False)
        eq_(c5.has_subclass(c2), False)
        eq_(c5.has_subclass(None), False)
        eq_(c1.has_subclass(c3), True)
        eq_(c1.has_subclass(c2), True)

    def test_class_unknown_non_positional_argument(self):
        t = CClass(self.mcl, "T")
        try:
            CClass(self.mcl, "ST", superclass=t)
            exception_expected_()
        except CException as e:
            eq_("unknown keyword argument 'superclass', should be one of: " +
                "['stereotype_instances', 'values', 'tagged_values', 'attributes', 'superclasses', 'bundles']",
                e.value)

    def test_superclasses_that_are_deleted(self):
        c1 = CClass(self.mcl, "C1")
        c1.delete()
        try:
            CClass(self.mcl, superclasses=[c1])
            exception_expected_()
        except CException as e:
            eq_(e.value, "cannot access named element that has been deleted")

    def test_superclasses_that_are_none(self):
        try:
            CClass(self.mcl, "C", superclasses=[None])
            exception_expected_()
        except CException as e:
            ok_(e.value.startswith("cannot add superclass 'None' to 'C': not of type"))


if __name__ == "__main__":
    nose.main()
