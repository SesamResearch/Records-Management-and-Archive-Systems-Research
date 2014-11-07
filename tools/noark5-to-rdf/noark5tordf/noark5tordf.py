#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Noark5 to RDF Converter version 1.0.0
# Author: Graham Moore, graham.moore@sesam.io

import os, argparse, logging
import xml.sax
from xml.sax.handler import feature_namespaces

from .config import *
from .utils import *
from .xmlhandler import GeneralXmlHandler


def process_xml_file(config, inputfile, logger=None):
    """ Process a single XML file and output RDF to output dir """
    if logger:
        logger.info("Processing XML from " + inputfile)
        logger.info("Writing RDF into " + config["output_dir"])

    parser = xml.sax.make_parser()
    
    # Turn on namespace support
    parser.setFeature(feature_namespaces, 1)
    parser.setContentHandler(GeneralXmlHandler(config, logger=logger))
    
    # Process the input file
    parser.parse(inputfile)


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

    process_xml_file(config, options.inputfile, logger=logger)


# Check if called from command line
if __name__ == '__main__':
    main()
