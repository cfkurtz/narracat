# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Methods that graph things
# -----------------------------------------------------------------------------------------------------------------

from narracat_constants import *
from narracat_stats import *
from narracat_data import *

import colorsys

import matplotlib
matplotlib.use('TkAgg') # do this before importing pylab

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import axes3d
from matplotlib.patches import Circle, Rectangle
from matplotlib.collections import PatchCollection

# -----------------------------------------------------------------------------------------------------------------
# graphing methods that write one PNG file
# -----------------------------------------------------------------------------------------------------------------

def graphPNGHistogramWithStatsMarked(numbersArray, graphName, pngFileName, pngFilePath, slice=ALL_DATA_SLICE):
	
	if not numbersArray:
		return
	
	# convert to numpy array
	npArray = np.array(numbersArray)
	
	# calculate basic descriptive stats
	mean = round(np.mean(npArray), 2)
	std = round(np.std(npArray), 2)
	if len(numbersArray) >= 20:
		skewness = round(stats.skew(npArray), 3)
		kurtosis = round(stats.kurtosis(npArray), 3)
		normaltestp = round(stats.normaltest(npArray)[1], 3) 
	else:
		skewness = "n/a"
		kurtosis = "n/a"
		normaltestp = "n/a"
	
	# create histograms
	plt.clf()
	figure = plt.figure()
	axes = figure.add_subplot(111)
	
	(n, bins, rects) = plt.hist(npArray, NUM_HISTOGRAM_BINS)
	
	minValue = 100000
	maxValue = 0
	for value in npArray:
		if value < minValue: 
			minValue = value
		if value > maxValue:
			maxValue = value
	range = maxValue - minValue
	
	if range == 0:
		return
	
	for rect in rects:
		if rect.get_height() > 0:
			plt.text(rect.get_x()+rect.get_width()/2.0, rect.get_height()*0.95, rect.get_height(), color='w', fontsize=8, horizontalalignment='center', verticalalignment='top')
	
	plt.subplots_adjust(top=0.95)
	plt.subplots_adjust(left=0.1)
	plt.subplots_adjust(right=0.98)
	
	# title and axis labels
	if DATA_HAS_SLICES:
		graphNameToShow = graphName + " (%s)" % slice
	else:
		graphNameToShow = graphName
	plt.title(graphNameToShow, fontsize=10)
	plt.ylabel("count with value")
	
	# mark mean and std. dev. on graph
	plt.axvline(mean, color='r', linewidth=2)
	plt.axvspan(mean-std, mean+std, color='y', alpha=0.2)
	
	axes.set_xlim(SLIDER_START, SLIDER_END)

	plt.text(0.5, 0.01, 
			'n = %s mean = %s std = %s\nskewness = %s kurtosis = %s normal-test p = %s' % (len(numbersArray), mean, std, skewness, kurtosis, normaltestp), 
			horizontalalignment='center', transform=figure.transFigure)
	
	plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)
	plt.close(figure)
	
def graphPNGBarChart(data, labels, graphName, pngFileName, pngFilePath, horizontal=True, figureWidth=5.5, figureHeight=5.5, slice=ALL_DATA_SLICE):
	# first must reverse data and labels - want to start at top, but barh starts them at bottom
	dataReversed = []
	dataReversed.extend(data)
	dataReversed.reverse()
	labelsReversed = []
	labelsReversed.extend(labels)
	labelsReversed.reverse()
	
	# convert to numpy array, create x array
	npArray = np.array(dataReversed)
	xLocations = np.arange(len(dataReversed)) + 0.5
	color = '#ccccff'
	edgeColor = '#aaaaee'
	textColor = '#000000'
	
	largestNumber = 0
	for number in data:
		if number > largestNumber:
			largestNumber = number
			
	longestLabelLength = 0
	for label in labels:
		if len(label) > longestLabelLength:
			longestLabelLength = len(label)

	# create bar chart
	plt.clf()
	figure = plt.figure(figsize=(figureWidth, figureHeight))
	axes = figure.add_subplot(111)
	if horizontal:
		rects = plt.barh(xLocations, npArray, height=0.5, align='center', color=color, edgecolor=edgeColor)
		
		axes.set_ylim(0, len(data) + 1)
		axes.set_xlim(0, largestNumber + 1)
		plt.yticks(xLocations, labelsReversed, fontsize=8) 
		plt.xticks(fontsize=8)
		
		i = 0
		for rect in rects:
			if npArray[i] > 0:
				plt.text(rect.get_width()*0.98, rect.get_y()+rect.get_height()/2.0, npArray[i], color=textColor, fontsize=8, horizontalalignment='right', verticalalignment='center')
			i += 1
		
		axes = figure.add_subplot(111)
		roomNeeded = max(0.05, min(longestLabelLength * 0.015, 0.6))
 		plt.subplots_adjust(left=roomNeeded)
		plt.subplots_adjust(right=0.98)
		plt.subplots_adjust(bottom=0.05)
		
	else:
		rects = plt.bar(xLocations, npArray, width=0.5, color=color)
		axes.set_xlim(0, len(data) + 1)
		axes.set_ylim(0, largestNumber + 1)
		plt.xticks(xLocations, labelsReversed, fontsize=8) 
		plt.yticks(fontsize=8)
		
		i = 0
		for rect in rects:
			if npArray[i] > 0:
				plt.text(rect.get_x()+rect.get_width()/2.0, rect.get_height()*0.98, npArray[i], color=textColor, fontsize=8, horizontalalignment='center', verticalalignment='top')
			i += 1
		
		axes = figure.add_subplot(111)
		roomNeeded = max(0.05, min(longestLabelLength * 0.015, 0.6))
		plt.subplots_adjust(bottom=roomNeeded)
		
	if DATA_HAS_SLICES:
		graphNameToShow = graphName + " (%s)" % slice
	else:
		graphNameToShow = graphName
	plt.suptitle(graphNameToShow, fontsize=10)
	
	plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)
	plt.close(figure)
	
def graphPNGContourF(xValues, yValues, zValues, xAxisName, yAxisName, graphName, pngFileName, pngFilePath, levels=100, slice=ALL_DATA_SLICE):
	
	npArrayX = np.array(xValues)
	npArrayY = np.array(yValues)
	npArrayZ = np.array(zValues)
	
	# http://www.scipy.org/Cookbook/Matplotlib/Gridding_irregularly_spaced_data
	interpolatedX = np.linspace(SLIDER_START, SLIDER_END, levels)
	interpolatedY = np.linspace(SLIDER_START, SLIDER_END, levels)
	try:
		interpolatedZ = mlab.griddata(npArrayX, npArrayY, npArrayZ, interpolatedX, interpolatedY)
	except Exception, e:
		print " >>>>>>>>>> could not save %s: %s" % (graphName, e)
		return
	
	plt.clf()
	figure = plt.figure(figsize=(6,6.5))
	axes = axes3d.Axes3D(figure)

	# you need a try-except here because of this error:
	# ValueError: need more than 0 values to unpack
	# it does NOT mean there are no Z values. i don't know what it means actually.
	# should figure it out someday.
	try:
		contourSet = axes.contourf(interpolatedX, interpolatedY, interpolatedZ)
		#axes.clabel(contourSet, fontsize=9, inline=1)
	
		axes.set_xlabel(xAxisName, fontsize=8)
		axes.set_ylabel(yAxisName, fontsize=8)
		
		if DATA_HAS_SLICES:
			graphNameToShow = graphName + " (%s)" % slice
		else:
			graphNameToShow = graphName
		plt.suptitle(graphNameToShow)
		
		plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)
		plt.close(figure)
	except Exception, e:
		print " >>>>>>>>>> could not save %s: %s" % (graphName, e)
		
def graphPNGScatterGraph(xValues, yValues, xAxisName, yAxisName, graphName, pngFileName, pngFilePath, colors=None, size=20, slice=ALL_DATA_SLICE):

	npArrayX = np.array(xValues)
	npArrayY = np.array(yValues)
	
	normal, r, rp = correlationStatsForTwoScales(xValues, yValues)
	
	plt.clf()
	figure = plt.figure()
	if DRAW_TRANSPARENT_DOTS_ON_SCATTER_GRAPHS:
		alpha = 0.2
	else:
		alpha = 1.0
	if colors:
		plt.scatter(npArrayX, npArrayY, c=colors, s=size, alpha=alpha)
	else:
		plt.scatter(npArrayX, npArrayY, s=size, alpha=alpha)
	
	plt.xlabel(xAxisName, fontsize=8)
	plt.ylabel(yAxisName, fontsize=8)
	
	if DATA_HAS_SLICES:
		graphNameToShow = graphName + " (%s)" % slice
	else:
		graphNameToShow = graphName
	plt.suptitle(graphNameToShow)
	
	# add stats label at bottom
	plt.text(0.5, 0.01, 
			'n=%s, both axes normal=%s, r=%.3f, p=%.3f' % (len(xValues), normal, r, rp), 
			horizontalalignment='center', transform=figure.transFigure)
	
	# add giant r value - uncomment if desired
	if rp < 0.05 and abs(r) >= 0.2:
		plt.text(0.88, 0.8, '%.2f' % r, fontsize=48, horizontalalignment='right', transform=figure.transFigure)

	axes = figure.add_subplot(111)
	axes.set_xlim(SLIDER_START, SLIDER_END)
	axes.set_ylim(SLIDER_START, SLIDER_END)

	plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)
	plt.close(figure)
	
def graphCircleMatrix(numRowsCols, labels, sizes, values, pValues, statLabel, colors, graphName, note, pngFileName, pngFilePath, slice=ALL_DATA_SLICE):
	gridValues = range(1, numRowsCols+1)
	
	# the Y values go from 0 at bottom, so want to flip them, and labels to match
	flippedGridValues = []
	flippedGridValues.extend(gridValues)
	flippedGridValues.reverse()
	flippedLabels = []
	flippedLabels.extend(labels)
	flippedLabels.reverse()
	
	# this is for sizing the figure so you can see all the labels, but no bigger
	longestLabel = 0
	for label in labels:
		if len(label) > longestLabel:
			longestLabel = len(label)

	plt.clf()
	figsize = 5 + longestLabel*0.08 + len(labels)*0.25
	figure = plt.figure(figsize=(figsize, figsize))
	axes = figure.add_subplot(111)
	axes.set_xlim(0, numRowsCols + 1)
	axes.set_ylim(0, numRowsCols + 1)

	axes.xaxis.grid(True, linestyle='-', which='major', color='#BEBEBE')
	axes.yaxis.grid(True, linestyle='-', which='major', color='#BEBEBE')
	axes.set_axisbelow(True)

	# generate circles
	for i in range(numRowsCols):
		for j in range(numRowsCols):
			if i == j:
				circle = Circle((gridValues[i], flippedGridValues[j]), 0.05, color='grey')
			elif i > j:
				circle = Circle((gridValues[i], flippedGridValues[j]), sizes[i][j], color=colors[i][j])
				if sizes[i][j] != 0 and values[i][j] != 0:
					if pValues:
						plt.text(gridValues[i], flippedGridValues[j]-0.1, "p = %.2f" % pValues[i][j], verticalalignment='top', horizontalalignment='center', fontsize=8)
						plt.text(gridValues[i], flippedGridValues[j]+0.1, "%s = %.2f" % (statLabel, values[i][j]), verticalalignment='bottom', horizontalalignment='center', fontsize=8)
					else:
						plt.text(gridValues[i], flippedGridValues[j]+0.1, "%.2f" % (values[i][j]), verticalalignment='center', horizontalalignment='center', fontsize=8)
			axes.add_patch(circle)
	
	# want the x axis ticks (names) on the top, not the bottom
	axes.xaxis.set_ticks_position('top')
	plt.xticks(gridValues, labels)
	# for some reason if the tick labels are at the top the normal command doesn't work
	# and you need to set the size and rotation on each separately
	for aLabel in axes.xaxis.get_ticklabels():
		aLabel.set_rotation(90)
		aLabel.set_size(8)
	plt.yticks(gridValues, flippedLabels, rotation=0, fontsize=8)
	
	# this gives a bit more room at the top and side to accommodate the labels
	plt.subplots_adjust(top=0.7)
	plt.subplots_adjust(left=0.3)
	plt.subplots_adjust(right=0.98)
	plt.subplots_adjust(bottom=0.05)
	
	#plt.xlabel(note, fontsize=10)
	
	#plt.suptitle(graphName)
	# add label at bottom
	if DATA_HAS_SLICES:
		graphNameToShow = graphName + " (%s)" % slice
	else:
		graphNameToShow = graphName
	plt.text(0.95, 0.01, graphNameToShow, horizontalalignment='right', fontsize=8, transform=figure.transFigure)
	
	plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)
	plt.close(figure)

def graphChiSquaredContingencyCircleMatrix(xLabels, yLabels, data, graphName, note, pngFileName, pngFilePath, slice=ALL_DATA_SLICE):
	chiSquaredValue, chiSquaredPValue, degreesOfFreedom, expectedFrequencies = chiSquaredExpectedContingencyTable(data)
	if not chiSquaredPValue:
		return
	if chiSquaredPValue > SIGNIFICANCE_VALUE_REPORTING_THRESHOLD:
		return
	
	print '  printing graph: %s' % graphName

	xValues, flippedYValues, longestXLabel, longestYLabel, flippedYLabels = setUpContingencyLabelsAndTableValues(xLabels, yLabels)
	observedSizes, maxValue = contingencySizesForData(data, multiplier=0.7)
	expectedSizes, maxValue = contingencySizesForData(expectedFrequencies, multiplier=0.7, startWithMaxValue=maxValue)
				
	plt.clf()
	figure = plt.figure(figsize=(4 + longestXLabel*0.05 + len(xLabels)*0.14, 2 + longestYLabel*0.18 + len(yLabels)*0.14))
	axes = figure.add_subplot(111)
	# why is this necessary? no idea. for gender (2 slices) it comes out different
	if len(xValues) == 2:
		axes.set_xlim(0, len(xValues) + 2)
	else:
		axes.set_xlim(0, len(xValues) + 1)
	axes.set_ylim(0, len(flippedYValues) + 2)
	axes.xaxis.grid(True, linestyle='-', which='major', color='#BEBEBE')
	axes.yaxis.grid(True, linestyle='-', which='major', color='#BEBEBE')
	axes.set_axisbelow(True)
	
	# generate circles
	for i in range(len(xValues)):
		for j in range(len(flippedYValues)):
			observedSize = observedSizes[i][j]
			expectedSize = expectedSizes[i][j]
			if observedSize > 0:
				expectedCircle = Circle((xValues[i], flippedYValues[j]), expectedSize, edgecolor="#B8B8B8", facecolor='none', fill=False, linewidth=1)
				axes.add_patch(expectedCircle)
				observedCircle = Circle((xValues[i], flippedYValues[j]), observedSize, edgecolor="#FF0000", facecolor='none', fill=False, linewidth=1)
				axes.add_patch(observedCircle)
				plt.text(xValues[i], flippedYValues[j], '%d obs/%d exp' % (data[i][j], expectedFrequencies[i][j]), horizontalalignment='center', verticalalignment='center', fontsize=8)
		
	# want the x axis ticks (names) on the top, not the bottom
	axes.xaxis.set_ticks_position('top')
	plt.xticks(xValues, xLabels)
	# for some reason if the tick labels are at the top the normal command doesn't work
	# and you need to set the size and rotation on each separately
	for aLabel in axes.xaxis.get_ticklabels():
		aLabel.set_rotation(90)
		aLabel.set_size(8)
	plt.yticks(flippedYValues, yLabels, rotation=0, fontsize=8)
	
	# this gives a bit more room at the top and side to accommodate the labels
	roomNeededTop = 1.0 - max(0.2, min(longestXLabel * 0.018, 0.6))
	plt.subplots_adjust(top=roomNeededTop)
	roomNeededLeft = max(0.2, min(longestYLabel * 0.015, 0.6))
	plt.subplots_adjust(left=roomNeededLeft)
	plt.subplots_adjust(right=0.98)
	plt.subplots_adjust(bottom=0.1) # was 0.05; added 0.05 for second row of text
	
	plt.xlabel(note, fontsize=8)
	
	if DATA_HAS_SLICES:
		graphNameToShow = graphName + " (%s)" % slice
	else:
		graphNameToShow = graphName
	plt.text(0.95, 0.01, "Chi squared = %.3f, p = %.3f (red observed, grey expected)" % (chiSquaredValue, chiSquaredPValue), horizontalalignment='right', transform=figure.transFigure, fontsize=8)
	plt.text(0.95, 0.05, graphNameToShow, horizontalalignment='right', transform=figure.transFigure, fontsize=8)
	
	plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)
	plt.close(figure)
	
def graphContingencyCircleMatrix(xLabels, yLabels, data, graphName, note, pngFileName, pngFilePath, slice=ALL_DATA_SLICE):
	xValues, flippedYValues, longestXLabel, longestYLabel, flippedYLabels = setUpContingencyLabelsAndTableValues(xLabels, yLabels)
	sizes, maxValue = contingencySizesForData(data)
	percentages = []
	for k in range(len(data)):
		percentages.append([])
		totalForThisColumn = 0
		for l in range(len(data[k])):
			if l > 0:
				totalForThisColumn += abs(data[k][l])
		for l in range(len(data[k])):
			if totalForThisColumn > 0:
				percentage = int(100.0 * abs(data[k][l]) / totalForThisColumn)
				percentages[k].append(percentage)
			else:
				percentages[k].append(0)
				
	atLeastOnePointInTheGraphIsFarFromAverage = False
	totalDeviation = 0
	numDeviations = 0
	for i in range(len(xValues)):
		if i == 0 or i == len(xValues)-1:
			continue
		for j in range(len(flippedYValues)):
			if j == 0:
				continue
		 	percentage = percentages[i][j]
		 	percentageAllThisRow = percentages[0][j]
		 	totalAllThisRow = abs(data[0][j])
		 	totalAllThisColumn = abs(data[i][0])
		 	# graph must have at least one row-column combination that is different from the combined figure
		 	# for that row (for the "all answers" slice which is first)
		 	# by at least CONTINGENCY_PERCENTAGE_THRESHOLD
		 	# also don't consider any rows for which the total is less than the global cutoff
		 	if valueDeviatesEnoughToShow(percentage, percentageAllThisRow, totalAllThisRow, totalAllThisColumn):
				atLeastOnePointInTheGraphIsFarFromAverage = True
				totalDeviation += abs(percentage - percentageAllThisRow)
				numDeviations += 1
				#print 'MATCH: ', graphName, i, j, percentage, "% compared to", percentageAllThisRow, "% (", totalAllThisRow, ")"
			
	if numDeviations > 0:
		averageDeviation = 1.0 * totalDeviation / numDeviations
	else:
		averageDeviation = 0
			
	if atLeastOnePointInTheGraphIsFarFromAverage:
		print '  printing graph: %s' % graphName

		plt.clf()
		figure = plt.figure(figsize=(4 + longestXLabel*0.05 + len(xLabels)*0.14, 2 + longestYLabel*0.18 + len(yLabels)*0.14))
		axes = figure.add_subplot(111)
		# why is this necessary? no idea. for gender (2 slices) it comes out different
		if len(xValues) == 2:
			axes.set_xlim(0, len(xValues) + 2)
		else:
			axes.set_xlim(0, len(xValues) + 1)
		axes.set_ylim(0, len(flippedYValues) + 2)
	
		axes.xaxis.grid(True, linestyle='-', which='major', color='#BEBEBE')
		axes.yaxis.grid(True, linestyle='-', which='major', color='#BEBEBE')
		axes.set_axisbelow(True)
		
		# generate circles
		for i in range(len(xValues)):
			for j in range(len(flippedYValues)):
				size = sizes[i][j] 
				dataPoint = data[i][j]
				percentage = percentages[i][j]
				if size > 0:
					percentageAllThisRow = percentages[0][j]
					totalAllThisRow = data[0][j]
					totalAllThisColumn = data[i][0]
					
					if i == 0 or j == 0 or i == len(xValues)-1:
						circleColor = "#EE9A00"
						textColor = "#000000"
					elif INCLUDE_PERCENTAGES_IN_CONTINGENCY_DIAGRAMS and valueDeviatesEnoughToShow(percentage, percentageAllThisRow, totalAllThisRow, totalAllThisColumn):
						circleColor = "#FF0000"
						textColor = "#000000"
						#print '     ', graphName, i, j, percentage, "% compared to", percentageAllThisRow, "% (", totalAllThisRow, ")"
					else:
						circleColor = "#FFE4B5"
						textColor = "#919191"
					
					circle = Circle((xValues[i], flippedYValues[j]), size, color=circleColor, fill=True, linewidth=1)
					axes.add_patch(circle)
				
					if not INCLUDE_PERCENTAGES_IN_CONTINGENCY_DIAGRAMS:
						plt.text(xValues[i], flippedYValues[j], '%s' % dataPoint, horizontalalignment='center', verticalalignment='center', fontsize=8)
					else:
						if j == 0:
							plt.text(xValues[i], flippedYValues[j], '%s' % dataPoint, horizontalalignment='center', verticalalignment='center', fontsize=8)
						elif i == 0:
							plt.text(xValues[i], flippedYValues[j], '%s/%s%%' % (dataPoint,percentage), color=textColor, horizontalalignment='center', verticalalignment='center', fontsize=8)
						else:
							plt.text(xValues[i], flippedYValues[j], '%s%%' % percentage, color=textColor, horizontalalignment='center', verticalalignment='center', fontsize=8)
		
		# want the x axis ticks (names) on the top, not the bottom
		axes.xaxis.set_ticks_position('top')
		plt.xticks(xValues, xLabels)
		# for some reason if the tick labels are at the top the normal command doesn't work
		# and you need to set the size and rotation on each separately
		for aLabel in axes.xaxis.get_ticklabels():
			aLabel.set_rotation(90)
			aLabel.set_size(8)
		plt.yticks(flippedYValues, yLabels, rotation=0, fontsize=8)
		
		# this gives a bit more room at the top and side to accommodate the labels
		roomNeededTop = 1.0 - max(0.2,min(longestXLabel * 0.015, 0.6))
		plt.subplots_adjust(top=roomNeededTop)
		roomNeededLeft = max(0.2,min(longestYLabel * 0.015, 0.6))
		plt.subplots_adjust(left=roomNeededLeft)
		plt.subplots_adjust(right=0.98)
		plt.subplots_adjust(bottom=0.05)
		
		plt.xlabel(note, fontsize=8)
		
		if DATA_HAS_SLICES:
			graphNameToShow = graphName + " (%s)" % slice
		else:
			graphNameToShow = graphName
		plt.text(0.95, 0.01, graphNameToShow, horizontalalignment='right', transform=figure.transFigure, fontsize=8)
		
		plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)
		plt.close(figure)
		
def setUpContingencyLabelsAndTableValues(xLabels, yLabels):
	xValues = range(1, len(xLabels) + 1)
	# the Y values go from 0 at bottom, so want to flip them, and labels to match
	yValues = range(1, len(yLabels) + 1)
	flippedYValues = []
	flippedYValues.extend(yValues)
	flippedYValues.reverse()
	flippedYLabels = []
	flippedYLabels.extend(yLabels)
	flippedYLabels.reverse()
	# this is for sizing the figure so you can see all the labels, but no bigger
	longestXLabel = 0
	for label in xLabels:
		if len(label) > longestXLabel:
			longestXLabel = len(label)
	longestYLabel = 0
	for label in yLabels:
		if len(label) > longestYLabel:
			longestYLabel = len(label)
	return xValues, flippedYValues, longestXLabel, longestYLabel, flippedYLabels

def contingencySizesForData(data, multiplier=1.0, startWithMaxValue=0):
	maxValue = startWithMaxValue
	for k in range(len(data)):
		for l in range(len(data[k])):
			if abs(data[k][l]) > maxValue:
				maxValue = abs(data[k][l])
	sizes = []
	for k in range(len(data)):
		sizes.append([])
		totalForThisColumn = 0
		for l in range(len(data[k])):
			if l > 0:
				totalForThisColumn += abs(data[k][l])
		for l in range(len(data[k])):
			if maxValue != 0:
				size = multiplier * 0.8 * abs(data[k][l]) / maxValue
			else:
				size = 0
			sizes[k].append(size)
	return sizes, maxValue

def valueDeviatesEnoughToShow(percentage, percentageAllThisRow, totalAllThisRow, totalAllThisColumn):
	absoluteTotalIsHighEnough = totalAllThisRow >= LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS and totalAllThisColumn >= LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS
	valueIsFarEnoughFromAverage = abs(percentage - percentageAllThisRow) >= CONTINGENCY_PERCENTAGE_THRESHOLD
	return absoluteTotalIsHighEnough and valueIsFarEnoughFromAverage
	
def graphSliceValuesMatrix(xLabels, yLabels, data, colors, graphName, note, pngFileName, pngFilePath, sizeMultiplier=0.8):
	xValues = range(1, len(xLabels) + 1)
	
	# the Y values go from 0 at bottom, so want to flip them, and labels to match
	yValues = range(1, len(yLabels) + 1)
	flippedYValues = []
	flippedYValues.extend(yValues)
	flippedYValues.reverse()
	flippedYLabels = []
	flippedYLabels.extend(yLabels)
	flippedYLabels.reverse()
	
	# this is for sizing the figure so you can see all the labels, but no bigger
	longestXLabel = 0
	for label in xLabels:
		if len(label) > longestXLabel:
			longestXLabel = len(label)
	longestYLabel = 0
	for label in yLabels:
		if len(label) > longestYLabel:
			longestYLabel = len(label)
			
	maxValue = 0
	for k in range(len(data)):
		for l in range(len(data[k])):
			if abs(data[k][l]) > maxValue:
				maxValue = abs(data[k][l])
				
	sizes = []
	for k in range(len(data)):
		sizes.append([])
		totalForThisColumn = 0
		for l in range(len(data[k])):
			if l > 0:
				totalForThisColumn += abs(data[k][l])
		for l in range(len(data[k])):
			if maxValue != 0:
				size = 0.8 * abs(data[k][l]) / maxValue
			else:
				size = 0
			sizes[k].append(size)
	
	print '  printing graph: %s' % graphName

	plt.clf()
	figure = plt.figure(figsize=(4 + longestYLabel*0.05 + len(xLabels)*0.14, 2 + longestXLabel*0.18 + len(yLabels)*0.14))
	axes = figure.add_subplot(111)
	# why is this necessary? no idea. for 2 slices it comes out different
	if len(xValues) == 2:
		axes.set_xlim(0, len(xValues) + 2)
	else:
		axes.set_xlim(0, len(xValues) + 1)
	axes.set_ylim(0, len(yValues) + 2)

	axes.xaxis.grid(True, linestyle='-', which='major', color='#BEBEBE')
	axes.yaxis.grid(True, linestyle='-', which='major', color='#BEBEBE')
	axes.set_axisbelow(True)
	
	# generate circles
	for i in range(len(xValues)):
		for j in range(len(yValues)):
			size = sizes[i][j] * sizeMultiplier
			dataPoint = data[i][j]
			color = colors[i][j]
			if size > 0:
				if dataPoint == 0.00001: # means not enough data:
					rect = Rectangle((xValues[i] - 0.1/2, flippedYValues[j]), 0.1, 0.1, color=color, fill=True, linewidth=1)
					#rect = Rectangle((xValues[i], flippedYValues[j]), size, 0.75, color=color, fill=True, linewidth=1)
					axes.add_patch(rect)
				else:	
					rect = Rectangle((xValues[i] - 0.75/2, flippedYValues[j]), 0.75, size, color=color, fill=True, linewidth=1)
					#rect = Rectangle((xValues[i], flippedYValues[j]), size, 0.75, color=color, fill=True, linewidth=1)
					axes.add_patch(rect)
					plt.text(xValues[i], flippedYValues[j]-0.2, '%s' % dataPoint, 
							horizontalalignment='center', verticalalignment='center', fontsize=7)
	
	# want the x axis ticks (names) on the top, not the bottom
	axes.xaxis.set_ticks_position('top')
	plt.xticks(xValues, xLabels)
	# for some reason if the tick labels are at the top the normal command doesn't work
	# and you need to set the size and rotation on each separately
	for aLabel in axes.xaxis.get_ticklabels():
		aLabel.set_rotation(90)
		aLabel.set_size(8)
	plt.yticks(flippedYValues, yLabels, rotation=0, fontsize=8)
	
	# this gives a bit more room at the top and side to accommodate the labels
	roomNeededTop = 1.0 - min(longestXLabel * 0.01, 0.6)
	plt.subplots_adjust(top=roomNeededTop)
	roomNeededLeft = min(longestYLabel * 0.015, 0.6)
	plt.subplots_adjust(left=roomNeededLeft)
	plt.subplots_adjust(right=0.98)
	plt.subplots_adjust(bottom=0.05)
	
	plt.xlabel(note, fontsize=8)
	plt.text(0.95, 0.01, graphName, horizontalalignment='right', transform=figure.transFigure, fontsize=8)
	
	plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)
	plt.close(figure)
		
