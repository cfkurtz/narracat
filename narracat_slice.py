# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Methods that compile data across slice slices and create larger summaries
# -----------------------------------------------------------------------------------------------------------------

from narracat_graph import *
from narracat_compile import *

# -----------------------------------------------------------------------------------------------------------------
# questions alone
# -----------------------------------------------------------------------------------------------------------------

def graphAnswerCountsForSlices(questions, stories, columns):

	choiceQuestions = gatherChoiceQuestions(questions)
	path = createPathIfNonexistent(createPathIfNonexistent(OUTPUT_PATH + "slices" + os.sep) + "answer counts" + os.sep)

	for choiceQuestion in choiceQuestions:
		print '      ', choiceQuestion.shortName
		counts = {}
		slices = []
		maxCount = 0
		for columnID in columns:
			for columnAnswer in columns[columnID]:
				slice = "%s: %s" % (columnID, columnAnswer)
				slices.append(slice)
				answersToCheck = []
				answersToCheck.append(ALL_ANSWERS)
				answersToCheck.extend(choiceQuestion.shortResponseNames)
				answersToCheck.append(NO_ANSWER)
				answersToCheck = removeDuplicates(answersToCheck)
				for answer in answersToCheck:
					numStoriesWithThisAnswer = 0
					for story in stories:
						if (columnID == "All" or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer) and \
							story.hasAnswerForQuestionID(answer, choiceQuestion.id):
								numStoriesWithThisAnswer += 1
					if not counts.has_key(answer):
						counts[answer] = {}
					counts[answer][slice] = numStoriesWithThisAnswer
					if numStoriesWithThisAnswer > maxCount:
						maxCount = numStoriesWithThisAnswer

		slices.sort()
		answersToSort = []
		for answer in counts:
			if not answer == NO_ANSWER: #in [ALL_ANSWERS, NO_ANSWER]:
				answersToSort.append(answer)
		answersToSort.sort()

		sortedAnswers = []
		#sortedAnswers.append(ALL_ANSWERS)
		sortedAnswers.extend(answersToSort)
		sortedAnswers.append(NO_ANSWER)

		data = []
		colors = []
		
		rowsWritten = 0
		rowLabels = []
		for answer in sortedAnswers:
			rowLabels.append(answer)
			data.append([])
			colors.append([])
			colsWritten = 0
			for slice in slices:
				if counts[answer].has_key(slice):
					numStories = counts[answer][slice]
				else:
					numStories = 0
					color = "#000000"
				data[rowsWritten].append(numStories)
				#if numStories >= maxCount // 2:
				color = "#31B94D" 
				#else:
				#	color = "#C5E3BF"
				colors[rowsWritten].append(color)
				colsWritten += 1
			rowsWritten += 1
			
		if len(data):
			transposedData = map(lambda *row: [elem or 0 for elem in row], *data)
			transposedColors = map(lambda *row: [elem or 0 for elem in row], *colors)
			name = choiceQuestion.shortName
			graphSliceValuesMatrix(slices, rowLabels, transposedData, transposedColors, name, "", name, path)
	
def graphAnswerContingenciesForSlices(questions, stories, columns):
	
	choiceQuestions = gatherChoiceQuestions(questions)
	path = createPathIfNonexistent(createPathIfNonexistent(OUTPUT_PATH + "slices" + os.sep) + "answer contingency counts" + os.sep)

	questionCombinationsConsidered = {}
	for firstQuestion in choiceQuestions:
		for secondQuestion in choiceQuestions:
			if secondQuestion.id == firstQuestion.id:
				continue
			if questionCombinationsConsidered.has_key((firstQuestion.id, secondQuestion.id)) or \
				questionCombinationsConsidered.has_key((secondQuestion.id, firstQuestion.id)):
				continue
			print firstQuestion.shortName, "x", secondQuestion.shortName
			counts = {}
			slices = []
			maxCount = 0
			for columnID in columns:
				for columnAnswer in columns[columnID]:
					slice = "%s: %s" % (columnID, columnAnswer)
					slices.append(slice)
					
					firstAnswersToCheck = []
					firstAnswersToCheck.extend(firstQuestion.shortResponseNames)
					firstAnswersToCheck = removeDuplicates(firstAnswersToCheck)
					
					secondAnswersToCheck = []
					secondAnswersToCheck.extend(secondQuestion.shortResponseNames)
					secondAnswersToCheck = removeDuplicates(secondAnswersToCheck)
					
					# show number of stories in slice
					numStories = 0
					for story in stories:
						if  (columnID == ALL_DATA_SLICE or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer):
								numStories += 1
					combo = ("", "anything", "", "anything")
					if not counts.has_key(combo):
						counts[combo] = {}
					counts[combo][slice] = numStories
					if numStories > maxCount:
						maxCount = numStories
				
					combinationsConsidered = {}
					for firstAnswer in firstAnswersToCheck:
						for secondAnswer in secondAnswersToCheck:
							combo = (firstQuestion.shortName, firstAnswer, secondQuestion.shortName, secondAnswer)
							reversedCombo = combo = (secondQuestion.shortName, secondAnswer, firstQuestion.shortName, firstAnswer)
							if combinationsConsidered.has_key(combo) or combinationsConsidered.has_key(reversedCombo):
								continue
							numStories = 0
							for story in stories:
								if  (columnID == ALL_DATA_SLICE or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer) and \
									story.hasAnswerForQuestionID(firstAnswer, firstQuestion.id) and \
									story.hasAnswerForQuestionID(secondAnswer, secondQuestion.id):
										numStories += 1
							combinationsConsidered[combo] = 1
							if not counts.has_key(combo):
								counts[combo] = {}
							counts[combo][slice] = numStories
							if numStories > maxCount:
								maxCount = numStories
	
			slices.sort()
			sortedCombos = []
			sortedCombos.extend(counts.keys())
			sortedCombos.sort()
	
			data = []
			colors = []
			
			rowsWritten = 0
			rowLabels = []
			for combo in sortedCombos:
				if counts[combo]["All: All"] >= LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS:
					comboString = "%s x %s" % (combo[1], combo[3])
					rowLabels.append(comboString)
					data.append([])
					colors.append([])
					colsWritten = 0
					for slice in slices:
						if counts[combo].has_key(slice):
							numStories = counts[combo][slice]
						else:
							numStories = 0
							color = "#000000"
						data[rowsWritten].append(numStories)
						if numStories >= maxCount // 2:
							color = "#31B94D" 
						else:
							color = "#C5E3BF"
						colors[rowsWritten].append(color)
						colsWritten += 1
					rowsWritten += 1
				
			if len(data) > 1:
				transposedData = map(lambda *row: [elem or 0 for elem in row], *data)
				transposedColors = map(lambda *row: [elem or 0 for elem in row], *colors)
				name = "%s x %s" % (firstQuestion.shortName, secondQuestion.shortName)
				graphSliceValuesMatrix(slices, rowLabels, transposedData, transposedColors, name, "", name, path, sizeMultiplier=2.0)
			
			questionCombinationsConsidered[(firstQuestion.id, secondQuestion.id)] = 1
	
# -----------------------------------------------------------------------------------------------------------------
# scales with questions
# -----------------------------------------------------------------------------------------------------------------

def graphTTestValuesForSlices(questions, stories, columns):
	
	scaleQuestions = gatherScaleQuestions(questions)
	choiceQuestions = gatherChoiceQuestions(questions)
	#lowerLimitStoryNumber = 20
	path = createPathIfNonexistent(createPathIfNonexistent(OUTPUT_PATH + "slices" + os.sep) + "t test summaries" + os.sep)

	linesPerCombo = {}
	for lowerLimitStoryNumber in [20]:#, 30]:
		numResults = 0
		for scaleQuestion in scaleQuestions:
			#print scaleQuestion.shortName
			for choiceQuestion in choiceQuestions:
				#print '      ', choiceQuestion.shortName
				name = "%s + %s" % (scaleQuestion.veryShortName(), choiceQuestion.shortName)
				answersToCheck = []
				answersToCheck.extend(choiceQuestion.shortResponseNames)
				#answersToCheck.append(NO_ANSWER)
				answersToCheck = removeDuplicates(answersToCheck)
				ttestResults = {}
				slices = []
				for columnID in columns:
					for columnAnswer in columns[columnID]:
						slice = "%s: %s" % (columnID, columnAnswer)
						slices.append(slice)
						answerValuesForThisQuestion = {}
						for answer in answersToCheck:
							storiesWithThisAnswer = []
							for story in stories:
								if  (columnID == "All" or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer) and \
									story.hasAnswerForQuestionID(answer, choiceQuestion.id):
										storiesWithThisAnswer.append(story)
							scaleValues = scaleQuestion.gatherScaleValuesFromStories(storiesWithThisAnswer)
							answerValuesForThisQuestion[answer] = scaleValues
						if len(answerValuesForThisQuestion) > 0:
							i = 0
							j = 0
							combinationsSaved = {}
							for firstAnswer in answerValuesForThisQuestion:
								for secondAnswer in answerValuesForThisQuestion:
									answerNames = "%s x %s" % (firstAnswer, secondAnswer)
									if not ttestResults.has_key(answerNames):
										ttestResults[answerNames] = {}
									if firstAnswer != secondAnswer and (not combinationsSaved.has_key((firstAnswer, secondAnswer))) and \
											(not combinationsSaved.has_key((secondAnswer, firstAnswer))):
										if answerValuesForThisQuestion.has_key(firstAnswer) and answerValuesForThisQuestion.has_key(secondAnswer):
											if len(answerValuesForThisQuestion[firstAnswer]) < lowerLimitStoryNumber or len(answerValuesForThisQuestion[secondAnswer]) < lowerLimitStoryNumber:
												ttestResults[answerNames][slice] = (0.00001, "#666666")
											else:
												normal, t, tp = ttestForTwoChoiceQuestions(answerValuesForThisQuestion[firstAnswer], answerValuesForThisQuestion[secondAnswer])
												if tp <= 0.05 and abs(t) >= 1.0: 
													if normal:
														color = posNegNormalColor(t, normal)
													else:
														color = "#67E6EC" # non-parametric test has no -ve values
													ttestResults[answerNames][slice] = (round(t, 2), color)
												else:
													ttestResults[answerNames][slice] = (None, None)
										else:
											ttestResults[answerNames][slice] = (None, None)
										combinationsSaved[(firstAnswer, secondAnswer)] = 1
									j += 1
								i += 1
	
				slices.sort()
				sortedAnswerNames = []
				sortedAnswerNames.extend(ttestResults.keys())
				sortedAnswerNames.sort()
				data = []
				colors = []
				
				rowsWritten = 0
				rowLabels = []
				for answerNames in sortedAnswerNames:
					rowHasData = False
					for slice in slices:
						if ttestResults[answerNames].has_key(slice):
							t, color = ttestResults[answerNames][slice]
						else:
							t = None
						if t and t!= 0.00001:
							rowHasData = True
							break
					if rowHasData:
						rowLabels.append(answerNames)
						data.append([])
						colors.append([])
						colsWritten = 0
						for slice in slices:
							if ttestResults[answerNames].has_key(slice):
								t, color = ttestResults[answerNames][slice]
							else:
								t = 0
								color = "#000000"
							data[rowsWritten].append(t)
							colors[rowsWritten].append(color)
							colsWritten += 1
						while colsWritten < len(slices):
							data[rowsWritten].append(0)
							colors[rowsWritten].append(0)
							colsWritten += 1
						rowsWritten += 1
					
				if len(data) > 1:
					numResults += 1
					if not linesPerCombo.has_key(name):
						linesPerCombo[name] = []
					linesPerCombo[name].append(len(data))
					transposedData = map(lambda *row: [elem or 0 for elem in row], *data)
					transposedColors = map(lambda *row: [elem or 0 for elem in row], *colors)
					graphSliceValuesMatrix(slices, rowLabels, transposedData, transposedColors, name, "", name, path, sizeMultiplier=0.3)
		print numResults
	
# -----------------------------------------------------------------------------------------------------------------
# scales alone
# -----------------------------------------------------------------------------------------------------------------

def graphScaleMeansAndStdDevsForSlices(questions, stories, columns):
	
	scaleQuestions = gatherScaleQuestions(questions)
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	path = createPathIfNonexistent(createPathIfNonexistent(OUTPUT_PATH + "slices" + os.sep) + "scale means and std devs" + os.sep)

	for graphName in ["Means for all scales", "Standard deviations of all scales", "Kurtosis for all scales", "Skew for all scales"]:
		result = {}
		slices = []
		for columnID in columns:
			for columnAnswer in columns[columnID]:
				slice = "%s: %s" % (columnID, columnAnswer)
				slices.append(slice)
				
				# do one row across all scales
				scaleIDs = [] 
				for question in scaleQuestions:
					scaleIDs.append(question.id)
				allScaleValuesForThisSlice = []
				for story in stories:
					if (columnID == "All" or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer):
						values = story.gatherScaleValuesForListOfIDs(scaleIDs, convertToInt=True)
						if values:
							allScaleValuesForThisSlice.extend(values)
				if not  result.has_key("All"):
					 result["All"] = {}
				if len(allScaleValuesForThisSlice) > 2:
					result["All"][slice] = statisticForValues(allScaleValuesForThisSlice, graphName)
				else:
					result["All"][slice] = (None, None)
					
				for question in scaleQuestions:
					questionName = question.veryShortName()
					print slice, questionName
					storiesInThisSlice = []
					for story in stories:
						if (columnID == "All" or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer):
							storiesInThisSlice.append(story)
					if not result.has_key(questionName):
						 result[questionName] = {}
					numbersArray = question.gatherScaleValuesFromStories(storiesInThisSlice)
					if len(numbersArray) > 2:
						result[questionName][slice] = statisticForValues(numbersArray, graphName)
					else:
						result[questionName][slice] = (None, None)
	
		slices.sort()
		questionNamesToSort = []
		for name in  result:
			if name != "All":
				questionNamesToSort.append(name)
		questionNamesToSort.sort()
	
		sortedQuestionNames = []
		sortedQuestionNames.append("All")
		sortedQuestionNames.extend(questionNamesToSort)
		
		data = []
		colors = []
		
		rowsWritten = 0
		rowLabels = []
		for questionName in sortedQuestionNames:
			rowLabels.append(questionName)
			data.append([])
			colors.append([])
			colsWritten = 0
			for slice in slices:
				mean, normal = result[questionName][slice]
				data[rowsWritten].append(mean)
				if mean > 0:
					color = "#31B94D" 
				else:
					color = "#FF0000"
				colors[rowsWritten].append(color)
				colsWritten += 1
			rowsWritten += 1
			
		if len(data):
			transposedData = map(lambda *row: [elem or 0 for elem in row], *data)
			transposedColors = map(lambda *row: [elem or 0 for elem in row], *colors)
			graphSliceValuesMatrix(slices, rowLabels, transposedData, transposedColors, graphName, "", graphName, path)
			
def graphOneScaleStatsForSlices(questions, stories, columns):
	
	scaleQuestions = gatherScaleQuestions(questions)
	path = createPathIfNonexistent(createPathIfNonexistent(OUTPUT_PATH + "slices" + os.sep) + "scale stats" + os.sep)

	for question in scaleQuestions:
		result = {}
		slices = []
		for columnID in columns:
			for columnAnswer in columns[columnID]:
				slice = "%s: %s" % (columnID, columnAnswer)
				slices.append(slice)
				storiesInThisSlice = []
				for story in stories:
					if (columnID == "All" or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer):
						storiesInThisSlice.append(story)
				if len(storiesInThisSlice):
					numbersArray = question.gatherScaleValuesFromStories(storiesInThisSlice)
					npArray = np.array(numbersArray)
					normal = isNormal(npArray)
					for graphName in ["Mean", "Skew", "Standard deviation", "Kurtosis"]:
						if not result.has_key(graphName):
							 result[graphName] = {}
						if graphName.find("Mean") >= 0:
							mean, std = np.mean(npArray), np.std(npArray)
							value = round(mean, 2)
						elif graphName.find("Standard") >= 0:
							mean, std = np.mean(npArray), np.std(npArray)
							value = round(std, 2)
						elif graphName.find("Kurtosis") >= 0:
							value = round(stats.kurtosis(npArray), 2)
						elif graphName.find("Skew") >= 0:
							value = round(stats.skew(npArray), 2)
						result[graphName][slice] = (value, normal)
	
		slices.sort()
		graphNames = []
		graphNames.extend(result.keys())
		graphNames.reverse()
			
		data = []
		colors = []
		
		rowsWritten = 0
		rowLabels = []
		for graphName in graphNames:
			rowLabels.append(graphName)
			data.append([])
			colors.append([])
			colsWritten = 0
			total = 0
			for slice in slices:
				value, normal = result[graphName][slice]
				total += abs(value)
			mean = total / len(slices)
			maxDeviation = 0
			for slice in slices:
				value, normal = result[graphName][slice]
				deviation = abs(value) - mean
				if deviation > maxDeviation:
					maxDeviation = deviation
			for slice in slices:
				value, normal = result[graphName][slice]
				data[rowsWritten].append(value)
				color = posNegNormalColor(value, normal)
				if abs(value) - mean == maxDeviation:
					color = lighterOrDarkerColor(color, -100)
				colors[rowsWritten].append(color)
				colsWritten += 1
			rowsWritten += 1
			
		if len(data):
			transposedData = map(lambda *row: [elem or 0 for elem in row], *data)
			transposedColors = map(lambda *row: [elem or 0 for elem in row], *colors)
			name = question.shortName
			graphSliceValuesMatrix(slices, rowLabels, transposedData, transposedColors, name, "", name, path)
			
def statisticForValues(values, graphName):
	npArray = np.array(values)
	normal = isNormal(npArray) 
	if graphName.find("Mean") >= 0:
		mean = np.mean(npArray)
		return round(mean, 2), normal
	elif graphName.find("Standard") >= 0:
		std = np.std(npArray)
		return round(std, 2), normal
	elif graphName.find("Kurtosis") >= 0:
		return round(stats.kurtosis(npArray), 2), normal
	elif graphName.find("Skew") >= 0:
		return round(stats.skew(npArray), 2), normal
	

def graphScaleNAsForSlices(questions, stories, columns):
	
	scaleQuestions = gatherScaleQuestions(questions)
	path = createPathIfNonexistent(createPathIfNonexistent(OUTPUT_PATH + "slices" + os.sep) + "scale means and std devs" + os.sep)

	counts = {}
	slices = []
	for columnID in columns:
		for columnAnswer in columns[columnID]:
			slice = "%s: %s" % (columnID, columnAnswer)
			slices.append(slice)
			
			# do one row across all scales
			storiesInThisSlice = []
			for story in stories:
				if (columnID == "All" or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer):
					storiesInThisSlice.append(story)
			nasForThisSlice = 0
			for question in scaleQuestions:
				nasForThisSlice += question.gatherNumberOfSpecificValuesIfScale(storiesInThisSlice, DOES_NOT_APPLY)
			if not counts.has_key("All"):
				 counts["All"] = {}
			counts["All"][slice] = nasForThisSlice
				
			for question in scaleQuestions:
				questionName = question.veryShortName()
				print slice, questionName
				if not counts.has_key(questionName):
					 counts[questionName] = {}
				nas = question.gatherNumberOfSpecificValuesIfScale(storiesInThisSlice, DOES_NOT_APPLY)
				counts[questionName][slice] = nas

	slices.sort()
	questionNamesToSort = []
	for name in  counts:
		if name != "All":
			questionNamesToSort.append(name)
	questionNamesToSort.sort()

	sortedQuestionNames = []
	sortedQuestionNames.append("All")
	sortedQuestionNames.extend(questionNamesToSort)
	
	data = []
	colors = []
	
	rowsWritten = 0
	rowLabels = []
	for questionName in sortedQuestionNames:
		rowLabels.append(questionName)
		data.append([])
		colors.append([])
		colsWritten = 0
		for slice in slices:
			mean = counts[questionName][slice]
			data[rowsWritten].append(mean)
			color = "#C5E3BF"
			colors[rowsWritten].append(color)
			colsWritten += 1
		rowsWritten += 1
		
	if len(data):
		transposedData = map(lambda *row: [elem or 0 for elem in row], *data)
		transposedColors = map(lambda *row: [elem or 0 for elem in row], *colors)
		graphName = "NA counts for all scales"
		graphSliceValuesMatrix(slices, rowLabels, transposedData, transposedColors, graphName, "", graphName, path)

def graphCorrelationValuesForSlices(questions, stories, columns):
	
	scaleQuestions = gatherScaleQuestions(questions)
	choiceQuestions = gatherChoiceQuestions(questions)
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	path = createPathIfNonexistent(createPathIfNonexistent(OUTPUT_PATH + "slices" + os.sep) + "correlations" + os.sep)

	numResults = 0
	for i in range(len(scaleQuestions)):
		for j in range(len(scaleQuestions)):
			if i < j:
				cross = "%s x %s" % (scaleQuestions[i].veryShortName(), scaleQuestions[j].veryShortName())
				print cross
				correlations = {}
				slices = []
				for columnID in columns:
					for columnAnswer in columns[columnID]:
						slice = "%s: %s" % (columnID, columnAnswer)
						slices.append(slice)
						# do one row without all stories
						storiesInThisSlice = []
						for story in stories:
							if (columnID == "All" or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer):
								storiesInThisSlice.append(story)
						r, normal = correlationForStoriesAndTwoScaleQuestionIDs(storiesInThisSlice, 
																			scaleQuestions[i].id, scaleQuestions[j].id)
						if not correlations.has_key("All"):
							correlations["All"] = {}
						if r:
							correlations["All"][slice] = (round(r, 2), posNegNormalColor(r, normal))
						else:
							correlations["All"][slice] = (None, None)
						for choiceQuestion in choiceQuestions:
							answersToCheck = []
							answersToCheck.append(ALL_ANSWERS)
							answersToCheck.extend(choiceQuestion.shortResponseNames)
							answersToCheck.append(NO_ANSWER)
							answersToCheck = removeDuplicates(answersToCheck)
							for answer in answersToCheck:
								storiesWithThisAnswerInGeneral = []
								for story in stories:
									if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
										storiesWithThisAnswerInGeneral.append(story)
								if len(storiesWithThisAnswerInGeneral) >= LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS:
									qAndA = "%s: %s" % (choiceQuestion.shortName, answer)
									storiesWithThisAnswerInThisSlice = []
									for story in stories:
										if (columnID == "All" or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer) and \
											story.hasAnswerForQuestionID(answer, choiceQuestion.id):
											storiesWithThisAnswerInThisSlice.append(story)
									if not correlations.has_key(qAndA):
										correlations[qAndA] = {}
									if len(storiesWithThisAnswerInThisSlice) >= lowerLimitStoryNumber: 
										r, normal = correlationForStoriesAndTwoScaleQuestionIDs(storiesWithThisAnswerInThisSlice, 
												scaleQuestions[i].id, scaleQuestions[j].id)
										if r:
											correlations[qAndA][slice] = (round(r, 2), posNegNormalColor(r, normal))
										else:
											correlations[qAndA][slice] = (None, None)
									else:
										# the 0.00001 is a special code that means "not enough data" - dumb i know
										correlations[qAndA][slice] = (0.00001, "#666666")

				slices.sort()
				qAndAsToSort = []
				for qAndA in correlations:
					if qAndA != "All":
						qAndAsToSort.append(qAndA)
				qAndAsToSort.sort()
		
				sortedQAndAs = []
				sortedQAndAs.append("All")
				sortedQAndAs.extend(qAndAsToSort)
				
				data = []
				colors = []
				
				rowsWritten = 0
				rowLabels = []
				for qAndA in sortedQAndAs:
					rowHasData = False
					for slice in slices:
						if correlations[qAndA].has_key(slice):
							r, color = correlations[qAndA][slice]
						else:
							r = None
						if r and r != 0 and r != 0.00001:
							rowHasData = True
							break
					if rowHasData or qAndA == "All":
						rowLabels.append(qAndA)
						data.append([])
						colors.append([])
						colsWritten = 0
						for slice in slices:
							if correlations[qAndA].has_key(slice):
								r, color = correlations[qAndA][slice]
							else:
								r = 0
								color = "#000000"
							data[rowsWritten].append(r)
							colors[rowsWritten].append(color)
							colsWritten += 1
						while colsWritten < len(slices):
							data[rowsWritten].append(0)
							colors[rowsWritten].append("#000000")
							colsWritten += 1
						rowsWritten += 1
					
				if len(data) > 1:
					numResults += 1
					transposedData = map(lambda *row: [elem or 0 for elem in row], *data)
					transposedColors = map(lambda *row: [elem or 0 for elem in row], *colors)
					graphSliceValuesMatrix(slices, rowLabels, transposedData, transposedColors, cross, "", cross, path)
	print numResults
					
def posNegNormalColor(value, normal):
	if value < 0:
		if normal:
			return "#FF0000"
		else:
			return "#FFCCCC" 
	else:
		if normal:
			return "#31B94D" 
		else:
			return"#C5E3BF"
		
def correlationForStoriesAndTwoScaleQuestionIDs(selectedStories, firstID, secondID, rThreshold=0.3):
	xValues = []
	yValues = []
	lowerLimitValueNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	for story in selectedStories:
		xy = story.gatherScaleValuesForListOfIDs([firstID, secondID])
		if xy:
			xValues.append(int(xy[0]))
			yValues.append(int(xy[1]))
	if len(xValues) >= lowerLimitValueNumber and len(yValues) >= lowerLimitValueNumber:
		normal, r, rp = correlationStatsForTwoScales(xValues, yValues, roundValues=False)
		if rp <= 0.05 and abs(r) >= rThreshold:
			return (r, normal)
		else:
			return (None, None)
	else:
		return (None, None)
	
def graphOneCorrelationGridForSlices(questions, stories, columns):
	
	scaleQuestions = gatherScaleQuestions(questions)
	lowerLimitStoryNumber = LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	path = createPathIfNonexistent(createPathIfNonexistent(OUTPUT_PATH + "slices" + os.sep) + "correlations" + os.sep)

	correlations = {}
	slices = []
	for columnID in columns:
		for columnAnswer in columns[columnID]:
			slice = "%s: %s" % (columnID, columnAnswer)
			slices.append(slice)
			storiesInThisSlice = []
			for story in stories:
				if (columnID == "All" or story.gatherFirstAnswerForQuestionID(columnID) == columnAnswer):
					storiesInThisSlice.append(story)
			for i in range(len(scaleQuestions)):
				for j in range(len(scaleQuestions)):
					if i < j:
						cross = "%s x %s" % (scaleQuestions[i].shortName, scaleQuestions[j].shortName)
						print slice, cross
						r, normal = correlationForStoriesAndTwoScaleQuestionIDs(storiesInThisSlice, 
										scaleQuestions[i].id, scaleQuestions[j].id, rThreshold=0.2)
						if not correlations.has_key(cross):
							correlations[cross] = {}
						if r:
							correlations[cross][slice] = (round(r, 2), posNegNormalColor(r, normal))
						else:
							correlations[cross][slice] = (None, None)

	slices.sort()
	sortedCrosses = []
	sortedCrosses.extend(correlations.keys())
	sortedCrosses.sort()
	
	data = []
	colors = []
	
	rowsWritten = 0
	rowLabels = []
	for cross in sortedCrosses:
		rowHasData = False
		for slice in slices:
			if correlations[cross].has_key(slice):
				r, color = correlations[cross][slice]
			else:
				r = None
			if r:
				rowHasData = True
				break
		if rowHasData:
			rowLabels.append(cross)
			data.append([])
			colors.append([])
			colsWritten = 0
			for slice in slices:
				if correlations[cross].has_key(slice):
					r, color = correlations[cross][slice]
				else:
					r = 0
					color = "#000000"
				data[rowsWritten].append(r)
				colors[rowsWritten].append(color)
				colsWritten += 1
			while colsWritten < len(slices):
				data[rowsWritten].append(0)
				colors[rowsWritten].append(0)
				colsWritten += 1
			rowsWritten += 1
			
	transposedData = map(lambda *row: [elem or 0 for elem in row], *data)
	transposedColors = map(lambda *row: [elem or 0 for elem in row], *colors)
	name = "All correlations"
	graphSliceValuesMatrix(slices, rowLabels, transposedData, transposedColors, name, "", name, path)
					

