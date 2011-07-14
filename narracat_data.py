# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Data handling objects and methods
# -----------------------------------------------------------------------------------------------------------------

import pickle, re, os, csv, sys, random, codecs

from narracat_constants import *
from narracat_utils import *

import numpy as np

# -----------------------------------------------------------------------------------------------------------------
class ColumnDefinition():
# -----------------------------------------------------------------------------------------------------------------
	def __init__(self, row, rowIndex):
		self.readFromRow(row, rowIndex)
		
	def readFromRow(self, row, rowIndex):
		if row:
			self.id = row[1]
			self.refersTo = row[2]
			if self.refersTo == "":
				self.refersTo = 'story' 
			self.longName = row[3]
			self.shortName = row[4]
			if FORMAT_FILE_HAS_MERGE_COLUMN:
				self.type = row[9]
			else: # this is for backward compatibility, added column in January 2011
				self.type = row[8]
		
			if row[0].strip():
				self.fieldNumber = int(row[0])
			else:
				self.fieldNumber = rowIndex
				
			self.codes = self.listFromStringRemovingBlankLines(row[5])
			self.longResponseNames = self.listFromStringRemovingBlankLines(row[6])
			
			if self.type in [TYPE_SLIDER, TYPE_TERNARY]:
				if SLIDERS_ARE_SINGLE_COLUMNS:
					self.codes = []
					self.codes.extend(SLIDER_SHORT_NAMES)
					self.longResponseNames = []
					self.longResponseNames.extend(SLIDER_SHORT_NAMES)
					self.shortResponseNames = []
					self.shortResponseNames.extend(SLIDER_SHORT_NAMES)
				else:
					self.shortResponseNames = self.listFromStringRemovingBlankLines(row[7])
					if FORMAT_FILE_HAS_MERGE_COLUMN and USE_MERGED_ANSWERS:
						lumpedNames = self.listFromStringRemovingBlankLines(row[8])
						if lumpedNames:
							self.shortResponseNames = []
							self.shortResponseNames.extend(lumpedNames)
				if PART_OF_SLIDER_NAME_TO_HIDE_FROM_GRAPHS:
					if self.shortName.find(PART_OF_SLIDER_NAME_TO_HIDE_FROM_GRAPHS) >= 0:
						self.type = TYPE_SLIDER_DO_NOT_GRAPH
			else:
				self.shortResponseNames = self.listFromStringRemovingBlankLines(row[7])
				if FORMAT_FILE_HAS_MERGE_COLUMN and USE_MERGED_ANSWERS:
					lumpedNames = self.listFromStringRemovingBlankLines(row[8])
					if lumpedNames:
						self.shortResponseNames = []
						self.shortResponseNames.extend(lumpedNames)
					
			if self.type == TYPE_MULTI_CHOICE:
				self.idWithListReference = "%s-%s" % (self.id, self.codes[0])
			else:
				self.idWithListReference = self.id
				
			if HAS_SEPARATE_QUESTIONS_FOR_SEPARATE_STORIES:
				self.storyNumber = 0
				# find out which story (if any) it refers to
				if self.refersTo in ["participant", "discard"]:
					self.storyNumber = 0 
				else:
					storyNumberText = stringBeyond(self.id, "Branch")
					self.storyNumber = int(storyNumberText) 
			else:
				self.storyNumber = -1

			#print self.id, self.refersTo, self.type, self.storyNumber
			
	def listFromStringRemovingBlankLines(self, aString):
		result = []
		pieces = aString.split("\n")
		for piece in pieces:
			if piece:
				result.append(piece)
		return result
				
	# simple gets ---------------------------------------------
	
	def shortResponseNameForCode(self, code):
		i = 0
		for aCode in self.codes:
			if code == aCode:
				return self.shortResponseNames[i]
			i += 1
		return ""
	
	def idWithoutStoryNumber(self):
		if self.storyNumber >= 0: 
			return stringUpTo(self.id, STORY_NUMBER_SUFFIX)
		else:
			return self.id
	
# -----------------------------------------------------------------------------------------------------------------
class Question():
# -----------------------------------------------------------------------------------------------------------------
	def __init__(self, id=None, refersTo=None, longName=None, shortName=None, type=None, codes=None, longResponseNames=None, shortResponseNames=None, storyNumber=None):
		self.id = id
		self.refersTo = refersTo
		self.longName = longName
		self.shortName = shortName
		self.type = type
		self.codes = [] 
		self.codes.extend(codes)
		self.longResponseNames = []
		self.longResponseNames.extend(longResponseNames)
		self.shortResponseNames = []
		self.shortResponseNames.extend(shortResponseNames)
		self.storyNumber = storyNumber
	
	# simple gets ---------------------------------------------
	
	def isChoiceQuestion(self):
		return self.type == TYPE_SINGLE_CHOICE or self.type == TYPE_MULTI_CHOICE or self.type == TYPE_MULTIPLE_CHOICE_DELIMITED
	
	def isScale(self):
		return self.type == TYPE_SLIDER
	
	def veryShortName(self):
		# often different for each project
		if self.shortName.find(":") >= 0:
			return stringUpTo(self.shortName, ":")
		else:
			return self.shortName
	
	def codeForShortResponseName(self, responseName):
		i = 0
		for name in self.shortResponseNames:
			if name == responseName:
				return self.codes[i]
			i += 1
		return None
	
	# adding data ---------------------------------------------
	
	def addColumnToAnswers(self, codes, longResponseNames, shortResponseNames):
		for code in codes:
			if len(code.strip()):
				self.codes.append(code)
		for name in longResponseNames:
			if len(name.strip()):
				self.longResponseNames.append(name)
		for name in shortResponseNames:
			if len(name.strip()):
				self.shortResponseNames.append(name)
				
	# gathering data from stories ---------------------------------------------
	
	def gatherAnswersFromStories(self, stories, slice=ALL_DATA_SLICE):
		result = []
		for story in stories:
			if story.matchesSlice(slice):
				values = story.gatherAnswersForQuestionID(self.id)
				if values:
					result.extend(values)
		return result
	
	def gatherScaleValuesFromStories(self, stories, slice=ALL_DATA_SLICE):
		if self.isScale():
			answers = self.gatherAnswersFromStories(stories, slice=slice)
			result = []
			for answer in answers:
				if answer and answer != DOES_NOT_APPLY:
					result.append(int(answer))
			return result
		else:
			return None
		
	def gatherTernaryValuesFromStories(self, stories, slice=ALL_DATA_SLICE):
		if self.type == TYPE_TERNARY:
			answers = self.gatherAnswersFromStories(stories, slice=slice)
			result = []
			for answer in answers:
				if answer and answer != DOES_NOT_APPLY:
					xyzTexts = answer.strip().split(TERNARY_VALUE_DELIMITER)
					result.append((int(xyzTexts[0]), int(xyzTexts[1]), int(xyzTexts[2])))
			return result
		else:
			return None
		
	def gatherRankedStoriesWithValues(self, stories):
		if self.isScale():
			storiesWithThisScale = []
			for story in stories:
				values = story.gatherAnswersForQuestionID(self.id)
				if values[0] and values[0] != DOES_NOT_APPLY:
					storiesWithThisScale.append((story, int(values[0])))
			storiesWithThisScale.sort(lambda a,b: cmp(a[1], b[1]))
			return storiesWithThisScale
		else:
			return None
		
	def gatherNumberOfSpecificValuesIfScale(self, stories, specificValue, slice=ALL_DATA_SLICE):
		if self.isScale():
			answers = self.gatherAnswersFromStories(stories, slice=slice)
			result = 0
			for answer in answers:
				if answer == specificValue:
					result += 1
			return result
		else:
			return None
		
	def gatherNumberOfNAsIfTernarySet(self, stories, slice=ALL_DATA_SLICE):
		if self.type == TYPE_TERNARY:
			answers = self.gatherAnswersFromStories(stories, slice=slice)
			result = 0
			for answer in answers:
				if answer == DOES_NOT_APPLY:
					result += 1
			return result
		else:
			return None
		
	def gatherNumberOfStoriesWithValuesAboveOrBelow(self, stories, aboveOrBelow, threshold, slice=ALL_DATA_SLICE):
		if self.isScale():
			answers = self.gatherAnswersFromStories(stories, slice=slice)
			result = 0
			for answer in answers:
				if aboveOrBelow == 'above':
					if answer and answer != DOES_NOT_APPLY and int(answer) > threshold:
						result += 1
				else:
					if answer and answer != DOES_NOT_APPLY and int(answer) < threshold:
						result += 1
			return result
		else:
			return None
		
	def gatherNumberOfNAsIfChoiceQuestion(self, stories, slice=ALL_DATA_SLICE):
		if self.isChoiceQuestion():
			count = 0
			for story in stories:
				if story.matchesSlice(slice):
					if story.gatherAnswersForQuestionID(self.id) is None:
						count += 1
			return count
		else:
			return None
		
	def gatherNamesAndCountsOfChoiceAnswers(self, stories, slice=ALL_DATA_SLICE):
		names = []
		counts = []
		if self.isChoiceQuestion():
			for answer in self.shortResponseNames:
				if not answer in names: # this is because of some duplicate answer names in a survey
					countForThisAnswer = 0
					for story in stories:
						if story.matchesSlice(slice):
							if story.hasAnswerForQuestionID(answer, self.id):
								countForThisAnswer += 1
					names.append(answer)
					counts.append(countForThisAnswer)
			numStoriesWithoutAnswers = 0
			for story in stories:
				if story.hasNoAnswerForQuestionID(self.id):
					numStoriesWithoutAnswers += 1
			if numStoriesWithoutAnswers > 0:
				names.append(NO_ANSWER)
				counts.append(numStoriesWithoutAnswers)
		return names, counts
	
# -----------------------------------------------------------------------------------------------------------------
class Respondent():
# -----------------------------------------------------------------------------------------------------------------
	def __init__(self, row, rowIndex, columnDefinitions):
		self.stories = []
		for i in range(MAX_POSSIBLE_STORIES_PER_RESPONDENT):
			story = Story()
			self.stories.append(story)
		self.readDataFromRowAndColumnDefinitions(row, rowIndex, columnDefinitions)
		
	def findFirstBlankStoryIndex(self):
		i = 0
		for story in self.stories:
			if not story.text.strip() and not story.title.strip():
				return i
			i += 1
		 
	def readDataFromRowAndColumnDefinitions(self, row, rowIndex, columnDefinitions):
		overallStoryIndex = self.findFirstBlankStoryIndex()
		colIndex = 0
		shiftColDefLookupBy = 0
		
		#print 'row', rowIndex
			
		while colIndex < len(row):
			
			cell = row[colIndex].strip()
			
			#print ' --- > cell', cell, 'shiftColDefLookupBy', shiftColDefLookupBy
			
			# find definition saying what column means
			colDef = None
			for aColDef in columnDefinitions:
				if aColDef.fieldNumber-1 == colIndex + shiftColDefLookupBy:
					colDef = aColDef
			if not colDef:
				print 'COULD NOT FIND DEFINITION FOR COLUMN INDEX', colIndex
				colIndex += 1
				continue 
			
			# deal with columns that refer to a numbered story
			if colDef.storyNumber >= 0:
				storyIndex = colDef.storyNumber-1
			else:
				storyIndex = overallStoryIndex
				
			# skip columns marked as discardable
			if colDef.refersTo == "discard":
				pass
			
			# participant data
			elif colDef.refersTo == "participant":
				
				# if this is the ID field, record it
				if colDef.id.find(RESPONDENT_ID_FIELD) >= 0:
					for story in self.stories:
						story.respondentPassword = cell
						self.id = cell 
				else:
					# apply data about participant to ALL stories that belong to it
					# this skip bug is a problem in one particular data format where blank scale values shift the line one cell
					# may not be necessary to keep
					for story in self.stories:
						datatHasSkipBugAndScaleCellIsEmpty = self.processCellForStory(cell, colDef, story, removeStoryNumber=False)
					if datatHasSkipBugAndScaleCellIsEmpty:
						shiftColDefLookupBy -= 1
						colIndex += 1
			else: # story data
				
				# story title
				if colDef.id.find(STORY_TITLE_FIELD) >= 0:
					if cell:
						self.stories[storyIndex].title = cell
					else:
						self.stories[storyIndex].title = NO_STORY_TITLE
					self.stories[storyIndex].number = storyIndex
					if (not QUESTION_NUMBER_APPEARS_AS_QUESTION) and INCLUDE_QUESTION_NUMBER_QUESTION:
						self.stories[storyIndex].addAnswer(QUESTION_NUMBER_ID, QUESTION_NUMBER_NAMES[storyIndex]) 
						
				# deal with story text
				elif colDef.id.find(STORY_TEXT_FIELD) >= 0:
					value = cell
					if not value.strip():
						value = NO_STORY_TEXT
					self.stories[storyIndex].text = value
					
				else:
					
					# deal with all other data about story
					datatHasSkipBugAndScaleCellIsEmpty = self.processCellForStory(cell, colDef, self.stories[storyIndex], removeStoryNumber=True)
					if datatHasSkipBugAndScaleCellIsEmpty:
						shiftColDefLookupBy -= 1
						colIndex += 1
			colIndex += 1
			
	def processCellForStory(self, cell, colDef, story, removeStoryNumber):
		
		type = colDef.type
		valuesToAdd = []
		datatHasSkipBugAndScaleCellIsEmpty = False
		
		if type == TYPE_SINGLE_CHOICE:
			if type in DATA_TYPES_WITH_CODES:
				value = self.codeLookup(colDef, cell)
				#if cell:
				#	print '  cell', cell, 'id', colDef.id, 'codes', colDef.codes, 'value', value
			else:
				value = cell
			if value:
				valuesToAdd.append(value)
				
		elif type == TYPE_MULTI_CHOICE:
			if type in DATA_TYPES_WITH_CODES:
				if COLUMN_VALUES_ARE_ALL_ONES: 
					if cell == "1":
						value = colDef.shortResponseNameForCode(colDef.codes[0])
					else:
						value = None
				else:
					value = self.codeLookup(colDef, cell)
			else:
				value = cell
			if value:
				valuesToAdd.append(value)
				
		elif type == TYPE_MULTIPLE_CHOICE_DELIMITED:
			if cell:
				pieces = cell.split(MULTIPLE_CHOICE_DELIMITED_DELIMITER)
				for piece in pieces:
					if piece.strip():
						if type in DATA_TYPES_WITH_CODES:
							value = self.codeLookup(colDef, piece.strip())
						else:
							value = piece.strip()
						if value:
							valuesToAdd.append(value)
		
		elif type == TYPE_STORY_BOX:
			if cell:
				valuesToAdd.append(cell)
			
		elif type == TYPE_COMMENT_BOX:
			if cell:
				valuesToAdd.append(cell)
				
		elif type == TYPE_REGULAR_TEXT_BOX:
			if cell:
				valuesToAdd.append(cell)
				
		elif type == TYPE_NUMERICAL_TEXT_BOX:
			if cell:
				valuesToAdd.append(cell)
		
		elif type == TYPE_SLIDER:
			if DATA_HAS_SLIDER_SHIFT_BUG and not cell:
				datatHasSkipBugAndScaleCellIsEmpty = True
				value = DOES_NOT_APPLY
			else:
				if type in DATA_TYPES_WITH_CODES:
					if COLUMN_VALUES_ARE_ALL_ONES:
						if cell == "1":
							value = colDef.shortResponseNameForCode(colDef.codes[0])
						else:
							value = None
					else:
						if SLIDER_VALUE_HAS_TWO_DELIMITED_PARTS:
							code = stringUpTo(cell, TWO_PART_SLIDER_VALUE_DELIMITER)
							if code and SLIDER_SECOND_PART_IS_MAXIMUM:
								maximum = stringBeyond(cell, TWO_PART_SLIDER_VALUE_DELIMITER)
								number = int(code)
								maxNumber = int(maximum)
								code = str(max(SLIDER_START, min(SLIDER_END, int(number * 100.0 / maxNumber))))
						else:
							code = cell
						if code and colDef.id in SLIDERS_TO_REVERSE:
							code = str(SLIDER_END - int(code) + SLIDER_START)
						value = self.codeLookup(colDef, code)
						#if code:
						#	print '  code', code, 'id', colDef.id, 'codes', colDef.codes, 'value', value
				else:
					value = cell
			if value:
				valuesToAdd.append(value)
		
		elif type == TYPE_TERNARY:
			if type in DATA_TYPES_WITH_CODES:
				value = self.codeLookup(colDef, cell)
			else:
				value = cell
			if value:
				valuesToAdd.append(value)
				
		if removeStoryNumber:
			colDefIDToUse = colDef.idWithoutStoryNumber()
		else:
			colDefIDToUse = colDef.id
			
		for valueToAdd in valuesToAdd:
			if valueToAdd:
				story.addAnswer(colDefIDToUse, valueToAdd)
				
		return datatHasSkipBugAndScaleCellIsEmpty
	
	def codeLookup(self, colDef, code):
		if code:
			value = colDef.shortResponseNameForCode(code)
			if not value:
				print 'NO MATCH:', colDef.id, colDef.codes, '---', code
		else:
			value = None 
		return value
			
	def removeEmptyStories(self):
		storiesToRemove = []
		for story in self.stories:
			if (not story.text.strip() or story.text == NO_STORY_TEXT) and (not story.title.strip() or story.title == NO_STORY_TITLE):
				storiesToRemove.append(story)
		numStoriesRemoved = len(storiesToRemove)
		for story in storiesToRemove:
			self.stories.remove(story)
		i = 0
		for story in self.stories:
			story.number = i
			i += 1
		#print 'for respondent %s, %s empty stories were removed' % (self.id, numStoriesRemoved)
		
	def acceptStoriesFrom(self, aRespondent):
		for story in aRespondent.stories:
			self.stories.append(story)
			
	# gathering data from stories ---------------------------------------------
	
	def gatherScaleValues(self, questions, fillWithZerosForMissingValues=True, slice=ALL_DATA_SLICE):
		allScaleValues = []
		for question in questions:
			if question.isScale():
				for story in self.stories:
					if story.matchesSlice(slice):
						values = story.gatherAnswersForQuestionID(question.id)
						if values:
							for value in values:
								if value and value != DOES_NOT_APPLY:
									allScaleValues.append(int(value))
								else:
									if fillWithZerosForMissingValues:
										allScaleValues.append(0)
						else:
							if fillWithZerosForMissingValues:
								allScaleValues.append(0)
		return allScaleValues
	
	def gatherTernaryValues(self, questions, slice=ALL_DATA_SLICE):
		allTernaryValues = []
		for question in questions:
			if question.type == TYPE_TERNARY:
				for story in self.stories:
					if story.matchesSlice(slice):
						values = story.gatherAnswersForQuestionID(question.id)
						if values:
							if values and values[0] != DOES_NOT_APPLY:
								xyzTexts = values[0].strip().split(TERNARY_VALUE_DELIMITER)
								allTernaryValues.append((int(xyzTexts[0]), int(xyzTexts[1]), int(xyzTexts[2])))
		return allTernaryValues
		
	def gatherMeanAndSDAmongAllScaleValues(self, questions, slice=ALL_DATA_SLICE):
		allScaleValues = []
		for question in questions:
			if question.isScale():
				for story in self.stories:
					if story.matchesSlice(slice):
						values = story.gatherAnswersForQuestionID(question.id)
						if values:
							for value in values:
								if value and value != DOES_NOT_APPLY:
									allScaleValues.append(int(value))
		if len(allScaleValues) > 2:
			npArray = np.array(allScaleValues)
			return np.mean(npArray), np.std(npArray)
		return None, None
	
	def getParticipantValueFromStories(self, questions, shortName):
		for question in questions:
			if question.shortName == shortName:
				values = self.stories[0].gatherAnswersForQuestionID(question.id)
				if values:
					return values[0]
				else:
					return None
		
# -----------------------------------------------------------------------------------------------------------------
class Story():
# -----------------------------------------------------------------------------------------------------------------
	def __init__(self):
		self.title = ''
		self.text = ''
		self.number = 0
		self.respondentPassword = ''
		self.answers = {}
		
	def allDetailsForDisplay(self, questions, includeCodes=False):
		result = ""
		result += "%s\n\n%s\n\n" % (self.title, self.text)
		resultStrings = []
		for refersTo in ["story", "participant"]:
			resultStrings.append("-------------------------\n")
			answerKeys = []
			answerKeys.extend(self.answers.keys())
			answerKeys.sort()
			for questionID in answerKeys:
				question = questionForID(questions, questionID)
				if question and question.refersTo == refersTo:
					if includeCodes:
						thisResult = '%s (%s): ' % (question.shortName, question.id)
					else:
						thisResult = '%s: ' % question.shortName
					for answer in self.answers[questionID]:
						code = question.codeForShortResponseName(answer)
						if code and code != answer and includeCodes:
							thisResult += '	%s (%s)' % (answer, code)
						else:
							thisResult += '	%s' % answer
						if answer != self.answers[questionID][-1]:
							thisResult += ", "
					resultStrings.append(thisResult + "\n")
		resultStrings.append("-------------------------\n")
		result += "".join(resultStrings)
		result = result.replace("\t", " ") # for some reason there are tabs in it?
		result += 'Respondent password: %s\n\n\n' % self.respondentPassword
		return result
		
	# adding data ---------------------------------------------
	
	def addAnswer(self, id, value):
		if len(value.strip()):
			if not self.answers.has_key(id):
				self.answers[id] = []
			self.answers[id].append(value)
			
	# gathering data from answers ---------------------------------------------
	
	def matchesSlice(self, slice):
		if slice == ALL_DATA_SLICE or len(SLICES) == 0:
			return True
		else:
			mySlices = self.gatherAnswersForQuestionID(SLICE_QUESTION_ID)
			if mySlices:
				mySlice = mySlices[0]
				return mySlice in [slice, ALL_DATA_SLICE]
			else:
				#print 'The story "', self.title, '" has no slice.'
				return False
			
	def hasAnswerForQuestionID(self, answer, id, includePartialMatches=False):
		if answer == NO_ANSWER:
			return self.hasNoAnswerForQuestionID(id)
		elif answer == ALL_ANSWERS:
			return self.hasAnyAnswerForQuestionID(id)
		else:
			answers = self.gatherAnswersForQuestionID(id)
			if answers:
				for anAnswer in answers:
					if includePartialMatches:
						if anAnswer.lower().find(answer.lower()) >= 0:
							return True
					else:
						if anAnswer == answer:
							return True
				return False
			return False
	
	def hasNoAnswerForQuestionID(self, id):
		answers = self.gatherAnswersForQuestionID(id)
		return answers is None
	
	def hasAnyAnswerForQuestionID(self, id):
		answers = self.gatherAnswersForQuestionID(id)
		return answers is not None
	
	def hasBothOfTwoQuestionAnswerTuples(self, firstQA, secondQA):
		if firstQA[1] == NO_ANSWER:
			haveFirstAnswer = self.hasNoAnswerForQuestionID(firstQA[0].id)
		elif firstQA[1] == ALL_ANSWERS:
			haveFirstAnswer = self.hasAnyAnswerForQuestionID(firstQA[0].id)
		else:
			haveFirstAnswer = self.hasAnswerForQuestionID(firstQA[1], firstQA[0].id)
		if secondQA[1] == NO_ANSWER:
			haveSecondAnswer = self.hasNoAnswerForQuestionID(secondQA[0].id)
		elif secondQA[1] == ALL_ANSWERS:
			haveSecondAnswer = self.hasAnyAnswerForQuestionID(secondQA[0].id)
		else:
			haveSecondAnswer = self.hasAnswerForQuestionID(secondQA[1], secondQA[0].id)
		return haveFirstAnswer and haveSecondAnswer
	
	def gatherAnswersForQuestionID(self, id):
		if self.answers.has_key(id):
			return self.answers[id]
		return None
	
	def gatherFirstAnswerForQuestionID(self, id):
		if self.answers.has_key(id):
			answers = self.answers[id]
			if len(answers):
				return answers[0]
		return None
	
	def gatherScaleValuesForListOfIDs(self, ids, convertToInt=False):
		result = []
		for id in ids:
			if self.answers.has_key(id):
				if self.answers[id][0] and self.answers[id][0] != DOES_NOT_APPLY:
					if convertToInt:
						result.append(int(self.answers[id][0]))
					else:
						result.append(self.answers[id][0])
		if len(result) == len(ids):
			return result
		else:
			return None
		
	def gatherScaleValue(self, id):
		if self.answers.has_key(id):
			if self.answers[id][0] and self.answers[id][0] != DOES_NOT_APPLY:
				return self.answers[id][0]
		return None
		
	def getStabilityValue(self, questions):
		stabilityQuestion = questionWithShortName(questions, STABILITY_QUESTION_NAME)
		if stabilityQuestion:
			if self.answers.has_key(stabilityQuestion.id):
				answer = self.answers[stabilityQuestion.id][0]
				if answer != DOES_NOT_APPLY:
					return int(answer)
		return None
		
# -----------------------------------------------------------------------------------------------------------------
# utility methods for gathering subsets of data
# -----------------------------------------------------------------------------------------------------------------

def questionWithShortName(questions, shortName):
	result = []
	for question in questions:
		if question.shortName == shortName:
			return question
	return None

def questionWithVeryShortName(questions, shortName):
	result = []
	for question in questions:
		if question.veryShortName() == shortName:
			return question
	return None

def questionForID(questions, id):
	result = []
	for question in questions:
		if question.id == id:
			return question
	return None
			
def gatherScaleQuestions(questions, includeStability=True, includeNonGraphed=False):
	result = []
	for question in questions:
		if question.type == TYPE_SLIDER or (includeNonGraphed and question.type == TYPE_SLIDER_DO_NOT_GRAPH):
			if includeStability or question.shortName != STABILITY_QUESTION_NAME:
				result.append(question)
	return result

def gather3DScaleQuestions(questions):
	result = []
	for question in questions:
		if question.type == TYPE_TERNARY:
			result.append(question)
	return result

def gatherScaleQuestionShortNames(questions):
	result = []
	for question in questions:
		if question.type == TYPE_SLIDER:
			result.append(question.shortName)
	return result

def gatherScaleQuestionVeryShortNames(questions):
	result = []
	for question in questions:
		if question.type == TYPE_SLIDER:
			result.append(question.veryShortName())
	return result

def gatherChoiceQuestions(questions):
	result = []
	for question in questions:
		if question.isChoiceQuestion():
			result.append(question)
	return result

def gatherChoiceQuestionShortNames(questions):
	result = []
	for question in questions:
		if question.isChoiceQuestion():
			result.append(question.shortName)
	return result

def gatherChoiceQuestionAnswers(questions):
	result = []
	for question in questions:
		if question.isChoiceQuestion():
			for answer in question.shortResponseNames:
				if answer:
					result.append((question, answer))
	return result

def gatherRespondentIDs(respondents):
	result = []
	for respondent in respondents:
		result.append(respondent.id)
	return result

def gatherScaleValuesByRespondent(questions, respondents, slice=ALL_DATA_SLICE):
	result = []
	for respondent in respondents:
		values = respondent.gatherScaleValues(questions, slice=slice)
		if values:
			result.append(values)
	return result

def gatherNamedScaleQuestions(questions, names):
	result = []
	for question in questions:
		if question.isScale() and question.veryShortName() in names:
			result.append(question)
	return result

def gatherStoriesWithTitle(stories, title):
	result = []
	for story in stories:
		if story.title == title:
			result.append(story)
	return result

def gatherSelection(questions, stories, selection):
	# Fairness, Ambition(...): 0-10,90-100(...): Emotional tone+Feel about(...): positive+happy(...)
	selectionParts = selection.split(":")
	scaleNames = [x.strip() for x in selectionParts[0].strip().split(",")]
	rangeStrings = [x.strip() for x in selectionParts[1].strip().split(",")]
	
	ranges = [] 
	for rangeString in rangeStrings:
		ranges.append([int(x) for x in rangeString.split("-")])
	if len(selectionParts) > 2:
		questionNamesString = selectionParts[2].strip()
		questionNames = questionNamesString.split("+")
		answersString = selectionParts[3].strip()
		answers = answersString.split("+")
	else:
		questionNames = None
		answers = None
		
	result = None
	scaleQuestions = gatherScaleQuestions(questions, includeNonGraphed=True)
	choiceQuestions = gatherChoiceQuestions(questions)
	scaleIDsToConsider = []
	scaleNamesToReport = []
	questionNamesToReport = []
	answersToReport = []
	includedStories = []
	includedStoriesReducedByQuestions = []

	allRangesOkay = True
	for i in range(len(ranges)):
		if len(ranges[i]) < 2: # this is if I forgot to type the "-" in a range
			allRangesOkay = False
	
	if allRangesOkay:
	
		for scaleQuestion in scaleQuestions:
			for name in scaleNames:
				if scaleQuestion.veryShortName().lower() == name.lower():
					scaleIDsToConsider.append(scaleQuestion.id)
					scaleNamesToReport.append(scaleQuestion.veryShortName())
					
		for story in stories:
			values = story.gatherScaleValuesForListOfIDs(scaleIDsToConsider)
			if values and len(values) == len(scaleIDsToConsider):
				matches = 0
				for i in range(len(ranges)):
					if len(values) > i:
						value = int(values[i])
						if value and value != DOES_NOT_APPLY and value >= ranges[i][0] and value <= ranges[i][1]:
							matches += 1
				if matches == len(ranges):
					includedStories.append(story)
					
		if questionNames and answers:
			questionsToConsider = []
			answersToConsider = []
			for i in range(len(questionNames)):
				for question in choiceQuestions:
					if question.shortName.lower() == questionNames[i].lower(): 
						questionsToConsider.append(question)
						answersToConsider.append(answers[i])
						questionNamesToReport.append(question.shortName)
						answersToReport.append(answers[i])
						break
			for story in includedStories:
				matches = 0
				# only does AND search on answers
				# could put in OR search sometime with special indicator?
				for i in range(len(questionsToConsider)):
					if story.hasAnswerForQuestionID(answersToConsider[i], questionsToConsider[i].id, includePartialMatches=False):
						matches += 1
				if matches == len(questionsToConsider):
					includedStoriesReducedByQuestions.append(story)
		else:
			includedStoriesReducedByQuestions.extend(includedStories)
			
	return scaleNamesToReport, scaleIDsToConsider, rangeStrings, questionNamesToReport, answersToReport, includedStoriesReducedByQuestions

def gatherSelectionWithChoiceQuestionOnly(questions, stories, selection):
	# Emotional tone+Feel about(...): positive+happy(...)
	selectionParts = selection.split(":")
	questionNames = [x.strip() for x in selectionParts[0].strip().split("+")]
	answers = [x.strip() for x in selectionParts[1].strip().split("+")]
	result = None
	questionNamesToReport = []
	questionIDsToReport = []
	choiceQuestions = gatherChoiceQuestions(questions)
	includedStories = []
	if questionNames and answers:
		for story in stories:
			answersMatchingForThisStory = 0
			for i in range(len(questionNames)):
				questionToConsider = None
				questionName = questionNames[i]
				answer = answers[i]
				for question in choiceQuestions:
					if question.shortName == questionName:
						questionToConsider = question
						if not question.shortName in questionNamesToReport:
							questionNamesToReport.append(question.shortName)
						if not question.id in questionIDsToReport:
							questionIDsToReport.append(question.id)
						break
				if questionToConsider:
					if story.hasAnswerForQuestionID(answer, questionToConsider.id, includePartialMatches=False):
						answersMatchingForThisStory += 1
			if answersMatchingForThisStory >= len(answers):
				includedStories.append(story)
	return questionNamesToReport, questionIDsToReport, answers, includedStories

# not being used; checks for stories with missing archetypes, where archetypes are questions
def printNamesOfStoriesWithNoArchetypeData(stories, questions):
	storiesWithNoArchetypeAssignmentsAtAll = []
	questionNames = ["Archetype"]
	choiceQuestions = gatherChoiceQuestions(questions)
	storiesToDisplay = []
	if questionNames:
		for story in stories:
			matchesForThisStory = 0
			for questionName in questionNames:
				questionToConsider = None
				for question in choiceQuestions:
					if question.shortName == questionName:
						questionToConsider = question
						break
				if questionToConsider:
					if story.hasNoAnswerForQuestionID(questionToConsider.id):
						matchesForThisStory += 1
			if matchesForThisStory >= len(questionNames):
				storiesToDisplay.append(story)
	for story in storiesToDisplay:
		print story.title

def themeCountsForSelectedStories(stories, themeFileName):
	themesAndCounts = {}
	themesFile = open(themeFileName, "U")
	try:
		themes = csv.reader(themesFile)
		storyTitlesAndThemes = {}
		for row in themes:
			storyTitle = row[0].strip()
			if storyTitle:
				themesForThisStory = []
				firstTheme = row[1].strip()
				if firstTheme:
					themesForThisStory.append(firstTheme)
				secondTheme = row[2].strip()
				if secondTheme:
					themesForThisStory.append(secondTheme)
				thirdTheme = row[3].strip()
				if thirdTheme:
					themesForThisStory.append(thirdTheme)
				storyTitlesAndThemes[storyTitle] = themesForThisStory
			
		for story in stories:
			match = False
			for storyTitle in storyTitlesAndThemes:
				naSearchTerm = row[1].strip()
				match = (storyTitle.strip() == story.title.strip())# or (story.text.find(naSearchTerm) >= 0)
				if match:
					themesForThisStory = storyTitlesAndThemes[storyTitle]
					for themeName in themesForThisStory:
						if not themesAndCounts.has_key(themeName):
							themesAndCounts[themeName] = 0
						themesAndCounts[themeName] += 1
					break
			if not match:
				print 'themes: no match for story title', story.title
	finally:
		themesFile.close()
	themesAndCountsSorted = []
	for theme in themesAndCounts:
		themesAndCountsSorted.append((theme, themesAndCounts[theme]))
	themesAndCountsSorted.sort(lambda a,b: cmp(b[1], a[1]))
	return themesAndCountsSorted 

def findStoriesWithText(stories, text):
	result = []
	for story in stories:
		if story.title.lower().find(text.lower()) >= 0 or story.text.lower().find(text.lower()) >= 0:
			result.append(story)
	return result

# -----------------------------------------------------------------------------------------------------------------
# reading data
# -----------------------------------------------------------------------------------------------------------------

def readDataFromCSVFiles(dataFileName, labelsFileName):
	print 'reading data from CSV files ...'
	
	columnDefinitions = []
	questions = []
	respondents = []
	stories = []
	
	dataFile = open(dataFileName, "U")
	labelsFile = open(labelsFileName, "U")
	
	try:
		labels = csv.reader(labelsFile)

		# first, read column definitions that say what each column means
		rowIndex = 0
		for row in labels:
			if rowIndex == 0: # skip header row
				rowIndex = 1
				continue
			if row[0] and row[0][0] == ";": # skip any lines with commenting semicolon first
				continue
			if len(row) > 2:
				colDef = ColumnDefinition(row, rowIndex)
				#print colDef.id, colDef.codes, colDef.shortResponseNames
				columnDefinitions.append(colDef)
			rowIndex += 1
				
		# next, build question list from column definitions
		for colDef in columnDefinitions:
			makeNewQuestion = False
			if colDef.type in DATA_TYPES_WITH_MULTIPLE_COLUMNS_PER_QUESTION: 
				foundQuestion = None
				for aQuestion in questions:
					if aQuestion.id == colDef.id:
						foundQuestion = aQuestion
				if foundQuestion:
					foundQuestion.addColumnToAnswers(colDef.codes, colDef.longResponseNames, colDef.shortResponseNames)
				else:
					makeNewQuestion = True
			else:
				makeNewQuestion = True
			makeNewQuestion = makeNewQuestion and not colDef.id in [RESPONDENT_ID_FIELD, STORY_TEXT_FIELD, STORY_TITLE_FIELD]
			if makeNewQuestion:
				question = Question(colDef.id, colDef.refersTo, colDef.longName, colDef.shortName, colDef.type, 
								colDef.codes, colDef.longResponseNames, colDef.shortResponseNames, colDef.storyNumber)
				questions.append(question)
				
		#for colDef in columnDefinitions:
		#	print colDef.id, colDef.codes, colDef.shortResponseNames
		
		#for question in questions:
		#	print question.id, '|', question.shortName, '|', question.type,'|', question.shortResponseNames
				
		# now remove questions marked "discard" and duplicate questions
		questionsToKeep = []
		for question in questions:
			if question.refersTo != "discard" :
				if  question.refersTo == "participant":
					questionsToKeep.append(question)
				else:
					if HAS_SEPARATE_QUESTIONS_FOR_SEPARATE_STORIES:
						if question.id.find(STORY_NUMBER_SUFFIX) >= 0:
							question.id = stringUpTo(question.id, STORY_NUMBER_SUFFIX)
							questionsToKeep.append(question)
					else:
						questionsToKeep.append(question)
		questions = []
		questions.extend(questionsToKeep)
		
		#for question in questions:
		#	print question.id, '|', question.type,'|', question.codes, '|', question.shortResponseNames
		
		# finally, read data, using column definitions to connect stories to questions
		
		if True:
		
			data = csv.reader(dataFile)
			rowIndex = 0
			for row in data:
				if rowIndex < LINES_TO_SKIP_AT_START_OF_DATA_FILE: # skip header row
					pass
				else:
					respondent = Respondent(row, rowIndex, columnDefinitions)
					if respondent.stories:
						respondents.append(respondent)
				rowIndex += 1
						
			if RESPONDENTS_COVER_MULTIPLE_ROWS_IN_DATA_FILE:
				respondentsPerPassword = {}
				for respondent in respondents:
					if not respondentsPerPassword.has_key(respondent.id):
						respondentsPerPassword[respondent.id] = []
					respondentsPerPassword[respondent.id].append(respondent)
				#for key in respondentsPerPassword:
				#	print key, len(respondentsPerPassword[key])
				# transfer stories to first in each list
				respondentsToDelete = []
				for key in respondentsPerPassword:
					respondentsWithThisPassword = respondentsPerPassword[key]
					if len(respondentsWithThisPassword) > 1:
						respondentToHoldStories = respondentsWithThisPassword[0]
						for respondentToGetStoriesFrom in respondentsWithThisPassword[1:]:
							respondentToHoldStories.acceptStoriesFrom(respondentToGetStoriesFrom)
							respondentsToDelete.append(respondentToGetStoriesFrom)
				# remove extra respondents
				for respondentToDelete in respondentsToDelete:
					respondents.remove(respondentToDelete)
					
			for respondent in respondents:
				respondent.removeEmptyStories()
				
			for respondent in respondents:
				stories.extend(respondent.stories)
			
			# finally, add question for story number, so it will come out in graphs
			if INCLUDE_QUESTION_NUMBER_QUESTION and not QUESTION_NUMBER_APPEARS_AS_QUESTION:
				questions.append(Question(QUESTION_NUMBER_ID, 'story', QUESTION_NUMBER_ID, QUESTION_NUMBER_ID, TYPE_SINGLE_CHOICE, 
										['1', '2', '3', '4', '5', '6', '7'], QUESTION_NUMBER_NAMES, QUESTION_NUMBER_NAMES, 
										True, 0)) 
				
	finally:
		dataFile.close()
		labelsFile.close()
	
	print '  done reading data from CSV files: %s stories, %s respondents, %s questions.' % (len(stories), len(respondents), len(questions))
	return questions, respondents, stories

def printDataToCheckItWasReadRight(questions, stories, respondents):
	i = 0
	for story in stories:
		print '---------------------------------------------------------'
		print "Title: ", story.title
		print story.text[:100] # not the whole thing!
		if i <= 1000: # to check just first few 
			for key in story.answers:
				print '	', key, story.answers[key]
		i += 1
	print '---------------------------------------------------------'
	print '---------------------------------------------------------'
	for question in questions:
		print question.refersTo, "|", question.id, "|", question.shortName, "|", question.type
	print '---------------------------------------------------------'
	print '---------------------------------------------------------'
	for respondent in respondents:
		print respondent.id, len(respondent.stories)
	print '%s stories, %s respondents, %s questions' % (len(stories), len(respondents), len(questions))
	
def printResultForSpecificQuestionID(questions, stories, questionID):
	numAnswers = 0
	for story in stories:
		answers = story.gatherAnswersForQuestionID(questionID)
		print story.title, answers
		if answers:
			numAnswers += len(answers)
	print '%s stories, %s answers to %s' % (len(stories), numAnswers, questionID)
	
def readData(pickleFileName, dataFileName, labelsFileName, forceReread=False):
	if os.path.exists(pickleFileName) and not forceReread:
		print 'reading data from pickle file ...'
		pickleFile = open(pickleFileName, 'rb')
		allData = pickle.load(pickleFile)
		questions = allData[0]
		respondents = allData[1]
		stories = allData[2]
		print '   done reading data from pickle file: %s stories, %s respondents, %s questions.' % (len(stories), len(respondents), len(questions))
	else:
		questions, respondents, stories = readDataFromCSVFiles(dataFileName, labelsFileName)
		print 'writing pickle file ...'
		allData = []
		allData.append(questions)
		allData.append(respondents)
		allData.append(stories)
		outputFile = open(DATA_PATH + PICKLE_FILE_NAME, 'wb')
		pickle.dump(allData, outputFile, 01)
		print '  done writing pickle file.'
	return questions, respondents, stories

# -----------------------------------------------------------------------------------------------------------------
# writing data for use in spreadsheet
# -----------------------------------------------------------------------------------------------------------------

def writeSimplifiedDataToCSV(questions, stories):
	print 'writing data to CSV file ...'
	outputFileName = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep) + "Simplified data.csv"
	outputFile = open(outputFileName, 'w')
	try:
		
		# header
		cols = []
		cols.append("Respondent")
		cols.append("Number")
		cols.append("Title")
		cols.append("Text")
		for question in questions:
			if question.type in  CSV_WRITE_AS_MULTIPLE_COLUMNS:
				if question.type == TYPE_TERNARY:
					cols.append("%s: x" % question.shortName)
					cols.append("%s: y" % question.shortName)
					cols.append("%s: z" % question.shortName)
				else:
					# make a copy of the answer names to remove duplicates created by lumping answers together in format file
					possibleAnswers = []
					possibleAnswers.extend(question.shortResponseNames)
					possibleAnswers = removeDuplicates(possibleAnswers)
					for answer in possibleAnswers:
						cols.append("%s: %s" % (question.shortName, answer))
			else:
				cols.append(question.shortName)
		outputFile.write(",".join(cols))
		outputFile.write("\n")
		
		for story in stories:
			cols = []
			cols.append(story.respondentPassword)
			cols.append("%s" % (story.number + 1))
			cols.append('"%s"' % story.title.replace('"', "'")) # quotes INSIDE the title mess things up
			cols.append('"%s"' % story.text.replace('"', "'")) # quotes INSIDE the text mess things up
			for question in questions:
				if question.type in CSV_WRITE_AS_SINGLE_COLUMNS:
					answers = story.gatherAnswersForQuestionID(question.id)
					if answers:
						if question.type == TYPE_MULTIPLE_CHOICE_DELIMITED:
							answers = removeDuplicates(answers)
							answersCombined = CSV_WRITE_MULTI_VALUE_IN_ONE_COL_DELIMITER.join(answers)
							cols.append('"%s"' % answersCombined)
						elif question.type == TYPE_TERNARY:
							convertedAnswer = answers[0].replace(TERNARY_VALUE_DELIMITER, CSV_WRITE_MULTI_VALUE_IN_ONE_COL_DELIMITER)
							cols.append('"%s"' % convertedAnswer)
						else:
							cols.append('"%s"' % answers[0])
					else:
						cols.append("")
				elif question.type in CSV_WRITE_AS_MULTIPLE_COLUMNS:
					if question.type == TYPE_TERNARY:
						answers = story.gatherAnswersForQuestionID(question.id)
						pieces = answers.split(TERNARY_VALUE_DELIMITER)
						if pieces:
							for piece in pieces:
								cols.append('"%s"' % piece)
						else:
							cols.append("")
							cols.append("")
							cols.append("")
					else:
						# make a copy of the answer names to remove duplicates created by lumping answers together in format file
						possibleAnswers = []
						possibleAnswers.extend(question.shortResponseNames)
						possibleAnswers = removeDuplicates(possibleAnswers)
						for answer in possibleAnswers:
							if story.hasAnswerForQuestionID(answer, question.id):
								cols.append('"%s"' % answer)
							else:
								cols.append("")
							
			colString = ",".join(cols)
			outputFile.write(colString)
			outputFile.write("\n")
	finally:
		outputFile.close()
	print '  done writing data to CSV file.'

def writeStoriesToTextFile(questions, stories):
	print 'writing stories to TXT file ...'
	outputFileName = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep) + "Stories.txt"
	text = ''
	for story in stories:
		text += story.allDetailsForDisplay(questions)
		text += '\n\n'
	outputFile = open(outputFileName, 'w')
	try:
		outputFile.write(text)
	finally:
		outputFile.close()
	print '  done writing stories to TXT file.'
		
def writeOtherResponsesToQuestions(questions, stories):
	print 'writing other answers to TXT file ...'
	outputFileName = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep) + "Other responses.txt"
	text = ''
	for question in questions:
		if question.type == TYPE_REGULAR_TEXT_BOX:
			text += '%s\n\n' % question.shortName
			allAnswers = []
			for story in stories:
				answers = story.gatherAnswersForQuestionID(question.id)
				if answers:
					allAnswers.append(answers[0])
			uniqueAnswers = {}
			for answer in allAnswers:
				if not uniqueAnswers.has_key(answer):
					uniqueAnswers[answer] = 1
				else:
					uniqueAnswers[answer] += 1
			for answer in uniqueAnswers:
				text += "%s - %s\n" % (answer, uniqueAnswers[answer])
			text += '\n\n'
	outputFile = open(outputFileName, 'w')
	try:
		outputFile.write(text)
	finally:
		outputFile.close()
	print '  done writing other answers to TXT file.'
	
# counts how many stories people told, depending on which answers they gave to questions about themselves
# if people varied in this it might mean something
def writeInfoAboutPeopleAndNumberOfStoriesTold(questions, stories, respondents):
	print 'writing number of stories told to CSV file ...'
	outputFileName = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep) + "Number of stories per respondent.csv"
	answerStoryCounts = {}
	for respondent in respondents:
		for question in questions:
			if question.refersTo == "participant":
				if not answerStoryCounts.has_key(question.shortName):
					answerStoryCounts[question.shortName] = {}
				thisDict = answerStoryCounts[question.shortName]
				answers = respondent.stories[0].gatherAnswersForQuestionID(question.id)
				thisDict[NO_ANSWER] = []
				if answers:
					for answer in answers:
						if not thisDict.has_key(answer):
							thisDict[answer] = []
						thisDict[answer].append(len(respondent.stories))
				else:
					thisDict[NO_ANSWER].append(len(respondent.stories))
				if answers:
					for answer in answers:
						if thisDict.has_key(answer):
							thisDict[answer].sort()
				thisDict[NO_ANSWER].sort()
	
	outputFile = open(outputFileName, 'w')
	try:
		outputFile.write("Question,Answer,Mean num stories, Num stories (one cell per respondent lowest to highest)\n")
		for question in questions:
			if question.refersTo == "participant" and question.shortName.find("other") < 0:
				if answerStoryCounts.has_key(question.shortName):
					questionDict = answerStoryCounts[question.shortName]
					for answer in question.shortResponseNames:
						if questionDict.has_key(answer):
							outputFile.write("%s,%s," % (question.shortName, answer))
							if len(questionDict[answer]) == 0:
								mean = 0
							elif len(questionDict[answer]) == 1:
								mean = questionDict[answer][0]
							else:
								total = 0
								for value in questionDict[answer]:
									total += value
								mean = 1.0 * total / len(questionDict[answer])
							outputFile.write("%f," % mean)
							for value in questionDict[answer]:
								outputFile.write("%s," % value)
							outputFile.write("\n")
					answer = NO_ANSWER
					outputFile.write("%s,%s," % (question.shortName, answer))
					if len(questionDict[answer]) == 0:
						mean = 0
					elif len(questionDict[answer]) == 1:
						mean = questionDict[answer][0]
					else:
						total = 0
						for value in questionDict[answer]:
							total += value
						mean = 1.0 * total / len(questionDict[answer])
					outputFile.write("%f," % mean)
					for value in questionDict[answer]:
						outputFile.write("%s," % value)
					outputFile.write("\n")
	finally:
		outputFile.close()
	print '  done writing information about number of stories told to CSV file.'
	return answerStoryCounts
				
