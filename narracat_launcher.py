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

class TxtboxOut(object):
	def __init__(self, tkintertxt):
		self.T = tkintertxt
 
	def write(self, txt):
		self.T.insert(END, "%s" % str(txt))
		self.T.yview(MOVETO, 1.0)

class NarracatLauncher(Frame):

	def __init__(self, master=None, questions=None, respondents=None, stories=None):
		Frame.__init__(self, master)
		self.questions = questions
		self.respondents = respondents
		self.stories = stories
		
		# custom
		#mergeDataFiles_2()
		#graphNetworkNodeDiagram(DATA_PATH + "archetypes.csv", "test", "test", OUTPUT_PATH)
		
		self.BUTTON_FUNCTION_MAP = [
			["Overall", "LABEL"],
			["Data integrity check", self.dataIntegrityCheck],
			["Data output", self.dataOutput],
			["Choices", "LABEL"],
			["Choice graphs", self.choiceGraphs],
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
			["Stability landscapes", "LABEL"],
			["Stability landscapes", self.stabilityLandscapes],
			["Stability landscapes by choice", self.stabilityLandscapesByChoice],
			["Cluster analysis", "LABEL"],
			["K-means (3 clusters)", self.clusterAnalysis_KMeans_3Clusters],
			["K-means (4 clusters)", self.clusterAnalysis_KMeans_4Clusters],
			["K-means (5 clusters)", self.clusterAnalysis_KMeans_5Clusters],
			["Agglomerative (best number of clusters)", self.clusterAnalysis_Agglomerative],
			["Slices", "LABEL"],
			["Slice graphs", self.sliceGraphs],
			["Ternary sets", "LABEL"],
			["Ternary set data integrity check", self.dataIntegrityCheckForTernarySets],
			["Ternary set graphs", self.ternarySetGraphs],
			["Ternary set graphs by choice", self.ternarySetGraphsByChoice],
			["Ternary set by ternary set graphs", self.ternarySetByTernarySetGraphs],
			["Ternary set by ternary set graphs by choice", self.ternarySetByTernarySetGraphsByChoice],
			["Ternary set with scale graphs", self.ternarySetByScaleGraphs],
			["Ternary set with scale graphs by choice", self.ternarySetByScalesGraphsByChoice],
			["  ", "LABEL"]]
		
		self.BUTTON_FUNCTION_MAP_WITHOUT_LABELS = []
		for name, function in self.BUTTON_FUNCTION_MAP:
			if function != "LABEL":
				self.BUTTON_FUNCTION_MAP_WITHOUT_LABELS.append([name, function])
		
		self.pack(fill=BOTH, expand=YES)
		self.buildWindow()
		
	def buildWindow(self):
		operationsFrame = Frame(self, relief=SUNKEN, borderwidth=3)
		operationsFrame.pack(side=LEFT, fill=BOTH)
		
		littleFont = tkFont.Font(family="Helvetica", size=12)
		
		label = Label(operationsFrame, foreground='blue', text="File loaded", font=littleFont)
		label.pack(side=TOP, anchor=W)
		self.currentFileName = Text(operationsFrame, width=30, height=3, relief=SUNKEN, borderwidth=1, font=littleFont)
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

		label = Label(operationsFrame, foreground='blue', text="Console", font=littleFont)
		label.pack(side=TOP, anchor=W)

		self.console = Text(operationsFrame, width=30, height=10, relief=SUNKEN, borderwidth=1, font=littleFont)
		self.console.pack(side=TOP, fill=BOTH)
		newout = TxtboxOut(self.console)
		console = sys.stdout
		sys.stdout = newout			
				
		browserFrame = Frame(self, relief=SUNKEN, borderwidth=3)
		browserFrame.pack(side=RIGHT, fill=BOTH)
		self.browser = NarracatBrowser(master=browserFrame, questions=self.questions, respondents=self.respondents, stories=self.stories)
		
	def doOperations(self):
		commandsToDo = []
		i = 0
		for state in self.checkBoxStates:
			if state.get():
				commandsToDo.append(self.BUTTON_FUNCTION_MAP_WITHOUT_LABELS[i])
			i += 1
		for name, function in commandsToDo:
			print '-------------------------------------- calling', name
			function()
			
	def loadFile(self):
		self.questions, self.respondents, self.stories = readData(DATA_PATH + PICKLE_FILE_NAME, 
				DATA_FILE_PATH, LABELS_FILE_PATH, forceReread=self.readCSVCheckBoxState.get())
		self.browser.questions = self.questions
		self.browser.respondents = self.respondents
		self.browser.stories = self.stories
		
		self.currentFileName.delete('0.0', END)
		self.currentFileName.insert(END, "  " + DATA_PATH + PICKLE_FILE_NAME)
		self.browser.initializeQABox()

	# OVERALL
	
	def dataIntegrityCheck(self):
		if not self.questions and self.respondents and self.stories:
			return
		printDataToCheckItWasReadRight(self.questions, self.stories, self.respondents)
		for slice in SLICES:
			graphOneGiantHistogramOfAllScaleValues(self.questions, self.stories, slice=slice)
			graphMeanAndSDAmongScaleValuesPerRespondent(self.questions, self.respondents, slice=slice)
			graphBarChartOfExtremeAndNAProportionsPerScale(self.questions, self.stories, slice=slice)
			graphBarChartOfNAProportionsPerChoiceQuestion(self.questions, self.stories, slice=slice)
		if DATA_HAS_TERNARY_SETS:
			for slice in SLICES:
				graphOneGiantTernaryPlotOfAllTernarySetValues(self.questions, self.stories, slice=slice)
				
		# custom
		#printResultForSpecificQuestionID(self.questions, self.stories, "Come from")
		#printNamesOfStoriesWithNoArchetypeData(self.stories, self.questions)
		print 'dataIntegrityCheck DONE'
				
	def dataOutput(self):
		if not self.questions and self.respondents and self.stories:
			return
		writeSimplifiedDataToCSV(self.questions, self.stories)
		writeStoriesToTextFile(self.questions, self.stories)
		writeOtherResponsesToQuestions(self.questions, self.stories)
		writeInfoAboutPeopleAndNumberOfStoriesTold(self.questions, self.stories, self.respondents)
		print 'dataOutput DONE'
	
	# CHOICES
	
	def choiceGraphs(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphBarChartsOfAnswerCountsPerQuestion(self.questions, self.stories, slice=slice)
		print 'choiceGraphs DONE'
	
	def answerContingencies(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphBarChartOfAnswerCombinationCounts(self.questions, self.stories) 
			graphAnswerContingencies(self.questions, self.stories, slice=slice)
		print 'answerContingencies DONE'
	
	# SCALES
	
	def scaleHistograms(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphScaleHistograms(self.questions, self.stories, inOwnDirectory=False, slice=slice)
		print 'scaleHistograms DONE'
	
	# SCALES WITH CHOICES
	
	def tTests(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			doTTestsToCompareScaleValuesWithQuestionAnswers(self.questions, self.stories, slice=slice, byQuestion=False)
		print 'tTests DONE'
	
	def skewDifferences(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			compareSkewInScaleValuesWithQuestionAnswers(self.questions, self.stories, slice=slice, byQuestion=False)
		print 'skewDifferences DONE'
	
	def scaleHistogramsByChoice(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphScaleHistogramsPerQuestionAnswer(self.questions, self.stories, slice=slice)
		print 'scaleHistogramsByChoice DONE'
	
	# SCALES WITH SCALES
	
	def correlationMatrix(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphScaleCorrelationMatrix(self.questions, self.stories, slice=slice)
		print 'correlationMatrix DONE'
	
	def scatterGraphs(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphScaleScattergrams(self.questions, self.stories, slice=slice, separateDirectories=False)
		print 'scatterGraphs DONE'
	
	# SCALES WITH SCALES AND CHOICES
	
	def correlationMatricesByChoice(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphScaleCorrelationMatrixForQuestionAnswers(self.questions, self.stories, slice=slice)
			writeCorrelationsToCSVForQuestionAnswers(self.questions, self.stories, slice=slice)
		print 'correlationMatricesByChoice DONE'
	
	def scatterGraphsByChoice(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphScaleScattergramsForQuestionAnswers(self.questions, self.stories, slice=slice)
		print 'scatterGraphsByChoice DONE'
	
	# STABILITY
	
	def stabilityLandscapes(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphScaleContourGraphsAgainstStability(self.questions, self.stories, STABILITY_QUESTION_NAME, separateDirectories=False, slice=slice)
		print 'stabilityLandscapes DONE'
	
	def stabilityLandscapesByChoice(self):
		if not self.questions and self.respondents and self.stories:
			return
		for slice in SLICES:
			graphScaleContourGraphsAgainstStabilityForQuestionAnswers(self.questions, self.stories, STABILITY_QUESTION_NAME, slice=slice)
		print 'stabilityLandscapesByChoice DONE'

	# SLICES
	
	def sliceGraphs(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not DATA_HAS_SLICES:
			print "no slices set up in data"
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
		print 'sliceGraphs DONE'
	
	# TERNARY SETS
	
	def dataIntegrityCheckForTernarySets(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "no ternary sets set up in data"
			return
		calculateThirdValueStrengthForTernaryAnswers(self.questions, self.stories)
		graphTernaryPlotValuesPerRespondent(self.questions, self.stories, self.respondents)
		print 'dataIntegrityCheckForTernarySets DONE'
	
	def ternarySetGraphs(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "no ternary sets set up in data"
			return
		graphTernaryPlots(self.questions, self.stories, separateDirectories=False)
		print 'ternarySetGraphs DONE'
		
	def ternarySetGraphsByChoice(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "no ternary sets set up in data"
			return
		graphTernaryPlotsForQuestionAnswers(self.questions, self.stories)
		compareTernaryMeansForScaleValuesWithQuestionAnswers(self.questions, self.stories, byQuestion=False)
		print 'ternarySetGraphsByChoice DONE'
	
	def ternarySetByTernarySetGraphs(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "no ternary sets set up in data"
			return
		graphDifferencesBetweenTernaryPlots(self.questions, self.stories, separateDirectories=False)
		print 'ternarySetByTernarySetGraphs DONE'
	
	def ternarySetByTernarySetGraphsByChoice(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "no ternary sets set up in data"
			return
		graphTernaryPlotDifferencesForQuestionAnswers(self.questions, self.stories)
		print 'ternarySetByTernarySetGraphsByChoice DONE'
	
	def ternarySetByScaleGraphs(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "no ternary sets set up in data"
			return
		graphTernaryPlotsAgainstScales(self.questions, self.stories, separateDirectories=False)
		print 'ternarySetByScaleGraphs DONE'
	
	def ternarySetByScalesGraphsByChoice(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not DATA_HAS_TERNARY_SETS:
			print "no ternary sets set up in data"
			return
		graphTernaryPlotsAgainstScalesForQuestionAnswers(self.questions, self.stories)
		print 'ternarySetByScalesGraphsByChoice DONE'
	
	# CLUSTERS
	
	def clusterAnalysis_KMeans_3Clusters(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not self.checkIfWeCanDoClusterAnalysis(slice):
			return
		self.clusterAnalysis(method="k-means", k=3)
		
	def clusterAnalysis_KMeans_4Clusters(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not self.checkIfWeCanDoClusterAnalysis(slice):
			return
		self.clusterAnalysis(method="k-means", k=4)
		
	def clusterAnalysis_KMeans_5Clusters(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not self.checkIfWeCanDoClusterAnalysis(slice):
			return
		self.clusterAnalysis(method="k-means", k=5)
		
	def clusterAnalysis_Agglomerative(self):
		if not self.questions and self.respondents and self.stories:
			return
		if not self.checkIfWeCanDoClusterAnalysis(slice):
			return
		self.clusterAnalysis(method="agglomerative")

	def clusterAnalysis(self, method, k=3):
		# k-means
		if method == "k-means":
			for slice in SLICES:
				# to include only SOME questions, change the second self.questions here
				calculateClusterMembershipsAndWriteToFile(self.questions, self.questions, self.respondents, method=method, slice=slice, k=k)
				printCountsOfClusterRespondents(self.questions, self.respondents, method=method, slice=slice, k=k)
				graphClusterMeansAndHistograms(self.questions, self.respondents, method=method, slice=slice, k=k)
				graphClusterAnswerCounts(self.questions, self.respondents, method=method, slice=slice, k=k)
				graphClusterScatterGraphs(self.questions, self.respondents, method=method, slice=slice, k=k)
				graphClusterContours(self.questions, self.respondents, method=method, slice=slice, k=k)
		elif method == "agglomerative":
			for slice in SLICES:
				# to include only SOME questions, change the second self.questions here
				calculateClusterMembershipsAndWriteToFile(self.questions, self.questions, self.respondents, method=method, slice=slice)
				graphClusterMeansAndHistograms(self.questions, self.respondents, method=method, slice=slice)
				graphClusterAnswerCounts(self.questions, self.respondents, method=method, slice=slice)
				graphClusterScatterGraphs(self.questions, self.respondents, method=method, slice=slice)
		print 'clusterAnalysis DONE'
		
	def checkIfWeCanDoClusterAnalysis(self, slice):
		# the cluster analysis methods cannot deal with situations where there are not the same number of values per respondent
		# so if there are, we will just use the first X number of values, where X is the largest number EVERY respondent has
		scaleValuesByRespondent = gatherScaleValuesByRespondent(self.questions, self.respondents, slice=slice)
		minNumValuesPerRespondent = 100000
		maxNumValuesPerRespondent = 0
		for respondentValueSet in scaleValuesByRespondent:
			if len(respondentValueSet) < minNumValuesPerRespondent:
				minNumValuesPerRespondent = len(respondentValueSet)
			if len(respondentValueSet) > maxNumValuesPerRespondent:
				maxNumValuesPerRespondent = len(respondentValueSet)
				
		if minNumValuesPerRespondent != maxNumValuesPerRespondent:
			print 'cluster analysis requires all respondents to have the same number of scale values.'
			return False
		else:
			return True
	