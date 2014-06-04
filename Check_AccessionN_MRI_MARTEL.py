#!/usr/bin/python 

import sys, os
import string
import shutil
import itertools
import glob ##Unix style pathname pattern expansion
import time
import shlex, subprocess
from dictionaries import my_aet, hostID, local_port, clinical_aet, clinical_IP, clinical_port, remote_aet, remote_IP, remote_port

# ******************************************************************************
print '''
-----------------------------------------------------------
Runs batch Exam list to get Dicom Exams on a local folder based on list of 
Exam_list.txt(list of MRN StudyIDs DicomExam# )

Run on master folder: Z:\Cristina\Pipeline4Archive
where Z: amartel_data(\\srlabs)

usage: 	python Get_Anonymized_DicomExam.py AccesionstoGet.txt
	[INPUTS]	
		Exam_list.txt (required) sys.argv[1] 

% Copyright (C) Cristina Gallego, University of Toronto, 2012 - 2013
% April 26/13 - Created first version that queries StudyId based on the AccessionNumber instead of DicomExamNo
% Sept 18/12 - 	Added additional options for retrieving only specific sequences (e.g T1 or T2)

-----------------------------------------------------------
'''
def get_only_filesindirectory(mydir):
     return [name for name in os.listdir(mydir) 
            if os.path.isfile(os.path.join(mydir, name))]
            
def check_pacs(path_rootFolder, remote_aet, remote_port, remote_IP, local_port, PatientID, StudyID, AccessionN):
	print 'EXECUTE DICOM/Archive Commands ...'
	print 'Query,  Pull,  Anonymize, Push ...'
	
	print '\n--------- QUERY Suject (MRN): "' + PatientID + '" in "' + remote_aet + '" from "'+ my_aet + '" ----------'
	print "Checking whether wanted exam is archived on 'MRI_MARTEL'.\n"
	
	cmd='findscu -S -k 0008,0020="" -k 0010,0010="" -k 0010,0020="" -k 0008,0018="" -k 0008,103e="" -k 0020,000e="" '+\
            '-k 0008,0050='+AccessionN+' -k 0008,0052="SERIES" \
        -aet '+my_aet+' -aec '+remote_aet+' '+remote_IP+' '+remote_port+' > '+ 'outcome'+os.sep+'querydata_'+AccessionN+'.txt' 
        
        #cmd = 'findscu -v -P -k 0008,1030="" -k 0008,103e="" -k 0010,0010="" -k 0010,0020="' + StudyID + '*''"\
	#-k 0008,1030="" -k 0008,0052="STUDY" -k 0008,0020="" -k 0020,0010="" -k 0008,0050="*" \
	#-k 0008,0060="" -k 0020,0011="" -k 0020,000D= -k 0020,1002="" \
	#-aet '+my_aet+' -aec '+remote_aet+' '+remote_IP+' '+remote_port+' > '+ 'outcome'+os.sep+'querydata_'+AccessionN+'.txt' 	

	#cmd = 'findscu -v -S -k 0008,1030="" -k 0010,0010="" -k 0010,0020="" -k 0020,0010="" -k 0008,0020="" \
	#-k 0008,0052="STUDY" -k 0020,000D="" -k 0012,0040="' + StudyID + '" -k 0008,0060="" \
	#-aet ' + my_aet + ' -aec ' + remote_aet + ' ' + remote_IP + ' ' + remote_port + ' >'+ 'outcome'+os.sep+'querydata_'+AccessionN+'.txt' 
	
	print '\n---- Begin query with ' + remote_aet + ' by PatientID ....' ;
	print "cmd -> " + cmd
	p1 = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE)
	p1.wait()
	
	#################################################
	# Check mthat accession exists
	readQueryFile1 = open('outcome'+os.sep+'querydata_'+AccessionN+'.txt' , 'r')
	readQueryFile1.seek(0)
	line = readQueryFile1.readline()
	ListOfSeries = []
	while ( line ) : # readQueryFile1.readlines()):
		#print line
		if '(0008,0020) DA [' in line: #(0020,000d) UI
			lineStudyDate = line
			item = lineStudyDate
			pullStudyDate = item[item.find('[')+1:item.find(']')]
			
			nextline =  readQueryFile1.readline(),
			
			if '(0008,0050) SH' in nextline[0]:	# Filters by Modality MR
				item = nextline[0]
				newAccessionN = item[item.find('[')+1:item.find(']')]
			
			nextline =  readQueryFile1.readline(),
			while ( '(0008,103e) LO' not in nextline[0]) : #(0008,1030) LO 
				nextline = readQueryFile1.readline(),
			
			item = nextline[0]
			pullExamsDescriptions = item[item.find('[')+1:item.find(']')]
			print 'MRStudyDate => ' + pullStudyDate
			print 'newAccessionNumber => ' + newAccessionN
			print 'pullExamsDescriptions => ' + pullExamsDescriptions
							
			'''---------------------------------------'''
			ListOfSeries.append([pullStudyDate, newAccessionN, pullExamsDescriptions])
			line = readQueryFile1.readline()
		else:
			line = readQueryFile1.readline()
	
	#################################################
	# Added: User input to pull specific Exam by Accession
	# Added by Cristina Gallego. April 26-2013			
	#################################################
	iExamPair=[]	
	flagfound = 1
	for iExamPair in ListOfSeries: # iExamID, iExamUID in ListOfExamsUID: #
		SelectedAccessionN = iExamPair[1]
		str_count = '';
		
		if SelectedAccessionN.strip() == AccessionN.strip():
			flagfound = 0
		
	if flagfound == 1:
		os.chdir(program_loc)
		fil=open('outcome'+os.sep+'Errors_pull.txt','a')
		fil.write(str(AccessionN)+'\tAccession number not found in '+remote_aet+'\n')
		fil.close()
		print "\n===============\n"
		sys.exit('Error. Accession number not found in '+remote_aet)
	else:
		print "\n===============\n"
		sys.exit('Accession number found in '+remote_aet)
			
	return

program_loc = os.path.dirname(os.path.abspath(__file__))
########################### START ####################################
if __name__ == '__main__':
	# Get Root folder ( the directory of the script being run)
	path_rootFolder = os.path.dirname(os.path.abspath(__file__))
	print path_rootFolder
	
	if not os.path.exists('outcome'):
		os.makedirs('outcome')
	
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
				# 2) Annonimize StudyId/AccessionN pair from pacs
				check_pacs(path_rootFolder, remote_aet, remote_port, remote_IP, local_port, PatientID, StudyID, AccessionN)
							
							
		finally:
			file_ids.close()
	

