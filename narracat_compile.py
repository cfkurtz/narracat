# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Methods that pull together data in order to graph things
# -----------------------------------------------------------------------------------------------------------------

from narracat_graph import *

# -----------------------------------------------------------------------------------------------------------------
# data integrity checks
# -----------------------------------------------------------------------------------------------------------------

# whether people varied too little in their responses
def graphMeanAndSDAmongScaleValuesPerParticipant(questions, participants, slice=ALL_DATA_SLICE):
	print 'writing within-participant means and std devs ...'
	participantsPath = createPathIfNonexistent(OUTPUT_PATH + "participants" + os.sep)
	means = []
	stdevs = []
	for participant in participants:
		mean, stdev = participant.gatherMeanAndSDAmongAllScaleValues(questions, slice=slice)
		if mean:
			means.append(mean)
		if stdev:
			stdevs.append(stdev)
	graphPNGHistogramWithStatsMarked(means, 'Means of scale values within participants', 'Means within participants', participantsPath, slice=slice)
	graphPNGHistogramWithStatsMarked(stdevs, 'Std dev in scale values within participants', 'SD within participants', participantsPath, slice=slice)
	print '  done writing within-participant means and std devs. (%s)' % slice

def graphAllScaleValuesPerParticipant(questions, participants):
	print 'writing within-participant scalar value distributions ...'
	participantsPath = createPathIfNonexistent(OUTPUT_PATH + "participants" + os.sep)
	for participant in participants:
		valuesForParticipant = []
		for question in questions:
			if question.isScale():
				for story in participant.stories:
					values = story.gatherAnswersForQuestionID(question.id)
					if values:
						for value in values:
							if value and value != DOES_NOT_APPLY:
								valuesForParticipant.append(int(value))
		if len(valuesForParticipant) > 2:
			graphPNGHistogramWithStatsMarked(valuesForParticipant, "All scale values for participant " + participant.id, participant.id, participantsPath)

def graphHowManyScaleValuesWereEnteredPerParticipant(questions, participants):
	print 'writing per-participant scalar value counts ...'
	participantsPath = createPathIfNonexistent(OUTPUT_PATH + "participants" + os.sep)
	numValuesPerParticipant = []
	scaleQuestions = gatherScaleQuestions(questions)
	for participant in participants:
		numValues = 0
		for story in participant.stories:
			for question in scaleQuestions:
				values = story.gatherAnswersForQuestionID(question.id)
				if values:
					for value in values:
						if value and value != DOES_NOT_APPLY:
							numValues += 1
		numValuesPerParticipant.append(numValues)
	name = "Number of scale values per participant"
	# may need to change start, end and number of histogram bins to fit max number of scale answers collected
	graphPNGHistogramWithStatsMarked(numValuesPerParticipant, name, name, participantsPath, bins=10, start=0, end=20)

# how many stories have a N/A value for each scale (or don't have any value at all)
# how many stories have extreme high or low values for each scale
def graphBarChartOfExtremeAndNAProportionsPerScale(questions, stories, slice=ALL_DATA_SLICE):
	print 'writing NA scale graph ... (%s)' % slice
	overallPath = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep)
	if DATA_HAS_SLICES:
		overallPathWithSlice = createPathIfNonexistent(overallPath + slice + os.sep)
	else:
		overallPathWithSlice = overallPath
	# scale n/as
	scaleQuestions = gatherScaleQuestions(questions)
	labels = gatherScaleQuestionShortNames(scaleQuestions)
	data = []
	for question in scaleQuestions:
		numberOfNAs = question.gatherNumberOfSpecificValuesIfScale(stories, DOES_NOT_APPLY, slice=slice)
		numberOrScalesNotFilledIn = question.gatherNumberOfMissingValuesIfScale(stories, slice=slice)
		numberOfNAsOrMissingValues = numberOfNAs + numberOrScalesNotFilledIn
		if numberOfNAsOrMissingValues is not None:
			data.append(numberOfNAsOrMissingValues)
		else:
			data.append(0)
	graphPNGBarChart(data, labels, 'Number N/As or missing values per scale', 'Scale NAs and missing values', overallPathWithSlice, slice=slice)
	# scale low extreme
	data = []
	for question in scaleQuestions:
		numberOfNAs = question.gatherNumberOfStoriesWithValuesAboveOrBelow(stories, 'below', LOWER_SCALE_EXTREME_FOR_HIGH_LOW_GRAPHS+1, slice=slice)
		if numberOfNAs is not None:
			data.append(numberOfNAs)
		else:
			data.append(0)
	graphPNGBarChart(data, labels, 
					'Number of stories with value %s or below' % LOWER_SCALE_EXTREME_FOR_HIGH_LOW_GRAPHS, 
					'Scale low values', overallPathWithSlice, slice=slice)
	# scale high extreme
	data = []
	for question in scaleQuestions:
		numberOfNAs = question.gatherNumberOfStoriesWithValuesAboveOrBelow(stories, 'above', UPPER_SCALE_EXTREME_FOR_HIGH_LOW_GRAPHS-1, slice=slice)
		if numberOfNAs is not None:
			data.append(numberOfNAs)
		else:
			data.append(0)
	graphPNGBarChart(data, labels, 
					'Number of stories with value %s or above' % UPPER_SCALE_EXTREME_FOR_HIGH_LOW_GRAPHS, 
					'Scale high values', overallPathWithSlice, slice=slice)
	if DATA_HAS_TERNARY_SETS:
		# ternary n/as
		data = []
		ternaryQuestions = gather3DScaleQuestions(questions)
		labels = []
		for question in ternaryQuestions:
			numberOfNAs = question.gatherNumberOfNAsIfTernarySet(stories, slice=slice)
			labels.append(question.shortName)
			if numberOfNAs is not None:
				data.append(numberOfNAs)
			else:
				data.append(0)
		graphPNGBarChart(data, labels, 'Number N/As per ternary set', 'Ternary set NAs', overallPathWithSlice, slice=slice)
	print '   done writing NA scale graphs. (%s)' % slice
	
# how many people didn't respond to each single-choice or multiple-choice question
def graphBarChartOfNAProportionsPerChoiceQuestion(questions, stories, slice=ALL_DATA_SLICE):
	print 'writing NA question graph ... (%s)' % slice
	overallPath = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep)
	if DATA_HAS_SLICES:
		overallPathWithSlice = createPathIfNonexistent(overallPath + slice + os.sep)
	else:
		overallPathWithSlice = overallPath
	labels = gatherChoiceQuestionShortNames(questions)
	data = []
	for question in questions:
		numberOfNAs = question.gatherNumberOfNAsIfChoiceQuestion(stories, slice=slice)
		if numberOfNAs is not None:
			data.append(numberOfNAs)
	graphPNGBarChart(data, labels, 'Number N/As per question', 'Question NAs', overallPathWithSlice, slice=slice)
	print '  done writing NA question graph. (%s)' % slice
	
# -----------------------------------------------------------------------------------------------------------------
# graphing scale values
# -----------------------------------------------------------------------------------------------------------------

def graphOneGiantHistogramOfAllScaleValues(questions, stories, slice=ALL_DATA_SLICE):
	print 'writing giant all scales histogram ... (%s)' % slice
	scaleQuestions = gatherScaleQuestions(questions)
	allArray = []
	for question in scaleQuestions:
		numbersArray = question.gatherScaleValuesFromStories(stories, slice=slice)
		if numbersArray:
			allArray.extend(numbersArray)
	overallPath = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep)
	if DATA_HAS_SLICES:
		overallPathWithSlice = createPathIfNonexistent(overallPath + slice + os.sep)
	else:
		overallPathWithSlice = overallPath
	name = "All scale values"
	graphPNGHistogramWithStatsMarked(allArray, name, name, overallPathWithSlice, slice=slice)
	print '  done writing giant all scales histogram. (%s)' % slice

# plain histograms of scale values
def graphScaleHistograms(questions, stories, inOwnDirectory=True, slice=ALL_DATA_SLICE):
	print 'writing scale histograms ... (%s)' % slice
	scaleQuestions = gatherScaleQuestions(questions)
	for question in scaleQuestions:
		numbersArray = question.gatherScaleValuesFromStories(stories, slice=slice)
		if numbersArray:
			startPath = createPathIfNonexistent(OUTPUT_PATH + "scale histograms" + os.sep)
			if DATA_HAS_SLICES:
				startPathWithSlice = createPathIfNonexistent(startPath + slice + os.sep)
			else:
				startPathWithSlice = startPath
			if inOwnDirectory:
				path = createPathIfNonexistent(startPathWithSlice + cleanTextForFileName(question.shortName) + os.sep)
			else:
				path = startPathWithSlice
			graphPNGHistogramWithStatsMarked(numbersArray, question.shortName, question.shortName, path, slice=slice)
	print '  done writing scale histograms. (%s)' % slice
	
# scale histograms sliced by answers to questions (happy, sad, etc)
def graphScaleHistogramsPerQuestionAnswer(questions, stories, slice=ALL_DATA_SLICE, writeSelections=True):
	print 'writing scale histograms by answer ... (%s)' % slice
	graphsWritten = 0
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	choiceQuestions = gatherChoiceQuestions(questions)
	scaleQuestions = gatherScaleQuestions(questions)
	for choiceQuestion in choiceQuestions:
		print '  ... considering question %s ... ' % choiceQuestion.shortName
		for answer in choiceQuestion.shortResponseNames:
			storiesWithThisAnswer = []
			for story in stories:
				if story.matchesSlice(slice):
					if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
						storiesWithThisAnswer.append(story)
			if len(storiesWithThisAnswer) >= lowerLimitStoryNumber: 
				for scaleQuestion in scaleQuestions:
					numbersArray = scaleQuestion.gatherScaleValuesFromStories(storiesWithThisAnswer)
					if numbersArray and len(numbersArray) >= lowerLimitStoryNumber:
						name = "%s with %s - %s" % (scaleQuestion.shortName, choiceQuestion.shortName, answer)
						startPath = createPathIfNonexistent(OUTPUT_PATH + "scale histograms" + os.sep)
						if DATA_HAS_SLICES:
							startPathWithSlice = createPathIfNonexistent(startPath + slice + os.sep)
						else:
							startPathWithSlice = startPath
						path = createPathIfNonexistent(startPathWithSlice + cleanTextForFileName(scaleQuestion.shortName) + os.sep)
						graphPNGHistogramWithStatsMarked(numbersArray, name, name, path, slice=slice)
						graphsWritten += 1
						if graphsWritten % 20 == 0:
							print '  ... %s graphs written' % graphsWritten
		# stories with no answer
		storiesWithNoAnswer = []
		for story in stories:
			if story.matchesSlice(slice):
				if story.hasNoAnswerForQuestionID(choiceQuestion.id):
					storiesWithNoAnswer.append(story)
		if len(storiesWithNoAnswer) >= lowerLimitStoryNumber: 
			for scaleQuestion in scaleQuestions:
				numbersArray = scaleQuestion.gatherScaleValuesFromStories(storiesWithNoAnswer)
				if numbersArray and len(numbersArray) >= lowerLimitStoryNumber:
					name = "%s with %s - %s" % (scaleQuestion.shortName, choiceQuestion.shortName, 'No answer')
					startPath = createPathIfNonexistent(OUTPUT_PATH + "scale histograms" + os.sep)
					if DATA_HAS_SLICES:
						startPathWithValue = createPathIfNonexistent(startPath + slice + os.sep)
					else:
						startPathWithValue = startPath
					path = createPathIfNonexistent(startPathWithValue + cleanTextForFileName(scaleQuestion.shortName) + os.sep)
					graphPNGHistogramWithStatsMarked(numbersArray, name, name, path, slice=slice)
					graphsWritten += 1
					if graphsWritten % 20 == 0:
						print '  ... %s graphs written' % graphsWritten
		# stories with any answer
		storiesWithAnyAnswer = []
		for story in stories:
			if story.matchesSlice(slice):
				if story.hasAnyAnswerForQuestionID(choiceQuestion.id):
					storiesWithAnyAnswer.append(story)
		if len(storiesWithAnyAnswer) >= lowerLimitStoryNumber: 
			for scaleQuestion in scaleQuestions:
				numbersArray = scaleQuestion.gatherScaleValuesFromStories(storiesWithAnyAnswer)
				if numbersArray and len(numbersArray) >= lowerLimitStoryNumber:
					name = "%s with %s - %s" % (scaleQuestion.shortName, choiceQuestion.shortName, 'Any answer')
					startPath = createPathIfNonexistent(OUTPUT_PATH + "scale histograms" + os.sep)
					if DATA_HAS_SLICES:
						startPathWithSlice = createPathIfNonexistent(startPath + slice + os.sep)
					else:
						startPathWithSlice = startPath
					path = createPathIfNonexistent(startPathWithSlice + cleanTextForFileName(scaleQuestion.shortName) + os.sep)
					graphPNGHistogramWithStatsMarked(numbersArray, name, name, path, slice=slice)
					graphsWritten += 1
					if graphsWritten % 20 == 0:
						print '  ... %s graphs written' % graphsWritten
						
	print '  done writing scale histograms by answer. (%s)' % slice
	
# -----------------------------------------------------------------------------------------------------------------
# graphing question answers
# -----------------------------------------------------------------------------------------------------------------

# how many answers were gathered for each possible answer
def graphBarChartsOfAnswerCountsPerQuestion(questions, stories, slice=ALL_DATA_SLICE):
	print 'writing question answer bar charts ... (%s)' % slice
	chartsPath = createPathIfNonexistent(OUTPUT_PATH + "question barcharts" + os.sep)
	if DATA_HAS_SLICES:
		chartsPathWithSlice = createPathIfNonexistent(chartsPath + slice + os.sep)
	else:
		chartsPathWithSlice = chartsPath
	for question in questions:
		labels, data = question.gatherNamesAndCountsOfChoiceAnswers(stories, slice=slice)
		if labels and data:
			graphPNGBarChart(data, labels, question.shortName, question.shortName, chartsPathWithSlice, slice=slice)
	print '  done writing question answer bar charts. (%s)' % slice
	
# whether answers co-occurred (or didn't)
def graphBarChartOfAnswerCombinationCounts(questions, stories, slice=ALL_DATA_SLICE):
	print 'writing answer combination graphs ... (%s)' % slice
	overallPath = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep)
	if DATA_HAS_SLICES:
		overallPathWithSlice = createPathIfNonexistent(overallPath + slice + os.sep)
	else:
		overallPathWithSlice = overallPath
	labelsAndData = []
	print '  ... gathering'
	allAnswers = gatherChoiceQuestionAnswers(questions)
	
	print '  ... combining'
	numCombinationsConsidered = 0
	for i in range(len(allAnswers)):
		for j in range(len(allAnswers)):
			if i < j and allAnswers[i][0].id != allAnswers[j][0].id:
				countForThisCombination = 0
				for story in stories:
					if story.matchesSlice(slice):
						if story.hasBothOfTwoQuestionAnswerTuples(allAnswers[i], allAnswers[j]):
							countForThisCombination += 1
				firstAnswerLabel = "%s: %s" % (allAnswers[i][0].shortName, allAnswers[i][1])
				secondAnswerLabel = "%s: %s" % (allAnswers[j][0].shortName, allAnswers[j][1])
				combinedLabel = "%s X %s" % (firstAnswerLabel, secondAnswerLabel)
				labelsAndData.append((combinedLabel, countForThisCombination))
				numCombinationsConsidered += 1
				if numCombinationsConsidered % 1000 == 0:
					print '	... %s combinations considered' % numCombinationsConsidered
	print '  ... sorting'
	labelsAndData.sort(lambda a,b: cmp(a[1], b[1]))
	
	data = []
	labels = []
	for labelAndData in labelsAndData:
		labels.append(labelAndData[0])
		data.append(labelAndData[1])
	
	# if there are so many combinations with few entries that they overwhelm the graph,
	# write them to a text file instead
	writeToText = True

	if writeToText:
		combinationCountBottomCutoff = 10
		outputFile = open(overallPath + "Answer combinations with 0-%s responses.txt" % combinationCountBottomCutoff, 'w')
		try:
			for labelAndData in labelsAndData:
				if labelAndData[1] <= combinationCountBottomCutoff:
					outputFile.write("%s - %s\n" % (labelAndData[0], labelAndData[1]))
		finally:
			outputFile.close()
	else:
		numCombinationsToShowAtBottom = 50
		graphPNGBarChart(data[0:numCombinationsToShowAtBottom-1], labels[0:numCombinationsToShowAtBottom-1], 
					'Lowest answer combination frequencies', 'Lowest answer combination frequencies', 
					overallPathWithSlice, figureHeight=10, slice=slice)
		
	# for top combinations, always draw bar graph
	numCombinationsToShowAtTop = 50
	graphPNGBarChart(data[-numCombinationsToShowAtTop:], labels[-numCombinationsToShowAtTop:], 
				'Highest answer combination frequencies', 'Highest answer combination frequencies', 
				overallPathWithSlice, figureHeight=10, slice=slice)
	print '  done writing answer combination graphs. (%s)' % slice
	
# chi squared test for answer combination frequencies (contingencies)
def graphAnswerContingencies(questions, stories, chiSquared=False, slice=ALL_DATA_SLICE):
	print 'writing answer contingencies ... (%s)' % slice
	if chiSquared:
		contingenciesPath = createPathIfNonexistent(OUTPUT_PATH + "chi-squared answer contingencies" + os.sep)
	else:
		contingenciesPath = createPathIfNonexistent(OUTPUT_PATH + "answer contingencies" + os.sep)
	if DATA_HAS_SLICES:
		contingenciesPathWithSlice = createPathIfNonexistent(contingenciesPath + slice + os.sep)
	else:
		contingenciesPathWithSlice = contingenciesPath
	labelsAndData = []
	
	numGraphsWritten = 0
	collectedResultsForChiSquaredCSVReport = []
	choiceQuestions = gatherChoiceQuestions(questions)
	for i in range(len(choiceQuestions)):
		for j in range(len(choiceQuestions)):
			if 1:# i < j: 
				firstQuestion = choiceQuestions[i]
				secondQuestion = choiceQuestions[j]
				data = []
				colors = []
				firstAnswersToCheck = []
				if not chiSquared:
					firstAnswersToCheck.append(ALL_ANSWERS)
				firstAnswersToCheck.extend(firstQuestion.shortResponseNames)
				if not chiSquared:
					firstAnswersToCheck.append(NO_ANSWER)
				firstAnswersToCheck = removeDuplicates(firstAnswersToCheck) # because of extra answers in survey
				if chiSquared:
					firstAnswersToCheck = removeSpecificListItemsFromList(firstAnswersToCheck, EXCLUDE_FROM_CHI_SQUARED_TESTS)
				for firstAnswer in firstAnswersToCheck:
					data.append([])
					colors.append([])
					secondAnswersToCheck = []
					if not chiSquared:
						secondAnswersToCheck.append(ALL_ANSWERS)
					secondAnswersToCheck.extend(secondQuestion.shortResponseNames)
					if not chiSquared:
						secondAnswersToCheck.append(NO_ANSWER)
					secondAnswersToCheck = removeDuplicates(secondAnswersToCheck) # because of extra answers in survey
					if chiSquared:
						secondAnswersToCheck = removeSpecificListItemsFromList(secondAnswersToCheck, EXCLUDE_FROM_CHI_SQUARED_TESTS)
					for secondAnswer in secondAnswersToCheck:
						numStoriesForThisCombination = 0
						for story in stories:
							if story.matchesSlice(slice):
								if story.hasBothOfTwoQuestionAnswerTuples((firstQuestion, firstAnswer), (secondQuestion, secondAnswer)):
									numStoriesForThisCombination += 1
						value = numStoriesForThisCombination
						data[-1].append(value) 
						colors[-1].append("#FF0000")
				if 1: #firstQuestion.shortName != secondQuestion.shortName or firstQuestion.type == TYPE_MULTI_CHOICE:
					graphName = "%s X %s" % (firstQuestion.shortName, secondQuestion.shortName)
					note = ""#"Size of circle is number of stories\nwith both answers in common."
					xLabels = firstAnswersToCheck
					yLabels = secondAnswersToCheck
					if chiSquared:
						smallestCellValue = 10000
						for k in range(len(data)):
							for l in range(len(data[k])):
								if abs(data[k][l]) < smallestCellValue:
									smallestCellValue = abs(data[k][l])
						chiSquaredValue, chiSquaredPValue = graphChiSquaredContingencyCircleMatrix(xLabels, yLabels, data, 
												graphName, note, graphName, contingenciesPathWithSlice, slice=slice)
						collectedResultsForChiSquaredCSVReport.append((firstQuestion.shortName, secondQuestion.shortName, 
												chiSquaredValue, chiSquaredPValue, smallestCellValue))
					else:
						graphContingencyCircleMatrix(xLabels, yLabels, data, 
												graphName, note, graphName, contingenciesPathWithSlice, slice=slice)
					numGraphsWritten += 1
					if numGraphsWritten % 10 == 0:
						print '  ... %s combinations considered' % numGraphsWritten
	outputFileName = contingenciesPathWithSlice + "Chi-squared test results.csv"
	outputFile = open(outputFileName, 'w')
	try:
		# leave space for "first question" entry
		outputFile.write(",")
		# write line of "second question" names across the top (these are repeated over and over, so just use question list instead)
		for question in choiceQuestions:
			outputFile.write(question.shortName + ",")
		# for each result, write it in the cells in order
		# when a new "first question" is considered, add a carriage return
		lastFirstQuestion = None
		for line in collectedResultsForChiSquaredCSVReport:
			if line[0] != lastFirstQuestion:
				outputFile.write("\n%s," % line[0])
				lastFirstQuestion = line[0]
			if line[4] >= 5:
				if line[3] <= SIGNIFICANCE_VALUE_REPORTING_THRESHOLD:
					outputFile.write("p=%.3f c=%.3f n=%s," %(line[3], line[2], line[4]))
				else:
					outputFile.write('NS,')
			else:
				outputFile.write(",")
		outputFile.write("\n")
	finally:
		outputFile.close()
	print '  done writing answer contingencies. (%s)' % slice
	
# -----------------------------------------------------------------------------------------------------------------
# graphing scales with question answers
# -----------------------------------------------------------------------------------------------------------------

# whether scale values differed when questions were answered differently
def doTTestsToCompareScaleValuesWithQuestionAnswers(questions, stories, slice=ALL_DATA_SLICE, byQuestion=True):
	print 'writing answer combination t tests ... (%s)' % slice
	questionsConsidered = 0
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	scaleQuestions = gatherScaleQuestions(questions)
	for scaleQuestion in scaleQuestions:
		print '  ... scale %s' % scaleQuestion.shortName
		for choiceQuestion in questions:
			if choiceQuestion.isChoiceQuestion():
				print '	  ... choice question %s' % choiceQuestion.shortName
				atLeastOneComparisonIsSignificant = False
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
						scaleValues = scaleQuestion.gatherScaleValuesFromStories(storiesWithThisAnswer)
						if len(scaleValues) >= lowerLimitStoryNumber:
							answerValuesForThisQuestion[answer] = scaleValues
				results = []
				i = 0
				j = 0
				sizes = []
				values = []
				pValues = []
				colors = []
				answerSubsetsToGraph = []
				for firstAnswer in answerValuesForThisQuestion:
					sizes.append([])
					values.append([])
					pValues.append([])
					colors.append([])
					for secondAnswer in answerValuesForThisQuestion:
						if firstAnswer != secondAnswer:
							normal, t, tp = ttestForTwoChoiceQuestions(answerValuesForThisQuestion[firstAnswer], answerValuesForThisQuestion[secondAnswer])
							size, color = sizeAndColorForTTestStats(normal, t, tp)
							if tp < SIGNIFICANCE_VALUE_REPORTING_THRESHOLD and abs(t) >= T_TEST_VALUE_REPORTING_THRESHOLD:
								pValue = tp
								answerSubsetsToGraph.append(firstAnswer)
								answerSubsetsToGraph.append(secondAnswer)
							else:
								pValue = 0
							value = t
						else:
							size = 0
							color = "#000000"
							value = 0
							pValue = 0
						sizes[i].append(size)
						values[i].append(value)
						pValues[i].append(pValue)
						colors[i].append(color)
						if pValue != 0:
							atLeastOneComparisonIsSignificant = True
						j += 1
					i += 1
				if atLeastOneComparisonIsSignificant:
					# set labels with scale names
					labels = answerValuesForThisQuestion.keys()
					# set path to save file in
					ttestsStartPath = createPathIfNonexistent(OUTPUT_PATH + "answer t tests" + os.sep)
					if DATA_HAS_SLICES:
						ttestsStartPathWithSlice = createPathIfNonexistent(ttestsStartPath + slice + os.sep)
					else:
						ttestsStartPathWithSlice = ttestsStartPath
					if byQuestion:
						byQuestionPath = createPathIfNonexistent(ttestsStartPathWithSlice + "by question" + os.sep)
						ttestsPath = createPathIfNonexistent(byQuestionPath + cleanTextForFileName(choiceQuestion.shortName) + os.sep)
					else:
						byScalePath = createPathIfNonexistent(ttestsStartPathWithSlice + "by scale" + os.sep)
						ttestsPath = createPathIfNonexistent(byScalePath + cleanTextForFileName(scaleQuestion.shortName) + os.sep)
					graphName = "T tests - %s with %s" % (scaleQuestion.shortName, choiceQuestion.shortName)
					note = ""#"Size of circle is degree of difference between means; bright is normal, pale is non-normal or unequal variance."
					if len(labels) > 1:
						graphCircleMatrix(len(labels), labels, sizes, values, pValues, 't', colors, 
										graphName, note, graphName, ttestsPath, slice=slice)
					if DRAW_COMPARISON_HISTOGRAMS_FOR_SIGNIFICANT_T_TESTS:
						for answer in answerSubsetsToGraph:
							storiesWithThisAnswer = []
							for story in stories:
								if story.matchesSlice(slice):
									if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
										storiesWithThisAnswer.append(story)
							numbersArray = scaleQuestion.gatherScaleValuesFromStories(storiesWithThisAnswer)
							if numbersArray and len(numbersArray) >= lowerLimitStoryNumber:
								name = "%s with %s - %s" % (scaleQuestion.shortName, choiceQuestion.shortName, answer)
								graphPNGHistogramWithStatsMarked(numbersArray, name, name, ttestsPath, slice=slice)
	print '  done writing answer combination t tests. (%s)' % slice
	
def sizeAndColorForTTestStats(normal, t, tp):
	if tp < SIGNIFICANCE_VALUE_REPORTING_THRESHOLD:
		size = abs(t) / 40.0
		if normal:
			color = '#FF7722'
		else:
			color = '#FFCC99'
	else:
		size = 0
		color = '#000000'
	return size, color
	
def compareSkewInScaleValuesWithQuestionAnswers(questions, stories, slice=ALL_DATA_SLICE, byQuestion=True):
	print 'writing answer combination skew diffs ... (%s)' % slice
	questionsConsidered = 0
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	scaleQuestions = gatherScaleQuestions(questions)
	for scaleQuestion in scaleQuestions:
		print '  ... scale %s' % scaleQuestion.shortName
		for choiceQuestion in questions:
			if choiceQuestion.isChoiceQuestion():
				print '	  ... choice question %s' % choiceQuestion.shortName
				atLeastOneComparisonIsSignificant = False
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
						scaleValues = scaleQuestion.gatherScaleValuesFromStories(storiesWithThisAnswer)
						if len(scaleValues) > lowerLimitStoryNumber:
							answerValuesForThisQuestion[answer] = scaleValues
				results = []
				i = 0
				j = 0
				sizes = []
				values = []
				colors = []
				answerSubsetsToGraph = []
				for firstAnswer in answerValuesForThisQuestion:
					sizes.append([])
					values.append([])
					colors.append([])
					for secondAnswer in answerValuesForThisQuestion:
						if firstAnswer != secondAnswer:
							firstSkewness = stats.skew(np.array(answerValuesForThisQuestion[firstAnswer]))
							secondSkewness = stats.skew(np.array(answerValuesForThisQuestion[secondAnswer]))
							skewnessDifference = firstSkewness - secondSkewness
							size, color = sizeAndColorForSkewnessDifference(skewnessDifference, SKEW_DIFFERENCE_REPORTING_THRESHOLD)
							value = skewnessDifference
							if abs(value) > SKEW_DIFFERENCE_REPORTING_THRESHOLD:
								answerSubsetsToGraph.append(firstAnswer)
								answerSubsetsToGraph.append(secondAnswer)
						else:
							size = 0
							color = "#000000"
							value = 0
						sizes[i].append(size)
						values[i].append(value)
						colors[i].append(color)
						if abs(value) > SKEW_DIFFERENCE_REPORTING_THRESHOLD:
							atLeastOneComparisonIsSignificant = True
						j += 1
					i += 1
				if atLeastOneComparisonIsSignificant:
					# set labels with scale names
					labels = answerValuesForThisQuestion.keys()
					# set path to save file in
					ttestsStartPath = createPathIfNonexistent(OUTPUT_PATH + "answer skew diffs" + os.sep)
					if DATA_HAS_SLICES:
						ttestsStartPathWithSlice = createPathIfNonexistent(ttestsStartPath + slice + os.sep)
					else:
						ttestsStartPathWithSlice = ttestsStartPath
					if byQuestion:
						byQuestionPath = createPathIfNonexistent(ttestsStartPathWithSlice + "by question" + os.sep)
						ttestsPath = createPathIfNonexistent(byQuestionPath + cleanTextForFileName(choiceQuestion.shortName) + os.sep)
					else:
						byScalePath = createPathIfNonexistent(ttestsStartPathWithSlice + "by scale" + os.sep)
						ttestsPath = createPathIfNonexistent(byScalePath + cleanTextForFileName(scaleQuestion.shortName) + os.sep)
					graphName = "Skew diffs - %s with %s" % (scaleQuestion.shortName, choiceQuestion.shortName)
					note = ""#"Size of circle is degree of difference between means; bright is normal, pale is non-normal or unequal variance."
					if len(labels) > 1:
						graphCircleMatrix(len(labels), labels, sizes, values, None, None, colors, 
										graphName, note, graphName, ttestsPath, slice=slice)
					if DRAW_COMPARISON_HISTOGRAMS_FOR_SKEW_DIFFERENCES:
						for answer in answerSubsetsToGraph:
							storiesWithThisAnswer = []
							for story in stories:
								if story.matchesSlice(slice):
									if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
										storiesWithThisAnswer.append(story)
							numbersArray = scaleQuestion.gatherScaleValuesFromStories(storiesWithThisAnswer)
							if numbersArray and len(numbersArray) >= lowerLimitStoryNumber:
								name = "%s with %s - %s" % (scaleQuestion.shortName, choiceQuestion.shortName, answer)
								graphPNGHistogramWithStatsMarked(numbersArray, name, name, ttestsPath, slice=slice)
	print '  done writing answer combination skew comparisons. (%s)' % slice
	
def sizeAndColorForSkewnessDifference(difference, threshold):
	if abs(difference) > threshold:
		size = abs(difference) / 10.0
		color = '#FF7722'
	else:
		size = 0
		color = '#000000'
	return size, color
	
# -----------------------------------------------------------------------------------------------------------------
# two scales together
# -----------------------------------------------------------------------------------------------------------------

def graphScaleCorrelationMatrix(questions, stories, extraName=None, separateDirectories=True, slice=ALL_DATA_SLICE):
	graphScaleScattergramsOrCorrelationMatrix(questions, stories, drawMatrix=True, separateDirectories=separateDirectories, slice=slice)

def graphScaleScattergrams(questions, stories, extraName=None, separateDirectories=True, slice=ALL_DATA_SLICE):
	graphScaleScattergramsOrCorrelationMatrix(questions, stories, drawMatrix=False, separateDirectories=separateDirectories, slice=slice)
	
# pairwise combinations of scales
def graphScaleScattergramsOrCorrelationMatrix(questions, stories, extraName=None, separateDirectories=True, drawMatrix=False, slice=ALL_DATA_SLICE):
	print 'writing scale scatter graphs or correlation matrices ...  (%s)' % slice
	if extraName:
		print '   for %s' % extraName
	scatterPath = createPathIfNonexistent(OUTPUT_PATH + "scale scatter graphs" + os.sep)
	if DATA_HAS_SLICES:
		scatterPathWithSlice = createPathIfNonexistent(scatterPath + slice + os.sep)
	else:
		scatterPathWithSlice = scatterPath
	scaleQuestions = gatherScaleQuestions(questions)
	graphsWritten = 0
	lowCounts = {}
	lowerLimitValueNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	if drawMatrix:
		sizes = []
		values = []
		pValues = []
		colors = []
	for i in range(len(scaleQuestions)):
		if drawMatrix:
			sizes.append([])
			values.append([])
			pValues.append([])
			colors.append([])
		for j in range(len(scaleQuestions)):
			if 1: #i < j or drawMatrix:
				xValues = []
				yValues = []
				for story in stories:
					if story.matchesSlice(slice):
						xy = story.gatherScaleValuesForListOfIDs([scaleQuestions[i].id, scaleQuestions[j].id])
						if xy:
							xValues.append(int(xy[0]))
							yValues.append(int(xy[1]))
				if drawMatrix:
					if len(xValues) >= lowerLimitValueNumber and len(yValues) >= lowerLimitValueNumber:
						normal, r, rp = correlationStatsForTwoScales(xValues, yValues, roundValues=False)
						size, color = sizeAndColorForCorrelationStats(normal, r, rp)
						if rp <= SIGNIFICANCE_VALUE_REPORTING_THRESHOLD and abs(r) >= CORRELATION_COEFF_REPORTING_THRESHOLD:
							pValue = rp
						else:
							pValue = 0
						value = r
					else:
						size = 0.05 # this is a mark that says there was not enough data to compare
						value = 0
						pValue = 0
						color = '#222222'
					sizes[i].append(size)
					values[i].append(value)
					pValues[i].append(pValue)
					colors[i].append(color)
				else:
					if len(xValues) >= lowerLimitValueNumber and len(yValues) >= lowerLimitValueNumber:
						combinedName = "%s X %s" % (scaleQuestions[i].veryShortName(), scaleQuestions[j].veryShortName())
						if separateDirectories:
							comboPath = createPathIfNonexistent(scatterPathWithSlice + cleanTextForFileName(combinedName) + os.sep)
						else:
							comboPath = scatterPathWithSlice
						if extraName:
							combinedName = "%s\n%s" % (combinedName, extraName)
						graphPNGScatterGraph(xValues, yValues, scaleQuestions[i].shortName, scaleQuestions[j].shortName, 
											combinedName, combinedName, comboPath, slice=slice)
						graphsWritten += 1
						print '  ... %s graphs written' % graphsWritten
	if drawMatrix:
		# set labels with scale names
		labels = []
		for question in scaleQuestions:
			labels.append(question.shortName)
		# set path to save file in
		corrMatrixPath = createPathIfNonexistent(OUTPUT_PATH + "correlation matrix" + os.sep)
		if DATA_HAS_SLICES:
			corrMatrixPathWithSlice = createPathIfNonexistent(corrMatrixPath + slice + os.sep)
		else:
			corrMatrixPathWithSlice = corrMatrixPath
		# set name of graph
		graphName = "Correlation matrix"
		if extraName:
			graphName = "%s - %s" % (extraName, graphName)
		note = "Circle size is R value; strong/pale is normal/non-normal; green is positive, red is negative correlation."
		graphCircleMatrix(len(scaleQuestions), labels, sizes, values, pValues, 'r', colors, 
						graphName, note, graphName, corrMatrixPathWithSlice, slice=slice)
	print '  done writing scale scatter graphs or correlation matrices. (%s)' % slice
	
def sizeAndColorForCorrelationStats(normal, r, rp):
	if rp < SIGNIFICANCE_VALUE_REPORTING_THRESHOLD:
		if abs(r) < CORRELATION_COEFF_REPORTING_THRESHOLD:
			size = 0
		else:
			size = abs(r) * 0.8 # usually need to change for data sets
		if r < 0:
			if normal:
				color = '#CD0000'
			else:
				color = '#FF6666'
		else:
			if normal:
				color = '#458B00'
			else:
				color = '#C0D9AF'
	else:
		size = 0
		color = '#000000'
	return size, color
	
# pairwise combinations of scales sliced by answers to questions (happy, sad, etc) 
def graphScaleScattergramsOrCorrelationMatrixForQuestionAnswers(questions, stories, drawMatrix=False, slice=ALL_DATA_SLICE):
	print 'writing scale scatter graphs by question answer ... (%s)' % slice
	graphsWritten = 0
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	lowCountAnswers = []
	for choiceQuestion in questions:
		if choiceQuestion.isChoiceQuestion():
			answersToCheck = []
			answersToCheck.extend(choiceQuestion.shortResponseNames)
			answersToCheck.append(NO_ANSWER)
			answersToCheck = removeDuplicates(answersToCheck)
			for answer in answersToCheck:
				storiesWithThisAnswer = []
				for story in stories:
					if story.matchesSlice(slice):
						if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
							storiesWithThisAnswer.append(story)
				if len(storiesWithThisAnswer) >= lowerLimitStoryNumber: 
					name = "%s: %s" % (choiceQuestion.shortName, answer)
					graphScaleScattergramsOrCorrelationMatrix(questions, storiesWithThisAnswer, 
							extraName=name, separateDirectories=True, drawMatrix=drawMatrix, slice=slice)
	print '  done writing scale scatter graphs by question answer. (%s)' % slice
	
def graphScaleCorrelationMatrixForQuestionAnswers(questions, stories, slice=ALL_DATA_SLICE):
	graphScaleScattergramsOrCorrelationMatrixForQuestionAnswers(questions, stories, drawMatrix=True, slice=slice)

def graphScaleScattergramsForQuestionAnswers(questions, stories, slice=ALL_DATA_SLICE):
	graphScaleScattergramsOrCorrelationMatrixForQuestionAnswers(questions, stories, drawMatrix=False, slice=slice)
	
def writeCorrelationsToCSVForQuestionAnswers(questions, stories, slice=ALL_DATA_SLICE):
	print 'writing correlation values to CSV by question answer ... (%s)' % slice
	outputFileName = OUTPUT_PATH + 'correlations by question answer.csv'
	csvOutput = codecs.open(outputFileName, encoding='utf-8', mode='w+')
	csvOutput.write('Scale 1 x Scale 2 x Question, Question, Answer, p (significance value), r (correlation coefficient), n (sample size)\n')
	try:
		lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
		scaleQuestions = gatherScaleQuestions(questions)
		choiceQuestions = gatherChoiceQuestions(questions)
		for choiceQuestion in choiceQuestions:
			answersToCheck = []
			answersToCheck.extend(choiceQuestion.shortResponseNames)
			answersToCheck.append(NO_ANSWER)
			answersToCheck = removeDuplicates(answersToCheck)
			for answer in answersToCheck:
				storiesWithThisAnswer = []
				for story in stories:
					if story.matchesSlice(slice):
						if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
							storiesWithThisAnswer.append(story)
				if len(storiesWithThisAnswer) >= lowerLimitStoryNumber: 
					for i in range(len(scaleQuestions)):
						for j in range(len(scaleQuestions)):
							if i < j:
								xValues = []
								yValues = []
								for story in storiesWithThisAnswer:
									if story.matchesSlice(slice):
										xy = story.gatherScaleValuesForListOfIDs([scaleQuestions[i].id, scaleQuestions[j].id])
										if xy:
											xValues.append(int(xy[0]))
											yValues.append(int(xy[1]))
								if len(xValues) >= lowerLimitStoryNumber and len(yValues) >= lowerLimitStoryNumber:
									normal, r, rp = correlationStatsForTwoScales(xValues, yValues, roundValues=False)
									pValue = round(rp, 4)
									value = round(r, 4)
								else:
									value = 100
									pValue = 100
								csvOutput.write('%s x %s x %s,%s,%s,%s,%s,%s\n' % (
																	scaleQuestions[i].shortName, 
																	scaleQuestions[j].shortName, 
																	choiceQuestion.shortName,
																	choiceQuestion.shortName,
																	answer, pValue, value, len(xValues)))
	finally:
		csvOutput.close()
	
# -----------------------------------------------------------------------------------------------------------------
# stability landscapes
# -----------------------------------------------------------------------------------------------------------------

# two scales with a third Z-axis for stability (should be unstable at top)
def graphScaleContourGraphsAgainstStability(questions, stories, stabilityQuestionName, extraName=None, separateDirectories=True, slice=ALL_DATA_SLICE):
	print 'writing scale landscapes ...  (%s)' % slice
	if extraName:
		print '   for %s' % extraName
	landscapesPath = createPathIfNonexistent(OUTPUT_PATH + "scale landscapes" + os.sep)
	if DATA_HAS_SLICES:
		landscapesPathWithSlice = createPathIfNonexistent(landscapesPath + slice + os.sep)
	else:
		landscapesPathWithSlice = landscapesPath
	stabilityQuestion = questionWithShortName(questions, stabilityQuestionName)
	scaleQuestions = gatherScaleQuestions(questions)
	graphsWritten = 0
	if stabilityQuestion:
		for i in range(len(scaleQuestions)):
			for j in range(len(scaleQuestions)):
				#if i < j and scaleQuestions[i].shortName != stabilityQuestionName and scaleQuestions[j].shortName != stabilityQuestionName:
				if scaleQuestions[i].shortName != stabilityQuestionName and scaleQuestions[j].shortName != stabilityQuestionName:
					xArray = []
					yArray = []
					zArray = []
					for story in stories:
						if story.matchesSlice(slice):
							xyz = story.gatherScaleValuesForListOfIDs([scaleQuestions[i].id, scaleQuestions[j].id, stabilityQuestion.id])
							if xyz:
								xArray.append(xyz[0])
								yArray.append(xyz[1])
								if STABILITY_QUESTION_VALUE_IS_REVERSED:
									zArray.append(str(SLIDER_END - int(xyz[2]) + SLIDER_START))
								else:
									zArray.append(xyz[2])
					if len(xArray):
						combinedName = "%s X %s" % (scaleQuestions[i].veryShortName(), scaleQuestions[j].veryShortName())
						if separateDirectories:
							comboPath = createPathIfNonexistent(landscapesPathWithSlice + cleanTextForFileName(combinedName) + os.sep)
						else:
							comboPath = landscapesPathWithSlice
						if extraName:
							combinedName = "%s\n%s" % (combinedName, extraName)
						graphPNGContourF(xArray, yArray, zArray, 
										scaleQuestions[i].shortName, scaleQuestions[j].shortName, 
										combinedName, combinedName, comboPath, levels=100, slice=slice)
						graphsWritten += 1
						print '  ... %s graphs written' % graphsWritten
	print '  done writing scale landscapes. (%s)' % slice
	
# two scales with Z stability sliced by answers to questions (happy, sad, etc) 
def graphScaleContourGraphsAgainstStabilityForQuestionAnswers(questions, stories, stabilityQuestionName, slice=ALL_DATA_SLICE):
	print 'writing scale landscapes by question answer ... (%s)' % slice
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
					if story.matchesSlice(slice):
						if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
							storiesWithThisAnswer.append(story)
				if len(storiesWithThisAnswer) >= lowerLimitStoryNumber: 
					name = "%s: %s" % (choiceQuestion.shortName, answer)
					graphScaleContourGraphsAgainstStability(questions, storiesWithThisAnswer, stabilityQuestionName,
							extraName=name, separateDirectories=True, slice=slice)
	print '  done writing scale landscapes by question answer. (%s)' % slice
	

def printNumAnswersPerChoiceQuestion(questions, stories, slice=ALL_DATA_SLICE):
	choiceQuestions = gatherChoiceQuestions(questions)
	for choiceQuestion in choiceQuestions:
		answerCounts = []
		for story in stories:
			if story.matchesSlice(slice):
				answers = story.gatherAnswersForQuestionID(choiceQuestion.id)
				if answers:
					answerCounts.append(len(answers))
		npArray = np.array(answerCounts)
		mean = np.mean(npArray)
		std = np.std(npArray)
		print choiceQuestion.shortName, mean, std
		

def printParticipantAnswersPerQuestion(questions, stories, participants):
	printParticipantAnswersPerStory(questions, stories)
	choiceQuestions = gatherChoiceQuestions(questions)
	for choiceQuestion in choiceQuestions:
		for participant in participants:
			answers = participant.stories[0].gatherAnswersForQuestionID(choiceQuestion.id)
			printString = choiceQuestion.shortName + "\t"
			for name in choiceQuestion.shortResponseNames:
				if answers and name in answers:
					printString += "1\t"
				else:
					printString += "\t"
			print printString
				
					
def printParticipantAnswersPerStory(questions, stories):
	choiceQuestions = gatherChoiceQuestions(questions)
	for choiceQuestion in choiceQuestions:
		for story in stories:
			answers = story.gatherAnswersForQuestionID(choiceQuestion.id)
			printString = choiceQuestion.shortName + "\t"
			for name in choiceQuestion.shortResponseNames:
				if answers and name in answers:
					printString += "1\t"
				else:
					printString += "\t"
			print printString
					
def printScaleMeansPerQuestionAnswer(questions, stories, slice=ALL_DATA_SLICE, writeSelections=True):
	print 'writing scale means by answer ... (%s)' % slice
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	choiceQuestions = gatherChoiceQuestions(questions)
	scaleQuestions = gatherScaleQuestions(questions)
	for choiceQuestion in choiceQuestions:
		for answer in choiceQuestion.shortResponseNames:
			storiesWithThisAnswer = []
			for story in stories:
				if story.matchesSlice(slice):
					if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
						storiesWithThisAnswer.append(story)
			if len(storiesWithThisAnswer) >= lowerLimitStoryNumber: 
				for scaleQuestion in scaleQuestions:
					numbersArray = scaleQuestion.gatherScaleValuesFromStories(storiesWithThisAnswer)
					if numbersArray:
						npArray = np.array(numbersArray)
						mean = np.mean(npArray)
						print "%s\t%s\t%s\t%s\t%s" % (scaleQuestion.shortName, choiceQuestion.shortName, answer, mean, len(numbersArray))
		# stories with no answer
		storiesWithNoAnswer = []
		for story in stories:
			if story.matchesSlice(slice):
				if story.hasNoAnswerForQuestionID(choiceQuestion.id):
					storiesWithNoAnswer.append(story)
		if len(storiesWithNoAnswer) >= 1: 
			for scaleQuestion in scaleQuestions:
				numbersArray = scaleQuestion.gatherScaleValuesFromStories(storiesWithNoAnswer)
				if numbersArray:
					npArray = np.array(numbersArray)
					mean = np.mean(npArray)
					print "%s\t%s\t%s\t%s\t%s" % (scaleQuestion.shortName, choiceQuestion.shortName, "No answer", mean, len(numbersArray))
		# stories with any answer
		storiesWithAnyAnswer = []
		for story in stories:
			if story.matchesSlice(slice):
				if story.hasAnyAnswerForQuestionID(choiceQuestion.id):
					storiesWithAnyAnswer.append(story)
		if len(storiesWithAnyAnswer) >= 1: 
			for scaleQuestion in scaleQuestions:
				numbersArray = scaleQuestion.gatherScaleValuesFromStories(storiesWithAnyAnswer)
				if numbersArray:
					npArray = np.array(numbersArray)
					mean = np.mean(npArray)
					print "%s\t%s\t%s\t%s\t%s" % (scaleQuestion.shortName, choiceQuestion.shortName, "Any answer", mean, len(numbersArray))
	print '  done writing scale means by answer. (%s)' % slice
	

	
