#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Noark5 to RDF Converter version 1.0.0
# Author: Graham Moore, graham.moore@sesam.io

import sys, os, errno
import xml.sax
import argparse
import logging
import yaml


def _is_sequence(arg):
    """ Checks if "arg" is a proper sequence or not (i.e. list, tuple..) """
    return not hasattr(arg, "strip") and (hasattr(arg, "__getitem__") or hasattr(arg, "__iter__"))


def assertDir(path, rootdir=None):
    """ Make sure the given directory/ies exists in the given or current path """

    if _is_sequence(path):
        for p in path:
            assertDir(p, rootdir=rootdir)
    else:
        if not rootdir:
            rootdir = os.path.realpath(os.path.curdir)

        if not os.path.isabs(path):
            path = rootdir + os.sep + path
        
        if os.path.isdir(path):
            return

        # python 2.x is stupid.
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(rootdir + os.sep + path):
                pass
            else:
                raise


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
    """ Escape the string literal as per NTriples rules """
    literal = literal.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"').replace('\r', '\\r').replace('\v', '')
    literal = _xmlcharref_encode(literal, "ascii")
    return literal


# TODO: how do we RDF-ify attributes?
class Entity:
    """ Class to encapsulate XML entities """
    def __init__(self, name, attrs, config, parent=None, count_dict={}):
        self._name = name
        self._attrs = attrs
        self._properties = []
        self._entities = []
        self._contained_objects = []
        self._parent = parent
        self._id = None
        self._subject = None
        self._config = config

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

    def getNumberedId(self):
        return "%s-%s" % (self._name, self._counter)

    def getId(self):
        """
        Figure out the ID that this entity has and cache it. ID-less entities are
        treated as RDF blank nodes.
        """
        if self._id is not None:
            return self._id

        if self.isContainedObject():
            # Blank node
            self._id = None
        elif self._config["ObjectElements"][self._name]["id"][0]=="@":
            # Attribute id
            id_attribute = self._config["ObjectElements"][self._name]["id"].replace("@","")
            self._id = self._attrs.getValue(id_attribute)
        else:
            # Normal property value
            id_element = self._config["ObjectElements"][self._name]["id"]
            # Pick the last matching element if there are several
            props = [prop for prop in self._properties if prop.getName() == id_element]
            self._id =  props[-1].getValue()
        
        return self._id
        
    def isContainedObject(self):
        """ Checks if this entity is a ID-less entity contained object (aka blank node) """
        return self._config["ObjectElements"][self._name]["id"] is None

    def getSubject(self):
        """ Return the subject URI for this entity - it is computed from the config and the id """
        if self._subject:
            return self._subject

        id = self.getId()

        if id is None:
            # Blank nodes are just numbered elements
            self._subject = "_:%s" % self.getNumberedId()
        else:
            # Get subject prefix for element, or the global one if none is configured
            self._subject = "<" + self._config["ObjectElements"][self._name].get("subject_prefix", self._config["subject_prefix"]) + id + ">"
       
        return self._subject
        
    def addEntity(self, entity):
        """ Add a contained entity """
        self._entities.append(entity)
    
    def getEntities(self):
        return self._entities
 
    def addProperty(self, prop):
        """ Add a property element object instance """
        self._properties.append(prop)

    def getProperties(self):
        return self._properties

    def __str__(self):
        """ Return a string representation of this entity """
        return "Entity '%s' (id: %s)" % (self._name, self.getId() or self.getNumberedId())

    def getType(self):
        """ Get the type (postfix) to use, it's either given the element name or
        a given xsi:type attribute. It can be overridden in the config using a "type" value.
        """

        # Deault type postfix is capitalized element name
        etype = self._name
        
        # Is there xsi:type in the attributes?
        if "xsi:type" in self._attrs.keys():
            etype = self._attrs["xsi:type"]
            
        # Check for override in config
        if etype in self._config["ObjectElements"].keys():
            # Leave the decision to capitalize or not to the config if its overridden
            return self._config["ObjectElements"][etype].get("type", etype.title())
            
        return etype.title()
        
    def generateNTriples(self, recurse=True):
        """
        Serialize the properties and entities of this entity as RDF NTriples.
        If "recurse" is True, it will traverse the three and serialize all nodes
        """

        subject = self.getSubject()
        s = ""

        s = s + "%s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%s>.\n" % (subject, self._config["type_prefix"] + self.getType())

        for prop in self._properties:
            s = s + '%s <%s> "%s".\n' % (subject, prop.getPredicate(), escape_literal(prop.getValue()))
        
        # We link to our parent if we're not a blank node
        if not self.isContainedObject() and self._parent is not None:
            # Normal objects link *to* parents
            s = s + '%s <%s> %s.\n' % (subject, self._config["type_prefix"] + self._parent.getName(), self._parent.getSubject())

        for entity in self._entities:
            if entity.isContainedObject():
                # We link *to* the blank nodes
                s = s + '%s <%s> %s.\n' % (subject, self._config["type_prefix"] + entity.getName(), entity.getSubject())
            if recurse:
                s = s + entity.generateNTriples()

        return s


# TODO: how do we RDF-ify attributes?
class Property:
    """ Class that encapsulates ordinary elements (properties) """
    def __init__(self, name, attrs, config, parent):
        self._name = name
        self._attrs = attrs
        self._value = ""
        self._parent = parent
        self._config = config

        parent.addProperty(self)

    def getName(self):
        return self._name

    def getAttrs(self):
        return self._attrs

    def getParent(self):
        return self._parent

    def getPredicate(self):
        """ Return the predicate to use when serializing objects of this type in RDF """
        return self._config["type_prefix"] + self._name
    
    def setValue(self, value):
        self._value = value

    def getValue(self):
        return self._value


class Noark5XmlHandler(xml.sax.ContentHandler):
    """
    SAX content handler class that can traverse a NOARK 5 compliant XML file
    and construct a object tree that is then serialized to RDF (NTriples format)
    """
    def __init__(self, config, logger=None):
        self.parent = ""
        self.properties = []
        self.subject = ""
        self.root = None
        self.currentProperty = None
        self.currentEntity = []
        self.config = config
        self.count_dict = {}
        self.logger = logger

    def startElement(self, name, attrs):
        """ Create a entity or property object based on config lookup """
        if name in self.config["ObjectElements"]:
            if self.logger:
                self.logger.debug("Start of entity:" + name)
            # Create a Entity
            parent = len(self.currentEntity) > 0 and self.currentEntity[0] or None
            entity = Entity(name, attrs, self.config, parent, self.count_dict)
            if parent is None:
                # This entity is the root
                self.root = entity
            self.currentEntity.insert(0, entity)
        else:
            self.currentProperty = Property(name, attrs, self.config, self.currentEntity[0])
 
    def characters(self, text):
        """ Add text value if the current node is a property """
        if self.currentProperty:
            if self.logger:
                self.logger.debug("Value of element: " + text)
            self.currentProperty.setValue(text);

    def endElement(self, name):
        """ Serialize to RDF if the ended element node is a entity """
        if name in self.config["ObjectElements"]:
            if self.logger:
                self.logger.debug("end of entity: " + name)

            entity = self.currentEntity[0]
            
            id = entity.getId() or self.root.getId() + "-" + entity.getNumberedId()

            filename = self.config.get("output_dir",".") + os.path.sep + "%s.nt" % id

            if self.logger:
                self.logger.info("Writing %s to file '%s'" % (entity, filename))

            with open(filename, "w") as output:
                output.write(entity.generateNTriples(recurse=False))
            
            self.currentEntity = self.currentEntity[1:]
        else:
            self.currentProperty = None


def getCurrDir():
    """ Get the current directory """
    return os.path.realpath(os.path.curdir)


def readConfig(configfile, logfile=None, loglevel=None, env=None, logger=None):
    """ Read a config file or return the default config """
    if not env:
        env = os.environ.copy()

    default_config = {
        # Default "schema" prefix
        "type_prefix" : "http://www.arkivverket.no/standarder/noark5/arkivstruktur/",

        # Default subject prefix
        "subject_prefix" : "http://sesam.io/sys1/",

        # ObjectElements are the names of XML elements that should produce new RDF resources
        # The form is Key : idElement - if the idElement begins with a "@" it is an attribute,
        # else it is a element name. If there are several, only the last value is used.
        # if idElement is None, it is treated as a blank node in the output
        # if no "subject_prefix" is given, the default is used

        "ObjectElements" : {
            "arkiv" : {"id" : "systemID", "subject_prefix" : "http://sesam.io/sys1/", "type" : "Arkiv"},
            "arkivdel" : {"id" : "systemID"},
            "mappe" : {"id" : "systemID"},
            "registrering" : {"id" : "systemID"},
            "skjerming" : {"id" : None},
            "kassasjon" : {"id" : None},
            "korrespondansepart" : {"id" : None},
            "arkivskaper": {"id" : "arkivskaperID"},
        },
        "output_dir" : "",
        "logfile" : logfile,
        "loglevel" : loglevel
    }
        
    config_file = configfile.strip()
    if not os.path.isabs(config_file):
        root_folder = getCurrDir()
        config_file = os.path.join(root_folder, config_file)

    if logger:
        logger.debug("Reading config file from '%s'..." % config_file)

    if os.path.isfile(config_file):
        stream = open(config_file, 'r')
        config = yaml.load(stream)
        stream.close()
    else:
        config = {}
        msg = "Could not find config file '%s'. Using defaults." % config_file
        if logger:
            logger.warning(msg)
        

    default_config.update(config)
    if not os.path.isabs(default_config["output_dir"]):
        root_folder = getCurrDir()
        default_config["output_dir"] = os.path.join(root_folder, default_config["output_dir"])

    assertDir(default_config["output_dir"])

    if not os.path.isabs(default_config["logfile"]):
        log_folder = getCurrDir()
        assertDir(log_folder)
        default_config["logfile"] = os.path.join(log_folder, default_config["logfile"])

    if not default_config["loglevel"]:
        default_config["loglevel"] = loglevel

    return default_config
    

def main():
    """ Parse arguments, set logger, read config and parse input """
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('noark5-to-rdf')
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    parser = argparse.ArgumentParser(description="Noark5 to RDF 1.0.0")
    parser.add_argument("-i", "--input", dest='inputfile',
                        help='Path to input XML file', required=True)

    parser.add_argument("-c", "--config", dest='configfile',
                        help='Path to config yaml file', default="config/config.yaml")
    parser.add_argument("-l", "--loglevel", dest="loglevel",
                        help="Loglevel (INFO, DEBUG, WARN..), default is INFO", metavar="LOGLEVEL", default="INFO")
    parser.add_argument("-f", "--logfile", dest="logfile", default="noark5-to-rdf.log",
                        help="Filename to log to if logging to file, the default is 'noark5-to-rdf.log' in the current directory")

    options = parser.parse_args()

    config = readConfig(options.configfile, logfile=options.logfile, loglevel=options.loglevel, logger=logger)

    logger.setLevel({"INFO":logging.INFO, "DEBUG":logging.DEBUG, "WARN":logging.WARNING, "ERROR":logging.ERROR}.get(config["loglevel"], logging.INFO))
    logger.debug("Config: \n%s" % str(config))

    file_handler = logging.FileHandler(config["logfile"])
    file_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(file_handler)

    logger.info("Processing XML from " + options.inputfile)
    logger.info("Writing RDF into " + config["output_dir"])

    parser = xml.sax.make_parser()
    parser.setContentHandler(Noark5XmlHandler(config, logger=logger))
    parser.parse(open(options.inputfile,"r"))


# Check if called from command line
if __name__ == '__main__':
    main()
