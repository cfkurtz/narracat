# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Testing - methods for regression testing on stats and compilation methods
# -----------------------------------------------------------------------------------------------------------------

from narracat_constants import *
from narracat_utils import *
from narracat_stats import *
from narracat_graph import *

import numpy as np
import scipy
import scipy.stats as stats

TEST_SAMPLE_SIZES = [20, 50, 100, 500, 1000]
TESTING_DIR = os.path.dirname(sys.argv[0]) + os.sep + "testing" + os.sep

# -----------------------------------------------------------------------------------------------------------------
# normal distribution, normality test
# -----------------------------------------------------------------------------------------------------------------

def generateAndSaveNormalData():
	for sampleSize in TEST_SAMPLE_SIZES:
		# normal
		normalData = np.random.normal(50, 25, sampleSize)
		outputFileName = "%snormal_size%s.txt" % (TESTING_DIR, sampleSize)
		outputFile = open(outputFileName, 'w')
		outputFile.write(";Test data for normal distribution: mean = 50, sd = 25\n")
		try:
			for dataPoint in normalData:
				outputFile.write("%s\n"% dataPoint)
		finally:
			outputFile.close()
		# uniform
		uniformData = np.random.uniform(0, 100, sampleSize)
		outputFileName = "%suniform_size%s.txt" % (TESTING_DIR, sampleSize)
		outputFile = open(outputFileName, 'w')
		outputFile.write(";Test data for uniform distribution from 0 to 100\n")
		try:
			for dataPoint in uniformData:
				outputFile.write("%s\n"% dataPoint)
		finally:
			outputFile.close()
			
def graphHistogramsOfNormalAndUniformTestData():
	for sampleSize in TEST_SAMPLE_SIZES:
		for distributionType in ["normal", "uniform"]:
			testingFileName = "%s%s_size%s.txt" % (TESTING_DIR, distributionType, sampleSize)
			testingFile = open(testingFileName, "U")
			values = []
			try:
				for line in testingFile:
					if line[0] != ";":
						values.append(float(line))
			finally:
				testingFile.close()
			graphName = "Test %s distribution" % distributionType
			pngFileName = "%s_size%s" % (distributionType, sampleSize)
			graphPNGHistogramWithStatsMarked(values, graphName, pngFileName, TESTING_DIR, slice=ALL_DATA_SLICE, bins=10, start=0, end=100)
 
# -----------------------------------------------------------------------------------------------------------------
# t test for differences between means
# to do: add non normal distributoons
# -----------------------------------------------------------------------------------------------------------------

DIFFERENCES = [2, 5, 20]

def generateAndSaveTTestData():
	for sampleSize in TEST_SAMPLE_SIZES:
		for differenceBetweenMeans in DIFFERENCES:
			for useMean in [50-differenceBetweenMeans//2, 50+differenceBetweenMeans//2]:
				normalData = np.random.normal(useMean, 25, sampleSize)
				outputFileName = "%sttest_mean%s_size%s.txt" % (TESTING_DIR, useMean, sampleSize)
				outputFile = open(outputFileName, 'w')
				outputFile.write(";Test data for t-test normal distribution comparison: mean = %s, sd = 25\n" % useMean)
				try:
					for dataPoint in normalData:
						outputFile.write("%s\n"% dataPoint)
				finally:
					outputFile.close()
	
def graphHistogramsAndTTestResultsOfTTestData():
	outputFileName = "%sttest_results.csv" % (TESTING_DIR)
	outputFile = open(outputFileName, 'w')
	try:
		outputFile.write("Testing t-test results\n" )
		outputFile.write("Sample size,Difference between means,Both distributions normal?,T-test result,P value\n")
		for sampleSize in TEST_SAMPLE_SIZES:
			for differenceBetweenMeans in DIFFERENCES:
				bothSetsOfValues = []
				for useMean in [50-differenceBetweenMeans//2, 50+differenceBetweenMeans//2]:
					testingFileName = "%sttest_mean%s_size%s.txt" % (TESTING_DIR, useMean, sampleSize)
					inputFile = open(testingFileName, "U")
					values = []
					try:
						for line in inputFile:
							if line[0] != ";":
								values.append(float(line))
					finally:
						inputFile.close()
					bothSetsOfValues.append(values)
					graphName = "Test %s distribution" % type
					pngFileName = "ttest_mean%s_size%s" % (useMean, sampleSize)
					graphPNGHistogramWithStatsMarked(values, graphName, pngFileName, TESTING_DIR, slice=ALL_DATA_SLICE, bins=10, start=0, end=100)
				normal, t, tp = ttestForTwoChoiceQuestions(bothSetsOfValues[0], bothSetsOfValues[1])
				outputFile.write("%s,%s,%s,%s,%s\n" % (sampleSize, differenceBetweenMeans, normal, t, tp))
	finally:
		outputFile.close()

# -----------------------------------------------------------------------------------------------------------------
# chi squared (yet to be done)
# -----------------------------------------------------------------------------------------------------------------

def generateAndSaveChiSquaredData():
	pass

# -----------------------------------------------------------------------------------------------------------------
# correlations (yet to be done)
# -----------------------------------------------------------------------------------------------------------------
	
def generateAndSaveCorrelationData():
	pass
		
	