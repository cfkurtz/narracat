# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Cluster analysis methods
# -----------------------------------------------------------------------------------------------------------------

from narracat_data import *
from narracat_graph import *

from scipy.cluster import vq
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist

# NOTE
# NOTE
# NOTE that this file has not been used recently and needs some extra watching over to be sure it is working correctly.
# NOTE
# NOTE

# -----------------------------------------------------------------------------------------------------------------
# cluster stats
# -----------------------------------------------------------------------------------------------------------------

def calculateClustersFromScaleValues(scaleValuesByParticipant, method="k-means", k=4):
	# http://en.wikipedia.org/wiki/Cluster_analysis
	
	npArrayOfObservations = np.array(scaleValuesByParticipant)
	
	if method == "k-means":
		# http://docs.scipy.org/doc/scipy/reference/cluster.vq.html
		# the k_or_guess parameter here has to be arrived at by experiment - usually one of 3, 4 or 5 is best
		# (choose which gives the best distinctions)
		whitenedObservations = vq.whiten(npArrayOfObservations)
		codebook, distortion = vq.kmeans(whitenedObservations, k_or_guess=k)
		codes, distortions = vq.vq(whitenedObservations, codebook)
		linkages = []
	else: # method = "agglomerative"
		# http://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
		# the t parameter here has to be arrived at by experiment
		# (choose which gives the best distinctions and reasonable number of clusters)
		distanceMatrix = pdist(npArrayOfObservations)
		linkages = hierarchy.linkage(distanceMatrix, method='complete')
		timesTried = 0
		maxCode = 100
		addition = 0
		increment = 0.01
		while ((maxCode > 5) or (maxCode < 2)) and timesTried < 1000:
			t = 1.15 + addition
			codes = hierarchy.fcluster(linkages, t=t)
			maxCode = 0
			for code in codes:
				if code > maxCode:
					maxCode = code
			if maxCode > 5:
				addition += increment
				increment *= 0.75
			elif maxCode < 2:
				addition -= increment
				increment *= 0.75
			timesTried += 1
			print "max code", maxCode, 't', t, 'addition', addition, 'increment', increment
		distortions = None
	return codes, linkages, distortions

# -----------------------------------------------------------------------------------------------------------------
# saving and reloading clustering results
# necessary because clusters are randomly assigned, thus different every time clustering is calculated
# -----------------------------------------------------------------------------------------------------------------

def calculateClusters(questions, participants, method, slice, k=4):
	scaleValuesByParticipant = gatherScaleValuesByParticipant(questions, participants, slice=slice)
	print "len(scaleValuesByParticipant)", len(scaleValuesByParticipant)
	codes, linkages, distortions = calculateClustersFromScaleValues(scaleValuesByParticipant, method, k=k) 
	maxCode = 0
	for code in codes:
		if code > maxCode:
			maxCode = code
	return codes, linkages, distortions, maxCode

def calculateClusterMembershipsAndWriteToFile(questions, scalesToConsider, participants, method="k-means", slice=ALL_DATA_SLICE, k=4):
	codes, linkages, distortions, maxCode = calculateClusters(scalesToConsider, participants, method, slice, k)
	
	membershipsFileName = membershipsFileNameForType(method, k, slice)
		
	# NOTE:
	# because this method sets up a cluster membership file for the other methods,
	# you should call it only ONCE per project - for each type of clustering - then NEVER AGAIN.
	# because of this the method will ONLY write the file if it doesn't exist already.
	# if you need to "reboot" the clustering by doing it all over again, DELETE the file.
	if os.path.exists(membershipsFileName):
		print 'not creating new cluster memberships file; exists already.'
	else:
		membershipsFile = open(membershipsFileName, 'w')
		try:
			membershipsFile.write(';Cluster memberships file: participant id and cluster code on each line\n')
			print len(participants), len(codes)
			i = 0
			for participant in participants:
				membershipsFile.write("%s,%s\n" % (participant.id, codes[i]))
				i += 1
		finally:
			membershipsFile.close()
	return membershipsFileName
		
def collectParticipantMembershipsFromStorageInFile(participants, method="k-means", slice=ALL_DATA_SLICE, k=4):
	participantIDs = {}
	for participant in participants:
		participantIDs[participant.id] = participant
		
	memberships = {}
	overallPath = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep)
	membershipsFileName = membershipsFileNameForType(method, k, slice)
	
	membershipsFile = open(membershipsFileName, "U")
	
	try:
		rows = csv.reader(membershipsFile)
		
		print 'rows', rows
		
		for row in rows:
			if row[0][0] == ";":
				continue
			participantID = row[0]
			if participantIDs.has_key(participantID):
				memberships[participantIDs[participantID]] = int(row[1])
	finally:
		membershipsFile.close()
	
	return memberships

def membershipsFileNameForType(method, k, slice):
	clustersPath = createPathIfNonexistent(OUTPUT_PATH + "clusters" + os.sep)
	if method == "k-means":
		membershipsFileName = clustersPath + "Cluster memberships for method %s k %s slice %s.csv" % (method, k, slice)
	else:
		membershipsFileName = clustersPath + "Cluster memberships for method %s slice %s.csv" % (method, slice)
	return membershipsFileName

def clustersSlicePath(method, slice, k=4):
	clustersPath = createPathIfNonexistent(OUTPUT_PATH + "clusters" + os.sep)
	clusterTypePath = createPathIfNonexistent(clustersPath + method + os.sep)
	if method == "k-means":
		kPath = createPathIfNonexistent(clusterTypePath + " %s clusters" % k + os.sep)
		slicePath = createPathIfNonexistent(kPath + slice + os.sep)
	else:
		slicePath = createPathIfNonexistent(clusterTypePath + slice + os.sep)
	return slicePath

# -----------------------------------------------------------------------------------------------------------------
# graphing results of clustering
# -----------------------------------------------------------------------------------------------------------------

def graphClusterMeansAndHistograms(questions, participants, method="k-means", slice=ALL_DATA_SLICE, k=4):
	print 'writing clusters %s %s ...'  % (method, slice)
	
	memberships = collectParticipantMembershipsFromStorageInFile(participants, method, slice, k)
	slicePath = clustersSlicePath(method, slice, k)
	
	overallPath = createPathIfNonexistent(OUTPUT_PATH + "overall" + os.sep)
	meanSDPath = createPathIfNonexistent(slicePath + "means and std devs" + os.sep)
	histByScalePath = createPathIfNonexistent(slicePath + "histograms by scale" + os.sep)
	histByClusterPath = createPathIfNonexistent(slicePath + "histograms by cluster" + os.sep)

	scaleQuestions = gatherScaleQuestions(questions)
	scaleValuesByCluster = {}
	i = 0
	for participant in participants:
		if memberships.has_key(participant):
			clusterIBelongIn = memberships[participant]
		else:
			continue
		if not scaleValuesByCluster.has_key(clusterIBelongIn):
			scaleValuesByCluster[clusterIBelongIn] = {}
		for scaleQuestion in scaleQuestions:
				if not scaleValuesByCluster[clusterIBelongIn].has_key(scaleQuestion.veryShortName()):
					scaleValuesByCluster[clusterIBelongIn][scaleQuestion.veryShortName()] = []
				for story in participant.stories:
					if story.matchesSlice(slice):
						values = story.gatherAnswersForQuestionID(scaleQuestion.id)
						if values:
							value = story.gatherAnswersForQuestionID(scaleQuestion.id)[0]
							if value and value != DOES_NOT_APPLY:
								scaleValuesByCluster[clusterIBelongIn][scaleQuestion.veryShortName()].append(int(value))
		i += 1
	
	graphsWritten = 0
	print '  ... writing means and std devs and histograms ... '
	for clusterNumber in scaleValuesByCluster:
		means = []
		stds = []
		labels = []
		if method == "k-means":
			numberToWrite = clusterNumber + 1
		else:
			numberToWrite = clusterNumber
		for scaleName in scaleValuesByCluster[clusterNumber]:
			name =  '%s %s' % (scaleName, numberToWrite)
			graphPNGHistogramWithStatsMarked(scaleValuesByCluster[clusterNumber][scaleName], name, name, histByScalePath)
			name =  '%s %s' % (numberToWrite, scaleName)
			graphPNGHistogramWithStatsMarked(scaleValuesByCluster[clusterNumber][scaleName], name, name, histByClusterPath)
			npArray = np.array(scaleValuesByCluster[clusterNumber][scaleName])
			mean = np.mean(npArray)
			std = np.std(npArray)
			means.append(mean)
			stds.append(std)
			labels.append(scaleName)
		graphName = "%s - means %s - cluster %s" % (method, slice, numberToWrite)
		graphPNGBarChart(means, labels, graphName, graphName, meanSDPath)
		graphName = "%s - std devs %s - cluster %s" % (method, slice, numberToWrite)
		graphPNGBarChart(stds, labels, graphName, graphName, meanSDPath)
		graphsWritten += 2
		if graphsWritten % 10 == 0:
			print '	... %s graphs written' % graphsWritten
	print '  done writing means and std devs and histograms. '

def graphClusterAnswerCounts(questions, participants, method="K-means", slice=ALL_DATA_SLICE, k=4):
	print 'writing %s %s clusters ...' % (method, slice)
	
	memberships = collectParticipantMembershipsFromStorageInFile(participants, method, slice, k)
	slicePath = clustersSlicePath(method, slice, k)
	
	scaleQuestions = gatherScaleQuestions(questions)
	answerCountsPath = createPathIfNonexistent(slicePath + "answer counts" + os.sep)

	print '  ... writing choice question counts for clusters ...'
	choiceCountsByCluster = {}
	i = 0
	for participant in participants:
		if memberships.has_key(participant):
			clusterIBelongIn = memberships[participant]
		else:
			continue
		if not choiceCountsByCluster.has_key(clusterIBelongIn):
			choiceCountsByCluster[clusterIBelongIn] = {}
		for choiceQuestion in questions:
			if choiceQuestion.isChoiceQuestion():
				if not choiceCountsByCluster[clusterIBelongIn].has_key(choiceQuestion.shortName):
					choiceCountsByCluster[clusterIBelongIn][choiceQuestion.shortName] = {}
				questionDict = choiceCountsByCluster[clusterIBelongIn][choiceQuestion.shortName]
				for answer in choiceQuestion.shortResponseNames:
					if not choiceCountsByCluster[clusterIBelongIn][choiceQuestion.shortName].has_key(answer):
						questionDict[answer] = 0
					for story in participant.stories:
						if story.matchesSlice(slice):
							if story.hasAnswerForQuestionID(answer, choiceQuestion.id):
								questionDict[answer] += 1
		i += 1
	graphsWritten = 0
	for clusterNumber in choiceCountsByCluster:
		questionDict = choiceCountsByCluster[clusterNumber]
		for questionKey in questionDict:
			data = []
			labels = []
			for answerKey in questionDict[questionKey]:
				data.append(questionDict[questionKey][answerKey])
				labels.append(answerKey)
			if method == "k-means":
				numberToWrite = clusterNumber + 1
			else:
				numberToWrite = clusterNumber
			graphName = "%s %s - cluster %s" % (questionKey, slice, numberToWrite)
			graphPNGBarChart(data, labels, graphName, graphName, answerCountsPath)
			graphsWritten += 1
			if graphsWritten % 10 == 0:
				print '	... %s graphs written' % graphsWritten

	print '  done writing %s %s clusters.'	% (method, slice)

def graphClusterScatterGraphs(questions, participants, method="K-means", slice=ALL_DATA_SLICE, k=4):
	print 'writing %s %s clusters ...' % (method, slice)

	memberships = collectParticipantMembershipsFromStorageInFile(participants, method, slice, k)
	maxCode = 0
	for code in memberships.values():
		if code > maxCode:
			maxCode = code
	slicePath = clustersSlicePath(method, slice, k)
	
	scaleQuestions = gatherScaleQuestions(questions)
	scatterGraphsPath = createPathIfNonexistent(slicePath + "scatter graphs" + os.sep)

	print '  ... writing scatter graphs ... '
	graphsWritten = 0
	for i in range(len(scaleQuestions)):
		for j in range(len(scaleQuestions)):
			if i < j:
				xValues = []
				yValues = []
				colorNames = []
				r = 0
				for participant in participants:
					if memberships.has_key(participant):
						clusterIBelongIn = memberships[participant]
					else:
						continue
					for story in participant.stories:
						if story.matchesSlice(slice):
							xy = story.gatherScaleValuesForListOfIDs([scaleQuestions[i].id, scaleQuestions[j].id])
							if xy:
								xValues.append(int(xy[0]))
								yValues.append(int(xy[1]))
								colorNames.append(colorNameForCluster(clusterIBelongIn, maxCode))
					r += 1
				combinedName = "%s X %s %s" % (scaleQuestions[i].veryShortName(), scaleQuestions[j].veryShortName(), slice)
				graphPNGScatterGraph(xValues, yValues, 
									scaleQuestions[i].shortName, scaleQuestions[j].shortName, 
									combinedName, combinedName, scatterGraphsPath,
									colors=colorNames, size=20)
				graphsWritten += 1
				if graphsWritten % 10 == 0:
					print '	... %s graphs written' % graphsWritten
	print '  done writing %s %s clusters.'	% (method, slice)

def colorNameForCluster(code, maxCode):
	# http://objectmix.com/python/352080-how-make-rainbow-rgb-values.html
	# "Consider using an HSV->RGB conversion function. Saturation (S) and value (V) 
	# should remain constant, while Hue (H) varies to get your rainbow effect."
	#proportion = (1.0 * code / maxCode) * 0.9 + 0.1
	#print code, maxCode, proportion
	#color = colorsys.hsv_to_rgb(proportion, 1.0, 1.0)
	# this works well for lots of clusters, but for few some fixed colors are better
	# i have here red, green, blue, then orange and aqua
	# if you need more than 5, add more to this list
	if code == 0:
		color = "#FF0000"
	elif code == 1:
		color = "#00FF00"
	elif code == 2:
		color = "#0000FF"
	elif code == 3:
		color = "#FFFF00"
	elif code == 4:
		color = "#00FFFF"
	else:
		raise "no color for code %s" % code
	return color

def graphClusterContours(questions, participants, method="K-means", slice=ALL_DATA_SLICE, k=4):
	print 'writing %s %s clusters ...' % (method, slice)

	memberships = collectParticipantMembershipsFromStorageInFile(participants, method, slice, k)
	maxCode = 0
	for code in memberships.values():
		if code > maxCode:
			maxCode = code
	print 'maxCode', maxCode
	slicePath = clustersSlicePath(method, slice, k)

	scaleQuestions = gatherScaleQuestions(questions, includeStability=False)
	contourGraphsPath = createPathIfNonexistent(slicePath + "contour graphs" + os.sep)

	print '  ... writing contour graphs ... '
	graphsWritten = 0
	for i in range(len(scaleQuestions)):
		for j in range(len(scaleQuestions)):
			if i < j:
				for clusterToGraph in range(maxCode+1):
					xValues = []
					yValues = []
					zValues = []
					participantIndex = 0
					for participant in participants:
						if memberships.has_key(participant):
							participantCluster = memberships[participant]
						else:
							continue
						if participantCluster == clusterToGraph:
							for story in participant.stories:
								if story.matchesSlice(slice):
									xy = story.gatherScaleValuesForListOfIDs([scaleQuestions[i].id, scaleQuestions[j].id])
									z = story.getStabilityValue(questions)
									if xy and z:
										xValues.append(int(xy[0]))
										yValues.append(int(xy[1]))
										zValues.append(z)
						participantIndex += 1
					if len(xValues):
						if method == "k-means":
							numberToWrite = clusterToGraph + 1
						else:
							numberToWrite = clusterToGraph
						combinedName = "%s X %s - %s %s k%s" % (scaleQuestions[i].veryShortName(), scaleQuestions[j].veryShortName(), numberToWrite, slice, k)
						graphPNGContourF(xValues, yValues, zValues, 
								scaleQuestions[i].shortName, scaleQuestions[j].shortName, combinedName, combinedName, contourGraphsPath, levels=100)
						graphsWritten += 1
						if graphsWritten % 10 == 0:
							print '	... %s graphs written' % graphsWritten
	print '  done writing %s %s clusters.'	% (method, slice)
	
def printCountsOfClusterParticipants(questions, participants, method="k-means", slice=ALL_DATA_SLICE, k=4):
	memberships = collectParticipantMembershipsFromStorageInFile(participants, method, slice, k)
	counts = {}
	for i in range(len(participants)):
		if memberships.has_key(participants[i]):
			participantCluster = memberships[participants[i]]
		else:
			continue
		if not counts.has_key(participantCluster):
			counts[participantCluster] = 0
		counts[participantCluster] += 1
	print 'participants per cluster for method %s, %s stories:'	% (method, slice)
	for key in counts:
		print '  cluster %s has %s participants' % ((key+1), counts[key])
	
# -----------------------------------------------------------------------------------------------------------------
# for finding out which variables produce the best clusters
# not often used
# -----------------------------------------------------------------------------------------------------------------

def graphSortedDistanceMeasuresForKMeansClusteringPairs(questions, participants, slice=ALL_DATA_SLICE):
	print 'comparing %s cluster distortions ...' % slice
	scaleQuestions = gatherScaleQuestions(questions)
	for k in [2,3,4,5,6,7,8]:
		sizes = []
		colors = []
		for i in range(len(scaleQuestions)):
			sizes.append([])
			colors.append([])
			for j in range(len(scaleQuestions)):
				scaleValuesByParticipant = gatherScaleValuesByParticipant([scaleQuestions[i], scaleQuestions[j]], participants, slice=slice)
				codes, linkages, distortions = calculateClustersFromScaleValues(scaleValuesByParticipant, "k-means", k)
				mean = np.mean(distortions)
				sizes[i].append((mean - 1.0) / 2.0)
				colors[i].append("#FF0000")
		labels = []
		for question in scaleQuestions:
			labels.append(question.veryShortName())
		graphName = "Mean cluster distortions for pairs of cluster dimensions - %s - k %s" % (slice, k)
		note = ""
		overallPath = OUTPUT_PATH + "overall" + os.sep 
		if not os.path.exists(overallPath):
			os.mkdir(overallPath)
		graphCircleMatrix(len(scaleQuestions), labels, sizes, colors, graphName, note, graphName, overallPath)
	print '  done comparing %s cluster distortions.' % slice

def printSortedDistanceMeasuresForKMeansClusteringTernarySets(questions, participants, slice=ALL_DATA_SLICE):
	print 'comparing %s cluster ternarySet distortions ...' % slice
	scaleQuestions = gatherScaleQuestions(questions)
	print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
	for k in [2,3,4,5,6]:
		print '-------------------'
		distortionStats = []
		for i in range(len(scaleQuestions)):
			for j in range(len(scaleQuestions)):
				for m in range(len(scaleQuestions)):
					if i != j and j != m and i != m:
						scaleValuesByParticipant = gatherScaleValuesByParticipant([scaleQuestions[i], scaleQuestions[j], scaleQuestions[m]], participants, slice=slice)
						codes, linkages, distortions = calculateClustersFromScaleValues(scaleValuesByParticipant, "k-means", k)
						mean = np.mean(distortions)
						std = np.std(distortions)
						min = np.min(distortions)
						max = np.max(distortions)
						name = "%s X %s X %s" % (scaleQuestions[i].veryShortName(), scaleQuestions[j].veryShortName(), scaleQuestions[m].veryShortName())
						distortionStats.append((name, mean, std, min, max))
		distortionStats.sort(lambda a,b: cmp(a[1], b[1]))
		for stat in distortionStats[0:18]:
			print "k %s %s - %s mean=%.3f std=%.3f min=%.3f max=%.3f" % (k, slice, stat[0], stat[1], stat[2], stat[3], stat[4])
	print '  done comparing %s cluster ternarySet distortions.' % slice

def printSortedDistanceMeasuresForKMeansClusteringQuads(questions, participants, slice=ALL_DATA_SLICE):
	print 'comparing %s cluster quad distortions ...' % slice
	scaleQuestions = gatherScaleQuestions(questions)
	print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
	for k in [2,3,4]:
		print '-------------------'
		distortionStats = []
		for i in range(len(scaleQuestions)):
			for j in range(len(scaleQuestions)):
				for m in range(len(scaleQuestions)):
					for n in range(len(scaleQuestions)):
						if i != j and j != m and i != m and i != n and j != n and m != n:
							scaleValuesByParticipant = gatherScaleValuesByParticipant([scaleQuestions[i], scaleQuestions[j], scaleQuestions[m], scaleQuestions[n]], participants, slice=slice)
							codes, linkages, distortions = calculateClustersFromScaleValues(scaleValuesByParticipant, "k-means", k)
							mean = np.mean(distortions)
							std = np.std(distortions)
							min = np.min(distortions)
							max = np.max(distortions)
							name = "%s X %s X %s X %s" % (scaleQuestions[i].veryShortName(), scaleQuestions[j].veryShortName(), scaleQuestions[m].veryShortName(), scaleQuestions[n].veryShortName())
							distortionStats.append((name, mean, std, min, max))
		distortionStats.sort(lambda a,b: cmp(a[1], b[1]))
		for stat in distortionStats[0:18]:
			print "k %s %s - %s mean=%.3f std=%.3f min=%.3f max=%.3f" % (k, slice, stat[0], stat[1], stat[2], stat[3], stat[4])
	print '  done comparing %s cluster quad distortions.' % slice


	
