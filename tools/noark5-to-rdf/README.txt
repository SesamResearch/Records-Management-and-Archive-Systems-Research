NOARK5 to RDF tool
==================

Converts a NOARK5 XML file to RDF.

Installing
==========

Navigate to root of the unpackaged source folder and issue:

    python setup.py install

Note that python needs to be python 3, if you have both installed use:
    
    python3 setup.py install

Usage
=====

Running the tool from the command line after installation:
    
    noark5tordf -i <inputfile.xml>
    
Or alternatively from the source code folder directly:

    python -m noark5tordf.noark5tordf -i <inputfile.xml>

This will convert the NOARK5 compliant XML file given in <inputfile.xml> to RDF and write the
result in NTriples format (*.nt) as one file per RDF subject in the current directory.

See "noark5tordf --help" or "python -m noark5tordf.noark5tordf --help" for a complete list of options
