# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 13:03:30 2013

@author: Karen Klassen
"""
from classes import Series
import counter
from dictionaries import program_loc
import os
import query

def objects(examID,exam_loc):
    """
    Uses the Series class to make an object for each series found in the local
    computer's files.
    Takes in examID and exam_loc as strings.
    Returns a list of Series's objects. 
    """
    series,filenames,user=query.harddrive(exam_loc) #needs dicom files only
    objects=[]
    
    print 'Creating objects...'
    j=0
    while j<len(series):
        objects.append(Series(series[j],filenames[j],examID,exam_loc))
        j+=1
    
    counter.count(objects,exam_loc,user)
    counter.size(objects)
    return objects

def run_code(examID,exam_loc):
    """
    Calls on objects, counter, and writes the information to a file that can 
    be viewed in Excel as a table.
    Takes in examID and exam_loc as strings.
    See Table.txt in program_loc for output.
    """
    obj=objects(examID,exam_loc)   
    
    os.chdir(program_loc)
    if not(os.path.exists(str(examID))):
        os.mkdir(str(examID))
    os.chdir(str(examID))
    data=open('Table.txt','w')
    
    header='Study ID \t Series UID \t Series Description \t Series Full Name'+\
        ' \t Type \t Processed \t Protocol Name \t TE \t TR \t '+\
        'Patient Position \t Side \t Subtracted \t Registered \t '+\
        'Fat Saturated \t 3D \t Contrast \t Image Array Size \t '+\
        'Voxel Spacing (mm) \t Time (hr:min:sec) \t Time Array (s) \t '+\
        'Image Orientation \t Orientation Matrix \n\n'
    data.write(header)
    
    for i in obj:
        line=str(i.DICOMnum)+'\t'+str(i.UID)+'\t'+str(i.series)+'\t'+\
            str(i.translation)+'\t'+str(i.type)+'\t'+str(i.processed)+'\t'+\
            str(i.protocol_name)+'\t'+str(i.te)+'\t'+str(i.tr)+'\t'+\
            str(i.position)+'\t'+str(i.side)+'\t'+str(i.sub)+'\t'+str(i.reg)+\
            '\t'+str(i.fat)+'\t'+str(i.dimension)+'\t'+str(i.contrast)+'\t'+\
            str(i.isize)+'\t'+str(i.vdim)+'\t'+str(i.intime)+'\t'+\
            str(i.timediffer)+'\t'+str(i.orient)+'\t'+str(i.ormatrix)+'\n'
        data.write(line)
        
    #makes sure file writes
    data.flush()
    os.fsync(data.fileno())
    data.close()
    return
    
#not apart of pipeline
def testing():
    """
    Used to test certain aspects of each object. Mainly for programmer's use.
    """
    obj=objects()
        
    os.chdir(program_loc)
    
    test=open('Testing.txt','w')
    header='Study ID \t Processed \t Type \n\n'
    test.write(header)
    for i in obj:
        line=str(i.DICOMnum)+'\t'+str(i.processed)+'\t'+str(i.type)+'\n'
        test.write(line)
    test.flush()
    os.fsync(test.fileno())
    test.close()
    return

"""
#finds the maximum length of a given attribute for a given exam ID
ser=[]
trans=[]
for x in objects:
    ser.append(len(x.series))
    trans.append(len(x.translation))
"""