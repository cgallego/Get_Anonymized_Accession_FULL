# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 15:43:24 2013

@author: Karen Klassen
"""
from dictionaries import data_loc, program_loc
import instances
import os
import query
import shutil
import SQL
import StudyIDs
import time

def fill_table(numberofstudies,option='SQL'):
    """
    Runs through every exam listed in 'List of StudyIDs.txt'. Either prints
    information to text files that can be viewed in Excel, or writes directly
    to the database.
    Takes in option as a string and numberofstudies as an integer.
    """
    start=time.time()
    os.chdir(program_loc)
    StudyIDs.create_list(numberofstudies)
    data=open('List of StudyIDs.txt','r')

    for line in data:
        try:
            examID=str(line[line.find('[')+1:line.find(']')])
            exam_loc=data_loc+'/'+examID
            query.queries(examID)
            if option=='Instances':
                instances.run_code(examID,exam_loc)
            elif option=='SQL':
                SQL.run_code(examID,exam_loc)
                os.chdir(program_loc)
            else:
                pass
            shutil.rmtree(exam_loc)     #deletes files after use
            os.chdir(program_loc)
        #writes any errors to a file. continues through loop
        except Exception as e:
            os.chdir(program_loc)
            fil=open('Errors.txt','a')
            fil.write(line+'\t'+str(e)+'\n')
            fil.close()
    
    data.close()
    end=time.time()
    #prints how long it took to run in seconds
    print end-start
    return
    
def update_table(accession):
    """
    Runs code for a single accession number. Assumes that DICOM images are 
    already on the local hard drive, in a folder with the name as the accesion 
    number, in data_loc.
    """
    accessnum=str(accession)
    exam_loc=data_loc+'/'+accessnum
    try:
        SQL.run_code(accessnum,exam_loc)
    except Exception as e:
        os.chdir(program_loc)
        fil=open('Errors.txt','a')
        fil.write(accessnum+'\t'+str(e)+'\n')
        fil.close()
        print "Error. Please check Errors.txt for more details."
    return

########## RUN COMMANDS HERE
#update_table(7021095) for testing
fill_table(1000,option='SQL')

