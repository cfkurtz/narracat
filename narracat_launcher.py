# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Launcher window - main interface window, calls and includes browser frame
# -----------------------------------------------------------------------------------------------------------------

from narracat_constants import *
from narracat_utils import *
from narracat_stats import *
from narracat_compile import *
from narracat_slice import *
from narracat_data import *
from narracat_browser import *
from narracat_network import *
from narracat_merge import *
from narracat_ternary import *
from narracat_cluster import *
from narracat_testing import *

class NarracatLauncher(Frame):

	def __init__(self, master=None, questions=None, participants=None, stories=None):
		Frame.__init__(self, master)
		self.questions = questions
		self.participants = participants
		self.stories = stories
		
		# custom
		#mergeDataFiles_2()
		#graphNetworkNodeDiagram(DATA_PATH + "archetypes.csv", "test", "test", OUTPUT_PATH)
		
		self.BUTTON_FUNCTION_MAP = [
			["Data integrity", "LABEL"],
			["Print data as read", self.dataIntegrityCheck_Printouts],
			["Answer summaries", self.dataIntegrityCheck_Values],
			["Participant summaries", self.dataIntegrityCheck_Participants],
			["Output stories and metadata", self.dataOutput],
			["Choices", "LABEL"],
			["Choice graphs", self.choiceGraphs],
			["Chi squared tests", self.chiSquaredContingencies],
			["Answer contingencies", self.answerContingencies],
			["Scales", "LABEL"],
			["Scale histograms", self.scaleHistograms],
			["Scales + choices", "LABEL"],
			["T tests", self.tTests],
			["Skew differences", self.skewDifferences],
			["Scale histograms by choice", self.scaleHistogramsByChoice],
			["Scales with scales", "LABEL"],
			["Correlation matrix", self.correlationMatrix],
			["Scatter graphs", self.scatterGraphs],
			["Scales x scales + choices", "LABEL"],
			["Correlation matrices by choice", self.correlationMatricesByChoice],
			["Scatter graphs by choice", self.scatterGraphsByChoice],
			]
		
		if STABILITY_QUESTION_NAME:
			stabilityOptions = [
				["Stability landscapes", "LABEL"],
				["Stability landscapes", self.stabilityLandscapes],
				["Stability landscapes by choice", self.stabilityLandscapesByChoice],
				]
			for option in stabilityOptions:
				self.BUTTON_FUNCTION_MAP.append(option)
		
		if SHOW_CLUSTER_ANALYSIS_OPTIONS:
			clusterOptions = [ 
				["Cluster analysis", "LABEL"],
				["K-means (3 clusters)", self.clusterAnalysis_KMeans_3Clusters],
				["K-means (4 clusters)", self.clusterAnalysis_KMeans_4Clusters],
				["K-means (5 clusters)", self.clusterAnalysis_KMeans_5Clusters],
				["Agglomerative (best number of clusters)", self.clusterAnalysis_Agglomerative],
				]
			for option in clusterOptions:
				self.BUTTON_FUNCTION_MAP.append(option)
		
		if DATA_HAS_SLICES:
			slicesOptions = [
				["Slices", "LABEL"],
				["Slice graphs", self.sliceGraphs],
				]
			for option in slicesOptions:
				self.BUTTON_FUNCTION_MAP.append(option)
		
		if DATA_HAS_TERNARY_SETS:
			ternaryOptions = [
				["Ternary sets", "LABEL"],
				["Ternary set data integrity check", self.dataIntegrityCheckForTernarySets],
				["Ternary set graphs", self.ternarySetGraphs],
				["Ternary set graphs by choice", self.ternarySetGraphsByChoice],
				["Ternary set by ternary set graphs", self.ternarySetByTernarySetGraphs],
				["Ternary set by ternary set graphs by choice", self.ternarySetByTernarySetGraphsByChoice],
				["Ternary set with scale graphs", self.ternarySetByScaleGraphs],
				["Ternary set with scale graphs by choice", self.ternarySetByScalesGraphsByChoice],
				]
			for option in ternaryOptions:
				self.BUTTON_FUNCTION_MAP.append(option)
				
		self.BUTTON_FUNCTION_MAP.append(["Testing", "LABEL"])
		self.BUTTON_FUNCTION_MAP.append(["Regression testing", self.testingGraphs])
				
		self.BUTTON_FUNCTION_MAP.append(["  ", "LABEL"])
		
		self.BUTTON_FUNCTION_MAP_WITHOUT_LABELS = []
		for name, function in self.BUTTON_FUNCTION_MAP:
			if function != "LABEL":
				self.BUTTON_FUNCTION_MAP_WITHOUT_LABELS.append([name, function])
		
		self.pack(fill=BOTH, expand=YES)
		self.buildWindow()
		
	def buildWindow(self):
		# on left, things to do
		operationsFrame = Frame(self, relief=SUNKEN, borderwidth=2)
		operationsFrame.pack(side=LEFT, fill=BOTH)
		littleFont = tkFont.Font(family="Helvetica", size=12)
		
		# file loaded
		label = Label(operationsFrame, foreground='blue', text="Data file", font=littleFont)
		label.pack(side=TOP, anchor=W)
		self.currentFileName = Text(operationsFrame, width=30, height=4, relief=SUNKEN, borderwidth=2, font=littleFont)
		self.currentFileName.pack(side=TOP, fill=BOTH)

		self.readCSVCheckBoxState = IntVar()
		readCSVCheckBox = Checkbutton(operationsFrame, variable=self.readCSVCheckBoxState, text="  Read from CSV", font=littleFont)
		readCSVCheckBox.pack(side=TOP, anchor=W)
		self.loadFileButton = Button(operationsFrame)
		self.loadFileButton["text"] = "  Load Data  "
		self.loadFileButton["command"] = self.loadFile
		self.loadFileButton.pack(side=TOP)

		label = Label(operationsFrame, foreground='blue', text="Operations", font=littleFont)
		label.pack(side=TOP, anchor=W)

		self.checkBoxStates = []
		for name, function in self.BUTTON_FUNCTION_MAP:
			if function == "LABEL":
				label = Label(operationsFrame, text=name, font=littleFont)
				label.pack(side=TOP, anchor=W)
			else:
				checkBoxState = IntVar()
				checkBox = Checkbutton(operationsFrame, variable=checkBoxState, text="  " + name, font=littleFont)
				checkBox.pack(side=TOP, anchor=W)
				self.checkBoxStates.append(checkBoxState)
		
		self.doOperationsButton = Button(operationsFrame)
		self.doOperationsButton["text"] = "  Perform Selected Operations   "
		self.doOperationsButton["command"] = self.doOperations
		self.doOperationsButton.pack(side=TOP)

		self.doOperationsButton = Button(operationsFrame)
		self.doOperationsButton["text"] = "  Uncheck All   "
		self.doOperationsButton["command"] = self.uncheckAll
		self.doOperationsButton.pack(side=TOP)

		Label(operationsFrame, text="   ").pack(side=TOP, anchor=W) # spacer so quit button stands out
		self.quitButton = Button(operationsFrame)
		self.quitButton["text"] = "  Quit   "
		self.quitButton["command"] = self.quit
		self.quitButton.pack(side=TOP)
		
		browserFrame = Frame(self, relief=SUNKEN, borderwidth=2)
		browserFrame.pack(side=RIGHT, fill=BOTH)
		self.browser = NarracatBrowser(master=browserFrame, questions=self.questions, participants=self.participants, stories=self.stories)
		
	def quit(self):
		sys.exit(0)
	
	def doOperations(self):
		commandsToDo = []
		i = 0
		for state in self.checkBoxStates:
			if state.get():
				commandsToDo.append(self.BUTTON_FUNCTION_MAP_WITHOUT_LABELS[i])
			i += 1
		for name, function in commandsToDo:
			print '\nPERFORMING OPERATION:\n   %s\n' % name
			function()
			
	def uncheckAll(self):
		for state in self.checkBoxStates:
			state.set(False)
			
	def loadFile(self):
		forceReread = self.readCSVCheckBoxState.get()
		if HAS_MULTIPLE_DATA_FILES:
			fileNamesWithPath = []
			for fileName in MULTIPLE_DATA_FILE_NAMES:
				fileNamesWithPath.append(DATA_PATH + fileName)
		else:
			fileNamesWithPath = None
		self.questions, self.participants, self.stories = readData(DATA_PATH + PICKLE_FILE_NAME, 
				DATA_FILE_PATH, LABELS_FILE_PATH, HAS_MULTIPLE_DATA_FILES, fileNamesWithPath, forceReread=forceReread)
		self.browser.questions = self.questions
		self.browser.participants = self.participants
		self.browser.stories = self.stories
		createPathIfNonexistent(OUTPUT_PATH)
		
		self.currentFileName.delete('0.0', END)
		self.currentFileName.insert(END, "  " + DATA_PATH + PICKLE_FILE_NAME)
		self.browser.initializeQABox()

	# OVERALL
	
	def dataIntegrityCheck_Printouts(self):
		if not self.questions and self.participants and self.stories:
			return
		printQuestionsToCheckTheyWereReadRight(self.questions)
		printStoriesToCheckTheyWereReadRight(self.questions, self.stories)
		printParticipantsToCheckTheyWereReadRight(self.questions, self.participants)
		printNumberOfResponsesToEachQuestion(self.questions, self.stories)
		printNumberOfResponsesForEachStory(self.questions, self.stories)
		print '\n data integrity check (printouts) DONE'
	
	def dataIntegrityCheck_Values(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphOneGiantHistogramOfAllScaleValues(self.questions, self.stories, slice=slice)
			graphBarChartOfExtremeAndNAProportionsPerScale(self.questions, self.stories, slice=slice)
			graphBarChartOfNAProportionsPerChoiceQuestion(self.questions, self.stories, slice=slice)
		# custom
		#printResultForSpecificQuestionID(self.questions, self.stories, "Come from")
		#printNamesOfStoriesWithNoArchetypeData(self.stories, self.questions)
		print '\n data integrity check (values) DONE'
				
	def dataIntegrityCheck_Participants(self):
		if not self.questions and self.participants and self.stories:
			return
		graphMeanAndSDAmongScaleValuesPerParticipant(self.questions, self.participants)
		graphAllScaleValuesPerParticipant(self.questions, self.participants) 
		graphHowManyScaleValuesWereEnteredPerParticipant(self.questions, self.participants) 
		print '\n data integrity check (participants) DONE'
				
	def dataOutput(self):
		if not self.questions and self.participants and self.stories:
			return
		writeSimplifiedDataToCSV(self.questions, self.stories)
		writeStoriesToTextFile(self.questions, self.stories, includeMetadata=False)
		writeStoriesToTextFile(self.questions, self.stories, includeMetadata=True)
		writeOtherResponsesToQuestions(self.questions, self.stories)
		writeEmptyThemesFile(self.stories)
		writeInfoAboutPeopleAndNumberOfStoriesTold(self.questions, self.stories, self.participants)
		print '\n data output DONE'
	
	# CHOICES
	
	def choiceGraphs(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphBarChartsOfAnswerCountsPerQuestion(self.questions, self.stories, slice=slice)
		print '\n choice graphs DONE'
	
	def answerContingencies(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphBarChartOfAnswerCombinationCounts(self.questions, self.stories) 
			graphAnswerContingencies(self.questions, self.stories, slice=slice)
		print '\n answer contingencies DONE'
		
	def chiSquaredContingencies(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphAnswerContingencies(self.questions, self.stories, slice=slice, chiSquared=True)
		print '\n chi squared tests DONE'
	
	# SCALES
	
	def scaleHistograms(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphScaleHistograms(self.questions, self.stories, inOwnDirectory=False, slice=slice)
		print '\n scale histograms DONE'
	
	# SCALES WITH CHOICES
	
	def tTests(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			doTTestsToCompareScaleValuesWithQuestionAnswers(self.questions, self.stories, slice=slice, byQuestion=False)
		print '\n t-tests DONE'
	
	def skewDifferences(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			compareSkewInScaleValuesWithQuestionAnswers(self.questions, self.stories, slice=slice, byQuestion=False)
		print '\n skew differences DONE'
	
	def scaleHistogramsByChoice(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphScaleHistogramsPerQuestionAnswer(self.questions, self.stories, slice=slice)
		print '\n scale histograms by choice DONE'
	
	# SCALES WITH SCALES
	
	def correlationMatrix(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphScaleCorrelationMatrix(self.questions, self.stories, slice=slice)
		print '\n correlation matrix DONE'
	
	def scatterGraphs(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphScaleScattergrams(self.questions, self.stories, slice=slice, separateDirectories=False)
		print '\n scatter graphs DONE'
	
	# SCALES WITH SCALES AND CHOICES
	
	def correlationMatricesByChoice(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphScaleCorrelationMatrixForQuestionAnswers(self.questions, self.stories, slice=slice)
			writeCorrelationsToCSVForQuestionAnswers(self.questions, self.stories, slice=slice)
		print '\n correlation matrices by choice DONE'
	
	def scatterGraphsByChoice(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphScaleScattergramsForQuestionAnswers(self.questions, self.stories, slice=slice)
		print '\n scatter graphs by choice DONE'
	
	# STABILITY
	
	def stabilityLandscapes(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphScaleContourGraphsAgainstStability(self.questions, self.stories, STABILITY_QUESTION_NAME, separateDirectories=False, slice=slice)
		print '\n stability landscapes DONE'
	
	def stabilityLandscapesByChoice(self):
		if not self.questions and self.participants and self.stories:
			return
		for slice in SLICES:
			graphScaleContourGraphsAgainstStabilityForQuestionAnswers(self.questions, self.stories, STABILITY_QUESTION_NAME, slice=slice)
		print '\n stability landscapes by choice DONE'

	# SLICES
	
	def sliceGraphs(self):
		if not self.questions and self.participants and self.stories:
			return
		if not DATA_HAS_SLICES:
			print "\n no slices set up in data"
			return

		columns = {}
		columns[SLICE_QUESTION_ID] = []
		for slice in SLICES_TO_CREATE:
			columns[SLICE_QUESTION_ID].append(slice)
		columns[ALL_DATA_SLICE] = [ALL_DATA_SLICE]
				
		# questions alone
		graphAnswerCountsForSlices(self.questions, self.stories, columns)
		graphAnswerContingenciesForSlices(self.questions, self.stories, columns)
		
		# scales alone
		graphOneScaleStatsForSlices(self.questions, self.stories, columns)
		graphScaleMeansAndStdDevsForSlices(self.questions, self.stories, columns)
		graphScaleNAsForSlices(self.questions, self.stories, columns)
		graphOneCorrelationGridForSlices(self.questions, self.stories, columns)
		graphCorrelationValuesForSlices(self.questions, self.stories, columns)
		
		# scales with questions
		graphTTestValuesForSlices(self.questions, self.stories, columns)
		print '\n slice graphs DONE'
	
	# TERNARY SETS
	
	def dataIntegrityCheckForTernarySets(self):
		if not self.questions and self.participants and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "\n no ternary sets set up in data"
			return
		for slice in SLICES:
			graphOneGiantTernaryPlotOfAllTernarySetValues(self.questions, self.stories, slice=slice)
		calculateThirdValueStrengthForTernaryAnswers(self.questions, self.stories)
		graphTernaryPlotValuesPerParticipant(self.questions, self.stories, self.participants)
		print '\n data integrity check for ternary sets DONE'
	
	def ternarySetGraphs(self):
		if not self.questions and self.participants and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "\n no ternary sets set up in data"
			return
		graphTernaryPlots(self.questions, self.stories, separateDirectories=False)
		print '\n ternary set graphs DONE'
		
	def ternarySetGraphsByChoice(self):
		if not self.questions and self.participants and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "\n no ternary sets set up in data"
			return
		graphTernaryPlotsForQuestionAnswers(self.questions, self.stories)
		compareTernaryMeansForScaleValuesWithQuestionAnswers(self.questions, self.stories, byQuestion=False)
		print '\n ternary set graphs by choice DONE'
	
	def ternarySetByTernarySetGraphs(self):
		if not self.questions and self.participants and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "\n no ternary sets set up in data"
			return
		graphDifferencesBetweenTernaryPlots(self.questions, self.stories, separateDirectories=False)
		print '\n ternary set by ternary set graphs DONE'
	
	def ternarySetByTernarySetGraphsByChoice(self):
		if not self.questions and self.participants and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "\n no ternary sets set up in data"
			return
		graphTernaryPlotDifferencesForQuestionAnswers(self.questions, self.stories)
		print '\n ternary set by ternary set graphs by choice DONE'
	
	def ternarySetByScaleGraphs(self):
		if not self.questions and self.participants and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "\n no ternary sets set up in data"
			return
		graphTernaryPlotsAgainstScales(self.questions, self.stories, separateDirectories=False)
		print '\n ternary set by scale graphs DONE'
	
	def ternarySetByScalesGraphsByChoice(self):
		if not self.questions and self.participants and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "\n no ternary sets set up in data"
			return
		graphTernaryPlotsAgainstScalesForQuestionAnswers(self.questions, self.stories)
		print '\n ternary set by scales graphs by choice DONE'
	
	# CLUSTERS
	
	def clusterAnalysis_KMeans_3Clusters(self):
		if not self.questions and self.participants and self.stories:
			return
		if not self.checkIfWeCanDoClusterAnalysis(slice):
			return
		self.clusterAnalysis(method="k-means", k=3)
		
	def clusterAnalysis_KMeans_4Clusters(self):
		if not self.questions and self.participants and self.stories:
			return
		if not self.checkIfWeCanDoClusterAnalysis(slice):
			return
		self.clusterAnalysis(method="k-means", k=4)
		
	def clusterAnalysis_KMeans_5Clusters(self):
		if not self.questions and self.participants and self.stories:
			return
		if not self.checkIfWeCanDoClusterAnalysis(slice):
			return
		self.clusterAnalysis(method="k-means", k=5)
		
	def clusterAnalysis_Agglomerative(self):
		if not self.questions and self.participants and self.stories:
			return
		if not self.checkIfWeCanDoClusterAnalysis(slice):
			return
		self.clusterAnalysis(method="agglomerative")

	def clusterAnalysis(self, method, k=3):
		# k-means
		if method == "k-means":
			for slice in SLICES:
				# to include only SOME questions, change the second self.questions here
				calculateClusterMembershipsAndWriteToFile(self.questions, self.questions, self.participants, method=method, slice=slice, k=k)
				printCountsOfClusterParticipants(self.questions, self.participants, method=method, slice=slice, k=k)
				graphClusterMeansAndHistograms(self.questions, self.participants, method=method, slice=slice, k=k)
				graphClusterAnswerCounts(self.questions, self.participants, method=method, slice=slice, k=k)
				graphClusterScatterGraphs(self.questions, self.participants, method=method, slice=slice, k=k)
				graphClusterContours(self.questions, self.participants, method=method, slice=slice, k=k)
		elif method == "agglomerative":
			for slice in SLICES:
				# to include only SOME questions, change the second self.questions here
				calculateClusterMembershipsAndWriteToFile(self.questions, self.questions, self.participants, method=method, slice=slice)
				graphClusterMeansAndHistograms(self.questions, self.participants, method=method, slice=slice)
				graphClusterAnswerCounts(self.questions, self.participants, method=method, slice=slice)
				graphClusterScatterGraphs(self.questions, self.participants, method=method, slice=slice)
		print '\n cluster analysis DONE'
		
	def checkIfWeCanDoClusterAnalysis(self, slice):
		# the cluster analysis methods cannot deal with situations where there are not the same number of values per participant
		# so if there are, we will just use the first X number of values, where X is the largest number EVERY participant has
		scaleValuesByParticipant = gatherScaleValuesByParticipant(self.questions, self.participants, slice=slice)
		minNumValuesPerParticipant = 100000
		maxNumValuesPerParticipant = 0
		for participantValueSet in scaleValuesByParticipant:
			if len(participantValueSet) < minNumValuesPerParticipant:
				minNumValuesPerParticipant = len(participantValueSet)
			if len(participantValueSet) > maxNumValuesPerParticipant:
				maxNumValuesPerParticipant = len(participantValueSet)
				
		if minNumValuesPerParticipant != maxNumValuesPerParticipant:
			print '\n cluster analysis requires all participants to have the same number of scale values.'
			return False
		else:
			return True
		
	# TESTING
	
	def testingGraphs(self):
		# normal, uniform distributions
		generateAndSaveNormalData()
		graphHistogramsOfNormalAndUniformTestData()
		# t tests
		generateAndSaveTTestData()
		graphHistogramsAndTTestResultsOfTTestData()
		print 'testing graphs DONE'
