#!/usr/bin/python 
#############################################################################################################################
# Usage ---

# M:\Pipeline4Archive>python Archive_ExamNo_bmri_win32.py -aem MIAGDICOM -aet AS0S
# UNB -aec MRI_MARTEL "1075470SHSC*" "331"#
#
# C:\~4Archive>																												#
#																															#
#	->Real use on MIAGDICOM or SMIALBCAD2.																					#
# C:\~4Archive>python Archive_bmri_win32.py "1132763SHSC*" "885"															#
# C:\~4Archive>python Archive_bmri_win32.py -aem MIAGDICOM -aet AS0SUNB -aec MRI_MARTEL "1132763SHSC*" "885"				#
# C:\~4Archive>python Archive_bmri_win32.py -aem SMIALBCAD2 -aet AS0SUNB -aec MRI_MARTEL "1132763SHSC*" "885"				#
# C:\~4Archive>python Archive_bmri_win32.py -aem BMRIWSTATION64 -aet AS0SUNB -aec MRI_MARTEL "2286003*" "888"				#
#																															#
#																															#
#	->Test use on MIAGDICOM or SMIALBCAD2.																					#
#																															#
# C:\~4Archive>python Archive_bmri_win32.py -aem SMIALBCAD2 -aet AS0SUNB -aec MIAGDICOM "2286003*" "888"					#
# C:\~4Archive>python Archive_bmri_win32.py -aem BMRIWSTATION64 -aet MRI_MARTEL -aec MIAGDICOM "5309895SHSC*" "869"			#
# C:\~4Archive>python Archive_bmri_win32.py -aem BMRIWSTATION64 -aet AS0SUNB -aec MIAGDICOM "2286003*" "888"				#
#																															#
# or																														#
#																															#
#	->Test use on MIAGDICOM or SMIALBCAD2.																					#
# >>> os.system('python Archive_bmri_win32.py -aem SMIALBCAD2     -aet AS0SUNB	 -aec MRI_MARTEL "2286003*"	"888" ')		#
# >>> os.system('python Archive_bmri_win32.py -aem BMRIWSTATION64 -aet AS0SUNB	 -aec MRI_MARTEL "2286003*" "888" ')		#
#																															#
#	->Test use on BMRIWSTATION64 or SMIALBCAD2.('BMRIWSTATION64' is for test only)											#
# >>> os.system('python Archive_bmri_win32.py -aem BMRIWSTATION64 -aet AS0SUNB	 -aec MIAGDICOM "2286003*" "888" ')			#
#																															#
# >>> os.system('python Archive_bmri_win32.py -aem BMRIWSTATION64 -aet MRI_MARTEL -aec MIAGDICOM "2211321*"	   "667" ')		#
# >>> os.system('python Archive_bmri_win32.py -aem BMRIWSTATION64 -aet MRI_MARTEL -aec MIAGDICOM "5309895SHSC*" "869" ')	#
# >>> os.system('python Archive_bmri_win32.py -aem BMRIWSTATION64 -aet MRI_MARTEL -aec MIAGDICOM "1194476SHSC*" "160" ')	#
# >>> os.system('python Archive_bmri_win32.py -aem BMRIWSTATION64 -aet MRI_MARTEL -aec MIAGDICOM "2108882*"	   "396" ')		#
#																															#
#																															#
# >>> os.system('python Archive_bmri_win32.py ServerAET ClientAET "2777576SHSC"') # "2186178SHSC*"')						#
#rem "2777576SHSC"  "2207308SHSC" "8141847SHSC*"	"2186178SHSC*"															#
# or																														#
# >>> import Archive_bmri_win32	from Archive_bmri_win32																		#
#############################################################################################################################


import sys, os
import string
import shutil
import itertools
import glob ##Unix style pathname pattern expansion
import time


def Archive_cmd(my_hostname, my_aet, local_port, remote_aet, remote_port, remote_signa, dest_aet, dest_port, dest_signa, PatientID, StudyNo):


	print '---------  Anonymisition is compulsory now with image archiving.  ----------'
	### Required for build new DICOM dataset UID
	### InstanceUID = SRI_DCM_UID.sdatetime.hostID.xxxx (StudyID/SeriesNo/ImageID)
	# Need to modify hostID Ip based on local machine
	hostID = '142.76.30.200' # (Shar machine)
	hostIDwidth = len(hostID)	
	shostID = hostID[hostIDwidth-6:hostIDwidth] # Take the last 6 digits
	SRI_DCM_UID = '1.2.826.0.1.3680043.2.1009.'

	test=0
	if (test):
		print 'Check out system date/time to form StudyInstUID and SeriesInstUID ' # time.localtime() 
		tt= time.time()						# e.g. '1335218455.013'(14), '1335218447.9189999'(18)
		#print 'localtime -> ', repr(tt), 'lsize -> ', len(repr(tt))
		shorttime = '%10.5f' % (tt)			# This only works for Python v2.5. You need change if newer versions.
		print 'SRI_DCM_UID =' + SRI_DCM_UID, 'shorttime -> ' + shorttime #shorttime: xxxxx --> (16 digits)
							
		print 'SRI_DCM_UID =' + SRI_DCM_UID, ' ; hostID/shostID = ', hostID, ' and shorttime =', shorttime
		exit()


	#
	#Make an anonymized ID (1 or multiple values. Exhaust query is needed or 
	#duplicated-archive/mess-up happen!) for necessary query use.
	#
	aPatientID = StudyNo + 'CADPat' 
	aPatientName = 'Patient ' + StudyNo + 'Clinic'


	print
	print 'EXECUTE DICOM/Archive Commands ...'
	print 'Query,  Pull,  Anonymize, Push ...'
	print

	print '--------- QUERY Suject (MRN): "' + PatientID + '" with "' + dest_aet + '" at "'+ my_aet + '" ----------'
	print
	print

	#
	#'StudyNo' is good to check but not as robust as "PatientName" however, ... (it's controversy)!
	#Anyway, it's nice to try Query with 'StudyNo' first!
	#

	# Check whether wanted exam is archived on 'MRI_MARTEL'.
	print "Checking whether wanted exam is archived on 'MRI_MARTEL'.\n"
	
	cmd = 'findscu -v -S -k 0008,1030="" -k 0010,0010="" -k 0010,0020="" -k 0020,0010="" -k 0008,0020="" \
	-k 0008,0052="STUDY" -k 0020,000D="" -k 0012,0040="' + StudyNo + '" -k 0008,0060="" \
	-aet ' + my_aet + ' -aec ' + dest_aet + ' ' + dest_signa + ' ' + dest_port + ' > tmp/query_status0'			
			
	print "cmd -> " + cmd
	print 'Begin query with ' + dest_aet + ' by StudyNo ....' ;
	### Hide ###
	lines = os.system(cmd) 
	#print "The images are queried and result is saved in tmp\\query_status0."


	readQueryFile0 = open('tmp\\query_status0', 'r')
	#readQueryFile0.seek(0)
	line = readQueryFile0.readline()
	print
	print '---------------------------------------'
	ListOfArcSubjectExams = []
	while ( line ) :
		if '(0008,0060) CS [MR]' in line:	#Modality
			
			nextline = readQueryFile0.readline(),
			while ( 'PatientsName' not in nextline[0]) : #(0010,0010) PN
				nextline = readQueryFile0.readline(),
			item = nextline[0] 
			archivedPatName = item[item.find('[')+1:item.find(']')]		
			print 'archivedPatName => ' + archivedPatName	
			
			nextline =  readQueryFile0.readline(),
			while ( 'PatientID' not in nextline[0]) :	 #(0010,0020) LO
				nextline = readQueryFile0.readline(),			
			item = nextline[0]
			archivedPattID = item[item.find('[')+1:item.find(']')]
			print 'archivedPattID => ' + archivedPattID 
			
			nextline =  readQueryFile0.readline(),
			while ( 'StudyID' not in nextline[0]) :	 #(0020,0010) SH
				nextline = readQueryFile0.readline(),			
			item = nextline[0]
			archivedStudyID = item[item.find('[')+1:item.find(']')]
			print 'archivedStudyID => ' + archivedStudyID 
			
			ListOfArcSubjectExams.append([archivedStudyID, archivedPattID, archivedPatName])
			line = readQueryFile0.readline()
		else:
			line = readQueryFile0.readline()
	readQueryFile0.close()
	# print "List of Subjects/Studies (archived): ", ListOfArcSubjectExams
	print
	print


	
	print
	print '--------- Finished checking : "' + PatientID + '" at "' + dest_aet + '" at "'+ my_aet + '" ----------'
	print
	print
	

	

def pullimage(text):

	print "Pull image?"
	print text
	print """
	Everything is good!
	"""




	
if __name__ == '__main__':
	print """
	###
	# Note: a better parser is needed and it's leaving to you, the user of this script. Apr. 29, 2012 by Gary.
	#	Now, even all "ports" are no way to type in. No check is made if all input is validated or not. It's you 
	#	responsibility to make it.
	###
	"""
	
	argc = len(sys.argv)
	print sys.argv, argc

	if argc == 9 and sys.argv[1] == "-aem" and sys.argv[3] == "-aet" and sys.argv[5] == "-aec" :
		# Receive all three AE titles from 'command line'. However, the "ports" may be inconsistent with it. 
		# It's your, user's responsibility to assign a right one (check "List of AEs with Data warehouse").
		my_hostname = ''				# auto configure out self.
		my_aet = sys.argv[2]			# -aem
		print 'Client: "' + my_aet + '"'
		remote_aet = sys.argv[4]		# -aet
		print 'Server: "' + remote_aet + '"'
		dest_aet = sys.argv[6]			# -aec
		print 'DestAET: "' + dest_aet + '"'

		# Check registry to get corresponding PORT# and IP Address.
		if my_aet == "SMIALBCAD2" :
			local_port = '5006'
		elif my_aet == "MIAGDICOM" :
			local_port = '5006'
		elif my_aet == "BMRIWSTATION64" :
			local_port = '104'
		else :
			print "Please check commandline. The my_aet may not be all right."
			exit()
		print 'local_port: "' + local_port + '"'

		if remote_aet == "AS0SUNB" :
			remote_port = '104'
			remote_signa = '142.76.62.102'
		elif remote_aet == "MRI_MARTEL" :
			remote_port = '4006'
			remote_signa = '142.76.29.187'
		else :
			print "Please check commandline. The remote_aet may not be all right."
			exit()
		#remote_port = '4006'	#'104'			#5006
		#remote_signa = '142.76.29.187'		#'142.76.62.102'
		print 'remote_port: "' + remote_port + '"'
		

		if dest_aet == "MRI_MARTEL" :
			dest_port = '4006'
			dest_signa = '142.76.29.187'
		elif dest_aet == "MIAGDICOM" :
			dest_port = '5006'
			dest_signa = '142.76.29.100'
		else :
			print "Please check commandline. The dest_aet may not be all right."
			exit()		
		#dest_port = '5006'
		#dest_signa = '142.76.29.100'
		print 'dest_port: "' + dest_port + '"'

		print 'remote_signa: "' + remote_signa + '"'
		print 'dest_signa: "' + dest_signa + '"'

		# PatientID = sys.argv[1] # "2777576SHSC"
		PatientID = sys.argv[7]
		print 'PatientID -> "' + PatientID + '"'

		StudyNo = sys.argv[8]
		print 'StudyNo -> "' + StudyNo + '"'
 		
		
	elif argc == 3 :	
		print """
		###
		# Note: you need to determine if this is "Shar's' machine or 'MIAGDICOM' server. Apr. 29, 2012 by Gary.
		#		Otherwise you may make mistake.
		###
		"""
		# All uses default as three AE titles.
		my_hostname = ''	# auto configure out self ??? 			
		localAE = 'Shar'	#'Shar'	# 
		
		if localAE == 'Shar' :
			### This is Shar's machine.
			my_aet = "SMIALBCAD2"		# -aem
			local_port = '5006'
		elif localAE == 'MIAGDICOM' :
			### This is MIAGDICOM server.
			my_aet = "MIAGDICOM"		# -aem
			local_port = '5006'		
		else :
			print "Please check which machine you are using."
			exit()
		print 'Client: "' + my_aet + '"'
		
		remote_aet = "AS0SUNB"		# -aet
		print 'Server: "' + remote_aet + '"'
		
		dest_aet = "MRI_MARTEL"			# -aec
		print 'DestAET: "' + dest_aet + '"'

		# Check registry to get corresponding PORT# and IP Address.
		remote_port = '104'			#5006 #'4006'	#
		remote_signa = '142.76.62.102'	#
		dest_port = '4006'
		dest_signa = '142.76.29.187'	#'142.76.29.100'

		print 'local_port: "' + local_port + '"'
		print 'remote_port: "' + remote_port + '"'
		print 'dest_port: "' + dest_port + '"'
		print 'remote_signa: "' + remote_signa + '"'
		print 'dest_signa: "' + dest_signa + '"'

		PatientID = sys.argv[1]
		print 'PatientID -> "' + PatientID + '"'

		StudyNo = sys.argv[2]
		print 'StudyNo -> "' + StudyNo + '"'

		pass
	else :
		print 'Not enough arguments are inputed. '
		print """
		Usage: os.system(\'python Archive_bmri_win32.py [-aem my_aet -aet remote_aet -aec dest_aet] "XXXXXXXSHSC*" "StudyNo"\')
			-[OPTIONS]
			-my_aet			Local hostname
			-remote_aet		Remote hostname
			-dest_aet		Destination hostname
			-my_aet			Local hostname
			-XXXXXXXSHSC*	SubjectID (MRN) 
			-StudyNo		Subject Study Number
			-my_aet			Local hostname
		"""
		exit() #if argc <= 8 | 0:

	print
	print
	print
	print
	print
	print

	Archive_cmd(my_hostname, my_aet, local_port, remote_aet, remote_port, remote_signa, dest_aet, dest_port, dest_signa, PatientID, StudyNo)

	print """
		*****************************		
		*							*
		*All Exams are done.'		*
		*							*
		*							*
		*-------------Bye-----------*
			
			
	"""

	exit()
