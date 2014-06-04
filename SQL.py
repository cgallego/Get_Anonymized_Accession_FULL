# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 10:36:51 2013

@author: Karen Klassen
"""
from dictionaries import biomatrix_user, biomatrix_password, biomatrix_host,\
biomatrix_database, program_loc
import instances
import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY

Base=declarative_base()
class Table(Base):
    """
    Represents the tbl_pt_mri_series table. This is the one that is filled by
    the later code.
    """
    __tablename__='tbl_pt_mri_series'
    
    pt_mri_series_id=sqlalchemy.Column(sqlalchemy.Integer,\
                            primary_key=True)
    exam_img_dicom_txt=sqlalchemy.Column(sqlalchemy.Text)
    series_uid_txt=sqlalchemy.Column(sqlalchemy.Text)
    series_desc_txt=sqlalchemy.Column(sqlalchemy.Text)
    translation_txt=sqlalchemy.Column(sqlalchemy.Text)
    type_int=sqlalchemy.Column(sqlalchemy.Integer)
    processed_yn=sqlalchemy.Column(sqlalchemy.Integer)
    protocol_txt=sqlalchemy.Column(sqlalchemy.Text)
    te_double=sqlalchemy.Column(sqlalchemy.Float)
    tr_double=sqlalchemy.Column(sqlalchemy.Float)
    pt_position_int=sqlalchemy.Column(sqlalchemy.Integer)
    side_txt=sqlalchemy.Column(sqlalchemy.Text)
    subtracted_yn=sqlalchemy.Column(sqlalchemy.Integer)
    registered_yn=sqlalchemy.Column(sqlalchemy.Integer)
    fat_saturated_yn=sqlalchemy.Column(sqlalchemy.Integer)
    three_d_yn=sqlalchemy.Column(sqlalchemy.Integer)
    contrast_yn=sqlalchemy.Column(sqlalchemy.Integer)
    img_int_array=sqlalchemy.Column(ARRAY(sqlalchemy.Integer))     
    voxel_spc_double_arry=sqlalchemy.Column(ARRAY(sqlalchemy.Numeric))    
    start_time=sqlalchemy.Column(sqlalchemy.Time)
    length_of_time_arry=sqlalchemy.Column(ARRAY(sqlalchemy.Integer))   
    img_orientation_int=sqlalchemy.Column(sqlalchemy.Integer)
    orientation_txt=sqlalchemy.Column(sqlalchemy.Text)
    a_no_txt=sqlalchemy.Column(sqlalchemy.Text)
    updated_on=sqlalchemy.Column(sqlalchemy.DateTime,\
                default=sqlalchemy.func.now())  #func.now causes auto-update
    
    def __init__(self,obj):
        """
        Creates a Table object (a row) having the same values as a Series 
        object. Takes in a single Series object.
        """
        self.exam_img_dicom_txt=obj.DICOMnum
        self.series_uid_txt=obj.UID
        self.series_desc_txt=obj.series
        self.translation_txt=obj.translation
        self.type_int=obj.type
        self.processed_yn=obj.processed
        self.protocol_txt=obj.protocol_name
        self.te_double=obj.te
        self.tr_double=obj.tr
        self.pt_position_int=obj.position
        self.side_txt=obj.side
        self.subtracted_yn=obj.sub
        self.registered_yn=obj.reg
        self.fat_saturated_yn=obj.fat
        self.three_d_yn=obj.dimension
        self.contrast_yn=obj.contrast
        self.img_int_array=obj.isize
        self.voxel_spc_double_arry=obj.vdim
        self.start_time=obj.intime
        self.length_of_time_arry=obj.timediffer
        self.img_orientation_int=obj.orient
        self.orientation_txt=obj.ormatrix
        self.a_no_txt=obj.accnum

#not apart of pipeline      
class Exam(Base):
    """
    Represents the tbl_pt_exam table
    """
    __tablename__='tbl_pt_exam'
    
    pt_exam_id=sqlalchemy.Column(sqlalchemy.Integer,primary_key=True)
    exam_img_dicom_txt=sqlalchemy.Column(sqlalchemy.Integer)

def run_code(examID, exam_loc):
    """
    Sets up connection with Biomatrix, creates rows and writes them to the 
    table (commits them).
    Takes in examID and exam_loc as strings.
    """
    engine='postgresql+psycopg2://'+biomatrix_user+':'+biomatrix_password+'@'\
            +biomatrix_host+'/'+biomatrix_database
    engine1=sqlalchemy.create_engine(engine)  
    Base.metadata.create_all(engine1)
  
    Session=sessionmaker(bind=engine1)
    session=Session()
    
    objs=instances.objects(examID,exam_loc)
    
    #this section is for if the table was linked to tbl_pt_exam table
    """
    #finds primary_key for matching DICOM number to link the two tables
    q=session.query(Exam).all()
    for x in q:
        if x.exam_img_dicom_txt==objs[0].DICOMnum:
            key=x.pt_exam_id
            break
    """
    
    #checks for duplicates and creates rows
    rows=[]
    for i in objs:
        duplicates(engine1,i)
        rows.append(Table(i))
    
    print 'Writing to database...'
    session.add_all(rows)
    session.commit()
    
    os.chdir(program_loc)
    new=open('Usedlist.txt','a')   #records examIDs already done
    new.write('['+str(examID)+'] \n')
    new.close()    
    
    #disconnects from database
    session.close()
    engine1.dispose()
    return

def duplicates(engine,single):
    """
    Assumes Series UID is unique.
    Checks tbl_pt_mri_series to make sure that no duplicates get created.
    Takes engine as a SQLAlchemy object and single as a Series object. 
    Errors out if it finds a duplicate.
    """
    Session=sessionmaker(bind=engine)
    session=Session()
    rows=session.query(Table).all()
    
    for r in rows:
        if r.series_uid_txt==single.UID:
            raise RuntimeError('Series is already in table by UID')
        if r.a_no_txt==single.accnum:
            raise RuntimeError('Series is already in table by Accession')
    return
    
def testing():
    """
    Used to see which accession numbers are on the database. Also gives the 
    total number of studies on the database.
    """
    engine='postgresql+psycopg2://'+biomatrix_user+':'+biomatrix_password+'@'\
            +biomatrix_host+'/'+biomatrix_database
    engine1=sqlalchemy.create_engine(engine)    
    Base.metadata.create_all(engine1)
    
    Session=sessionmaker(bind=engine1)
    session=Session()
    
    q=session.query(Table).all()
    results=[]
    for x in q:
        results.append(x.a_no_txt)
    thing=set(results)
    thing2=list(thing)
    thing2.sort()
    for i in thing2:
        print i
    print 'Total entered: '+str(len(thing2))
    return
    
def testing2():
    """
    Prints all entries for a given DICOM number.
    """
    engine='postgresql+psycopg2://'+biomatrix_user+':'+biomatrix_password+'@'\
            +biomatrix_host+'/'+biomatrix_database
    engine1=sqlalchemy.create_engine(engine)    
    Base.metadata.create_all(engine1)
    
    Session=sessionmaker(bind=engine1)
    session=Session()
    
    q=session.query(Table).all()
    for x in q:
        if x.exam_img_dicom_txt=='16385':
            #print x.pt_mri_series_id
            print x.exam_img_dicom_txt
            print x.series_uid_txt
            print x.series_desc_txt
            print x.translation_txt
            #print x.type_int
            #print x.processed_yn
            #print x.protocol_txt
            #print x.te_double
            #print x.tr_double
            #print x.pt_position_int
            #print x.side_txt
            #print x.subtracted_yn
            #print x.registered_yn
            print x.fat_saturated_yn
            #print x.three_d_yn
            #print x.contrast_yn
            #print x.img_int_array
            #print x.voxel_spc_double_arry
            #print x.start_time
            #print x.length_of_time_arry
            #print x.img_orientation_int
            #print x.orientation_txt
            #print x.updated_on
    return
    
def testing3():
    """
    Tests something else
    """
    engine='postgresql+psycopg2://'+biomatrix_user+':'+biomatrix_password+'@'\
            +biomatrix_host+'/'+biomatrix_database
    engine1=sqlalchemy.create_engine(engine)    
    Base.metadata.create_all(engine1)
    
    Session=sessionmaker(bind=engine1)
    session=Session()
    
    q=session.query(Table).all()
    
    for x in q:
        if x.start_time:
            print x.start_time, x.length_of_time_arry
    return