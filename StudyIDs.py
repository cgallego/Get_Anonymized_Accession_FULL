# -*- coding: utf-8 -*-
"""
Created on Wed Mar 06 11:38:13 2013

@author: Karen Klassen
"""
from dictionaries import program_loc
import os
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#not apart of pipeline
def studyIDs():
    """
    Creates a text file containing all available study IDs. Uses file created 
    from querying the PACS directly (aka using Command Prompt).
    """
    os.chdir('/home/kklassen/Desktop/Query')
    
    queried=open('StudyIDs','r')
    new=open('Master.txt','w')
    
    studies=[]
    for line in queried:
        if line[0]=='I': continue
        if '(0008,0050)' in line:
            study=str(line[line.find('[')+1:line.find(']')]).rsplit()
            thing=study[0]
            if thing not in studies:
                new.write('['+thing+'] \n')
                studies.append(thing)
        
    queried.close()
    new.close()
    return

#not apart of pipeline  
def database_duplicates():
    """
    Looks for duplicates on the current database (aka tbl_pt_exam, the table
    that is being linked to). 
    Writes the DICOM numbers that were duplicated to a text file. 
    """
    Base=declarative_base()
    class Dicoms(Base):
        """
        Represents the tbl_pt_exam table.
        """
        __tablename__='tbl_pt_exam'
        
        pt_exam_id=sqlalchemy.Column(sqlalchemy.Integer,primary_key=True)
        exam_img_dicom_txt=sqlalchemy.Column(sqlalchemy.Text)
    
    engine='postgresql+psycopg2://biomatrix_ruser_mri_cad:'+\
            'bi0matrix4mricadSTUDY@142.76.29.187/biomatrixdb_raccess_mri_cad'
    engine1=sqlalchemy.create_engine(engine)
    Base.metadata.create_all(engine1)
    Session=sessionmaker(bind=engine1)
    session=Session()
    
    l=session.query(Dicoms).all()
    unique=[]   #contains unique DICOM numbers
    repeat=[]   #contains repeated DICOM numbers, ones already in unique
    for i in l:
        thing=i.exam_img_dicom_txt
        if thing not in unique:
            unique.append(thing)
        elif thing==None or thing=='image unrettriable by pacs' or thing==\
        'EXAM not on PACS' or thing=='bx' or thing=='MRN # is not on pacs':
            pass
        else:
            repeat.append(int(thing))
    
    cmd='findscu -v -S -k 0020,0010="" -k 0008,0052="STUDY" '+\
        '-aet MIAGDICOM2 -aec MRI_MARTEL 142.76.29.187 4006 2> dicoms'
    os.system(cmd)

    unique2=[]
    repeat2=[]
    dic={}
    stuff=open('dicoms','r')
    for i in stuff:
        if i[0]=='I': continue
        if '0020,0010' in i:
            dicom=str(i[i.find('[')+1:i.find(']')])
            if dicom not in unique2:
                unique2.append(dicom)
            else:
                repeat2.append(dicom)    
    
    os.chdir(program_loc)
    dup=open('Duplicates.txt','w')
    for x in repeat:
        dup.write('['+str(x)+'] \n')
    for i in repeat2:
        dup.write('['+str(i)+'] \n')
    dup.close()
    return 

def current_study_ids():
    """
    Creates a new document of all of the usable study IDs, removing the IDs
    that have already been written to the database.
    """
    os.chdir(program_loc)
    current=open('CurrentStudyIDs.txt','w')
    master=open('Master.txt','r')
    used=open('Usedlist.txt','r')
    nodata=open('No Data.txt','r')
    dup=open('AccessionDuplicates.txt','r')
    
    #finds ids in each line for each file
    masterlist=set([x[x.find('[')+1:x.find(']')] for x in master])
    nodatalist=set([l[l.find('[')+1:l.find(']')] for l in nodata])
    duplist=set([w[0:w.find(' ')] for w in dup])
    
    usedlist=[]
    for k in used:
        accnum=k[k.find('[')+1:k.find(']')].rsplit()
        usedlist.append(accnum[0])
    usedlist=set(usedlist)
    
    list2=masterlist.difference(usedlist)
    list3=list2.difference(nodatalist)
    list4=list3.difference(duplist)
    
    for w in list4:
        current.write('['+str(w)+'] \n')
    
    current.close()
    master.close()
    used.close()
    nodata.close()
    dup.close()
    return    

#not apart of pipeline
def comparison():
    """
    documentation!!
    """
    martins=[4023,4101,4463,4966,5763,5804,5955,6187,6317,6367,6414,6427,\
    7043,7399,7710,7844,8394,8461,8638,8817,8832,8904,9004,9030,9076,9467,\
    9586,9767,9889,9906,10096,10568,10906,10920,11043,11148,11166,11249,\
    11252,11312,12143,12288,12540,12867,13041,13297,13412,13785,14011,14020,\
    14795,14926,15108,16193,16273,16490,16640,16887,17102,17203,18060,18164,\
    18246,18730,20432]
    mine=database_duplicates()
    thing=[x for x in mine if x not in martins]
    return thing

#not apart of pipeline
def search():
    """
    Searches a file for repeated values.
    """
    ids=open('StudiesNotDone.txt','r')
    
    unique=[]
    repeat=[]
    for i in ids:
        if i not in unique:
            unique.append(i)
        else:
            repeat.append(i)
    return repeat

def create_list(number):
    """
    Creates a list of DICOM numbers to be added to the database.
    Takes in an integer and will create a list of that length.
    """
    current_study_ids()    
    
    current=open('CurrentStudyIDs.txt','r')
    new=open('List of StudyIDs.txt','w')
    
    lisofcur=[]
    for x in current:
        num=x[x.find('[')+1:x.find(']')]
        lisofcur.append(num)
    
    i=0
    while i<number:
        line='['+str(lisofcur[i])+'] \n'
        new.write(line)
        i+=1
    current.close()
    new.close()
    return
    
#not apart of pipeline
def other_docs(odoc,ndoc):
    os.chdir('/home/kklassen/Desktop/Query')
    old=open(odoc,'r')
    new=open(ndoc,'w')
    compare=open('ComparisonNoData.txt','w')
    
    for i in old:
        dicom=i[i.find('[')+1:i.find(']')]
        cmd='findscu -S -k 0020,0010='+str(dicom)+' -k 0008,0050="" -k '+\
        '0008,0052="STUDY" -aet MIAGDICOM2 -aec MRI_MARTEL 142.76.29.187 '+\
        '4006 2> switch.txt'
        os.system(cmd)
        fil=open('switch.txt','r')
        thing=[]
        for x in fil:
            if '0008,0050' in x:
                guy=x[x.find('[')+1:x.find(']')]
                thing.append(guy)
        line='['+str(thing[0])+'] \n'
        new.write(line)
        compare.write(str(dicom)+' '+str(thing)+'\n')
    old.close()
    new.close()
    compare.close()
    return