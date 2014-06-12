# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 10:33:35 2013

@author: Karen Klassen
# Modified by Cristina Gallego - April 26-2013
"""
#computer-dependent variables, should be changed before use of code
my_aet='MIAGDICOM'
local_port='5006'
my_port='5006'
hostID = '142.76.29.100'

remote_aet='MRI_MARTEL'
remote_IP='142.76.29.187'
remote_port='4005'

clinical_aet="AS0SUNB"
clinical_IP='142.76.62.102'
clinical_port='104'

program_loc='Z:\Cristina\Pipeline4Archive\Get_Anonymized_Accession_FULL'
data_loc='Z:\Cristina\Pipeline4Archive\Get_Anonymized_Accession_FULL\querydata_Database'
annotrevealer_loc='Z:\Cristina\Pipeline4Archive\Get_Anonymized_Accession_FULL\Annotrevealer\Annotrevealer_log.txt'

biomatrix_user='biomatrix_ruser_mri_cad'
biomatrix_password='bi0matrix4mricadSTUDY'
biomatrix_host='142.76.29.187'
biomatrix_database='biomatrixdb_raccess_mri_cad'
os_type='Windows'     #can be 'Windows' or 'Linux'

"""
Manufacturers' Dictionaries
"""
GEterms={}
GEterms['Vibrant']='Volume Imaging for Breast Assessment'
GEterms['VIBRANT']='Volume Imaging for Breast Assessment'
GEterms['Localizer']='Orientation Scan'
GEterms['LOC']='Localizer' 
GEterms['DWI']='Diffusion Weighted Imaging'
GEterms['FSE']='Fast Spin Echo'
#GEterms['MIP']='Maximum Intensity Projection'
#GEterms['spgr']='Spoiled Gradient Echo'
GEterms['mip']='MIP'
GEterms['L2']='Left MIP 2'
GEterms['L3']='Left MIP 3'
GEterms['L4']='Left MIP 4'
GEterms['R2']='Right MIP 2'
GEterms['R3']='Right MIP 3'
GEterms['R4']='Right MIP 4'
GEterms['PJN']='Rotated MIP'
GEterms['COR']='Coronal'

GEterms['Lt']='Left'
GEterms['LT']='Left'
GEterms['Rt']='Right'
GEterms['RT']='Right'
GEterms['Ax']='Axial'
GEterms['AX']='Axial'
GEterms['Sag']='Sagittal'
GEterms['SAG']='Sagittal'
GEterms['Bilat']='Bilateral'

GEterms['FS']='Fat Saturated'
GEterms['FAT SAT']='Fat Saturated'
GEterms['reg']='Registered'
GEterms['Gad']='Gadolinium' 
GEterms['sub']='Subtracted'
GEterms['3d']='3D'

GEterms['w']='with'
GEterms['wo']='without'


Philterms={}


Sieterms={}


"""
Tags' Dictionaries
"""
tags1={}
tags2={}
tags1['ImagesinSeries']='0025'
tags2['ImagesinSeries']='1007'
tags1['ImageNumber']='0020'
tags2['ImageNumber']='0013'
tags1['Contrast']='0018'
tags2['Contrast']='0010'
