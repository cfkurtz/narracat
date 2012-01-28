# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Methods that graph ternary data
# -----------------------------------------------------------------------------------------------------------------

from narracat_constants import *
from narracat_stats import *
from narracat_data import *

import colorsys

from narracat_graph import *

# -----------------------------------------------------------------------------------------------------------------
# graphing methods that write one PNG file
# -----------------------------------------------------------------------------------------------------------------

def graphPNGTernaryPlot(xValues, yValues, zValues, sizes, xAxisName, yAxisName, zAxisName, graphName, pngFileName, pngFilePath, drawStats=True):
	plotXValues = []
	plotYValues = []
	totalX = 0
	totalY = 0
	totalZ = 0
	
	#print graphName
	#print "%s\t%s\t%s" % (xAxisName, yAxisName, zAxisName)
	for i in range(len(xValues)):
		x = xValues[i]
		y = yValues[i]
		z = zValues[i]
		totalX += x
		totalY += y
		totalZ += z
		#print "%s\t%s\t%s" % (x, y, z)
		plotX, plotY = xyTransformForTernaryPlot(x, y, z)
		plotXValues.append(plotX)
		plotYValues.append(plotY)
		
	meanX = totalX / len(xValues)
	meanY = totalY / len(yValues)
	meanZ = totalZ / len(zValues)
	plotMeanX, plotMeanY = xyTransformForTernaryPlot(meanX, meanY, meanZ)
	stdX = np.std(np.array(xValues))
	stdY = np.std(np.array(yValues))
	stdZ = np.std(np.array(zValues))
	meanPlusStdX = min(1, meanX + stdX)
	meanPlusStdY = min(1, meanY + stdY)
	meanPlusStdZ = min(1, meanZ + stdZ)
	meanMinusStdX = max(0, meanX - stdX)
	meanMinusStdY = max(0, meanY - stdY)
	meanMinusStdZ = max(0, meanZ - stdZ)
	plotMeanPlusStdX, plotMeanPlusStdY = xyTransformForTernaryPlot(meanPlusStdX, meanPlusStdY, meanPlusStdZ)
	plotMeanMinusStdX, plotMeanMinusStdY = xyTransformForTernaryPlot(meanMinusStdX, meanMinusStdY, meanMinusStdZ)
	
	npArrayX = np.array(plotXValues)
	npArrayY = np.array(plotYValues)
	
	if len(xValues) > 100 or sizes:
		alpha = 0.5
	else:
		alpha = 1.0
		
	if sizes:
		numNonZeroSizes = 0
		for size in sizes:
			if size > 0:
				numNonZeroSizes += 1
		numValues = numNonZeroSizes
	else:
		numValues = len(xValues)

	plt.clf()
	figure = plt.figure(figsize=(6,6.5))

	axes = figure.add_subplot(111)
	roomNeeded = 0.2
	plt.subplots_adjust(left=roomNeeded)
	plt.subplots_adjust(right=1-roomNeeded)
	plt.subplots_adjust(top=1-roomNeeded)
	plt.subplots_adjust(bottom=roomNeeded)

	# hide normal axes 
	axes.set_frame_on(False)
	axes.get_xaxis().set_visible(False)
	axes.get_yaxis().set_visible(False)
	
	# draw inner lines at 20, 24, 60, 80% for X, Y and Z
	# X dimension
	plt.plot([0.2,0.60], [0, 0.693], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.4,0.70], [0, 0.520], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.6,0.80], [0, 0.346], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.8,0.90], [0, 0.173], linewidth=1, c='#E5E5E5', zorder=1)
	# Y dimension
	plt.plot([0.1,0.2], [0.173,0], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.2,0.4], [0.346,0], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.3,0.6], [0.520,0], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.4,0.8], [0.693,0], linewidth=1, c='#E5E5E5', zorder=1)
	# Z dimension
	plt.plot([0.90,0.10], [0.173,0.173], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.80,0.20], [0.346,0.346], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.70,0.30], [0.520,0.520], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.60,0.40], [0.693,0.693], linewidth=1, c='#E5E5E5', zorder=1)

	# draw outer boundaries
	plt.plot([0, 0.5], [0, 0.866], linewidth=1, c='#000000', zorder=2)
	plt.plot([1, 0.5], [0, 0.866], linewidth=1, c='#000000', zorder=2)
	plt.plot([1, 0], [0, 0], linewidth=1, c='#000000', zorder=2)
	
	# draw points
	if sizes:
		plt.scatter(npArrayX, npArrayY, c='#3333FF', marker='o', linewidth=0, s=sizes, zorder=10, alpha=alpha)
	else:
		plt.scatter(npArrayX, npArrayY, c='#3333FF', marker='o', linewidth=0, s=10, zorder=10, alpha=alpha)
	
	if drawStats:
	# draw mean, std
		plt.scatter(plotMeanX, plotMeanY, marker='o', c='#FF0000', linewidth=0, s=50, zorder=40)
		plt.scatter(plotMeanPlusStdX, plotMeanPlusStdY, marker='o', c='#FF0000', linewidth=0, s=20, zorder=20)
		plt.scatter(plotMeanMinusStdX, plotMeanMinusStdY, marker='o', c='#FF0000',linewidth=0, s=20, zorder=20)
		plt.plot([plotMeanX, plotMeanPlusStdX], [plotMeanY, plotMeanPlusStdY], linewidth=1.5, c='#FF0000', zorder=20)
		plt.plot([plotMeanX, plotMeanMinusStdX], [plotMeanY, plotMeanMinusStdY], linewidth=1.5, c='#FF0000', zorder=20)

	# label corners
	plt.text(0.5, 1, graphName, horizontalalignment='center', fontsize=12)
	plt.text(0.5, 0.9, xAxisName, horizontalalignment='center', fontsize=9)
	plt.text(-0.05, 0, yAxisName, horizontalalignment='right', fontsize=9)
	plt.text(1.05, 0, zAxisName, horizontalalignment='left', fontsize=9)
	
	plt.text(0.5, 0.25, 'n=%s' % numValues, horizontalalignment='center', transform=figure.transFigure)

	# standardize sizes - must do this AFTER everything is graphed
	axes.set_xlim((-0.2, 1.2))
	axes.set_ylim((-0.2, 1.2))
	
	# save to file
	plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)
	plt.close(figure)
		
def graphPNGTernaryPlotDifferences(xValues, yValues, zValues, xAxisName, yAxisName, zAxisName, graphName, pngFileName, pngFilePath, graph=True):
	plotX1Values = []
	plotY1Values = []
	plotX2Values = []
	plotY2Values = []
	
	#print graphName
	#print "%s\t%s\t%s" % (xAxisName, yAxisName, zAxisName)
	for i in range(len(xValues)):
		x = xValues[i]
		y = yValues[i]
		z = zValues[i]
		#print "%s\t%s\t%s" % (x, y, z)
		plotX, plotY = xyTransformForTernaryPlot(x, y, z)
		if i % 2 == 0:
			plotX1Values.append(plotX)
			plotY1Values.append(plotY)
		else:
			plotX2Values.append(plotX)
			plotY2Values.append(plotY)
		
	npArrayX1 = np.array(plotX1Values)
	npArrayY1 = np.array(plotY1Values)
	npArrayX2 = np.array(plotX2Values)
	npArrayY2 = np.array(plotY2Values)
	
	if len(xValues) < LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS:
		return 

	plt.clf()
	figure = plt.figure(figsize=(8,8))

	axes = figure.add_subplot(111)
	roomNeeded = 0.2
	plt.subplots_adjust(left=roomNeeded)
	plt.subplots_adjust(right=1-roomNeeded)
	plt.subplots_adjust(top=1-roomNeeded)
	plt.subplots_adjust(bottom=roomNeeded)

	# hide normal axes 
	axes.set_frame_on(False)
	axes.get_xaxis().set_visible(False)
	axes.get_yaxis().set_visible(False)
	
	# draw inner lines at 20, 24, 60, 80% for X, Y and Z
	# X dimension
	plt.plot([0.2,0.60], [0, 0.693], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.4,0.70], [0, 0.520], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.6,0.80], [0, 0.346], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.8,0.90], [0, 0.173], linewidth=1, c='#E5E5E5', zorder=1)
	# Y dimension
	plt.plot([0.1,0.2], [0.173,0], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.2,0.4], [0.346,0], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.3,0.6], [0.520,0], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.4,0.8], [0.693,0], linewidth=1, c='#E5E5E5', zorder=1)
	# Z dimension
	plt.plot([0.90,0.10], [0.173,0.173], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.80,0.20], [0.346,0.346], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.70,0.30], [0.520,0.520], linewidth=1, c='#E5E5E5', zorder=1)
	plt.plot([0.60,0.40], [0.693,0.693], linewidth=1, c='#E5E5E5', zorder=1)

	# draw outer boundaries
	plt.plot([0, 0.5], [0, 0.866], linewidth=1, c='#000000', zorder=2)
	plt.plot([1, 0.5], [0, 0.866], linewidth=1, c='#000000', zorder=2)
	plt.plot([1, 0], [0, 0], linewidth=1, c='#000000', zorder=2)
	
	# draw lines with circles at ends
	plt.plot([plotX1Values, plotX2Values], [plotY1Values, plotY2Values], linewidth=0.4, alpha=0.3, c='b', zorder=10)
	plt.scatter(plotX2Values, plotY2Values, marker='o', c='b', s=5, linewidth=0, zorder=20, alpha=0.3)

	# label corners
	plt.text(0.5, 1.1, graphName, horizontalalignment='center', fontsize=12)
	plt.text(0.5, 0.9, xAxisName, horizontalalignment='center', fontsize=9)
	plt.text(-0.05, 0, yAxisName, horizontalalignment='right', fontsize=9)
	plt.text(1.05, 0, zAxisName, horizontalalignment='left', fontsize=9)
	
	note = 'n=%s' % (len(xValues) // 2)
	plt.text(0.5, 0.25, note, horizontalalignment='center', fontsize=10, transform=figure.transFigure)

	# standardize sizes - must do this AFTER everything is graphed
	axes.set_xlim((-0.2, 1.2))
	axes.set_ylim((-0.2, 1.2))
	
	# save to file
	plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200, bbox_inches='tight', pad_inches=1.0)
	plt.close(figure)
		
def xyTransformForTernaryPlot(x, y, z):
	# from http://staff.aist.go.jp/a.noda/programs/ternary/ternary-en.html
	# and http://www.agu.org/pubs/eos-news/supplements/1995-2003/000562e.shtml
	plotX = 0.5 * (x + 2.0 * z) / (1.0 * x + y + z)
	plotY = (np.sqrt(3.0) / 2.0) * x / (1.0 * x + y + z)
	return (plotX, plotY)

# -----------------------------------------------------------------------------------------------------------------
# data integrity checks
# -----------------------------------------------------------------------------------------------------------------

def graphOneGiantTernaryPlotOfAllTernarySetValues(questions, stories):
	if not DATA_HAS_TERNARY_SETS:
		return
	print 'writing giant all ternarySets ternary plot...'
	ternaryQuestions = gather3DScaleQuestions(questions)
	allArray = []
	for question in ternaryQuestions:
		numbersArray = question.gatherTernaryValuesFromStories(stories)
		if numbersArray:
			allArray.extend(numbersArray)
	overallPath = OUTPUT_PATH + "overall" + os.sep
	if not os.path.exists(overallPath):
		os.mkdir(overallPath)
	xArray = []
	yArray = []
	zArray = []
	for x,y,z in allArray:
		xArray.append(x)
		yArray.append(y)
		zArray.append(z)
	name = "All ternarySet values"
	graphPNGTernaryPlot(xArray, yArray, zArray, None, 'x', 'y', 'z', name, name, overallPath)
	print '  done writing giant all ternarySets ternary plot.'
	
def graphTernaryPlotValuesPerParticipant(questions, stories, participants):
	if not DATA_HAS_TERNARY_SETS:
		return
	print 'writing participant ternarySets ternary plots...'
	participantPath = OUTPUT_PATH + "ternarySet values by participant" + os.sep
	if not os.path.exists(participantPath):
		os.mkdir(participantPath)
	graphsWritten = 0
	for participant in participants:
		values = participant.gatherTernaryValues(questions)
		xArray = []
		yArray = []
		zArray = []
		for x,y,z in values:
			xArray.append(x)
			yArray.append(y)
			zArray.append(z)
		name = "All ternarySet values - %.0f" % float(participant.id)
		graphPNGTernaryPlot(xArray, yArray, zArray, None, 'x', 'y', 'z', name, name, participantPath, drawStats=False)
		graphsWritten += 1
		print '  ... %s graphs written' % graphsWritten
	print '  done writing participant ternarySets ternary plots.'
	
def calculateThirdValueStrengthForTernaryAnswers(questions, stories):
	closeThreshold = 10
	farThreshold = 40
	numThirdIgnoresTotal = 0
	numTernarySetsTotal = 0
	ternaryQuestions = gather3DScaleQuestions(questions)
	for ternaryQuestion in ternaryQuestions:
		ternaryValues = ternaryQuestion.gatherTernaryValuesFromStories(stories)
		numThirdIgnoresForThisQuestion = 0
		numTernarySetsThisQuestion = 0
		for x, y, z in ternaryValues:
			numCloseTogether = 0
			numFarApart = 0
			if abs(x-y) < closeThreshold:
				numCloseTogether += 1
			if abs(x-z) < closeThreshold:
				numCloseTogether += 1
			if abs(y-z) < closeThreshold:
				numCloseTogether += 1
				
			if abs(x-y) > farThreshold:
				numFarApart += 1
			if abs(x-z) > farThreshold:
				numFarApart += 1
			if abs(y-z) > farThreshold:
				numCloseTogether += 1
				numFarApart += 1
			
			if numCloseTogether == 1 and numFarApart == 2:
				numThirdIgnoresForThisQuestion += 1
				ignored = True
			else:
				ignored = False
			#print ignored, numCloseTogether, x, y, z
			numTernarySetsTotal += 1
			numTernarySetsThisQuestion += 1
		numThirdIgnoresTotal += numThirdIgnoresForThisQuestion
		print ternaryQuestion.veryShortName(), numThirdIgnoresForThisQuestion, '/', numTernarySetsThisQuestion, '(', round(100.0 * numThirdIgnoresForThisQuestion / numTernarySetsThisQuestion), '%)'
	if numTernarySetsTotal > 0:
		print numThirdIgnoresTotal, numTernarySetsTotal, '(', round(100.0 * numThirdIgnoresTotal / numTernarySetsTotal), '%)'
	else:
		print 'no ternarySets'

# -----------------------------------------------------------------------------------------------------------------
# one ternary plot at a time
# -----------------------------------------------------------------------------------------------------------------

def graphTernaryPlots(questions, stories, scaleID=None, extraName=None, separateDirectories=True, overwriteFiles=False, slice=ALL_DATA_SLICE):
	if not DATA_HAS_TERNARY_SETS:
		return
	print 'writing ternary plots ... ' 
	if extraName:
		print '   for %s' % extraName
	if slice == ALL_DATA_SLICE:
		extra = ""
		if scaleID:
			ternaryLandscapesPath = OUTPUT_PATH + "ternary plots by scale" + os.sep
		else:
			ternaryLandscapesPath = OUTPUT_PATH + "ternary plots" + os.sep
	else:
		extra = slice
		if scaleID:
			ternaryLandscapesPath = OUTPUT_PATH + "ternary plots by scale" + extra + os.sep
		else:
			ternaryLandscapesPath = OUTPUT_PATH + "ternary plots" + extra + os.sep
	if not os.path.exists(ternaryLandscapesPath):
		os.mkdir(ternaryLandscapesPath)
	ternaryQuestions = gather3DScaleQuestions(questions)
	scaleQuestion = None
	if scaleID:
		scaleQuestion = questionForID(questions, scaleID)
		if not scaleQuestion:
			print "SCALE QUESTION NOT FOUND: %s" % scaleID
			return
	graphsWritten = 0
	for question in ternaryQuestions:
		#print question.shortName, scaleQuestion.shortName
		xArray = []
		yArray = []
		zArray = []
		sizes = []
		for story in stories:
			if story.matchesSlice(slice):
				if not scaleQuestion or story.gatherScaleValue(scaleQuestion.id):
					xyzText = story.gatherAnswersForQuestionID(question.id)
					if xyzText and xyzText != NO_ANSWER and xyzText != DOES_NOT_APPLY:
						xyzTexts = xyzText[0].strip().split('"')
						if xyzTexts[0] != DOES_NOT_APPLY:
							xArray.append(int(xyzTexts[0]))
							yArray.append(int(xyzTexts[1]))
							zArray.append(int(xyzTexts[2]))
							size = 0
							if scaleQuestion:
								value = story.gatherScaleValue(scaleQuestion.id)
								if value != NO_ANSWER and value != DOES_NOT_APPLY:
									size = int(value)
							sizes.append(size)
					#print story.title, xyzTexts[0], '\t', xyzTexts[1], '\t', xyzTexts[2], '\t', size
		#print question.veryShortName(), scaleQuestion.veryShortName(), xArray, yArray, aArray, sizes
		if len(xArray):
			axisNames = question.shortName.split(" and ")
			xAxisName = axisNames[0].strip()
			xAxisNameAndGraphName = xAxisName.split(":")
			xAxisName = xAxisNameAndGraphName[1].strip()
			graphName = xAxisNameAndGraphName[0].strip()
			yAxisName = axisNames[1].strip()
			zAxisName = axisNames[2].strip()
			if scaleQuestion:
				if extra:
					combinedName = "%s x %s - %s" % (graphName, scaleQuestion.veryShortName(), extra)
				else:
					combinedName = "%s x %s" % (graphName, scaleQuestion.veryShortName())
			else:
				if extra:
					combinedName = "%s - %s" % (graphName, extra)
				else:
					combinedName = graphName
			# do this before adding extra
			if separateDirectories:
				comboPath = ternaryLandscapesPath + cleanTextForFileName(combinedName) + os.sep
				if not os.path.exists(comboPath):
					os.mkdir(comboPath)
			else:
				comboPath = ternaryLandscapesPath
			if extraName:
				combinedName = "%s - %s" % (combinedName, extraName)
			if overwriteFiles or not os.path.exists(comboPath + cleanTextForFileName(combinedName) + ".png"):
				graphPNGTernaryPlot(xArray, yArray, zArray, sizes, xAxisName, yAxisName, zAxisName, combinedName, combinedName, comboPath)
			graphsWritten += 1
			print '  ... %s graphs written' % graphsWritten
	print '  done writing ternary plots.'
	
def graphTernaryPlotsForQuestionAnswers(questions, stories, overwriteFiles=False):
	if not DATA_HAS_TERNARY_SETS:
		return
	print 'writing ternary plots by question answer ...'
	graphsWritten = 0
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	for choiceQuestion in questions:
		if choiceQuestion.isChoiceQuestion():
			answersToCheck = []
			answersToCheck.extend(choiceQuestion.shortResponseNames)
			answersToCheck.append(NO_ANSWER)
			answersToCheck = removeDuplicates(answersToCheck) # because of extra answers in survey
			for answer in answersToCheck:
				storiesWithThisAnswer = []
				for story in stories:
					if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
						storiesWithThisAnswer.append(story)
				if len(storiesWithThisAnswer) >= lowerLimitStoryNumber: 
					name = "%s: %s" % (choiceQuestion.shortName, answer)
					graphTernaryPlots(questions, storiesWithThisAnswer, extraName=name, overwriteFiles=overwriteFiles)
	print '  done writing ternary plots by question answer.'

# -----------------------------------------------------------------------------------------------------------------
# two ternary plots compared
# -----------------------------------------------------------------------------------------------------------------

def graphDifferencesBetweenTernaryPlots(questions, stories, extraName=None, separateDirectories=True, overwriteFiles=False, slice=ALL_DATA_SLICE):
	if not DATA_HAS_TERNARY_SETS:
		return
	print 'writing ternary plot differences ... ' 
	if extraName:
		print '   for %s' % extraName
	if slice == ALL_DATA_SLICE:
		extra = ""
		ternaryLandscapesPath = OUTPUT_PATH + "ternary plot differences" + os.sep
	else:
		extra = slice
		ternaryLandscapesPath = OUTPUT_PATH + "ternary plot differences" + extra + os.sep
	if not os.path.exists(ternaryLandscapesPath):
		os.mkdir(ternaryLandscapesPath)
	ternaryQuestions = gather3DScaleQuestions(questions)
	graphsWritten = 0
	for i in range(len(ternaryQuestions)):
		for j in range(len(ternaryQuestions)):
			if i < j:
				firstQuestion = ternaryQuestions[i]
				secondQuestion = ternaryQuestions[j]
				xArray = []
				yArray = []
				zArray = []
				for story in stories:
					if story.matchesSlice(slice):
						answer1 = story.gatherAnswersForQuestionID(firstQuestion.id)
						answer2 = story.gatherAnswersForQuestionID(secondQuestion.id)
						if answer1 and answer2 and answer1[0] != DOES_NOT_APPLY and answer2[0] != DOES_NOT_APPLY:
							xyzTexts1 = answer1[0].strip().split('"')
							xArray.append(int(xyzTexts1[0]))
							yArray.append(int(xyzTexts1[1]))
							zArray.append(int(xyzTexts1[2]))
							#print xyzTexts1[0], '\t', xyzTexts1[1], '\t', xyzTexts1[2]
							
							xyzTexts2 = answer2[0].strip().split('"')
							xArray.append(int(xyzTexts2[0]))
							yArray.append(int(xyzTexts2[1]))
							zArray.append(int(xyzTexts2[2]))
							#print xyzTexts2[0], '\t', xyzTexts2[1], '\t', xyzTexts2[2]
				#print firstQuestion.id, secondQuestion.id, len(xArray), len(yArray), len(zArray)
				if len(xArray) >= LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS:
					axisNames1 = firstQuestion.shortName.split(" and ")
					xAxisName1 = axisNames1[0].strip()
					xAxisNameAndGraphName1 = xAxisName1.split(":")
					xAxisName1 = xAxisNameAndGraphName1[1].strip()
					graphName1 = xAxisNameAndGraphName1[0].strip()
					yAxisName1 = axisNames1[1].strip()
					zAxisName1 = axisNames1[2].strip()
					
					axisNames2 = secondQuestion.shortName.split(" and ")
					xAxisName2 = axisNames2[0].strip()
					xAxisNameAndGraphName2 = xAxisName2.split(":")
					xAxisName2 = xAxisNameAndGraphName2[1].strip()
					graphName2 = xAxisNameAndGraphName2[0].strip()
					yAxisName2 = axisNames2[1].strip()
					zAxisName2 = axisNames2[2].strip()
					
					graphName = graphName1 + " x \n" + graphName2
					xAxisName = xAxisName1 + " to \n" + xAxisName2
					yAxisName = yAxisName1 + " to \n" + yAxisName2
					zAxisName = zAxisName1 + " to \n" + zAxisName2
					
					if extra:
						combinedName = "%s %s" % (graphName, extra)
					else:
						combinedName = graphName
					# do this before adding extra
					if separateDirectories:
						comboPath = ternaryLandscapesPath + cleanTextForFileName(combinedName) + os.sep
						if not os.path.exists(comboPath):
							os.mkdir(comboPath)
					else:
						comboPath = ternaryLandscapesPath
					if extraName:
						combinedName = "%s - %s" % (combinedName, extraName)
					if overwriteFiles or not os.path.exists(comboPath + cleanTextForFileName(combinedName) + ".png"):
						graphPNGTernaryPlotDifferences(xArray, yArray, zArray, xAxisName, yAxisName, zAxisName, combinedName, combinedName, comboPath)
					graphsWritten += 1
					print '  ... %s graphs written' % graphsWritten
	print '  done writing ternary plot differnces.'
	
def graphTernaryPlotDifferencesForQuestionAnswers(questions, stories, overwriteFiles=False):
	if not DATA_HAS_TERNARY_SETS:
		return
	print 'writing ternary plot differences by question answer ...'
	graphsWritten = 0
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	for choiceQuestion in questions:
		if choiceQuestion.isChoiceQuestion():
			answersToCheck = []
			answersToCheck.extend(choiceQuestion.shortResponseNames)
			answersToCheck.append(NO_ANSWER)
			answersToCheck = removeDuplicates(answersToCheck) # because of extra answers in survey
			for answer in answersToCheck:
				storiesWithThisAnswer = []
				for story in stories:
					if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
						storiesWithThisAnswer.append(story)
				if len(storiesWithThisAnswer) >= lowerLimitStoryNumber: 
					name = "%s: %s" % (choiceQuestion.shortName, answer)
					graphDifferencesBetweenTernaryPlots(questions, storiesWithThisAnswer, extraName=name, separateDirectories=True, overwriteFiles=overwriteFiles)
	print '  done writing ternary plot differences by question answer.'
	
# -----------------------------------------------------------------------------------------------------------------
# ternary plots against choice questions
# -----------------------------------------------------------------------------------------------------------------

def compareTernaryMeansForScaleValuesWithQuestionAnswers(questions, stories, overwriteFiles=False, slice=ALL_DATA_SLICE, byQuestion=False):
	if not DATA_HAS_TERNARY_SETS:
		return
	print 'comparing ternary means by question answer ...'
	questionsConsidered = 0
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	ternaryQuestions = gather3DScaleQuestions(questions)
	for ternaryQuestion in ternaryQuestions:
		print '  ... ternary %s' % ternaryQuestion.shortName
		for choiceQuestion in questions:
			if choiceQuestion.isChoiceQuestion():
				print '	  ... choice question %s' % choiceQuestion.shortName
				atLeastOneComparisonIsWorthShowing = False
				answerValuesForThisQuestion = {}
				answersToCheck = []
				answersToCheck.extend(choiceQuestion.shortResponseNames)
				answersToCheck.append(NO_ANSWER)
				answersToCheck = removeDuplicates(answersToCheck) # because of extra answers in survey
				for answer in answersToCheck:
					storiesWithThisAnswer = []
					for story in stories:
						if story.matchesSlice(slice):
							if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
								storiesWithThisAnswer.append(story)
					if len(storiesWithThisAnswer) >= lowerLimitStoryNumber:
						ternaryValues = ternaryQuestion.gatherTernaryValuesFromStories(storiesWithThisAnswer)
						if len(ternaryValues) > lowerLimitStoryNumber:
							answerValuesForThisQuestion[answer] = ternaryValues
				results = []
				i = 0
				j = 0
				sizes = []
				values = []
				colors = []
				for firstAnswer in answerValuesForThisQuestion:
					sizes.append([])
					values.append([])
					colors.append([])
					for secondAnswer in answerValuesForThisQuestion:
						if firstAnswer != secondAnswer:
							distance = ternaryDistanceForTwoChoiceQuestions(answerValuesForThisQuestion[firstAnswer], answerValuesForThisQuestion[secondAnswer])
							size, color = sizeAndColorForTernaryDistance(distance)
							value = distance
						else:
							size = 0
							color = "#000000"
							value = 0
						sizes[i].append(size)
						values[i].append(value)
						colors[i].append(color)
						if size > 0:
							atLeastOneComparisonIsWorthShowing = True
						j += 1
					i += 1
				if atLeastOneComparisonIsWorthShowing:
					# set labels with scale names
					labels = answerValuesForThisQuestion.keys()
					# set path to save file in
					distanceTestsStartPath = OUTPUT_PATH + "answer ternary distance graphs" + os.sep
					if not os.path.exists(distanceTestsStartPath):
						os.mkdir(distanceTestsStartPath)
					if byQuestion:
						byQuestionPath = distanceTestsStartPath + "by question" + os.sep
						if not os.path.exists(byQuestionPath):
							os.mkdir(byQuestionPath)
						distancesPath = byQuestionPath + cleanTextForFileName(choiceQuestion.shortName) + os.sep
					else:
						byScalePath = distanceTestsStartPath + "by scale" + os.sep
						if not os.path.exists(byScalePath):
							os.mkdir(byScalePath)
						distancesPath = byScalePath + cleanTextForFileName(ternaryQuestion.veryShortName()) + os.sep
					if not os.path.exists(distancesPath):
						os.mkdir(distancesPath)
					graphName = "Distance - %s with %s (%s)" % (ternaryQuestion.veryShortName(), choiceQuestion.shortName, slice)
					note = ""#"Size of circle is degree of difference between means; bright is normal, pale is non-normal or unequal variance."
					if len(labels) > 1:
						graphCircleMatrix(len(labels), labels, sizes, values, None, None, colors, graphName, note, graphName, distancesPath)
	print '  done comparing ternary means by question answer.'
	
def sizeAndColorForTernaryDistance(distance):
	if distance >= 2.0: # arbitrary
		# highest distance was 6
		size = abs(distance) / 12.0
		color = '#FF7722'
	else:
		size = 0
		color = '#000000'
	return size, color

def ternaryDistanceForTwoChoiceQuestions(firstValues, secondValues):
	x1, y1, z1 = meanXYZOfTernaryValueList(firstValues)
	x2, y2, z2 = meanXYZOfTernaryValueList(secondValues)
	distance = (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1) + (z2-z1) * (z2-z1)
	distance = distance / 100.0
	return distance

def meanXYZOfTernaryValueList(valueList):
	totalX = 0
	totalY = 0
	totalZ = 0
	for i in range(len(valueList)):
		totalX += valueList[i][0]
		totalY += valueList[i][1]
		totalZ += valueList[i][2]
	return (totalX / len(valueList), totalY / len(valueList), totalZ / len(valueList))
	
# -----------------------------------------------------------------------------------------------------------------
# ternary plots against scales
# -----------------------------------------------------------------------------------------------------------------

def graphTernaryPlotsAgainstScales(questions, stories, extraName=None, separateDirectories=True, overwriteFiles=False, slice=ALL_DATA_SLICE):
	if not DATA_HAS_TERNARY_SETS:
		return
	print 'writing ternarySets against scales ...'
	scaleQuestions = gatherScaleQuestions(questions)
	for question in scaleQuestions:
		graphTernaryPlots(questions, stories, question.id, extraName, separateDirectories=separateDirectories, 
						overwriteFiles=overwriteFiles, slice=slice)
	print '  done writing ternarySets against scales.'

def graphTernaryPlotsAgainstScalesForQuestionAnswers(questions, stories, overwriteFiles=False):
	if not DATA_HAS_TERNARY_SETS:
		return
	print 'writing ternarySets against scales by question answer ...'
	graphsWritten = 0
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	for choiceQuestion in questions:
		if choiceQuestion.isChoiceQuestion():
			answersToCheck = []
			answersToCheck.extend(choiceQuestion.shortResponseNames)
			answersToCheck.append(NO_ANSWER)
			answersToCheck = removeDuplicates(answersToCheck) # because of extra answers in survey
			for answer in answersToCheck:
				storiesWithThisAnswer = []
				for story in stories:
					if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
						storiesWithThisAnswer.append(story)
				if len(storiesWithThisAnswer) >= lowerLimitStoryNumber: 
					name = "%s: %s" % (choiceQuestion.shortName, answer)
					graphTernaryPlotsAgainstScales(questions, storiesWithThisAnswer,
							extraName=name, separateDirectories=True, overwriteFiles=overwriteFiles)
	print '  done writing ternarySets against scales by question answer.'
	


