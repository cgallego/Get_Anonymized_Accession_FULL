# -*- coding: utf-8 -*-
"""
DICOM annotation revealer
"""

from glob import glob
import os
import dicom

tags = ['SliceLocation', 'SeriesNumber', 'SeriesDate',  'SeriesDescription',
    'StudyID', 'PatientID','SeriesInstanceUID','AccessionNumber']

def list_ann(directory, outfile, append=True):
    """
list_ann : get all DICOM annotation tags from specified directory

Parameters
==========

directory : string
    the full path to search for DICOM files within

outfile : string
    the full path of the file to write output to, or the name
    of a file in the current directory

append : bool [True]
    whether to append to a file, or to start a new file from
    scratch.

Output
======

The specified file is filled with python-parsable dictionaries,
one for each DICOM image containing an annotation. The annotation
itself is free text in the 'note' field.
    """
    allfiles = glob(directory+os.sep+'*')
    out = open(outfile,'a+')
    print "Looking for Annotations..."
    for myfile in allfiles:
        try:
            data = dicom.read_file(myfile)
            if data.get((0x029, 0x1300),None):
                print "Found Annotation"
                head = dict((tag,data.get(tag,None)) for tag in tags)
                head['note'] = data.get((0x029, 0x1300)).value
                print "\n##################\nFound annotation"
                print head
                print "\n##################\n"
                out.write(str(head)+'\n')
        except:
            continue #Not a DICOM file...
    out.close()