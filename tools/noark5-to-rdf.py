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

class Entity:

    def init(self):
        self.identity

class Property:
    def init(self):
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

    def init(self):
        self.parent = ""
        self.properties = []
        self.subject = ""
        self.currentProperty = None

    def startElement(self, name, attrs):
        self.currentProperty = Property()
        self.currentProperty.init()
        self.currentProperty.setPropertyType(noark5_prefix + name)

    def endElement(self, name):
        print("end " + name)

parser = xml.sax.make_parser()
parser.setContentHandler(Noark5XmlHandler())
parser.parse(open(noark5_filename,"r"))







