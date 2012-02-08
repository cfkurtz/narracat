# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Statistical functions (that do not graph anything)
# -----------------------------------------------------------------------------------------------------------------

from narracat_constants import *
from narracat_utils import *

import numpy as np
import scipy
import scipy.stats as stats

def isNormal(npArray):
	return stats.normaltest(npArray)[1] >= 0.05
 
def correlationStatsForTwoScales(xValues, yValues, roundValues=True):
	npArrayX = np.array(xValues)
	npArrayY = np.array(yValues)
	
	# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.normaltest.html#scipy.stats.normaltest
	xIsNormal = isNormal(npArrayX)
	yIsNormal = isNormal(npArrayY) 
	
	if xIsNormal and yIsNormal:
		# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html#scipy.stats.pearsonr
		r, rp = stats.pearsonr(npArrayX, npArrayY)
	else:
		# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html#scipy.stats.spearmanr
		# this gives divide by zero errors but they are not a problem -
		# from the scipy bug database:
		# Given that the diagonal of the correlation matrix returned by corrcoef
		# will *always* be 1s, the t matrix will have divide-by-zero issues on
		# the diagonal, and give inf values -- which get zero values for the t-
		# distribution's survival function, so everything's fine, output-wise.
		r, rp = stats.spearmanr(npArrayX, npArrayY)
		
	if roundValues:
		r = round(r, 3)
		rp = round(rp, 3)
		
	return xIsNormal and yIsNormal, r, rp

def ttestForTwoChoiceQuestions(xValues, yValues):
	npArrayX = np.array(xValues)
	npArrayY = np.array(yValues)
	
	# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.normaltest.html#scipy.stats.normaltest
	xIsNormal = isNormal(npArrayX)
	yIsNormal = isNormal(npArrayY) 
	
	if xIsNormal and yIsNormal:
		# Levene test for equal variances
		# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html#scipy.stats.levene
		l, lp = stats.levene(npArrayX, npArrayY)
		parametric = xIsNormal and yIsNormal and lp >- 0.05
	else:
		parametric = False
	
	if parametric:
		# if levene test comes out well and samples are normal, can use standard t-test for independent samples
		# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html#scipy.stats.ttest_ind
		t, tp = stats.ttest_ind(xValues, yValues, axis=0)
	else:
		# if not, use Kruskal-Wallis H-test instead
		# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html#scipy.stats.kruskal
		t, tp = stats.kruskal(npArrayX, npArrayY)
		t = t / 5.0 # these come out bigger than the t-test stats
	
	return parametric, t, tp

def chiSquaredExpectedContingencyTable(data):
	# http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2_contingency.html#scipy.stats.chi2_contingency
	# chi squared test cannot be used if ANY cell of the table has a count lower than five in it
	atLeastOneCountIsLessThanFive = False
	for k in range(len(data)):
		for l in range(len(data[k])):
			if abs(data[k][l]) < 5:
				atLeastOneCountIsLessThanFive = True
				break
	if atLeastOneCountIsLessThanFive:
		return None, None, None, None
	else:
		try:
			npData = np.array(data)
			# chi2_contingency returns chiSquaredValue, chiSquaredPValue, degreesOfFreedom, expectedFrequencies
			return stats.chi2_contingency(npData)
		except:
			# got this error; ValueError: The internally computed table of expected frequencies has a zero element
			return None, None, None, None 
