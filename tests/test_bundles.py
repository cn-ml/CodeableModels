import sys
sys.path.append("..")

import re

import nose
from nose.tools import ok_, eq_
from testCommons import neq_, exceptionExpected_


from codeableModels import CBundle, CMetaclass, CClass, CObject, CAttribute, CException, CEnum, CLayer, CPackage

class TestBundles():
    def setUp(self):
        self.mcl = CMetaclass("MCL")
        self.b1 = CBundle("B1")

    def testBundleNameFail(self):
        try:
            CBundle(self.mcl)
            exceptionExpected_()
        except CException as e:
            ok_(e.value.startswith("is not a name string: '"))
            ok_(e.value.endswith(" MCL'"))

    def testGetElementsWrongKwArg(self):
        try: 
            self.b1.getElements(x = CBundle)
            exceptionExpected_()
        except CException as e:
            eq_(e.value, "unknown argument to getElements: 'x'")

    def testGetElementWrongKwArg(self):
        try: 
            self.b1.getElement(x = CBundle)
            exceptionExpected_()
        except CException as e:
            eq_(e.value, "unknown argument to getElements: 'x'")

    def testPackageAndLayerSubclasses(self):
        layer1 = CLayer("L1")
        layer2 = CLayer("L2", subLayer = layer1)
        package1 = CPackage("P1")
        c1 = CClass(self.mcl, "C1")
        c2 = CClass(self.mcl, "C2")
        c3 = CClass(self.mcl, "C3")
        layer1.elements = [c1, c2]
        layer2.elements = [c3]
        package1.elements = [layer1, layer2] + layer1.elements + layer2.elements
        eq_(set(package1.elements), set([layer1, layer2, c1, c2, c3]))
        eq_(set(layer1.elements), set([c1, c2]))
        eq_(set(layer2.elements), set([c3]))
        eq_(set(c1.bundles), set([layer1, package1]))
        eq_(set(c2.bundles), set([layer1, package1]))
        eq_(set(c3.bundles), set([layer2, package1]))

    def testLayerSubLayers(self):
        layer1 = CLayer("L1")
        eq_(layer1.superLayer, None)
        eq_(layer1.subLayer, None)

        layer1 = CLayer("L1", subLayer = None)
        eq_(layer1.superLayer, None)
        eq_(layer1.subLayer, None)

        layer2 = CLayer("L2", subLayer = layer1)
        eq_(layer1.superLayer, layer2)
        eq_(layer1.subLayer, None)
        eq_(layer2.superLayer, None)
        eq_(layer2.subLayer, layer1)

        layer3 = CLayer("L3", subLayer = layer1)
        eq_(layer1.superLayer, layer3)
        eq_(layer1.subLayer, None)
        eq_(layer2.superLayer, None)
        eq_(layer2.subLayer, None)
        eq_(layer3.superLayer, None)
        eq_(layer3.subLayer, layer1)

        layer3.subLayer = layer2
        eq_(layer1.superLayer, None)
        eq_(layer1.subLayer, None)
        eq_(layer2.superLayer, layer3)
        eq_(layer2.subLayer, None)
        eq_(layer3.superLayer, None)
        eq_(layer3.subLayer, layer2)

        layer2.subLayer = layer1
        eq_(layer1.superLayer, layer2)
        eq_(layer1.subLayer, None)
        eq_(layer2.superLayer, layer3)
        eq_(layer2.subLayer, layer1)
        eq_(layer3.superLayer, None)
        eq_(layer3.subLayer, layer2)


    def testLayerSuperLayers(self):
        layer1 = CLayer("L1")
        eq_(layer1.superLayer, None)
        eq_(layer1.subLayer, None)

        layer1 = CLayer("L1", superLayer = None)
        eq_(layer1.superLayer, None)
        eq_(layer1.subLayer, None)

        layer2 = CLayer("L2", superLayer = layer1)
        eq_(layer1.superLayer, None)
        eq_(layer1.subLayer, layer2)
        eq_(layer2.superLayer, layer1)
        eq_(layer2.subLayer, None)

        layer3 = CLayer("L3", superLayer = layer1)
        eq_(layer1.superLayer, None)
        eq_(layer1.subLayer, layer3)
        eq_(layer2.superLayer, None)
        eq_(layer2.subLayer, None)
        eq_(layer3.superLayer, layer1)
        eq_(layer3.subLayer, None)

        layer3.superLayer = layer2
        eq_(layer1.superLayer, None)
        eq_(layer1.subLayer, None)
        eq_(layer2.superLayer, None)
        eq_(layer2.subLayer, layer3)
        eq_(layer3.superLayer, layer2)
        eq_(layer3.subLayer, None)

        layer2.superLayer = layer1
        eq_(layer1.superLayer, None)
        eq_(layer1.subLayer, layer2)
        eq_(layer2.superLayer, layer1)
        eq_(layer2.subLayer, layer3)
        eq_(layer3.superLayer, layer2)
        eq_(layer3.subLayer, None)

if __name__ == "__main__":
    nose.main()



