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

# Default "schema" prefix
type_prefix = "http://www.arkivverket.no/standarder/noark5/arkivstruktur/"

# Default subject prefix
subject_prefix = "http://sesam.io/sys1/"

# ObjectElements are the names of XML elements that should produce new RDF resources
# The form is Key : idElement - if the idElement begins with a "@" it is an attribute,
# else it is a element name. If there are several, only the last value is used.
# if idElement is None, it is treated as a blank node in the output
# if no "subject_prefix" is given, the default is used

ObjectElements = {
  "arkiv" : {"id" : "systemID", "subject_prefix" : "http://sesam.io/sys1/"},
  "arkivdel" : {"id" : "systemID"},
  "mappe" : {"id" : "systemID"},
  "registrering" : {"id" : "systemID"},
  "skjerming" : {"id" : None},
  "kassasjon" : {"id" : None},
  "korrespondansepart" : {"id" : None},
  "arkivskaper": {"id" : "arkivskaperID"},
}

# Just used to keep track of the blank nodes
count_dict = {}

# Used for escaping literals
def _xmlcharref_encode(unicode_data, encoding="ascii"):
    """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
    res = ""

    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            char.encode(encoding, 'strict')
        except UnicodeError:
            if ord(char) <= 0xFFFF:
                res += '\\u%04X' % ord(char)
            else:
                res += '\\U%08X' % ord(char)
        else:
            res += char

    return res

def escape_literal(literal):
    literal = literal.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"').replace('\r', '\\r').replace('\v', '')
    literal = _xmlcharref_encode(literal, "ascii")
    return literal


# "Objects" - (TODO: how do we RDF-ify attributes?)
class Entity:

    def __init__(self, name, attrs, parent=None):
        self._name = name
        self._attrs = attrs
        self._properties = []
        self._entities = []
        self._contained_objects = []
        self._parent = parent
        self._id = None
        self._subject = None

        # Number the entity (for blank nodes)        
        if not name in count_dict:
            count_dict[name] = 0
        count_dict[name] = count_dict[name] + 1
        self._counter = count_dict[name]
        if parent is not None:
            parent.addEntity(self)

    def getAttrs(self):
        return self._attrs
    
    def getName(self):
        return self._name

    def getId(self):
        if self._id is not None:
            return self._id

        if self.isContainedObject():
            # Blank node
            self._id = None
        elif ObjectElements[self._name]["id"][0]=="@":
            # Attribute id
            self._id = self._attrs.getValue(ObjectElements[self._name]["id"].replace("@",""))
        else:
            # Normal property value
            id_elem = ObjectElements[self._name]["id"]
            props = [prop for prop in self._properties if prop.getName() == id_elem]
            self._id =  props[-1].getValue()
        
        return self._id
        
    def isContainedObject(self):
        return ObjectElements[self._name]["id"] is None

    def getSubject(self):
        if self._subject:
            return self._subject

        id = self.getId()

        if id is None:
            # Blank node
            self._subject = "_:%s-%s" % (self._name, self._counter)
        else:
            self._subject = "<" + ObjectElements[self._name].get("subject_prefix", subject_prefix) + id + ">"
       
        return self._subject
        
    def addEntity(self, entity):
        self._entities.append(entity)
    
    def getEntities(self):
        return self._entities
 
    def addProperty(self, prop):
        self._properties.append(prop)

    def getProperties(self):
        return self._properties
    
    def generateNTriples(self):
        subject = self.getSubject()
        s = ""

        s = s + "%s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%s>.\n" % (subject, type_prefix + self._name.title())

        for prop in self._properties:
            s = s + '%s <%s> "%s".\n' % (subject, prop.getPredicate(), escape_literal(prop.getValue()))
        
        # We link to our parent if we're not a blank node
        if not self.isContainedObject() and self._parent is not None:
            # Normal objects link *to* parents
            s = s + '%s <%s> %s.\n' % (subject, type_prefix + self._parent.getName(), self._parent.getSubject())

        for entity in self._entities:
            if entity.isContainedObject():
                # We link *to* the blank nodes
                s = s + '%s <%s> %s.\n' % (subject, type_prefix + entity.getName(), entity.getSubject())
            s = s + entity.generateNTriples()
               
        return s

# Normal "properties" (TODO: how do we RDF-ify attributes?)
class Property:
    def __init__(self, name, attrs, parent):
        self._name = name
        self._attrs = attrs
        self._value = ""
        self._parent = parent

        parent.addProperty(self)

    def getName(self):
        return self._name

    def getAttrs(self):
        return self._attrs

    def getParent(self):
        return self._parent

    def getPredicate(self):
        return type_prefix + self._name
    
    def setValue(self, value):
        self._value = value

    def getValue(self):
        return self._value


class Noark5XmlHandler(xml.sax.ContentHandler):

    def __init__(self):
        self.parent = ""
        self.properties = []
        self.subject = ""
        self.root = None
        self.currentProperty = None
        self.currentEntity = []

    def startElement(self, name, attrs):
        print("Start " + name)
        if name in ObjectElements:
            # Create a Entity
            parent = len(self.currentEntity) > 0 and self.currentEntity[0] or None
            entity = Entity(name, attrs, parent)
            if parent is None:
                # This entity is the root
                self.root = entity
            self.currentEntity.insert(0, entity)
        else:
            self.currentProperty = Property(name, attrs, self.currentEntity[0])
 
    def characters(self, text):
        if self.currentProperty:
            print("Value: " + text)
            self.currentProperty.setValue(text);

    def endElement(self, name):
        if name in ObjectElements:
            entity = self.currentEntity[0]
            self.currentEntity = self.currentEntity[1:]
        else:
            self.currentProperty = None
        print("end " + name)
        
    def endDocument(self):
        # Output ntriples
        with open(rdf_filename,"w") as output:
            output.write(self.root.generateNTriples())

parser = xml.sax.make_parser()
parser.setContentHandler(Noark5XmlHandler())
parser.parse(open(noark5_filename,"r"))
