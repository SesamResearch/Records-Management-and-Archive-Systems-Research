#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from utils import *


def readConfig(configfile, logfile=None, loglevel=None, env=None, logger=None):
    """ Read a config file or return the default config """
    if not env:
        env = os.environ.copy()

    default_config = {
        # Default "schema" prefix
        "type_prefix" : "http://www.arkivverket.no/standarder/noark5/arkivstruktur/",

        # Default subject prefix
        "subject_prefix" : "http://sesam.io/sys1/",
        
        # Default id elements
        "ids" : ["systemID", "arkivskaperID"],

        # ObjectElements are the names of XML elements that should produce new RDF resources
        # The form is Key : idElement - if the idElement begins with a "@" it is an attribute,
        # else it is a element name. If there are several, only the last value is used.
        # if idElement is None, it is treated as a blank node in the output
        # if no "subject_prefix" is given, the default is used

        "ObjectElements" : {
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
