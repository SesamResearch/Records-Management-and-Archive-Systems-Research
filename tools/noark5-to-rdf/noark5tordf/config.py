#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yaml
from .utils import *

def readConfig(configfile, output_dir=None, input_dir=None, backup_dir=None, interval=None, logfile=None, loglevel=None, env=None, logger=None):
    """ Read a config file or return a default config """
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

    # Command line overrides config
    if output_dir:
        default_config["output_dir"] = output_dir

    if input_dir:
        default_config["input_dir"] = input_dir

    if backup_dir:
        default_config["backup_dir"] = backup_dir

    if not os.path.isabs(default_config["output_dir"]):
        root_folder = getCurrDir()
        default_config["output_dir"] = os.path.join(root_folder, default_config["output_dir"])

    if not os.path.isabs(default_config["input_dir"]):
        root_folder = getCurrDir()
        default_config["input_dir"] = os.path.join(root_folder, default_config["input_dir"])

    if not os.path.isabs(default_config["backup_dir"]):
        root_folder = env.get("SESAM_DATA", getCurrDir())
        default_config["backup_dir"] = os.path.join(root_folder, default_config["backup_dir"])

    if default_config["logfile"] is not None and not os.path.isabs(default_config["logfile"]):
        log_folder = getCurrDir()
        assertDir(log_folder)
        default_config["logfile"] = os.path.join(log_folder, default_config["logfile"])

    if not default_config["loglevel"]:
        default_config["loglevel"] = loglevel

    if interval is not None and interval > 0:
        default_config["interval"] = interval

    assertDir(default_config["input_dir"])
    assertDir(default_config["output_dir"])
    assertDir(default_config["backup_dir"])

    return default_config

