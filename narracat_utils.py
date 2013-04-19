# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Utility functions
# -----------------------------------------------------------------------------------------------------------------

import re, os

def createPathIfNonexistent(path):
	if not os.path.exists(path):
		os.mkdir(path)
	return path

def stringUpTo(aString, aDelimiter):
	if len(aString) == 0:
		return ""
	delimiterPos = aString.find(aDelimiter)
	if delimiterPos == -1:
		result = aString
	elif delimiterPos == 0:
		result = ""
	else:
		result = aString[:delimiterPos]
	return result

def stringBeyond(aString, aDelimiter):
	if len(aString) == 0:
		result = ""
		return result
	delimiterPos = aString.find(aDelimiter)
	if delimiterPos == -1:
		result = aString
	elif delimiterPos == len(aString) - 1:
		result = ""
	else:
		result = aString[delimiterPos + len(aDelimiter):]
	return result

def stringBetween(startString, endString, wholeString):
	result = stringUpTo(stringBeyond(wholeString.strip(), startString), endString)
	return result

def listFromStringRemovingBlankLines(aString):
	result = []
	pieces = aString.split("\n")
	for piece in pieces:
		if piece:
			result.append(piece)
	return result

def removeSpecificListItemsFromList(aList, listOfItemsToRemove):
	newList = []
	for item in aList:
		if len(listOfItemsToRemove) > 0 and item in listOfItemsToRemove:
			pass
		else:
			newList.append(item)
	return newList

def textOrDefaultIfBlank(text, aDefault):
	if len(text) > 0:
		return text
	else:
		return aDefault

def cleanTextForFileName(fileName):
	result = fileName.replace("" + os.sep, " ").replace(":", " ").replace(".", " ").replace("\n", " ")
	result = result.replace("  ", " ")
	return result

def removeDuplicates(aList):
	newList = []
	for item in aList:
		if not item in newList:
			newList.append(item)
	return newList

def listWithoutItem(aList, itemToRemove):
	newList = []
	for item in aList:
		if not item == itemToRemove:
			newList.append(item)
	return newList

def numNonEmptyElementsInList(aList):
	result = 0
	for item in aList:
		result += item != ''
	return result

def doesNotContainDigit(aString):
	# this SHOULD work !! but it does not !!
	#return not re.match("[0-9]+", aString)
	for number in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
		if number in aString:
			return False
	return True

def findDigitIn(aString):
	for letter in aString:
		if not doesNotContainDigit(letter):
			return letter

def doesNotContainDash(aString):
	return not "-" in aString 

def lighterOrDarkerColor(hexString, increment):
	if hexString[0] == '#': 
		hexString = hexString[1:]
	r, g, b = hexString[:2], hexString[2:4], hexString[4:]
	r, g, b = [int(n, 16) for n in (r, g, b)]
	r = min(255, max(0, r + increment))
	g = min(255, max(0, g + increment))
	b = min(255, max(0, b + increment))
	return '#%02x%02x%02x' % (r,g,b)

# this is 16 rainbow colors
RAINBOW_COLORS = [
				"#FF00FF",
				"#FF00CC",
				"#FF0099",
				"#FF0066",
				"#FF0033",
				"#FF0000",
				"#FF3300",
				"#FF6600",
				"#FF9900",
				"#FFCC00",
				"#FFFF00",
				"#CCFF00",
				"#99FF00",
				"#66FF00",
				"#33FF00",
				"#00FF00",]

LOREM_IPSUM = [
"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla malesuada arcu a lorem interdum euismod aliquet dui vehicula. Integer posuere mollis massa, ac posuere diam vestibulum eget. Quisque gravida arcu non lorem placerat tempus eget in risus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Aliquam velit nulla, tempus sit amet gravida vel, gravida sit amet libero. Maecenas bibendum nulla ac leo feugiat egestas. Suspendisse vel dui velit. Duis a velit eget augue pellentesque bibendum in non urna. Nunc vestibulum mi vitae neque pulvinar et feugiat urna auctor. Proin volutpat euismod nunc, adipiscing pharetra leo commodo a. Suspendisse potenti. Vestibulum luctus velit non purus laoreet elementum. Donec euismod, ipsum interdum facilisis porttitor, dui dui suscipit turpis, faucibus imperdiet ante metus tempus elit. Ut vulputate, leo quis tincidunt tincidunt, massa ante fringilla libero, iaculis varius tortor quam tempor ipsum. Praesent cursus consequat tellus, eget molestie dui aliquet vitae.",
"Cras sagittis nibh tempor orci pellentesque condimentum. Etiam vel ipsum tortor. Phasellus quam erat, aliquet sit amet egestas a, vehicula vitae risus. Nam ac quam sit amet risus imperdiet eleifend. Pellentesque nec arcu ut nunc rutrum posuere. Fusce at elit est, ac auctor sapien. Pellentesque semper enim et turpis euismod tincidunt. Donec nibh nunc, placerat vitae semper et, ullamcorper vel lectus. Praesent ut tellus eros. Ut sit amet odio vel risus auctor mollis. Duis luctus viverra diam, eu tincidunt ante sodales nec. Suspendisse potenti.",
"Fusce pharetra mauris eget neque adipiscing a suscipit ante laoreet. Sed nec risus risus, quis vulputate quam. Nam tristique fringilla tristique. Phasellus ultricies scelerisque feugiat. Etiam hendrerit elementum varius. Sed nibh massa, sollicitudin quis semper id, tempor nec nisl. Fusce sodales cursus nunc a elementum. Suspendisse potenti. Nulla facilisi. Maecenas mattis, nibh sed sodales congue, turpis nunc bibendum felis, ac malesuada erat mi id lorem. Fusce blandit venenatis gravida. In posuere diam at magna bibendum suscipit.",
"Fusce tincidunt iaculis justo, in viverra ipsum ullamcorper quis. Cras sed molestie libero. Praesent laoreet nisi volutpat enim bibendum porttitor. Duis rhoncus vestibulum justo nec adipiscing. Cras quam lorem, cursus ut gravida eget, porttitor ac nisl. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur eget mauris ante, sit amet convallis dui. Donec metus augue, condimentum ut tempus vel, ullamcorper et nisi. Integer vestibulum, risus eget accumsan malesuada, turpis ligula posuere eros, nec consectetur metus nisl nec ligula. Fusce non est sit amet mi pellentesque placerat eget ut magna. Nulla sit amet diam augue, quis gravida magna. Donec eleifend nunc sit amet lacus vehicula quis ornare sem sagittis. Duis sodales, lectus nec vestibulum lobortis, orci erat fermentum augue, interdum varius nulla ipsum ac mi. Sed at tellus quam, sed rhoncus enim. Pellentesque scelerisque consectetur turpis eu ullamcorper. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Mauris a sapien orci. Integer volutpat ornare urna non tristique. Nullam eget elit est, sed mollis ante. Sed eget risus tortor.",
"Nullam sapien ligula, suscipit adipiscing elementum et, faucibus quis metus. Aliquam ullamcorper libero et purus adipiscing ut feugiat ligula dictum. Duis ante est, volutpat vitae suscipit eu, ultricies sed orci. Fusce eleifend elit ullamcorper felis molestie vitae convallis mi vehicula. Nullam eu turpis non purus feugiat fringilla. Morbi egestas sem eget eros adipiscing a pharetra enim vestibulum. Ut eu nisl quis nisl elementum elementum. In feugiat sapien eu leo rhoncus aliquet. Cras porttitor adipiscing orci, nec tristique tellus adipiscing et. Nulla ut dui arcu, non tincidunt nulla. Nunc lacus turpis, adipiscing eget vestibulum vel, congue nec leo. Maecenas est arcu, pretium at congue sed, venenatis eget metus.",
]


# -----------------------------------------------------------------------------------------------------------------
# this is stuff I'm not using anymore
# -----------------------------------------------------------------------------------------------------------------

def _blob(x,y,area,colour):
     hs = np.sqrt(area) / 2
     xcorners = np.array([x - hs, x + hs, x + hs, x - hs])
     ycorners = np.array([y - hs, y - hs, y + hs, y + hs])
     plt.fill(xcorners, ycorners, colour, edgecolor=colour)
 
def hinton(W, maxWeight=None):
     """
     Draws a Hinton diagram for visualizing a weight matrix. 
     """
     plt.clf()
     height, width = W.shape
     if not maxWeight:
         maxWeight = 2**np.ceil(np.log(np.max(np.abs(W)))/np.log(2))
 
     plt.fill(np.array([0,width,width,0]),np.array([0,0,height,height]),'gray')
     plt.axis('off')
     plt.axis('equal')
     for x in xrange(width):
         for y in xrange(height):
             _x = x+1
             _y = y+1
             w = W[y,x]
             if w > 0:
                 _blob(_x - 0.5, height - _y + 0.5, min(1,w/maxWeight),'white')
             elif w < 0:
                 _blob(_x - 0.5, height - _y + 0.5, min(1,-w/maxWeight),'black')
	 # save to file
	 plt.savefig(pngFilePath + cleanTextForFileName(pngFileName) + ".png", dpi=200)

