# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 15:24:27 2013

@author: Karen Klassen
"""
import dicom
from dictionaries import my_aet, remote_aet, remote_IP, remote_port, my_port, os_type, program_loc
import numpy
import os

def count(obj,exam_loc,user):
    """
    Assigns to the number attribute and time attributes for each object.
    Takes in list of Series's objects, exam_loc as a string, and user as a 
    boolean value (1-all files are on the hard drive, 0-files need to be 
    downloaded).
    """
    for i in obj:
        process=i.processed
        if i.type==3:
            i.number=i.readinfo('ImagesInAcquisition')
            if not i.number:
                try:
                    i.number=int(i.readinfo('Images in Series'))
                except:
                    pass
        elif i.type==1:
            i.number=1
        elif i.type==2 and not process:
            if user:
                move_files(i,exam_loc)
            else:
                files(i,exam_loc)
            filenames=os.listdir(exam_loc+'/'+i.UID)
            num=len(filenames)
            i.number=num
            
            times=[]
            os.chdir(exam_loc+'/'+i.UID)
            for f in filenames:
                data=dicom.read_file(f)
                time=int(data.ContentTime)
                hr=time//10000
                mi=(time%10000)//100
                sec=time%100
                times.append(hr*3600+mi*60+sec)     #changes time to seconds
            times=numpy.unique(times)
            
            tarray=[]
            for x in times:
                dif=int(x)-int(times[0])
                if dif==0:
                    continue
                tarray.append(dif)
            
            if not tarray:
                i.timediffer=None
            else:
                i.timediffer=tarray
            
            #changes seconds back to hours:minutes:seconds
            initsec=times[0]%60
            newtime=times[0]-initsec
            newtime=newtime/60
            initmin=newtime%60
            newtime=newtime-initmin
            newtime=newtime/60
            inithr=newtime%24
            
            i.intime=str(inithr)+':'+str(initmin)+':'+str(initsec)
    return
    
def files(single,exam_loc):
    """
    Gets every file in a given series and puts them in a new folder.
    Takes single Series object and exam_loc as a string.
    Note: Uses DCMTK. Also the command lines have been written for Windows 
    Operating System.
    """
    current_loc = os.getcwd() 
    os.chdir(exam_loc)
    if os_type=='Windows':
        #queries Instance UID at the image level for a given Series UID
        cmd=program_loc+os.sep+'findscu -S -k 0008,0018="" -k 0020,000e="'+single.UID+\
            '" -k 0008,0050="'+single.accnum+'" '+\
            '-k 0008,0052="IMAGE" -aet '+\
            my_aet+' -aec '+remote_aet+' '+remote_IP+' '+remote_port+\
            ' > T1Dynamic'+str(single.accnum)
    elif os_type=='Linux':
        cmd=program_loc+os.sep+'findscu -S -k 0008,0018="" -k 0020,000e="'+single.UID+\
            '" -k 0008,0050="'+single.accnum+'" '+\
            '-k 0008,0052="IMAGE" -aet '+\
            my_aet+' -aec '+remote_aet+' '+remote_IP+' '+remote_port+\
            ' 2> T1Dynamic'+str(single.accnum)
    print 'Getting entire series...'
    os.system(cmd)
    
    data=open('T1Dynamic'+str(single.accnum),'r')    
    
    #creates a new folder in data_loc with the same name as the Series UID
    if not(os.path.exists(str(single.UID))):
            os.mkdir(str(single.UID))
    os.chdir(str(single.UID))
    
    for i in data:
        if '0008,0018' in i:        #0008,0018=InstanceUID
            instanceUID=str(i[i.find('[')+1:i.find(']')])
            #moves files of given InstanceUID
            cmd2=program_loc+os.sep+'movescu -S +P '+my_port+' -k 0008,0018="'+instanceUID+\
                '" -k 0008,0052="IMAGE" -aec '+remote_aet+' -aet '+my_aet+\
                ' -aem '+my_aet+' '+remote_IP+' '+remote_port
            os.system(cmd2)
        else:
            pass
    return

def move_files(single,exam_loc):
    """
    Moves the files of a given series into a folder.
    Takes in single, a Series object, and exam_loc as a string.
    """
    uid=single.UID
    filenames=os.listdir(exam_loc)
    
    os.chdir(exam_loc)
    if not(os.path.exists(str(single.UID))):
            os.mkdir(str(single.UID))
    
    print 'Moving files...'
    for f in filenames:
        try:
            data=dicom.read_file(f)
            data_uid=data.SeriesInstanceUID
            if data_uid==uid:
                os.rename(exam_loc+'/'+str(f),exam_loc+'/'+str(single.UID)+\
                        '/'+str(f))
                single.loc=exam_loc+'/'+str(single.UID)
        except:
            continue
    return

def size(obj):
    """
    Assigns to the isize attribute for each object.
    Takes in list of Series's objects.
    Must be called after count.
    """
    for i in obj:
        process=i.processed
        x=i.readinfo('Rows')
        y=i.readinfo('Columns')
        z=i.number
            
        elementlist=[float(x),float(y),z]
        i.isize=numpy.array(elementlist)
        if i.type==2 and process:
            i.isize=None
        else:
            pass
    return