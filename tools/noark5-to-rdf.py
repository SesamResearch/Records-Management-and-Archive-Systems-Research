# Noark5 to RDF Converter version 0.1
# Author: Graham Moore, graham.moore@sesam.io

import sys
import xml.sax

print("Noark5 to RDF v0.1")

if len(sys.argv) != 3:
    print("Error! Wrong number of parameters")
    print("Usage: noark5-to-rdf.py <noark5.xml> <output.ttl>")
    exit(1)

noark5_filename = sys.argv[1]
rdf_filename = sys.argv[2]

print("Processing XML from " + noark5_filename)
print("Writing RDF into " + rdf_filename)


# Noark5 Element Names
Arkiv_Element = "arkiv"
SystemId_Element = "systemID"

# ObjectElements are the names of XML elements that should produce new RDF resources
ObjectElements = ["arkiv", "arkivdel", "mappe", "registrering"]
ContainedObjectElements = ["skjerming", "kassasjon"]

noark5_prefix = "http://www.arkivverket.no/standarder/noark5/arkivstruktur/"

class Store:

    def __init__(self):
        self.entities = {}

    def addEntity(self, entity):
        self.entities[entity.id] = entity

class Entity:

    def __init__(self):
        self.id = ""
        self.type = ""
        self.__properties = []

    def addProperty(self, property):
        self.__properties.append(property)


class Property:
    def __init__(self):
        self.propType = ""
        self.propValue = ""
        self.isLiteral = ""

    def setPropertyType(self, propType):
        self.propType = type

    def setSubject(self, subject):
        self.subject = subject

    def setValue(self, val, isLiteral):
        self.propValue = val


def LowerFirstChar(val):
    pass


class Noark5XmlHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.parentEntity = ""
        self.currentEntity = None

    def startElement(self, name, attrs):
        if name in ObjectElements:
            pass
        elif name in ContainedObjectElements:
            # create contained entity
            pass
        else:
            # property
            pass


        self.currentProperty = Property()
        self.currentProperty.init()
        self.currentProperty.setPropertyType(noark5_prefix + name)

    def endElement(self, name):
        print("end " + name)

parser = xml.sax.make_parser()
parser.setContentHandler(Noark5XmlHandler())
parser.parse(open(noark5_filename,"r"))







