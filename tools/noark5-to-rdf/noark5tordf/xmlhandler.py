#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import xml.sax

from elements import Entity


class GeneralXmlHandler(xml.sax.ContentHandler):
    """
    SAX content handler class that can traverse a NOARK 5 compliant XML file
    and construct a object tree that is then serialized to RDF (NTriples format)
    """
    def __init__(self, config, logger=None):
        self.parent = ""
        self.subject = ""
        self.root = None
        self._entities = []
        self.config = config
        self.count_dict = {}
        self.logger = logger
        self.text = ""

    def getCurrentEntity(self, pop=False):
        current_entity = len(self._entities) > 0 and self._entities[0] or None
        
        if pop:
            self._entities = self._entities[1:]

        return current_entity
    
    def setCurrentEntity(self, entity):
        self._entities.insert(0, entity)
        return self._entities

    def startElementNS(self, nsname, qname, attrs):
        """ Create a entity or property object based on config lookup """
        uri, name = nsname
        
        if self.logger:
            self.logger.debug("Start of entity:" + name)
        
        # Create a Entity
        parent = self.getCurrentEntity()
        entity = Entity(name, attrs, self.config, parent, count_dict=self.count_dict, namespace=uri)
        
        if parent is None:
            # This entity is the root
            self.root = entity

        # Push the entity onto the stack
        self.setCurrentEntity(entity)
        self.text = ""

    def endElementNS(self, nsname, qname):
        """ Serialize to RDF if the ended element node is a entity """
        uri, name = nsname
        if self.logger:
            self.logger.debug("end of entity: " + name)

        # Pick a entity element off the stack
        entity = self.getCurrentEntity(pop=True)

#        if entity.getName() == "provider":        
#            import pdb;pdb.set_trace()
        
        # Is this a "property" type element?
        if len(entity.getEntities()) == 0:
            entity.setValue(self.text);
            if self.logger:
                self.logger.debug("Setting value of element '%s' to '%s'" % (str(entity), self.text))
            self.text = ""

        # If it is a "object" type element, serialize it to NTriples
        if not entity.isProperty():
            id = (entity.getId() or self.root.getId() or "root") + "-" + entity.getNumberedId()

            filename = self.config.get("output_dir",".") + os.path.sep + "%s.nt" % id

            if self.logger:
                self.logger.info("Writing %s to file '%s'" % (entity, filename))

            with open(filename, "w") as output:
                output.write(entity.generateNTriples())
                
            # We're done with this object now, hand it over to GC
            entity.cleanUp()
            del entity
       
    def characters(self, text):
        """ Accumulate text values """
        self.text += text
