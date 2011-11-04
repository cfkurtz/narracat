# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# GUI for browsing data
# fits inside launcher frame (main window)
# -----------------------------------------------------------------------------------------------------------------

from narracat_constants import *
from narracat_data import *

from Tkinter import *
import tkFont

helpText = """== Scales
Fairness, Ambition(...): 0-10,90-100(...)

== Choices
Tone+Feeling(...): positive+happy(...)

== Scales + choices
Fairness, Ambition(...): 0-10,90-100(...): 
Tone+Feeling(...): positive+happy(...)

== Search (case sensitive)
find: <text>
  
== Story name
<name>

== Story number 
#<number>
To show index codes for data checking, 
add plus at end - #12+

== Random story
random
"""

class TxtboxOut(object):
	def __init__(self, tkintertxt):
		self.T = tkintertxt
 
	def write(self, txt):
		self.T.insert(END, "%s" % str(txt))
		self.T.yview(MOVETO, 1.0)

class NarracatBrowser(Frame):
	def __init__(self, master=None, questions=None, respondents=None, stories=None):
		Frame.__init__(self, master)
		self.questions = questions
		self.respondents = respondents
		self.stories = stories
		self.selections = []
		self.currentSelectionIndex = 0
		
		self.pack(fill=BOTH, expand=YES)
		self.buildWindow()
		
	def buildWindow(self):
		font = tkFont.Font(family="Georgia", size=12)
		biggerFont = tkFont.Font(family="Georgia", size=16)
		littleFont = tkFont.Font(family="Helvetica", size=12)
		
		# frame to right, help + names + console
		namesFrame = Frame(self)
		namesFrame.pack(side=RIGHT, fill=BOTH)
		
		# console for program output information
		self.useConsoleCheckBoxState = IntVar()
		useConsoleCheckBox = Checkbutton(namesFrame, variable=self.useConsoleCheckBoxState, text="  Write output to console", font=littleFont)
		useConsoleCheckBox.pack(side=BOTTOM, anchor=W)
		useConsoleCheckBox["command"] = self.changeUseConsole
		
		self.console = Text(namesFrame, width=30, height=15, relief=SUNKEN, borderwidth=2, font=littleFont)
		self.console.pack(side=BOTTOM, fill=BOTH, expand=YES)
		consoleLabel = Label(namesFrame, foreground='blue', text="Output console", font=littleFont).pack(side=BOTTOM, anchor=W)
				
		# copy from (Q-A) box lists questions for copying to command line
		self.copyFrom = Text(namesFrame, width=30, height=15, relief=SUNKEN, borderwidth=2, font=font)
		self.copyFrom.pack(side=BOTTOM, fill=BOTH, expand=YES)
		qaLabel = Label(namesFrame, text="Q & A (copy from here)", foreground='blue', font=littleFont).pack(side=BOTTOM, anchor=W)
		
		# help box tells you what you can type into command line
		self.help = Text(namesFrame, width=30, height=15, relief=SUNKEN, borderwidth=2, font=font)
		self.help.insert(END, helpText)
		self.help.pack(side=BOTTOM, fill=BOTH, expand=YES)
		helpLabel = Label(namesFrame, text="Help on commands", foreground='blue', font=littleFont).pack(side=BOTTOM, anchor=W)
		
		outputFrame = Frame(self, width=600, relief=GROOVE, borderwidth=1)
		outputFrame.pack(side=LEFT, fill=BOTH)
	
		storyTextFrame = Frame(outputFrame, width=600, relief=GROOVE, borderwidth=1)
		storyTextFrame.pack(side=TOP, fill=BOTH, expand=YES)
		scrollbar = Scrollbar(storyTextFrame)
		scrollbar.pack(side=RIGHT, fill=Y)

		# where stories appear
		self.storyText = Text(storyTextFrame, wrap=WORD, width=100, undo=True, font=biggerFont, yscrollcommand=scrollbar.set)
		self.storyText.pack(side=TOP, fill=BOTH, expand=YES)
		scrollbar.config(command=self.storyText.yview)

		controlFrame = Frame(outputFrame, width=600, height=100, relief=GROOVE, borderwidth=1)
		controlFrame.pack(side=BOTTOM, fill=BOTH, expand=NO)
		
		# command line
		label = Label(controlFrame, text="Type commands here", foreground='blue', font=littleFont).pack(side=TOP, anchor=W)
		self.commandLine = Entry(controlFrame, width=50, font=biggerFont)
		self.commandLine.pack(side=TOP)
		self.commandLine.focus()                         
		self.commandLine.bind('<Return>', (lambda event: self.selectStoriesForTextBox()))   

		self.numStoriesSelectedStringVar = StringVar("")
		self.numStoriesSelected = Label(controlFrame, textvariable=self.numStoriesSelectedStringVar)
		self.numStoriesSelectedStringVar.set("No selection")
		self.numStoriesSelected.pack(side=BOTTOM)

		# buttons under command line
		buttonsFrame = Frame(controlFrame)
		buttonsFrame.pack(side=BOTTOM)

		self.copyButton = Button(buttonsFrame)
		self.copyButton["text"] = "  Copy   "
		self.copyButton["command"] = self.copy
		self.copyButton.pack(side=RIGHT)
		
		self.backButton = Button(buttonsFrame)
		self.backButton["text"] = "Back"
		self.backButton["command"] = self.goBackInSavedSelections
		self.backButton.pack(side=RIGHT)

		self.forwardButton = Button(buttonsFrame)
		self.forwardButton["text"] = "Forward"
		self.forwardButton["command"] = self.goForwardInSavedSelections
		self.forwardButton.pack(side=RIGHT)

		self.selectStories = Button(buttonsFrame)
		self.selectStories["text"] = "Select stories"
		self.selectStories["command"] = self.selectStoriesForTextBox
		self.selectStories.pack(side=RIGHT)

	def initializeQABox(self):
		if self.questions:
			names = gatherScaleQuestionVeryShortNames(self.questions)
			names.insert(0, " ")
			names.insert(0, "SCALES")
			names.append(" ")
			names.append("CHOICES")
			names.append(" ")
			names.extend(gatherChoiceQuestionShortNames(self.questions))
			names.append(" ")
			names.append("ANSWERS")
			names.append(" ")
			for question in self.questions:
				if question.isChoiceQuestion():
					uniqueAnswers = []
					for answer in question.shortResponseNames:
						if not answer in uniqueAnswers:
							uniqueAnswers.append(answer)
					for answer in uniqueAnswers:
						names.append("%s: %s" % (question.shortName, answer))
					names.append("")
			names.append(" ")
		else:
			names = []
		self.copyFrom.insert(END, "\n".join(names))
		self.copyFrom.insert(END, "COMMANDS ENTERED\n\n")
		
	def changeUseConsole(self):
		# can write output to "console" box on form or let it go to wherever it usually goes (the IDE console)
		if self.useConsoleCheckBoxState.get():
			newout = TxtboxOut(self.console)
			self.stdout = sys.stdout
			console = sys.stdout
			sys.stdout = newout		
		else:
			sys.stdout = self.stdout
	
	def copy(self):
		self.storyText.clipboard_clear()
		self.storyText.clipboard_append(self.storyText.get(1.0, END))
		
	def selectStoriesForTextBox(self):
		selection = self.commandLine.get()
		self.selections.append(selection)
		self.currentSelectionIndex = len(self.selections) - 1
		self.makeSelection(self.selections[self.currentSelectionIndex])
		
	def goBackInSavedSelections(self):
		if self.currentSelectionIndex + 1 > 0:
			self.currentSelectionIndex -= 1
			self.commandLine.delete(0, END)
			self.commandLine.insert(END, self.selections[self.currentSelectionIndex])
			self.makeSelection(self.selections[self.currentSelectionIndex])

	def goForwardInSavedSelections(self):
		if self.currentSelectionIndex + 1 < len(self.selections):
			self.currentSelectionIndex += 1
			self.commandLine.delete(0, END)
			self.commandLine.insert(END, self.selections[self.currentSelectionIndex])
			self.makeSelection(self.selections[self.currentSelectionIndex])

	def makeSelection(self, selection):
		if not self.stories:
			self.commandLine.delete(0, END)
			return
		self.copyFrom.insert(END, "%s\n" % selection)
		self.storyText.delete(1.0, END)
		if selection[0] == "*":
			showInfo = True
			selection = selection[1:]
		else:
			showInfo = False
		if selection:
			# find:happy
			# find text in a story
			if selection.find("find:") >= 0:
				findAndWhat = selection.split(":")
				whatToFind = findAndWhat[1].strip()
				storiesToShow = findStoriesWithText(self.stories, whatToFind)
				if storiesToShow:
					for story in storiesToShow:
						if showInfo:
							self.storyText.insert(END, story.allDetailsForDisplay(self.questions))
						else:
							self.storyText.insert(END, '\n\n%s\n\n%s\n\n' % (story.title, story.text))
					self.storyText.see(1.0)
					self.numStoriesSelectedStringVar.set("%s stories found" % len(storiesToShow))
				else:
					self.storyText.insert(END, "No result for %s" % selection)
					self.numStoriesSelectedStringVar.set("No selection")
			# random
			# pull up random story
			elif selection.lower().strip() == "random":
				randomIndex = random.randrange(len(self.stories))
				self.storyText.insert(END, self.stories[randomIndex].allDetailsForDisplay(self.questions))
				self.numStoriesSelectedStringVar.set("random story")
		    # #12
		    # choose story by number (add + to show codes, for checking data)
			elif selection.lower().strip().find("#") >= 0:
				storyIndexString = stringBeyond(selection.lower().strip(), "#")
				includeCodes = False
				if storyIndexString.find("+") >= 0:
					realStoryIndexString = stringUpTo(storyIndexString, "+")
					includeCodes = True
				else:
					realStoryIndexString = storyIndexString
				try:
					storyIndex = int(realStoryIndexString) - 1
					self.storyText.insert(END, self.stories[storyIndex].allDetailsForDisplay(self.questions, includeCodes=includeCodes))
					self.numStoriesSelectedStringVar.set("story %s" % (storyIndex + 1))
				except:
					self.storyText.insert(END, "No result for %s" % selection)
					self.numStoriesSelectedStringVar.set("No selection")
			else:
				selectionParts = selection.split(":")
				if len(selectionParts) == 1:
					# When I went to the zoo
					# no colon, must be story name
					storiesToShow = gatherStoriesWithTitle(self.stories, selection)
					if storiesToShow:
						for story in storiesToShow:
							self.storyText.insert(END, story.allDetailsForDisplay(self.questions))
						self.numStoriesSelectedStringVar.set("%s stories with title '%s'" % (len(storiesToShow), selection))
					else:
						self.storyText.insert(END, "No result for %s" % selection)
						self.numStoriesSelectedStringVar.set("No selection")
				elif doesNotContainDigit(selection) or doesNotContainDash(selection):
					# Emotional tone, Feel about(...): positive, happy(...)
					# no numbers: must be question(s) and answer(s)
					questionNamesToReport, questionIDsToReport, answers, storiesToShow = gatherSelectionWithChoiceQuestionOnly(self.questions, self.stories, selection)
					if storiesToShow:
						self.addThemeCountsToStoryDisplay(storiesToShow, selection)
						self.storyText.insert(END, "%s -- %s stories\n\n" % (selection, len(storiesToShow)))
						number = 1
						for story in storiesToShow:
							self.storyText.insert(END, "=== #%s " % number)
							if showInfo:
								self.storyText.insert(END, '\n\n%s' % story.allDetailsForDisplay(self.questions))
							else:
								self.storyText.insert(END, '\n\n%s\n\n%s\n\n' % (story.title, story.text))
							number += 1
						self.storyText.see(0.0)
						self.numStoriesSelectedStringVar.set("%s stories selected" % len(storiesToShow))
					else:
						self.storyText.insert(END, "No result for %s" % selection)
						self.numStoriesSelectedStringVar.set("No selection")
				else:
					# Fairness, Ambition(...): 0-10,90-100(...): Emotional tone+Feel about(...): positive+happy(...)
					# colon, must be scale(s) and range(s)
					scaleNamesToReport, scaleIDsToReport, rangeStrings, questionNameToReport, answer, storiesToShow = gatherSelection(self.questions, self.stories, selection)
					allScaleValues = {}
					if storiesToShow:
						self.addThemeCountsToStoryDisplay(storiesToShow, selection)
						self.storyText.insert(END, "%s -- %s stories\n\n" % (selection, len(storiesToShow)))
						number = 1
						for story in storiesToShow:
							self.storyText.insert(END, "=== #%s " % number)
							scaleValueStrings = []
							for i in range(len(scaleNamesToReport)):
								value = story.gatherAnswersForQuestionID(scaleIDsToReport[i])[0]
								scaleValueStrings.append("%s %s" % (scaleNamesToReport[i], value))
								if not allScaleValues.has_key(scaleNamesToReport[i]):
									allScaleValues[scaleNamesToReport[i]] = []
								allScaleValues[scaleNamesToReport[i]].append(value)
							self.storyText.insert(END, ", ".join(scaleValueStrings))
							if questionNameToReport:
								self.storyText.insert(END, ", %s %s" % (questionNameToReport, answer))
							if showInfo:
								self.storyText.insert(END, '\n\n%s' % story.allDetailsForDisplay(self.questions))
							else:
								self.storyText.insert(END, '\n\n%s\n\n%s\n\n' % (story.title, story.text))
							number += 1
						for scaleName in allScaleValues:
							total = 0
							for value in allScaleValues[scaleName]:
								total += int(value)
							mean = round(total / len(allScaleValues[scaleName]), 2)
							self.storyText.insert(END, "Mean value for %s: %s\n" % (scaleName, mean))
						self.storyText.see(0.0)
						self.numStoriesSelectedStringVar.set("%s stories selected" % len(storiesToShow))
					else:
						self.storyText.insert(END, "No result for %s" % selection)
						self.numStoriesSelectedStringVar.set("No selection")
		else:
			self.numStoriesSelectedStringVar.set("No selection")
			
	def addThemeCountsToStoryDisplay(self, storiesToShow, selection):
		if DATA_HAS_THEMES:
			themesAndCountsSorted = themeCountsForSelectedStories(storiesToShow, THEMES_FILE_PATH)
			total = 0
			for theme, count in themesAndCountsSorted:
				total += count
			self.storyText.insert(END, 'THEMES\n\n%s (%s)\n' % (selection, total))
			for theme, count in themesAndCountsSorted:
				self.storyText.insert(END, "%s %s\n" % (count, theme))
			self.storyText.insert(END, "  Total: %s\n\n" % total)
