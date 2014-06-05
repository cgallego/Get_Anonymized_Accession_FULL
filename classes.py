# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 09:11:10 2013

@author: Karen Klassen
"""
import dicom
import dictionaries
from dictionaries import data_loc
import numpy
import os

class Series():
    def __init__(self,series_descrip,filename,examID,exam_loc):
        """
        Creates each object (series). Calls every other function to set up the
        attributes. Each attribute represents a column of data in the table.
        Takes in the series description, filename, examID, and exam_loc as 
        strings.
        """
        #this order matters
        self.series=series_descrip
        self.filename=filename
        self.loc=exam_loc
        self.accnum=examID
        self.MRType()           #dimension
        self.patient_position() #position
        self.processor()        #processed
        self.contrast_tag()     #contrast
        self.TETR()             #te,tr
        self.translate()        #translation
        self.determine_side()   #side
        self.series_type()      #type
        self.fatsat_tag()       #fat
        self.orientation()      #orient
        self.size()             #vdim
        self.protocol_name=self.readinfo('Protocol Name')
        self.sub=self.boolean('Subtracted')
        self.reg=self.boolean('Registered')
        self.UID=self.readinfo('Series Instance UID')
        self.ormatrix=self.readinfo('Image Orientation Patient')
        self.DICOMnum=self.readinfo('Study ID')
        self.number=None
        self.isize=None
        self.intime=None
        self.timediffer=None
       
    def boolean(self,name):
        """
        Used to assign to the Subtracted and Registered attributes.
        Returns a boolean value (True-1, False-0)
        """
        typ=self.type
        
        if typ==3:
            boo=0
        elif typ==2:
            trans=self.translation
            if name in trans:
                boo=1
            else:
                boo=0
        else:
            boo=None    #MIPs are nullified for sub and reg
        return boo       
       
    def contrast_tag(self):
        """
        Used to assign to the Contrast attribute. 'contrast' is a boolean 
        value (Contrast-1, None-0)
        """
        con=self.readinfo('Contrast')
        process=self.processed
        
        if process:
            trast=None
        else:
            if con==None:
                trast=None
            elif 'GADOVIST' in con:
                trast=1
            else:
                trast=0
        self.contrast=trast
        return      
       
    def determine_side(self):
        """
        Determines which side of the body the series was taken from. 'side' is
        an integer (1-Left, 2-Right, or 3-Bilateral)
        """
        trans=self.translation
        
        if 'Left' in trans:
            sides=1     #Left
        elif 'Right' in trans:
            sides=2     #Right
        else:
            sides=3     #Bilateral
        self.side=sides
        return               
        
    #not currently used
    def fatsat(self):
        """
        Used to assign to the Fat Saturation attribute. 'fs' is a string.
        """
        process=self.processed
        typ=self.type
        name=self.series
        
        if process:
            fats='Processed'
        else:
            if typ=='Regular':
                if 'FS' in name or 'FAT SAT' in name and 'wo' not in name:
                    fats=1
                else:
                    fats=0
            else:
                fats=0
        self.fs=fats
        return     
        
    def fatsat_tag(self):
        """
        Uses Scan Options tag to determine Fat Saturation. 'fat' is a boolean
        value (Fat Saturated-1, Not-0)
        """
        process=self.processed
        tag=self.readinfo('Scan Options')
        print tag
        fats=None
        
        if tag:
            for i in tag:
                if i=='FS':
                    fats=1
                else:
                    pass
            if not fats:
                fats=0
        if process:      
            fats=None
        
        self.fat=fats
            
        return     
       
    def MRType(self):
        """
        Determines if the series is 3D or not. 'dimension' is a boolean value 
        (3D-1, 2D-0)
        """
        dimensions=self.readinfo('MR Acquisition Type')
        
        if dimensions==None:
            dim=None
        elif '3' in dimensions:
            dim=1
        else:
            dim=0
        self.dimension=dim
        return       
       
    def orientation(self):
        """
        Used to assign to the Image Orientation attribute. 'orient' is an 
        integer (1-Sagittal, 2-Axial, 3-Coronal, or 4-Oblique)
        """
        tag=self.readinfo('Image Orientation Patient')
        
        if tag==None:
            name=None
        elif tag==[-0,1,0,-0,-0,-1]:
            name=1      #Sagittal
        elif tag==[-1,-0,0,-0,-1,0]:
            name=2      #Axial
        elif tag==[1,0,0,0,0,-1]:
            name=3      #Coronal
        else:
            name=4      #Oblique
        self.orient=name
        return
       
    def patient_position(self):
        """
        Used to assign to the Patient Positon attribute. 'position' is an 
        integer (1-Prone or 2-Supine)
        """
        codes=self.readinfo('Patient Position')
        
        if codes==None:
            positions=None
        elif codes=='FFP':
            positions=1     #Prone
        elif codes=='HFS':
            positions=2     #Supine
        else:
            positions=None
        self.position=positions
        return
        
    def processor(self):
        """
        'Process them' 
        Used to assign to the Processed attribute. 'processed' is a boolean 
        value (Processed-1, Original-0)
        """
        nute=self.readinfo('Image Type')
        
        if not nute:
            gunray=None
        elif nute[0]=='DERIVED':
            gunray=1
        elif nute[0]=='ORIGINAL':
            gunray=0
        else:
            gunray=nute[0]
        self.processed=gunray
        return      
        
    def readinfo(self,tag):   
        """
        Used to find the information from a given tag. If tag is non-existent,
        returns None.
        Takes in the tag as a string.
        Returns the information as a string.
        """
        #gets rid of spacing in tag
        word=tag.rsplit()
        name=''             
        for i in word:
            name+=i
    
        os.chdir(self.loc)
        data=dicom.read_file(self.filename)
        if data.__contains__(name): # before if data.has_key(name): changed info due to port change
            info=data.__getattr__(name)
                    
        #checks if tag is in dictionaries (tags1 and tags2)
        elif name in dictionaries.tags1:
            try:
                info=data[dictionaries.tags1[name]\
                    ,dictionaries.tags2[name]].value
            except:
                print tag,"doesn't exist for",self.accnum,self.series
                info=None
        else:
            print tag,"doesn't exist for",self.accnum,self.series
            info=None
        return info        
        
    def series_type(self):
        """
        Determines the Series Type. 'type' is an integer (1-MIP, 2-T1 Dynamic,
        or 3-Other)
        """
        trans=self.translation
        
        if 'MIP' in trans:
            types=1     #MIP
        elif 'Subtracted' in trans or '3D' in trans or\
        'Volume Imaging for Breast Assessment' in trans or 'Registered'\
        in trans:
            types=2     #T1 Dynamic
        else:
            types=3     #Other
        self.type=types
        return       
    
    def size(self):
        """
        Used to find voxel spacing array. 
        Returns a numpy array of 3 float numbers.
        """
        x,y=self.readinfo('Pixel Spacing')
        z=self.readinfo('Slice Thickness')
            
        elementlist=[float(x),float(y),float(z)]
        element=numpy.array(elementlist)
        self.vdim=element
        return      
        
    def TETR(self):
        """
        Used to assign to the TE and TR attributes. 'te' and 'tr' are floats.
        """
        te=self.readinfo('Echo Time')
        tr=self.readinfo('Repetition Time')
        process=self.processed

        if process:
            te=None
            tr=None
        else:
            pass
        self.te=te
        self.tr=tr
        return     
      
    #not apart of pipeline
    def times(self):
        """
        Determines the time of each series. 'time' is a string.
        """
        types=self.type
        process=self.processed
    
        os.chdir(data_loc)    
        
        if process:
            time='Processed'
        else:
            if types=='T1 Dynamic':
                original=dicom.read_file(self.filename)
                time1=original.ContentTime
                time2=original.ContentTime
                #still has to go through entire hard drive
                files=os.listdir(data_loc)
                for i in files:
                    data=dicom.read_file(i)
                    if data.SeriesInstanceUID==original.SeriesInstanceUID:
                        if data.ContentTime<time1:
                            time1=data.ContentTime
                        elif data.ContentTime>time2:
                            time2=data.ContentTime
                        else:
                            pass
                    else:
                        pass
                time=str(time1)+'-'+str(time2)
            else:
                time=None
        self.time=time
        return       
        
    def translate(self):
        """
        Used to assign to the Translation attribute. 'translation' is a string
        """
        series_description=self.series
        os.chdir(self.loc)
        fil=dicom.read_file(self.filename)
        manufacturer=fil.Manufacturer
        break_down=series_description.rsplit()  
        trans=[]                                
        description=''                          
        
        for i in break_down:
            if manufacturer=='GE MEDICAL SYSTEMS':
                if i in dictionaries.GEterms:
                    trans.append(dictionaries.GEterms[i])
                elif '-' in series_description and '(' in series_description:
                    trans.append('Subtracted Image')
                else:
                    trans.append(i)
            else:
                trans.append('Unknown Manufacturer')
        
        for i in trans:
            description+=' '+i 
        self.translation=description
        return