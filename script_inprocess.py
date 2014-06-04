#!/usr/bin/python 

import sys, os
import string
import shutil
import itertools
import glob ##Unix style pathname pattern expansion
import time
import shlex, subprocess
import SQL
from dictionaries import my_aet, hostID, local_port, clinical_aet, clinical_IP, clinical_port, remote_aet, remote_IP, remote_port

# ******************************************************************************
print '''
-----------------------------------------------------------
Runs batch Exam list to get Dicom Exams on a local folder based on list of 
Exam_list.txt(list of MRN StudyIDs DicomExam# )

Run on master folder: Z:\Cristina\Pipeline4Archive
where Z: amartel_data(\\srlabs)

usage: 	python Get_Anonymized_DicomExam.py Exam_list.txt
	[INPUTS]	
		Exam_list.txt (required) sys.argv[1] 

% Copyright (C) Cristina Gallego, University of Toronto, 2012 - 2013
% April 26/13 - Created first version that queries StudyId based on the AccessionNumber instead of DicomExamNo
% Sept 18/12 - 	Added additional options for retrieving only specific sequences (e.g T1 or T2)

-----------------------------------------------------------
'''
def update_table(accession, data_loc, program_loc):
    """
    Runs code for a single accession number. Assumes that DICOM images are 
    already on the local hard drive, in a folder with the name as the accesion 
    number, in data_loc.
    """
    accessnum=str(accession)
    exam_loc=data_loc+'/'+accessnum
    
    SQL.run_code(accessnum, exam_loc)
    try:
        SQL.run_code(accessnum, exam_loc)
    except Exception as e:
        os.chdir(program_loc)
        fil=open('Errors.txt','a')
        fil.write(accessnum+'\t'+str(e)+'\n')
        fil.close()
        print "Error. Please check Errors.txt for more details."
    return
    
def get_only_filesindirectory(mydir):
     return [name for name in os.listdir(mydir) 
            if os.path.isfile(os.path.join(mydir, name))]
            
def pull_pacs(path_rootFolder, remote_aet, remote_port, remote_IP, local_port, PatientID, StudyID, AccessionN):
	print 'EXECUTE DICOM/Archive Commands ...'
	print 'Query,  Pull,  Anonymize, Push ...'
	
	print '\n--------- QUERY Suject (MRN): "' + PatientID + '" in "' + clinical_aet + '" from "'+ my_aet + '" ----------'
	
	cmd = 'C:/Software/NewPipeline/Get_Anonymized_Accession/findscu -v -P -k 0008,1030="" -k 0008,103e="" -k 0010,0010="" -k 0010,0020="' + PatientID + 'SHSC*''"\
	-k 0008,1030="" -k 0008,0052="STUDY" -k 0008,0020="" -k 0020,0010="" -k 0008,0050="*" \
	-k 0008,0060="" -k 0020,0011="" -k 0020,000D= -k 0020,1002="" -aet ' + my_aet + \
	' -aec ' + clinical_aet + ' ' + clinical_IP + ' ' + clinical_port + ' > ' + path_rootFolder +os.sep+ 'tmp'+os.sep+'query_status1.txt' 	#142.76.62.102

	print '\n---- Begin query with ' + clinical_aet + ' by PatientID ....' ;
	print "cmd -> " + cmd
	p1 = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
	p1.wait()
	
	readQueryFile1 = open('tmp/query_status1.txt', 'r')
	readQueryFile1.seek(0)
	line = readQueryFile1.readline()
	print
	print '---------------------------------------'
	ListOfExams = []
	ListOfExamsUID = [] ; 
	ListOfExamsID = []
	while ( line ) : # readQueryFile1.readlines()):
		if '(0008,0060) CS [MR]' in line:	#Modality
			nextline = readQueryFile1.readline(),
			while ( 'StudyInstanceUID' not in nextline[0]) : #(0020,000d) UI
				nextline = readQueryFile1.readline(),
				
			item = nextline[0] 
			pullStudyUID = item[item.find('[')+1:item.find(']')]		
			print 'pullStudyUID => ' + pullStudyUID	
			
			nextline =  readQueryFile1.readline(),
			while ( 'AccessionNumber' not in nextline[0]) :	#(0020,0010) SH
				nextline = readQueryFile1.readline(),
				
			item = nextline[0]
			newAccessionN = item[item.find('[')+1:item.find(']')]
			print 'newAccessionNumber => ' + newAccessionN
				
			ListOfExams.append([newAccessionN, pullStudyUID])
			line = readQueryFile1.readline()
		else:
			line = readQueryFile1.readline()
			
	readQueryFile1.close()
	
	#################################################
	# Added: User input to pull specific Exam by Accession
	# Added by Cristina Gallego. April 26-2013			
	#################################################
	iExamPair=[]	
	for iExamPair in ListOfExams: # iExamID, iExamUID in ListOfExamsUID: #
		SelectedAccessionN = iExamPair[0]
		SelectedExamUID = iExamPair[1]
		print SelectedExamUID, SelectedAccessionN
		str_count = '';
		
		if len(SelectedAccessionN.strip()) == len(AccessionN.strip()):
			for k in range(0,len(AccessionN.strip())):
				if SelectedAccessionN[k] == AccessionN[k]:
					str_count = str_count+'1'
							
			print len(AccessionN)
			print len(str_count)
			if( len(AccessionN) == len(str_count)):
				print "\n===============\n SelectedAccessionN, SelectedExamUID"
				iAccessionN = SelectedAccessionN
				iExamUID = SelectedExamUID
				print iAccessionN, iExamUID
				print "\n===============\n"
				break
			else:
				os.chdir(program_loc)
				fil=open('Errors_pull.txt','a')
				fil.write(str(SelectedAccessionN)+'\tAccession number not found in AS0SUNB\n')
				fil.close()
				print "Error. Please check Errors.txt for more details."
				break		
	
	# Create fileout to print listStudy information
	# if StudyID folder doesn't exist create it		
	if not os.path.exists(path_rootFolder+os.sep+str(StudyID)):
		os.makedirs(path_rootFolder+os.sep+str(StudyID))
	 
	os.chdir(path_rootFolder+os.sep+str(StudyID))
	 
	# if AccessionN folder doesn't exist create it		
	if not os.path.exists(str(AccessionN)):
		os.makedirs(str(AccessionN))
		
	os.chdir(str(path_rootFolder))	
				
	#The images are queried and result is saved in tmp\\query_status1."
	fileout =  'output'+os.sep+'query_status1'
	
	# Required for pulling images.
	writeRetrieveFile1 = open('tmp'+os.sep+'oRetrieveExam.txt', 'w')
	readRetrieveFile1 = open('tmp'+os.sep+'RetrieveExam.txt', 'r')
	print "Read original tags from tmp\\RetrieveExam.txt. ......"
	readRetrieveFile1.seek(0)
	line = readRetrieveFile1.readline()
	outlines = ''
	
	while ( line ) : # readRetrieveFile1.readlines()):
		if '(0020,000d) UI' in line:	#StudyUID
			#print line, 
			fakeStudyUID = line[line.find('[')+1:line.find(']')]		
			print 'fakeStudyUID => ' + fakeStudyUID 
			line = line.replace(fakeStudyUID, iExamUID)
			outlines = outlines + line
			line = readRetrieveFile1.readline()
		else:
			outlines = outlines + line
			line = readRetrieveFile1.readline()
	
	writeRetrieveFile1.writelines(outlines)
	writeRetrieveFile1.close()
	readRetrieveFile1.close()		
	#print "tmp\\oRetrieveExam.txt is saved."
			
	readRetrieveFile2 = open('tmp'+os.sep+'oRetrieveExam.txt', 'r')
	print "Updated tags from tmp\\oRetrieveExam.txt. ......"
	for line in readRetrieveFile2.readlines(): # failed to print out ????
		print line,
	readRetrieveFile2.close()
	
	print '---------------------------------------'
	# Form a tmp\\RetrieveExam.dcm for pulling image.
	print os.path.isfile('dump2dcm.exe')	
	cmd = 'dump2dcm tmp\\oRetrieveExam.txt tmp\\RetrieveExam.dcm' #r'dump2dcm
	print 'cmd -> ' + cmd
	print 'Begin dump to dcm ....' ;
	os.system(cmd)
	print "tmp\\RetrieveExam.dcm is formed for pulling image from remote_aet."
	print
	
	# Now Create a subfolder : AccessionN to pull images .
	os.chdir(path_rootFolder+os.sep+str(StudyID)+os.sep+str(AccessionN))
	
	########## START PULL #######################################		
	print 'Pulling images to cwd: ' + os.getcwd()
	cmd = path_rootFolder+os.sep+'movescu -v -P +P ' + local_port + ' -aem ' + my_aet + ' -aet ' + my_aet + ' -aec ' + clinical_aet \
	+ ' ' + clinical_IP + ' ' + clinical_port + ' ' + path_rootFolder+os.sep+'tmp'+os.sep+'RetrieveExam.dcm > ' + path_rootFolder+os.sep+'tmp'+os.sep+'out'   #142.76.62.102

	print 'cmd -> ' + cmd
	p1 = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
	p1.wait()
	########## END PULL #######################################
	
	print 'Next, to group "raw" image files into a hierarchical. ...'
	imagepath = path_rootFolder+os.sep+str(StudyID)+os.sep+str(AccessionN)
	print 'imagepath: ', imagepath
	
	# Group all image files into a number of series for StudyUID/SeriesUID generation.
	cmd = 'dcmdump +f -L +F +P "0020,000e" +P "0020,0011" "' + imagepath + '" > tmp\\pulledDicomFiles'  
	print 'cmd -> ' + cmd
	print 'Begin SortPulledDicom ....' ;
	lines = os.system(cmd)
	
	readPulledFiles = open('tmp\\pulledDicomFiles', 'r')
	
	print
	print '---------------------------------------'
	ListOfSeriesGroup    = [] ; # [SeriesNo, SeriesUID] # SeriesNumber
	ListOfSeriesGroupRev = [] ; # [SeriesUID, SeriesNo]     
	ListOfSeriesPairs    = [] ; # [imageFn, SeriesUID]
	#ListOfExamsID = []
	outlines = ""
	nextline = readPulledFiles.readline()
	while ( nextline ) : # readPulledFiles.readlines()):
		if 'dcmdump' in nextline:   #Modality
		
			item = nextline; #[0] 
			imageFn = item[item.find(')')+2 : item.find('\n')]      
			#print 'imageFn => ' + imageFn
			
			nextline = readPulledFiles.readline() # ( 'SeriesNumber' : #(0020,0011) IS
			item = nextline; #[0] 
			#print 'nextline: ', nextline, '; item: ', item
			SeriesNo = item[item.find('[')+1:item.find(']')]
			#print 'SeriesNo => ' + SeriesNo
			
			nextline =  readPulledFiles.readline() # ( 'SeriesInstanceUID' :    #(0020,000e) SH
			item = nextline; #[0]
			#print 'nextline: ', nextline, '; item: ', item
			SeriesUID = item[item.find('[')+1:item.find(']')]
			#print 'SeriesUID => ' + SeriesUID
						
			
			ListOfSeriesGroup.append([SeriesNo, SeriesUID])
			ListOfSeriesGroupRev.append([SeriesUID, SeriesNo])
			ListOfSeriesPairs.append([imageFn, SeriesUID])
			#outlines = outlines + imageFn + ', ' + SeriesUID + ', ' + SeriesNo + '\n'; 
			
			nextline = readPulledFiles.readline()
		else:
			nextline = readPulledFiles.readline()
	readPulledFiles.close()
	
	#
	# Make a compact dictionary for {ListOfSeriesGroup}.
	ListOfSeriesGroupUnique = dict(ListOfSeriesGroup) #ListOfSeriesGroup:
	ListOfSeriesGroupUniqueRev = dict(ListOfSeriesGroupRev)
	#
	
	# Make a compact dictionary\tuple for {ListOfSeriesPairs}.
	# ListOfSeriesAggregate = dict(ListOfSeriesGroup) #ListOfSeriesGroup:
	#
	
	outlines = outlines + '------ListOfSeriesPairs---------'+ '\n'
	for SeriesPair in ListOfSeriesPairs:
		outlines = outlines + SeriesPair[0] + ', ' + SeriesPair[1] + '\n';
		
		
	outlines = outlines + 'Size: ' + str(len(ListOfSeriesPairs)) + '\n\n';
	outlines = outlines + '------ListOfSeriesGroup---------' + '\n'
	
	#for SeriesPair in ListOfSeriesGroup:
	#   outlines = outlines + SeriesPair[0] + ', ' + SeriesPair[1] + '\n';
	for k,v in ListOfSeriesGroupUnique.iteritems():
		outlines = outlines + k + ', \t\t' + v + '\n';
	outlines = outlines + 'Size: ' + str(len(ListOfSeriesGroupUnique)) + '\n\n';
	
	outlines = outlines + '------ListOfSeriesGroupRev---------' + '\n'

	#Calculate total number of the files of each series
	for k,v in ListOfSeriesGroupUniqueRev.iteritems():
		imagefList = []
		#print 'key -> ', v, # '\n'
		for SeriesPair in ListOfSeriesPairs:
			if SeriesPair[1] == k: # v:
				#print SeriesPair[1], '\t\t', v 
				imagefList.append(SeriesPair[0])                
		#print '(', len(imagefList), 'images are sorted.)\n\n'
		outlines = outlines + k + ', \t\t' + v + '\t\t' + str(len(imagefList)) + '\n';
	outlines = outlines + 'Size: ' + str(len(ListOfSeriesGroupUniqueRev)) + '\n\n';
	outlines = outlines + 'StudyInstanceUID: ' + str(AccessionN) + '\n';

	outlines = outlines + '\n\n------ListOfSeriesGroup::image files---------' + '\n'

	#List all files of each series
	for k,v in ListOfSeriesGroupUniqueRev.iteritems():
		imagefList = []     
		for SeriesPair in ListOfSeriesPairs:
			if SeriesPair[1] == k: # v:
				imagefList.append(SeriesPair[0])                
				#outlines = outlines + SeriesPair[0] + '\n';
		outlines = outlines + k + ', \t\t' + v + '\t\t' + str(len(imagefList)) + '\n\n';
	#outlines = outlines + 'Size: ' + str(len(ListOfSeriesGroupUniqueRev)) + '\n';

	
	writeSortedPulledFile = open('tmp\\sortedPulledDicomFiles', 'w')    
	try:
		writeSortedPulledFile.writelines(outlines)
	finally:
		writeSortedPulledFile.close()   

	print "List of Series: ", ListOfSeriesGroupUnique, "\n\n", ListOfSeriesPairs, "\n\n", ListOfSeriesGroup
	

	#################################################################
	# Anonymize/Modify images.      								#
	# (0020,000D),StudyUID  (0020,000e),SeriesUID                   #
	# (0010,0010),PatientName/ID                                    #
	# (0012,0021),"BRCA1F"  (0012,0040),StudyNo                     #
	#################################################################
	print '\n---------------Anonymize images'
	
	# Make anonymized UID.
	print 'Check out system date/time to form StudyInstUID and SeriesInstUID ' # time.localtime() 
	tt= time.time() # time(). e.g. '1335218455.013'(14), '1335218447.9189999'(18)
	shorttime = '%10.5f' % (tt)         # This only works for Python v2.5. You need change if newer versions.
	print 'SRI_DCM_UID =' + SRI_DCM_UID, 'shorttime -> ' + shorttime #shorttime: xxxxx --> (16 digits)                 
	
	anonyStudyUID = SRI_DCM_UID + shorttime + '.' + hostID + str(AccessionN).strip() ;
	print 'anonyStudyUID->', anonyStudyUID, '\n'

	#For Loop: every Series# with the Exam# in Anonymizing  
	sIndex = 0  
	ClinicTrialNo = StudyNo.strip()
	print 'ClinicTrialNo: "' + ClinicTrialNo + '"'
	print 'Begin Modify ....' ;
	for k,v in ListOfSeriesGroupUniqueRev.iteritems():
		sIndex = sIndex + 1 
		imagefList = []
		tt= time.time() 
		shorttime = '%10.7f' % (tt)     
		anonySeriesUID = SRI_DCM_UID + '' + shorttime + '' + shostID + v + '%#02d' % (sIndex)       
		print 'key -> ', v, '\t', 'anonySeriesUID->', anonySeriesUID, # '\n' '\t\t\t', k    

		for SeriesPair in ListOfSeriesPairs:
			if SeriesPair[1] == k: # v:
				#print SeriesPair[1], '\t\t', v #, '\n' ###[0], '\t\t', k #, '\n'
				imagefList.append(SeriesPair[0])                
				cmd = 'dcmodify -gin -m "(0020,000D)=' + anonyStudyUID + '" -m "(0020,000e)=' + anonySeriesUID + '" \
				-m "(0010,0010)=' + aPatientName + '" -m "(0010,0020)=' + aPatientID +'" \
				-i "(0012,0021)=BRCA1F" -i "(0012,0040)=' + ClinicTrialNo + '" ' + SeriesPair[0] + ' > tmp\\dcmodified.txt'     
                                 
				lines = os.system(cmd)
				print cmd
				
		print '(', len(imagefList), ' images are anonymized.)'
		
	print 'Total Series: ' + str(len(ListOfSeriesGroupUniqueRev)) + '\n';
			
	
	bakimagepath = ('*.bak').strip() 
	print 'Clean backup files (' + imagepath + ') ....' ;
		
	for fl in glob.glob(bakimagepath): 
		#Do what you want with the file
		#print fl
		os.remove(fl)
	
	
	#####################################################################
	# Check anonymized Dicomd files resulted from modifing process.     #
	# This is used to compare with pulled Dicom Files.                  #
	#                                                                   #
	#####################################################################
	print 'Next, to group "anonymized" image files into a hierarchical. ...'
	print 'imagepath: ', imagepath
	
	# Group all image files into a number of series for StudyUID/SeriesUID generation.
	cmd = 'dcmdump +f -L +F +P "0020,000e" +P "0020,0011" "' + imagepath + '" > tmp\\anonyDicomFiles'   
	print 'cmd -> ' + cmd
	print 'Begin SortAnonyDicom ....' ;
	lines = os.system(cmd) 
	
	readAnonDicomFile = open('tmp\\anonyDicomFiles', 'r')
	#for line in readAnonDicomFile.readlines():
	#   print line,
	print
	print '---------------------------------------'
	ListOfSeriesGroup    = [] ; # [SeriesNo, SeriesUID] # SeriesNumber
	ListOfSeriesGroupRev = [] ; # [SeriesUID, SeriesNo]     
	ListOfSeriesPairs    = [] ; # [imageFn, SeriesUID]
	#ListOfExamsID = []
	outlines = ""
	nextline = readAnonDicomFile.readline()
	while ( nextline ) : 
		if 'dcmdump' in nextline:
		
			item = nextline; #[0] 
			imageFn = item[item.find(')')+2 : item.find('\n')]      
			#print 'imageFn => ' + imageFn
			
			nextline = readAnonDicomFile.readline() # ( 'SeriesNumber' : #(0020,0011) IS
			item = nextline; #[0] 
			#print 'nextline: ', nextline, '; item: ', item
			SeriesNo = item[item.find('[')+1:item.find(']')]
			#print 'SeriesNo => ' + SeriesNo
			
			nextline =  readAnonDicomFile.readline() # ( 'SeriesInstanceUID' :  #(0020,000e) SH
			item = nextline; #[0]
			#print 'nextline: ', nextline, '; item: ', item
			SeriesUID = item[item.find('[')+1:item.find(']')]
			#print 'SeriesUID => ' + SeriesUID
						
			
			ListOfSeriesGroup.append([SeriesNo, SeriesUID])
			ListOfSeriesPairs.append([imageFn, SeriesUID])
			#outlines = outlines + imageFn + ', ' + SeriesUID + ', ' + SeriesNo + '\n'; 
			
			nextline = readAnonDicomFile.readline()
		else:
			nextline = readAnonDicomFile.readline()
	readAnonDicomFile.close()
	
	#
	# Make a compact dictionary for {ListOfSeriesGroup}.
	ListOfSeriesGroupUnique = dict(ListOfSeriesGroup) #ListOfSeriesGroup:
	ListOfSeriesGroupUniqueRev = dict(ListOfSeriesGroupRev)
	#
				
	outlines = outlines + '------ListOfSeriesPairs---------'+ '\n'
	
	for SeriesPair in ListOfSeriesPairs:
		outlines = outlines + SeriesPair[0] + ', ' + SeriesPair[1] + '\n';

	outlines = outlines + 'Size: ' + str(len(ListOfSeriesPairs)) + '\n\n';
	outlines = outlines + '------ListOfSeriesGroup---------' + '\n'
	
	#for SeriesPair in ListOfSeriesGroup:
	#   outlines = outlines + SeriesPair[0] + ', ' + SeriesPair[1] + '\n';
	for k,v in ListOfSeriesGroupUnique.iteritems():
		outlines = outlines + k + ', \t\t' + v + '\n';
	outlines = outlines + 'Size: ' + str(len(ListOfSeriesGroupUnique)) + '\n\n';

	outlines = outlines + '------ListOfSeriesGroupRev---------' + '\n'

	#Calculate total number of the files of each series
	for k,v in ListOfSeriesGroupUniqueRev.iteritems():
		imagefList = []
		print 'key -> ', v, '\n'
		for SeriesPair in ListOfSeriesPairs:
			if SeriesPair[1] == k: # v:
				#print SeriesPair[1], '\t\t', v #, '\n' ###[0], '\t\t', k #, '\n'
				imagefList.append(SeriesPair[0])                
		print '(', len(imagefList), ' images.)\n'
		outlines = outlines + k + ', \t\t' + v + '\t\t' + str(len(imagefList)) + '\n';
	outlines = outlines + 'Size: ' + str(len(ListOfSeriesGroupUniqueRev)) + '\n\n';
	
	### Extra action to extract StudyInstUID.
	anyAnonDicomFile = (ListOfSeriesPairs[0])[0] #Take one file to extract StudyInstUID
	cmd = 'dcmdump +f -L +F +P "0020,000d" "' + anyAnonDicomFile.strip() + '" > tmp\\anonyDicomStudyUID'    
	print 'cmd -> ' + cmd
	print 'Begin SortDicom ....' ;
	lines = os.system(cmd) 
	
	readAnonDicomStudyUID = open('tmp\\anonyDicomStudyUID', 'r')
	nextline =  readAnonDicomStudyUID.readline()
	item =  readAnonDicomStudyUID.readline() # ( 'StudyInstanceUID' :   #(0020,000d) UI
	
	#   print 'nextline: ', nextline, '; item: ', item
	AnonStudyUID = item[item.find('[')+1:item.find(']')]
	print 'AnonStudyUID => ' + AnonStudyUID 
	readAnonDicomStudyUID.close()
	
	outlines = outlines + 'AnonStudyInstanceUID: ' + str(AnonStudyUID) + '\n'; #iExamUID

	outlines = outlines + '\n\n------ListOfSeriesGroup::image files---------' + '\n'

	#List all files of each series
	for k,v in ListOfSeriesGroupUniqueRev.iteritems():
		imagefList = []
		#print 'key -> ', v, '\n\n'
		for SeriesPair in ListOfSeriesPairs:
			if SeriesPair[1] == k: # v:
				imagefList.append(SeriesPair[0])                
				outlines = outlines + SeriesPair[0] + '\n';
		#print len(imagefList), '\n\n'
		outlines = outlines + k + ', \t\t' + v + '\t\t' + str(len(imagefList)) + '\n\n';
	#outlines = outlines + 'Size: ' + str(len(ListOfSeriesGroupUniqueRev)) + '\n';
	
	writeSortedAnonFile = open('tmp\\sortedAnonyDicomFiles', 'w')   
	try:
		writeSortedAnonFile.writelines(outlines)
		# Do things with fileh here
	finally:
		writeSortedAnonFile.close() 

	#print "List of Series: ", ListOfSeriesGroupUnique,  ListOfSeriesPairs, "\n\n", ListOfSeriesGroup
		

	#################################################################################
	# At this point, you need to check if the Exam to be archived.                  #
	# start PUSH                                                                            #
	#   
	print " imagepath -> ", imagepath
	cmd = 'storescu -v -aet ' + my_aet + ' -aec ' + dest_aet + ' ' + dest_signa + \
		' ' + dest_port + ' "' + imagepath + '" > tmp\\push'
	
	print "Push exam to destination (no exam found at destination). " 
	print "cmd -> " + cmd
	print 'Begin push ....' ;
	lines = os.system(cmd)
	print "This Exam has pushed succesfully."
		
	print """
	*       
	*   
	*The archiving for this Exam is done.'
	*   
	*   
	*Next Exam.
	"""
					
			
	
	
	
	
	
	
	
	
	
	
	print '\n---- Anonymization is compulsory now with image retrieving.  -----'
	print "Getting studyID# Accession# "
	print StudyID, AccessionN
			
	# Check whether wanted exam is archived on 'MRI_MARTEL'.
	print "---- Begin by checking if exam is archived on 'MRI_MARTEL'.\n"
	current_loc = os.getcwd() #'Z:'+os.sep+'Cristina'+os.sep+'Pipeline4Archive' 
	
	# the DICOM query model is strictly hierarchical and the information model hierarchy is PATIENT - STUDY - SERIES - INSTANCE
	# Each query can only retrieve information at exactly one of these levels, and the unique keys of all higher levels must be provided as part of the query. In practice that means you first have to identify a patient, then you can identify studies for that patient, then you can check which series within one study exist and finally you could see which instances (DICOM objects, images) there are within one series. 
	# First findscu will retrive SERIES for a given STUDYID
	cmd = 'C:/Software/NewPipeline/Get_Anonymized_Accession/findscu -v -S -k 0009,1002="" -k 0008,1030="" -k 0008,103e="" -k 0010,0010="" -k 0010,0020="" \
	-k 0008,0020="" -k 0008,0050=' + AccessionN + ' -k 0020,0010="" -k 0020,0011="" -k 0008,0052="SERIES" \
	-k 0020,000D="" -k 0020,000e="" -k 0020,1002="" \
	-aet ' + my_aet + ' -aec ' + remote_aet + ' ' + remote_IP + ' ' + remote_port+ ' > ' + path_rootFolder +os.sep+ 'output'+os.sep+'findscu_SERIES'	
		
	print '\n---- Begin query with ' + remote_aet + ' by AccessionN ....' ;
	print "cmd -> " + cmd
	#lines = os.system(cmd) 
	p1 = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
	p1.wait()
	
	# Create fileout to print listStudy information
	# if StudyID folder doesn't exist create it		
	if not os.path.exists(path_rootFolder+os.sep+str(StudyID)):
		os.makedirs(path_rootFolder+os.sep+str(StudyID))
	 
	os.chdir(path_rootFolder+os.sep+str(StudyID))
	 
	# if AccessionN folder doesn't exist create it		
	if not os.path.exists(str(AccessionN)):
		os.makedirs(str(AccessionN))
		
	os.chdir(str(path_rootFolder))	
				
	#The images are queried and result is saved in tmp\\findscu_SERIES."
	fileout =  'output'+os.sep+'findscu_SERIES'
	readQueryFile1 = open(fileout, 'r')
	readQueryFile1.seek(0) # Reposition pointer at the beginning once again
	line = readQueryFile1.readline()
	print
	print '---------------------------------------\n'
	ListOfExamsUID = []  
	ListOfSeriesUID = []
	ListOfSeriesID = []
	count = 0
	match = 0
	images_in_series = 0
		
	# write output to file sout
	seriesout =  path_rootFolder+os.sep+str(StudyID)+os.sep+str(AccessionN)+'_seriesStudy.txt'
	sout = open(seriesout, 'a')
	
	while ( line ) : # readQueryFile1.readlines()):
		if '(0008,0020) DA [' in line:	#SerieDate
			item = line
			exam_date = item[item.find('[')+1:item.find(']')]		
			#print 'exam_date => ' + exam_date	
			line = readQueryFile1.readline()
			
		elif '(0010,0010) PN [' in line:	#patient_name
			item = line
			patient_name = item[item.find('[')+1:item.find(']')] # this need to be anonymized
			patient_name = "AnonName"
			#print 'patient_name => ' + patient_name	
			line = readQueryFile1.readline()
			
		elif '(0008,1030) LO [' in line:	#exam_description
			item = line
			exam_description = item[item.find('[')+1:item.find(']')]		
			#print 'exam_description => ' + exam_description
			line = readQueryFile1.readline()
			
		elif '(0020,000d) UI [' in line:	#exam_uid
			item = line
			exam_uid = item[item.find('[')+1:item.find(']')]		
			#print 'exam_uid => ' + exam_uid	
			ListOfExamsUID.append(exam_uid)
			line = readQueryFile1.readline()
			
		elif '(0008,0050) SH [' in line:	#accession_number
			item = line
			accession_number = item[item.find('[')+1:item.find(']')]		
			#print 'accession_number => ' + accession_number	
			line = readQueryFile1.readline()
			
		elif '(0008,103e) LO [' in line:	#series_description
			item = line
			series_description = item[item.find('[')+1:item.find(']')]		
			#print 'series_description => ' + series_description
			line = readQueryFile1.readline()
			
		elif '(0020,000e) UI [' in line:	#series_uid
			item = line
			series_uid = item[item.find('[')+1:item.find(']')]		
			#print 'series_uid => ' + series_uid
			ListOfSeriesUID.append(series_uid)
			line = readQueryFile1.readline()
					
		elif '(0020,0011) IS [' in line:	#series_number
			item = line
			series_number = item[item.find('[')+1:item.find(']')]
			series_number = series_number.rstrip()
			ListOfSeriesID.append(series_number)
			#print 'series_number => ' + series_number
			if(match == 0):  # first series so far
				match = 1
				print " \nAccessionN: %1s %2s %3s %4s \n" % (accession_number, patient_name, exam_date, exam_description)
				print >> sout, " \nAccessionN: %1s %2s %3s %4s \n" % (accession_number, patient_name, exam_date, exam_description)
				#sout.write('AccessionN: '+str(accession_number)+' \t'+ str(patient_name)+ '\t ('+str(exam_date)+'\t'+str(exam_description)+')\n')
				print " series: # %2s %3s %4s \n" % ('series_number', 'series_description', '(#Images)')
				print >> sout, " series: # %2s %3s %4s \n" % ('series_number', 'series_description', '(#Images)')

			line = readQueryFile1.readline()
			
    		elif '(0020,1002) IS [' in line:	#images_in_series
    			item = line
			images_in_series = item[item.find('[')+1:item.find(']')]		
			#print 'images_in_series => ' + images_in_series
			line = readQueryFile1.readline()
			
    	 	elif( (line.rstrip() == '--------') and (match == 1) ):
    	 		if (images_in_series == 0): # some servers don't return 0020,1002, so count the series
    	 			cmd = current_loc+os.sep+'findscu -v -S -k 0009,1002="" -k 0008,1030="" -k 0008,103e="" -k 0010,0010="" -k 0010,0020="" \
				-k 0010,0020="" -k 0008,1030="" -k 0008,0020="" -k 0008,0050=' + AccessionN + ' -k 0020,0010="" -k 0020,0011="" -k 0008,0052="IMAGE" \
				-k 0020,000D="" -k 0020,000e='+series_uid+' -k 0020,0013="" \
				-aet ' + my_aet + ' -aec ' + remote_aet + ' ' + remote_IP + ' ' + remote_port + ' > output'+os.sep+'findscu_IMAGE'
				
				#lines = os.system(cmd) 
				p1 = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
				p1.wait()
				
				#The images are queried and result is saved in tmp\\findscu_SERIES."
				fileout_image = 'output'+os.sep+'findscu_IMAGE'
				readQueryFile2 = open(fileout_image, 'r')
				readQueryFile2.seek(0) # Reposition pointer at the beginning once again
				im_line = readQueryFile2.readline()
				
				while ( im_line ) :
					if '(0020,0013) IS [' in im_line: #image_number
						item = im_line
						image_number = item[item.find('[')+1:item.find(']')]
						#print 'image_number => ' + image_number
						images_in_series += 1 
						
					im_line = readQueryFile2.readline()	
				
				readQueryFile2.close()
			
			if( images_in_series > 1): 
				plural_string = "s"
			else: plural_string = "" 
				
			print ' series %2d: %3d %4s %5d image%s' % (int(count), int(series_number), series_description, int(images_in_series), plural_string)
			print >> sout, ' series %2d: %3d %4s %5d image%s' % (int(count), int(series_number), series_description, int(images_in_series), plural_string)
    	 	 	# ------------ FInish obtaining SERIES info 
    	 	 	
			line = readQueryFile1.readline()
			count += 1;
			images_in_series=0
		else:
			line = readQueryFile1.readline()
			
									
	
	sout.close()
	IDser = 0
	
	for IDseries in ListOfSeriesID:
		# if AccessionN folder doesn't exist create it	
		os.chdir(path_rootFolder+os.sep+str(StudyID))
		os.chdir(str(AccessionN))
     
           	# DO NOT SEPARATE STUDIES IN FOLDERS                            
           	#if not os.path.exists(str(ListOfSeriesID[int(IDser)])):
		#	os.makedirs(str(ListOfSeriesID[int(IDser)]))
		
		#os.chdir(str(ListOfSeriesID[int(IDser)]))
		
		# Proceed to retrive images
		# query protocol using the DICOM C-FIND primitive. 
		# For Retrieval the C-MOVE protocol requires that all primary keys down to the hierarchy level of retrieve must be provided
		cmd = current_loc+os.sep+'movescu -S +P '+ local_port +' -k 0008,0052="SERIES" -k 0020,000d=' + ListOfExamsUID[int(IDser)]+ ' -k 0020,000e=' + ListOfSeriesUID[int(IDser)] + '\
		-aec ' + remote_aet + ' -aet ' + my_aet + ' -aem ' + my_aet + ' ' + remote_IP + ' ' + remote_port
		print cmd
		
		# Image transfer takes place over the C-STORE primitive (Storage Service Class). 
		# All of that is documented in detail in pa  rt 4 of the DICOM standard.
		p1 = subprocess.Popen(cmd, shell=False)
		p1.wait()
		
	# After transfer Get total number of files to Anonymize
	path_Series_files = path_rootFolder+os.sep+str(StudyID)+os.sep+str(AccessionN)
	listSeries_files = get_only_filesindirectory(path_Series_files)
				
	# Anno Patient personal information such as "PatientName"
	for sfiles in listSeries_files:
		cmd = current_loc+os.sep+'dcmodify -ma "(0010,0010)=AnonName" '+sfiles
		p1 = subprocess.Popen(cmd, shell=False)
		p1.wait()
		try:
			p2 = subprocess.Popen(['rm', sfiles+'.bak'], shell=True, stdin=subprocess.PIPE)
			p2.wait()
		except ValueError:
			break

	# Go back - go to next 
	os.chdir(str(path_rootFolder))	
	IDser += 1 	
	
	#remove files
	os.remove(fileout)
	os.remove(fileout_image)
	
	return

program_loc = os.path.dirname(os.path.abspath(__file__))
########################### START ####################################
if __name__ == '__main__':
	# Get Root folder ( the directory of the script being run)
	path_rootFolder = os.path.dirname(os.path.abspath(__file__))
	print path_rootFolder
	
	if not os.path.exists('output'):
		os.makedirs('output')
	
	argc = len(sys.argv)
	if argc < 2 :
		print 'Not enough arguments are inputed. '
		print """
		usage: 	python Get_Anonymized_Accession.py Exam_list.txt 
		[INPUTS]
			Exam_list.txt (required) sys.argv[1] 
		"""
		exit() #if argc <= 2 | 0:
	else:		
			
		# Open filename list
		file_ids = open(sys.argv[1],"r")
		try:
			for fileline in file_ids:
				# Get the line: Study#, DicomExam#
				fileline = fileline.split()
				PatientID = fileline[0]
				StudyID = fileline[1]
				AccessionN = fileline[2]
								
				print '\n\n---- batch Get Anonymized DicomExam -----------------'
				print 'PatientID -> "' + PatientID + '"'
				print 'StudyID -> "' + StudyID + '"'
				print 'AccessionN -> "' + AccessionN + '"'
				
				# Call each one of these functions
				# 1) Pull StudyId/AccessionN pair from pacs 
				pull_pacs(path_rootFolder, remote_aet, remote_port, remote_IP, local_port, PatientID, StudyID, AccessionN)
				# 2) Annonimize StudyId/AccessionN pair from pacs
				
				# 3) Warite to Series/Level table in biomatrix 
				exam_loc = program_loc+os.sep+str(StudyID)
				update_table(AccessionN, exam_loc, program_loc) 
							
		finally:
			file_ids.close()
	

