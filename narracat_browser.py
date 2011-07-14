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
		namesFrame = Frame(self, relief=SUNKEN, borderwidth=1)
		namesFrame.pack(side=RIGHT, fill=BOTH)
		
		self.quitButton = Button(namesFrame)
		self.quitButton["text"] = "  Quit   "
		self.quitButton["command"] = self.quit
		self.quitButton.pack(side=BOTTOM)
		
		font = tkFont.Font(family="Georgia", size=12)
		biggerFont = tkFont.Font(family="Georgia", size=16)

		self.copyFrom = Text(namesFrame, width=30, relief=SUNKEN, borderwidth=1, font=font)
		self.copyFrom.pack(side=BOTTOM, fill=BOTH, expand=YES)
		label = Label(namesFrame, text="Q & A (copy from here)", foreground='blue').pack(side=BOTTOM)
		
		self.help = Text(namesFrame, width=30, relief=SUNKEN, borderwidth=1, font=font)
		self.help.insert(END, helpText)
		self.help.pack(side=BOTTOM)
		label = Label(namesFrame, text="Help", foreground='blue').pack(side=BOTTOM)
		
		outputFrame = Frame(self, width=600)
		outputFrame.pack(side=LEFT, fill=BOTH)
	
		scrollbar = Scrollbar(outputFrame)
		scrollbar.pack(side=RIGHT, fill=Y)

		self.text = Text(outputFrame, wrap=WORD, width=100, undo=True, font=biggerFont, yscrollcommand=scrollbar.set)
		self.text.pack(side=TOP, fill=BOTH, expand=YES)
		scrollbar.config(command=self.text.yview)

		controlFrame = Frame(outputFrame, width=600, height=100)
		controlFrame.pack(side=BOTTOM, fill=BOTH, expand=NO)
		
		self.entry = Entry(controlFrame, width=50, font=biggerFont)
		self.entry.pack(side=TOP)
		self.entry.focus()                         
		self.entry.bind('<Return>', (lambda event: self.selectStoriesForTextBox()))   

		self.numStoriesSelectedStringVar = StringVar("")
		self.numStoriesSelected = Label(controlFrame, textvariable=self.numStoriesSelectedStringVar)
		self.numStoriesSelectedStringVar.set("No selection")
		self.numStoriesSelected.pack(side=BOTTOM)

		buttonsFrame = Frame(controlFrame)
		buttonsFrame.pack(side=BOTTOM)

		self.forwardButton = Button(buttonsFrame)
		self.forwardButton["text"] = "Forward"
		self.forwardButton["command"] = self.goForwardInSavedSelections
		self.forwardButton.pack(side=RIGHT)

		self.backButton = Button(buttonsFrame)
		self.backButton["text"] = "Back"
		self.backButton["command"] = self.goBackInSavedSelections
		self.backButton.pack(side=RIGHT)

		self.selectStories = Button(buttonsFrame)
		self.selectStories["text"] = "Select stories"
		self.selectStories["command"] = self.selectStoriesForTextBox
		self.selectStories.pack(side=RIGHT)

		self.copyButton = Button(buttonsFrame)
		self.copyButton["text"] = "  Copy   "
		self.copyButton["command"] = self.copy
		self.copyButton.pack(side=RIGHT)
		
	def initializeQABox(self):
		if self.questions:
			names = gatherScaleQuestionVeryShortNames(self.questions)
			names.insert(0, "SCALES")
			names.insert(0, " ")
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
		else:
			names = []
		self.copyFrom.insert(END, "\n".join(names))
		
	def copy(self):
		self.text.clipboard_clear()
		self.text.clipboard_append(self.text.get(1.0, END))
		
	def selectStoriesForTextBox(self):
		selection = self.entry.get()
		self.selections.append(selection)
		self.currentSelectionIndex = len(self.selections) - 1
		self.makeSelection(self.selections[self.currentSelectionIndex])
		
	def goBackInSavedSelections(self):
		if self.currentSelectionIndex + 1 > 0:
			self.currentSelectionIndex -= 1
			self.entry.delete(0, END)
			self.entry.insert(END, self.selections[self.currentSelectionIndex])
			self.makeSelection(self.selections[self.currentSelectionIndex])

	def goForwardInSavedSelections(self):
		if self.currentSelectionIndex + 1 < len(self.selections):
			self.currentSelectionIndex += 1
			self.entry.delete(0, END)
			self.entry.insert(END, self.selections[self.currentSelectionIndex])
			self.makeSelection(self.selections[self.currentSelectionIndex])

	def makeSelection(self, selection):
		if not self.stories:
			self.entry.delete(0, END)
			return
		self.copyFrom.insert(1.0, "%s\n" % selection)
		self.text.delete(1.0, END)
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
							self.text.insert(END, story.allDetailsForDisplay(self.questions))
						else:
							self.text.insert(END, '\n\n%s\n\n%s\n\n' % (story.title, story.text))
					self.text.see(1.0)
					self.numStoriesSelectedStringVar.set("%s stories found" % len(storiesToShow))
				else:
					self.text.insert(END, "No result for %s" % selection)
					self.numStoriesSelectedStringVar.set("No selection")
			# random
			# pull up random story
			elif selection.lower().strip() == "random":
				randomIndex = random.randrange(len(self.stories))
				self.text.insert(END, self.stories[randomIndex].allDetailsForDisplay(self.questions))
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
					self.text.insert(END, self.stories[storyIndex].allDetailsForDisplay(self.questions, includeCodes=includeCodes))
					self.numStoriesSelectedStringVar.set("story %s" % (storyIndex + 1))
				except:
					self.text.insert(END, "No result for %s" % selection)
					self.numStoriesSelectedStringVar.set("No selection")
			else:
				selectionParts = selection.split(":")
				if len(selectionParts) == 1:
					# When I went to the zoo
					# no colon, must be story name
					storiesToShow = gatherStoriesWithTitle(self.stories, selection)
					if storiesToShow:
						for story in storiesToShow:
							self.text.insert(END, story.allDetailsForDisplay(self.questions))
						self.numStoriesSelectedStringVar.set("%s stories with title '%s'" % (len(storiesToShow), selection))
					else:
						self.text.insert(END, "No result for %s" % selection)
						self.numStoriesSelectedStringVar.set("No selection")
				elif doesNotContainDigit(selection) or doesNotContainDash(selection):
					# Emotional tone, Feel about(...): positive, happy(...)
					# no numbers: must be question(s) and answer(s)
					questionNamesToReport, questionIDsToReport, answers, storiesToShow = gatherSelectionWithChoiceQuestionOnly(self.questions, self.stories, selection)
					if storiesToShow:
						self.addThemeCountsToStoryDisplay(storiesToShow, selection)
						self.text.insert(END, "%s -- %s stories\n\n" % (selection, len(storiesToShow)))
						number = 1
						for story in storiesToShow:
							self.text.insert(END, "=== #%s " % number)
							if showInfo:
								self.text.insert(END, '\n\n%s' % story.allDetailsForDisplay(self.questions))
							else:
								self.text.insert(END, '\n\n%s\n\n%s\n\n' % (story.title, story.text))
							number += 1
						self.text.see(0.0)
						self.numStoriesSelectedStringVar.set("%s stories selected" % len(storiesToShow))
					else:
						self.text.insert(END, "No result for %s" % selection)
						self.numStoriesSelectedStringVar.set("No selection")
				else:
					# Fairness, Ambition(...): 0-10,90-100(...): Emotional tone+Feel about(...): positive+happy(...)
					# colon, must be scale(s) and range(s)
					scaleNamesToReport, scaleIDsToReport, rangeStrings, questionNameToReport, answer, storiesToShow = gatherSelection(self.questions, self.stories, selection)
					allScaleValues = {}
					if storiesToShow:
						self.addThemeCountsToStoryDisplay(storiesToShow, selection)
						self.text.insert(END, "%s -- %s stories\n\n" % (selection, len(storiesToShow)))
						number = 1
						for story in storiesToShow:
							self.text.insert(END, "=== #%s " % number)
							scaleValueStrings = []
							for i in range(len(scaleNamesToReport)):
								value = story.gatherAnswersForQuestionID(scaleIDsToReport[i])[0]
								scaleValueStrings.append("%s %s" % (scaleNamesToReport[i], value))
								if not allScaleValues.has_key(scaleNamesToReport[i]):
									allScaleValues[scaleNamesToReport[i]] = []
								allScaleValues[scaleNamesToReport[i]].append(value)
							self.text.insert(END, ", ".join(scaleValueStrings))
							if questionNameToReport:
								self.text.insert(END, ", %s %s" % (questionNameToReport, answer))
							if showInfo:
								self.text.insert(END, '\n\n%s' % story.allDetailsForDisplay(self.questions))
							else:
								self.text.insert(END, '\n\n%s\n\n%s\n\n' % (story.title, story.text))
							number += 1
						for scaleName in allScaleValues:
							total = 0
							for value in allScaleValues[scaleName]:
								total += int(value)
							mean = round(total / len(allScaleValues[scaleName]), 2)
							self.text.insert(END, "Mean value for %s: %s\n" % (scaleName, mean))
						self.text.see(0.0)
						self.numStoriesSelectedStringVar.set("%s stories selected" % len(storiesToShow))
					else:
						self.text.insert(END, "No result for %s" % selection)
						self.numStoriesSelectedStringVar.set("No selection")
		else:
			self.numStoriesSelectedStringVar.set("No selection")
			
	def addThemeCountsToStoryDisplay(self, storiesToShow, selection):
		if DATA_HAS_THEMES:
			themesAndCountsSorted = themeCountsForSelectedStories(storiesToShow, THEMES_FILE_PATH)
			total = 0
			for theme, count in themesAndCountsSorted:
				total += count
			self.text.insert(END, 'THEMES\n\n%s (%s)\n' % (selection, total))
			for theme, count in themesAndCountsSorted:
				self.text.insert(END, "%s %s\n" % (count, theme))
			self.text.insert(END, "  Total: %s\n\n" % total)
