#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Generate config for the XML to RDF Converter
# Author: Tom Bech, tom.bech@sesam.io

import sys, os, errno, shutil, glob, argparse, logging, time
import xml.sax
import yaml


class Entity:
    """ Class to encapsulate XML entities """
    def __init__(self, name, attrs, parent=None):
        self._name = name
        self._attrs = attrs
        self._parent = parent
        self._entities = []
        if parent is not None:
            parent.addEntity(self)

    def getAttrs(self):
        return self._attrs
    
    def getName(self):
        return self._name

    def addEntity(self, entity):
        """ Add a contained entity """
        self._entities.append(entity)
    
    def getEntities(self):
        return self._entities


class ConfigXmlHandler(xml.sax.ContentHandler):
    """
    SAX content handler class that can traverse a XML file
    and output a template for a XML to RDF config file
    """
    def __init__(self, outputfile, logger=None):
        self.root = None
        self.currentEntity = []
        self.outputfile = outputfile
        self.logger = logger
        self.entities = {}

    def startElement(self, name, attrs):
        parent = len(self.currentEntity) > 0 and self.currentEntity[0] or None
        entity = Entity(name, attrs, parent)
        if parent is None:
            # This entity is the root
            self.root = entity
        self.currentEntity.insert(0, entity)
 
    def endElement(self, name):
        entity = self.currentEntity[0]
        
        if not name in self.entities and len(entity.getEntities()) > 0:
            self.entities[name] = {"id" : None}
        
        entity._entities = []
        del entity
        self.currentEntity = self.currentEntity[1:]

    def endDocument(self):
        # Generate template config
        
        config = {
            # Default "schema" prefix
            "type_prefix" : "http://sesam.io/schema/",

            # Default subject prefix
            "subject_prefix" : "http://data.sesam.io/",

            "ObjectElements" : self.entities,
            "output_dir" : "output",
            "input_dir" : "input",
            "backup_dir" : "backup",
            "interval" : 5,
        }
        
        with open(self.outputfile, "w") as f:
            f.write(yaml.dump(config, default_flow_style=False))

def getCurrDir():
    """ Get the current directory """
    return os.path.realpath(os.path.curdir)


def main():
    """ Parse arguments, set logger, read config and parse input """
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('generateconfig')
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    parser = argparse.ArgumentParser(description="Genewrate config file templates for the XML to RDF converted")
    parser.add_argument("-i", "--input", dest='inputfile',
                        help='Path to input XML files', default=None)
    parser.add_argument("-o", "--output", dest='outputfile',
                        help='Path to output NTriple files', default=None)
    parser.add_argument("-l", "--loglevel", dest="loglevel",
                        help="Loglevel (INFO, DEBUG, WARN..), default is INFO", metavar="LOGLEVEL", default="INFO")
    parser.add_argument("-f", "--logfile", dest="logfile", default="generateconfig.log",
                        help="Filename to log to if logging to file, the default is 'generateconfig.log' in the current directory")

    options = parser.parse_args()

    logger.setLevel({"INFO":logging.INFO, "DEBUG":logging.DEBUG, "WARN":logging.WARNING, "ERROR":logging.ERROR}.get(options.loglevel, logging.INFO))

    file_handler = logging.FileHandler(options.logfile)
    file_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(file_handler)

    parser = xml.sax.make_parser()
    parser.setContentHandler(ConfigXmlHandler(options.outputfile, logger=logger))
    parser.parse(open(options.inputfile,"r"))


# Check if called from command line
if __name__ == '__main__':
    main()
