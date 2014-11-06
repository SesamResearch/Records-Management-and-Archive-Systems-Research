#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import *

class Entity:
    """ Class to encapsulate XML entities """
    def __init__(self, name, attributes, config, parent=None, namespace=None, count_dict=None):
        # Most of the properties are calculated only once and then
        # "frozen" so we can  GC things on the fly
        self._name = name
        self._attributes = attributes
        self._entities = []
        self._parent = parent
        self._id = None
        self._subject = None
        self._config = config
        self._namespace = namespace
        self._numbered_id = None
        self._str_rep = None
        self._value = None
        self._type = None
        self._type_prefix = None
        self._type_predicate = None
        self._predicate = None
        self._is_contained_object = None
        
        if count_dict is not None:
            # Number the entity (for blank nodes)        
            if not name in count_dict:
                count_dict[name] = 0
            count_dict[name] = count_dict[name] + 1
            self._counter = count_dict[name]

        if parent is not None:
            parent.addEntity(self)

    # Make things easy for the GC
    def cleanUp(self):
        self._entities = None
        self._attributes = None
        self._parent = None
        del self._entities
        del self._attributes
        
    def getAttributes(self):
        return self._attributes
    
    def getName(self):
        return self._name

    def isLiteral(self):
        if "literal" in self._config["ObjectElements"].get(self._name, {}):
            return self._config["ObjectElements"][self._name]["literal"]

        return True       
    
    def getDataType(self):
        if self.isLiteral() and "datatype" in self._config["ObjectElements"].get(self._name, {}):
            return self._config["ObjectElements"][self._name]["datatype"]

        return None

    def getLanguage(self):
        if self.isLiteral() and "lang" in self._config["ObjectElements"].get(self._name, {}):
            return self._config["ObjectElements"][self._name]["lang"]

        return None

    def setValue(self, value):
        # Check for value expression       
        if "value" in self._config["ObjectElements"].get(self._name, {}):
            params = {"value": value, "context" : self, "config" : self._config}
            exec(self._config["ObjectElements"][self._name]["value"], globals(), params)
            self._value = params["result"]
        else:
            self._value = value

    def getValue(self):
        return self._value
   
    def isProperty(self):
        return self._value is not None

    def getNumberedId(self):
        if self._numbered_id is None:
            self._numbered_id = "%s-%s" % (self._name, self._counter)
        
        return self._numbered_id

    def getId(self):
        """
        Figure out the ID that this entity has and "freeze" it. ID-less entities are
        treated as RDF blank nodes.
        """
        
        # If we have already computed this just return the previous result
        if self._id is not None:
            return self._id

        if self.isProperty():
            self._id = self._name
        else:
            # Check if the id is an expression
            
            # A blank node is either it's explicitly stated with a "id" config property set to None...
            if "id" in self._config["ObjectElements"].get(self._name, {}) and  self._config["ObjectElements"][self._name]["id"] is None:
                return None
            
            # ..or explicitly using a "id-expression" python expression
            
            if "id-expression" in self._config["ObjectElements"].get(self._name, {}):
                params = {"context" : self, "config" : self._config}
                exec(self._config["ObjectElements"][self._name]["id-expression"], globals(), params)
                self._id = params["result"]
                return self._id
 
            # ..or implicitly if none of the config given or global ids match any of its properties or attributes       
            ids = self._config["ObjectElements"].get(self._name,{}).get("id", [])
            if not is_sequence(ids):
                ids = [ids]
            
            ids = list(tuple(ids + self._config.get("ids", [])))
            
            for id_element in ids:
                # Attribute ID?
                if id_element[0] == "@":                
                    if id_element[1:] in self._attributes.getQNames():
                        self._id = self._attributes.getValueByQName(id_element[1:])
                        break
                else:
                    # Normal element value
                    props = [prop for prop in self.getProperties() if prop.getName() == id_element]
                    if len(props) > 0:
                        self._id =  props[-1].getValue()
                        break

        return self._id

    def isContainedObject(self):
        """ Checks if this entity is a ID-less entity contained object (aka blank node) """
        
        if self._is_contained_object is None:
            self._is_contained_object = self.getId() == None and not self.isProperty()

        return self._is_contained_object

    def getSubject(self):
        """ Return the subject URI for this entity - it is computed from the config and the id """
        if self._subject is not None:
            return self._subject

        id = self.getId()

        # Blank nodes are treated as a special case
        if id is None:
            self._subject = "_:%s" % self.getNumberedId()
        else:
            # Get subject prefix for element, or the global one if none is configured
            self._subject = "<" + self._config["ObjectElements"].get(self._name, {}).get("subject_prefix", self._config["subject_prefix"]) + id + ">"

        return self._subject
        
    def addEntity(self, entity):
        """ Add a contained entity """
        self._entities.append(entity)
    
    def getEntities(self):
        return self._entities
 
    def getParent(self):
        return self._parent

    def getProperties(self):
        for entity in self._entities:
            if entity.isProperty():
                yield entity

    def __str__(self):
        """ Return a string representation of this entity """
        if self._str_rep is None:
            self._str_rep = "Entity '%s' (id: %s)" % (self._name, self.getId() or self.getNumberedId())

        return self._str_rep
    
    def getTypePrefix(self):
        if self._type_prefix is not None:
            return self._type_prefix
        
        self._type_prefix = self._config["ObjectElements"].get(self._name, {}).get("type_prefix") or self._namespace or self._config["type_prefix"]
        if self._type_prefix[-1] != "/":
            self._type_prefix = self._type_prefix + "/"

        return self._type_prefix

    def getType(self):
        """ Get the type (postfix) to use, it's either given the element name or
        a given xsi:type attribute. It can be overridden in the config using a "type" value.
        """
        
        if self._type is not None:
            return self._type

        # Deault type postfix is capitalized element name
        etype = self._name
        
        # Is there xsi:type in the attributes?
        if ('http://www.w3.org/2001/XMLSchema-instance', 'type') in self._attributes.keys():
            etype = self._attributes[('http://www.w3.org/2001/XMLSchema-instance', 'type')]

        # Check for override in config
        if etype in self._config["ObjectElements"].keys():
            # Leave the decision to capitalize or not to the config if its overridden
            etype = self._config["ObjectElements"][etype].get("type", etype)
        
        self._type = etype
        return self._type
    
    def getTypePredicate(self):
        """
        Get the type predicate to use, it is either given by the namespace
        of the element or inherited from config
        """
        if self._type_predicate is not None:
            return self._type_predicate
        
        self._type_predicate = self.getTypePrefix() + self.getType().title()
        
        return self._type_predicate

    def getPredicate(self):
        """ Get the predicate to use when referring to this entity from elsewhere """
        if self._predicate is not None:
            return self._predicate
        
        self._predicate = self.getTypePrefix() + self.getType()
        
        return self._predicate
        
    def generateNTriples(self):
        """
        Serialize the properties and entities of this entity as RDF NTriples.
        If "recurse" is True, it will traverse the three and serialize all nodes
        """

        subject = self.getSubject()
        s = ""

        s = s + "%s <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%s>.\n" % (subject, self.getTypePredicate())

        # Treat attributes as string literals
        # TODO: what about language and datatype for these?
        for uri, attr in self._attributes.keys():
            if uri:
                predicate = uri + "/" + attr
            else:
                predicate = self._config["type_prefix"] + attr

            s = s + '%s <%s> "%s".\n' % (subject, predicate, escape_literal(self._attributes[(uri, attr)]))
        
        # We link to our parent (if we're not a blank node)
        if not self.isContainedObject() and self.getParent() is not None:
            s = s + '%s <%s> %s.\n' % (subject, self.getParent().getPredicate(), self.getParent().getSubject())

        # Serialize properties and add links to blank nodes
        for entity in self._entities:
            if entity.isProperty():
                if entity.isLiteral():
                    lang = entity.getLanguage()
                    
                    # According to the spec, you can't have both lang and type on a literal (string is implied if lang is set)
                    if lang is None or lang == "":
                        postfix = self.getDataType()
                        postfix = postfix and "^^<http://www.w3.org/2001/XMLSchema#>" + postfix or ""
                    else:
                        postfix = "@" + lang
                    
                    s = s + '%s <%s> "%s"%s.\n' % (subject, entity.getPredicate(), escape_literal(entity.getValue()), postfix)
                else:
                    s = s + '%s <%s> <%s>.\n' % (subject, entity.getPredicate(), escape_literal(entity.getValue()))

                # Entities with attributes are expanded to seperate literals
                # TODO: what about language and datatype for these?
                try:
                    prop_attrs = entity.getAttributes()
                except:
                    import pdb;pdb.set_trace()
                for uri, pred_id in prop_attrs.keys():
                    s = s + '%s <%s> "%s".\n' % (subject, entity.getPredicate() + "-" + pred_id, escape_literal(prop_attrs[(uri, pred_id)]))

                # Properties and blank node hierarchies can be disposed of after serialization
                entity.cleanUp()
                    
            elif entity.isContainedObject():
                # All parents link *to* their blank nodes
                s = s + '%s <%s> %s.\n' % (subject, entity.getPredicate(), entity.getSubject())
                
                # Serialize the blank node tree within its parent
                s = s + entity.generateNTriples()
            
                # Properties and blank node hierarchies can be disposed of after serialization
                entity.cleanUp()

        return s
