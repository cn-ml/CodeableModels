# import os
# import shutil
# from subprocess import call
from codeableModels import CException
from codeableModels.internal.commons import isCEnum, isCClassifier, setKeywordArgs, isCClass, isCObject
# from enum import Enum 
# from codeableModels import CNamedElement
from plantUMLRenderer.modelRenderer import RenderingContext, ModelRenderer

class ObjectRenderingContext(RenderingContext):
    def __init__(self):
        super().__init__()
        self.visitedLinks = set()
        self.renderAttributeValues = True
        self.renderEmptyAttributes = False
        self.renderLinkLabelsIfStereotyped = False
        self.excludedLinks = []

class ObjectModelRenderer(ModelRenderer):
    def renderObjectNameWithClassifier(self, object):
        objName = object.name
        if objName == None:
            objName = ""
        if isCClass(object):
            object = object.classObject

        sterotypeString = ""
        if object._classObjectClass != None:
            sterotypeString = self.renderStereotypes(object._classObjectClass, object._classObjectClass.stereotypeInstances)

        clName = object.classifier.name
        if clName == None:
            clName = ""
        return '"' + sterotypeString + self.padAndBreakName(objName + " : " + clName) + '"'

    def renderObjectSpecification(self, context, obj):
        context.addLine("class " + self.renderObjectNameWithClassifier(obj) + " as " + self.getNodeID(context, obj) + self.renderAttributeValues(context, obj))

    def renderAttributeValues(self, context, obj):
        if not context.renderAttributeValues:
            return ""
        attributeValueAdded = False
        attributeValueString = " {\n"
        for cl in obj.classPath:
            attributes = cl.attributes
            for attribute in attributes:
                name = attribute.name
                value = obj.getValue(name, cl)
                if not context.renderEmptyAttributes:
                    if value == None:
                        continue
                attributeValueAdded = True
                attributeValueString += self.renderAttributeValue(attribute, name, value) + "\n"
        attributeValueString += "}\n"
        if attributeValueAdded == False:
            attributeValueString = ""
        return attributeValueString

    def renderAttributeValue(self, attribute, name, value):
        type = attribute.type
        if type == str or isCEnum(type) or isCClassifier(type):
            value = '"' + value + '"'
        return name + " = " + value

    def renderLink(self, context, link):
        association = link.association 

        arrow = " --> "
        if association.aggregation:
            arrow = " o-- "
        elif association.composition:
            arrow = " *-- "

        sterotypeString = self.renderStereotypes(link, link.stereotypeInstances)

        label = ""
        if association.name != None and len(association.name) != 0:
            if not sterotypeString == "" and not context.renderLinkLabelsIfStereotyped:
                label = ": \"" + sterotypeString + "\" "
            else:
                label = ": \"" + sterotypeString + association.name + "\" "
        elif sterotypeString != "":
            label = ": \"" + sterotypeString + "\" "

        context.addLine(self.getNodeID(context, link.source) + arrow + self.getNodeID(context, link.target) + label)

    def renderLinks(self, context, obj, objList):
        for classifier in obj.classPath:
            for association in classifier.associations:
                links = [l for l in obj.linkObjects if l.association == association]
                for link in links:
                    if link in context.excludedLinks:
                        continue
                    source = link.source
                    if isCClass(source):
                        source = source.classObject
                    target = link.target
                    if isCClass(target):
                        target = target.classObject
                    if source != obj:
                        # only render links outgoing from this object
                        continue
                    if not link in context.visitedLinks:
                        context.visitedLinks.add(link)
                        if target in objList:
                            self.renderLink(context, link)

    def renderObjects(self, context, objects):
        objList = []
        for obj in objects:
            if isCClass(obj):
                # use class objects and not classes in this renderer
                objList.extend([obj._classObject])
            elif isCObject(obj):
                objList.extend([obj])
            else:
                raise CException(f"'{obj!s}' handed to object renderer is no an object or class'")
        for obj in objList:
            self.renderObjectSpecification(context, obj)
        for obj in objList:
            self.renderLinks(context, obj, objList)

    def renderObjectModel(self, objectList, **kwargs):
        context = ObjectRenderingContext()
        setKeywordArgs(context, 
            ["renderAttributeValues", "renderEmptyAttributes", "renderLinkLabelsIfStereotyped", "excludedLinks"], **kwargs)
        self.renderStartGraph(context)
        self.renderObjects(context, objectList)
        self.renderEndGraph(context)
        return context.result

    def renderObjectModelToFile(self, fileNameBase, classList, **kwargs):
        source = self.renderObjectModel(classList, **kwargs)
        self.renderToFiles(fileNameBase, source)
    

