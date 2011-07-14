# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Merging data - always custom
# this stuff is not often used, but is useful as a starting point when you need to merge two data files into one
# -----------------------------------------------------------------------------------------------------------------

import os, csv, sys, random, codecs

from narracat_constants import *
from narracat_utils import *


def mergeDataFiles_2():
	dataFileName = DATA_PATH + "Stories metadata missing info added.csv"
	respondentDataFileName = DATA_PATH + "Storytellers.csv"
	storyTextsFileName = DATA_PATH + "story texts missing info added.csv"
	outputFileName = DATA_PATH + "merged data.csv"
	format = '"%s",'
	
	dataFile = open(dataFileName, "U")
	try:
		dataRowsAsRead = csv.reader(dataFile)
		# this is necessary because the csv.reader object is "unscriptable"
		dataRows = []
		dataRows.extend(dataRowsAsRead)
	finally:
		dataFile.close()
		
	respondentDataFile = open(respondentDataFileName, "U")
	try:
		rowsAsRead = csv.reader(respondentDataFile)
		respondentDataRows = []
		respondentDataRows.extend(rowsAsRead)
	finally:
		respondentDataFile.close()
		
	storyTextsFile = open(storyTextsFileName, "U")
	try:
		rowsAsRead = csv.reader(storyTextsFile)
		storyTextsRows = []
		storyTextsRows.extend(rowsAsRead)
	finally:
		storyTextsFile.close()
			
	outputFile = codecs.open(outputFileName, encoding='utf-8', mode='w+')
	try:
		# write combined headers - 2 rows
		for i in range(2):
			for cell in dataRows[i]:
				outputFile.write(format % cell)
			for cell in respondentDataRows[i]:
				outputFile.write(format % cell)
			# one more for story text
			outputFile.write(format % "Text")
			outputFile.write("\n")
			
		# for each line in data file, write data from all files
		matches = {}
		i = 2
		storyTitlesMatched = []
		while i < len(dataRows) - 2:
			dataRow = dataRows[i]
			colsWritten = 0
			for cell in dataRows[i]:
				outputFile.write(format % cell)
				colsWritten += 1
			if colsWritten < len(dataRows[i]):
				for j in range(len(dataRows[i])-colsWritten):
					outputFile.write(",")
					colsWritten += 1
			foundRespondent = False
			for respondentRow in respondentDataRows:
				# in story data, respondent name is column 11 (starting at zero)
				# in respondent data, respondent name is column 9
				if len(respondentRow) > 0 and respondentRow[9].strip() == dataRow[11].strip():
					foundRespondent = True
					for cell in respondentRow:
						outputFile.write(format % cell)
						colsWritten += 1
					if colsWritten < len(respondentRow):
						for j in range(len(respondentRow)-colsWritten):
							outputFile.write(",")
							colsWritten += 1
			if not foundRespondent:
				print 'no respondent found for name', dataRow[11]
			titleFound = False
			for storyTextsRow in storyTextsRows:
				# in story data, story name is column 9 (starting at zero)
				# in story texts, story name is column 1
				titleFound = len(storyTextsRow) > 0 and storyTextsRow[1].strip() == dataRow[9].strip()
				if titleFound:
					outputFile.write(format % storyTextsRow[2])
					break
			if titleFound:
				storyTitlesMatched.append(dataRow[9])
			else:
				print 'no story found for name', dataRow[9]
			outputFile.write("\n")
			i += 1
		# print story texts with no matching data
		for storyTextsRow in storyTextsRows:
			if len(storyTextsRow) > 0 and storyTextsRow[1].strip():
				match = False
				for titleFound in storyTitlesMatched:
					match = storyTextsRow[1].strip() == titleFound.strip()
					if match:
						break
				if not match:
					print 'no data for story text', storyTextsRow[1]
	finally:
		outputFile.close()
		print "merge done"


def mergeDataFiles_1():
	dataFileName = DATA_PATH + "some data.csv"
	respondentDataFileNames = [DATA_PATH + "more data.csv", DATA_PATH + "even more data.csv"]
	outputFileName = DATA_PATH + "merged data.csv"
	format = '"%s",'
	
	dataFile = open(dataFileName, "U")
	#dataFile = codecs.open(dataFileName, encoding='utf-8')
	try:
		dataRowsAsRead = csv.reader(dataFile)
		# this is necessary because the csv.reader object is "unscriptable"
		dataRows = []
		dataRows.extend(dataRowsAsRead)
	finally:
		dataFile.close()
		
	respondentData = {}
	for respondentDataFileName in respondentDataFileNames:
		respondentDataFile = open(respondentDataFileName, "U")
		#respondentDataFile = codecs.open(dataFileName, encoding='utf-8')
		try:
			rowsAsRead = csv.reader(respondentDataFile)
			rows = []
			rows.extend(rowsAsRead)
			respondentData[respondentDataFileName] = rows
		finally:
			respondentDataFile.close()
			
	outputFile = codecs.open(outputFileName, encoding='utf-8', mode='w+')
	try:
		# write combined headers - 2 rows
		for i in range(2):
			for cell in dataRows[i]:
				outputFile.write(format % cell)
			for fileName in respondentData.keys():
				for cell in respondentData[fileName][i]:
					outputFile.write(format % cell)
				# there was a padding bug here but i fixed it by hand
			outputFile.write("\n")
		# for each line in data file, write data from all files
		i = 2
		while i < len(dataRows) - 2:
			matchesForThisRow = 0
			dataRow = dataRows[i]
			colsWritten = 0
			for cell in dataRows[i]:
				outputFile.write(format % cell)
				colsWritten += 1
			# kludge
			if colsWritten < 263:
				for j in range(263-colsWritten):
					outputFile.write(",")
					colsWritten += 1
			for fileName in respondentData.keys():
				for row in respondentData[fileName]:
					if len(row) > 0 and row[0].strip() == dataRow[0].strip(): # connecting ID must be in first column of all files
						matchesForThisRow += 1
						for cell in row:
							outputFile.write(format % cell)
							colsWritten += 1
						# kludge
						# note there was a bug here where if a respondent had info in one file but not the other,
						# the cols did not get padded. but it was only one person so i fixed it by hand
						if fileName.find("screening") >= 0 and colsWritten < 286:
							for j in range(286-colsWritten):
								outputFile.write(",")
								colsWritten += 1
						elif fileName.find("psychology") >= 0 and colsWritten < 398:
							for j in range(398-colsWritten):
								outputFile.write(",")
								colsWritten += 1
						if colsWritten != 286 and colsWritten != 398:
							print colsWritten, '    cols written (%s)' % fileName
			outputFile.write("\n")
			i += 1
	finally:
		outputFile.close()
		#for key in matches:
		#	print key, len(matches[key].keys())
		#	if key < 2:
				#print ", ".join(matches[key].keys())
		#		for id in matches[key].keys():
		#			print '    ', id
		print "merge done"
			
		
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
