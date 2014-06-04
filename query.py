# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 09:32:54 2013

@author: Karen Klassen
"""
import dicom
from dictionaries import program_loc, data_loc, my_aet, my_port, remote_aet,\
remote_IP, remote_port, os_type
import os

def queries(examID):      
    """
    Finds necessary data and stores it in 'querydata'. Gets a file from each 
    series.
    Takes examID as a string.
    Note: Uses DCMTK. Also, the command lines have been written for Windows 
    Operating System.  """   
    
    os.chdir(data_loc)    
    
    if os_type=='Windows':
        #gets InstanceUID, SeriesDescription, and SeriesUID for each series
        cmd=program_loc+os.sep+'findscu -v -S -k 0008,0018="" -k 0008,1030="" -k 0008,103e="" \
            -k 0008,0050='+examID+' -k 0020,000e="" -k 0008,0052="SERIES" \
            -k 0020,000D="" -k 0020,000e="" -k 0020,1002="" -k 0008,0070="" \
            -aet '+my_aet+' -aec '+remote_aet+' '+remote_IP+' '+remote_port+' > querydata'+examID
      
    elif os_type=='Linux':
        cmd=program_loc+os.sep+'findscu -v -S -k 0009,1002="" -k 0008,1030="" -k 0008,103e="" -k 0010,0010="" -k 0010,0020="" \
            -k 0008,0020="" -k 0008,0050='+examID+' -k 0020,0011="" -k 0008,0052="SERIES" \
            -k 0020,000D="" -k 0020,000e="" -k 0020,1002="" -k 0008,0070="" \
            -aet '+my_aet+' -aec '+remote_aet+' '+remote_IP+' '+remote_port+' 2> querydata'+examID 
      
    print 'Searching Accession...'
    print examID
    os.system(cmd)
    print cmd
    
    data=open('querydata'+examID)
    
    if not(os.path.exists(str(examID))):
        os.mkdir(str(examID))
    os.chdir(str(examID))    
    
    cmd2='Empty'
    for i in data:
        if '(0008,0018) UI (no value available)' in i: 
            pass
        
        elif '0008,0018' in i:        #0008,0018=InstanceUID
            instanceUID=str(i[i.find('[')+1:i.find(']')])
            print instanceUID
            #moves files of given InstanceUID
            cmd2=program_loc+os.sep+'movescu -S -v +P '+my_port+' -k 0008,0018="'+instanceUID+\
                '" -k 0008,0052="IMAGE" -aec '+remote_aet+' -aet '+my_aet+\
                ' -aem '+my_aet+' '+remote_IP+' '+remote_port
            os.system(cmd2)
       
        else:
            pass

    if cmd2=='Empty':
        new=open('No Data.txt','a')
        new.write('['+str(examID)+'] \n')

    data.close()
    return

#not apart of pipeline 
def series():
    """
    Reads the SeriesDescription and saves it in a list. Creates a list of the 
    file names in the same order as the series descriptions.
    Returns both lists.
    """  
    series=[]                   
    tag='SeriesDescription'
    names=os.listdir(data_loc)
    filenames=[]
    numbers=[]                      #keeps a list of SeriesUIDs already used
    datalength=(len(names)*10)+20
    os.chdir(program_loc)
    data=open('querydata')
    
    os.chdir(data_loc)

    k=0
    i=0
    while i<=datalength:
        line=data.readline()
        if line=='': break
        if line[0]=='I': continue
        if tag in line:
            series.append(line[line.find('[')+1:line.find(']')])
            position=data.tell()
            sernum=data.readline()      #current SeriesUID
            numbers.append(sernum[sernum.find('[')+1:sernum.find(']')])
            data.seek(position)
            
            for j in names:
                n=dicom.read_file(j)
                if str(n.SeriesInstanceUID).split()==numbers[k].split():
                    filenames.append(j)
                else:
                    pass
            k+=1
        elif len(series)!=len(filenames):
            print "Error with list lengths"
            break
        else:
            pass
        i+=1
    return series, filenames

#not apart of pipeline
def retrieval (examID):
    """
    Finds and gets a file from each series and lists the series descriptions 
    by calling query and series.
    Takes examID as a string or integer.
    Returns a list of series descriptions and a list of file names.
    """
    queries(examID)
    s, f=series()
    return s, f

def harddrive(exam_loc):
    """
    Finds a file for each series in a given location on the hard drive.
    Takes in exam_loc as a string.
    Returns a list of series descriptions, a list of file names as strings, 
    and user as a boolean (determines whether or not all of the files were
    on the hard drive).
    """
    os.chdir(exam_loc)
    filenames=os.listdir(exam_loc)
    usable_files=[]
    UIDs=[]                  #keeps track of the UIDs already used
    series=[]
    counters={}
  
    for x in filenames:
        data=dicom.read_file(x, force=True)
        print data
        if not usable_files:
            usable_files.append(x)
            UIDs.append(data.SeriesInstanceUID)
            series.append(data.SeriesDescription)
            counters[data.SeriesInstanceUID]=0
        for i in UIDs:
            ID=data.SeriesInstanceUID
            if ID not in UIDs:
                usable_files.append(x)
                UIDs.append(ID)
                #in case Series Description isn't a keyword
                if data.has_key('SeriesDescription'):
                    series.append(data.SeriesDescription)
                else:
                    series.append(data['0008','103e'].value)
                counters[ID]=0
            elif ID==i:
                counters[ID]+=1
    user=0
    for i in UIDs:
        if counters[i]>1:
            user=1
            break
    return series, usable_files, user