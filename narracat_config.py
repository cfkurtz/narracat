# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Configuration particular to project
# -----------------------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------------------
# file names - overrides from defaults of "pickle.txt", "data.csv", "labels.csv", "themes.csv"
# better to use the defaults when possible! less to remember
# -----------------------------------------------------------------------------------------------------------------

DATA_FILE_NAME = "data.csv"
LABELS_FILE_NAME = "labels.csv"
PICKLE_FILE_NAME = "pickle.txt"

# to read from two or more data files with the same format, use this method
# there is no checking for redundancy of participants between files (ie no participant should be in more than one file)
HAS_MULTIPLE_DATA_FILES = False 
MULTIPLE_DATA_FILE_NAMES = []

DATA_HAS_THEMES = False
THEMES_FILE_NAME = "themes.csv"

DOES_NOT_APPLY = "N/A"
NO_ANSWER = "No answer"
ALL_ANSWERS = "All answers"
NO_STORY_TITLE = "Untitled"
NO_STORY_TEXT = "No story text"

# -----------------------------------------------------------------------------------------------------------------
# data column types as referenced in data format specification CSV file
# -----------------------------------------------------------------------------------------------------------------

# single choice question with one answer per cell (may be raw data or may be a lookup code linking to meaning in labels file)
TYPE_SINGLE_CHOICE = "Single Value Radio Buttons"

# multiple choice question with one answer per cell (may be raw data or may be a code)
TYPE_MULTI_CHOICE = "Multi Value Check Box"

# multiple choice question with multiple delimited answers in one cell (each may be raw data or may be a code)
TYPE_MULTIPLE_CHOICE_DELIMITED = "Single Value Delimited Radio Buttons"
MULTIPLE_CHOICE_DELIMITED_DELIMITER = "|"

# story text
TYPE_STORY_BOX = "Story Text Box" 

# any text OTHER than main story text that is NOT the title
TYPE_COMMENT_BOX = "Open-End Text Box"

# free entry text - including story title
TYPE_REGULAR_TEXT_BOX = "Other Text Box"

# also free entry text, but numerical. not yet used for anything other than free entry.
TYPE_NUMERICAL_TEXT_BOX = "Numeric Text Box"

# numerical range, usually one number but could be two complementary (second one is ignored)
TYPE_SLIDER = "Matrix Radio Buttons"

# do-not-graph sliders are for questions that were asked as sliders but are not important to graph (cluttery)
TYPE_SLIDER_DO_NOT_GRAPH = "Matrix Radio Buttons (do not graph)"

# three complementary numbers that add up to 100
TYPE_TERNARY = "Three dimension values"

# -----------------------------------------------------------------------------------------------------------------
# accommodating variations in data file structures
# -----------------------------------------------------------------------------------------------------------------

# commented lines at beginning
LINES_TO_SKIP_AT_START_OF_DATA_FILE = 2

# set this higher than will ever be used
MAX_POSSIBLE_STORIES_PER_PARTICIPANT = 15
# sometimes a person is a line with multiple stories in it; sometimes a person is several lines, one per story
PARTICIPANTS_COVER_MULTIPLE_ROWS_IN_DATA_FILE = True

# these help read survey output when stories were elicited one after another (story 1 then story 2, etc)
# when the questions have identical ids they will be merged
HAS_SEPARATE_QUESTIONS_FOR_SEPARATE_STORIES = False
FORMAT_FILE_HAS_STORY_NUMBER_COLUMN = False # can specify story number of question by separate column in format file
STORY_NUMBER_SUFFIX = None # or can specify it by a suffix to the field ID

# in some surveys the story title/text can be entered in more than one place
# this will read only non-blank entries in all possible title/text columns
MULTIPLE_STORY_TITLE_FIELDS = False
MULTIPLE_STORY_TEXT_FIELDS = False

# is the question answered in the data, or do you have to figure it out 
QUESTION_NUMBER_APPEARS_AS_QUESTION = True
QUESTION_NUMBER_ID = "Question answered"
QUESTION_NUMBER_NAMES = ["1", "2", "3", "4", "5", "6"]
INCLUDE_QUESTION_NUMBER_QUESTION = False

# ways to identify special fields - teller, name, text of story
PARTICIPANT_ID_FIELD = "Name of participant"
STORY_TITLE_FIELD = "Story title"
STORY_TEXT_FIELD = "Text"

# more on how things are arrayed in the data file

# some input formats have "1" in multiple-choice columns to mean "yes"
COLUMN_VALUES_ARE_ALL_ONES = False

# sometimes there is a numerical code that stands for a choice, and not the choice itself
DATA_TYPES_WITH_CODES = [TYPE_SLIDER, TYPE_SINGLE_CHOICE, TYPE_MULTI_CHOICE, TYPE_MULTIPLE_CHOICE_DELIMITED]

# sometimes for multi-choice questions the answers are arrayed out into columns, sometimes they are not
DATA_TYPES_WITH_MULTIPLE_COLUMNS_PER_QUESTION = [TYPE_SINGLE_CHOICE, TYPE_MULTI_CHOICE]

# specifications for sliders

# sometimes sliders have one value, sometimes a column for each possible value
SLIDERS_ARE_SINGLE_COLUMNS = True

# sometimes people put a slider value as just a number, like 25; sometimes two numbers, like 25/75
SLIDER_VALUE_HAS_TWO_DELIMITED_PARTS = True
TWO_PART_SLIDER_VALUE_DELIMITER = '/'

# sometimes the second number in the slider pair is not 25/75 but an "out of" number like 25/100
SLIDER_SECOND_PART_IS_MAXIMUM = True

# sliders don't always go from 1 to 100; sometimes it's 1 to 10 or even 1 to 5
SLIDER_START = 1
SLIDER_END = 100

# this is create a lookup list for slider values; you can ignore it
SLIDER_SHORT_NAMES = []
i = SLIDER_START
while i <= SLIDER_END:
	SLIDER_SHORT_NAMES.append(`i`)
	i += 1
SLIDER_SHORT_NAMES.append(DOES_NOT_APPLY)

# if you want to do a 3D landscape view you should have a slider whose value maps to the Z axis on the 3D graph; this is it
STABILITY_QUESTION_NAME = "Predictability: none to much"
# maybe you asked it backwards from the way you want to look at it?
STABILITY_QUESTION_VALUE_IS_REVERSED = True
# sometimes a slider is reversed in the asking, to make responses less automatic; 
# you can re-reverse them here for clarity when comparing answers
# when you do this, IF the slider covers multiple rows in your data file,
# you must reverse the column definitions in the format file to match the reversal
SLIDERS_TO_REVERSE = [
					"Remember: trivial to never forget", 
					"Behaviour: despicable to admirable",
					]

# SLICES with which to consider subsets of data separately; see narracat_slice.py
DATA_HAS_SLICES = False
# these are examples
SLICE_QUESTION_ID = "Position"
SLICES_TO_CREATE = ["Manager", "Employee"]

ALL_DATA_SLICE = "All"
SLICES = []
if DATA_HAS_SLICES:
	SLICES.extend(SLICES_TO_CREATE)
SLICES.append(ALL_DATA_SLICE)

# specifications for ternary values (ternarys)
DATA_HAS_TERNARY_SETS = False
TERNARY_VALUE_DELIMITER = '"'

# added lumped (merged) answers column to data format file in January 2011 
# this is for backward compatibility with earlier format files - will normally be True
FORMAT_FILE_HAS_ANSWERS_LUMPING_COLUMN = True
USE_LUMPED_ANSWERS = True # you can use this to temporarily turn off lumping when you need it off

# -----------------------------------------------------------------------------------------------------------------
# how things look in the output
# -----------------------------------------------------------------------------------------------------------------

# setting limits to what graphs are generated
# this is for two reasons: to deal with small data sets (in which there may be very weak trends)
# and to reduce huge numbers of output files produced
# to see how these impact the particular tests, search for them in the other code files
LOWER_LIMIT_STORY_NUMBER_FOR_COMPARISONS = 20
SIGNIFICANCE_VALUE_REPORTING_THRESHOLD = 0.05
T_TEST_VALUE_REPORTING_THRESHOLD = 1.0
SKEW_DIFFERENCE_REPORTING_THRESHOLD = 1.0
CORRELATION_COEFF_REPORTING_THRESHOLD = 0.2
CONTINGENCY_PERCENTAGE_THRESHOLD = 0
INCLUDE_PERCENTAGES_IN_CONTINGENCY_DIAGRAMS = False


# if true, draws "companion" histograms for different-meaned subsets of data
# so you don't have to go looking for them
DRAW_COMPARISON_HISTOGRAMS_FOR_SIGNIFICANT_T_TESTS = True
DRAW_COMPARISON_HISTOGRAMS_FOR_SKEW_DIFFERENCES = True

# some choices should be excluded from choice comparisons because they are too small
EXCLUDE_FROM_CHI_SQUARED_TESTS = ["not sure"]

# how to draw slider data
NUM_HISTOGRAM_BINS = 10
LOWER_SCALE_EXTREME_FOR_HIGH_LOW_GRAPHS = 10
UPPER_SCALE_EXTREME_FOR_HIGH_LOW_GRAPHS = 90
PART_OF_SLIDER_NAME_TO_HIDE_FROM_GRAPHS = None 
DRAW_TRANSPARENT_DOTS_ON_SCATTER_GRAPHS = True # if few possible points, dots overlap

# writing to CSV
CSV_WRITE_AS_SINGLE_COLUMNS = [TYPE_SINGLE_CHOICE, TYPE_SLIDER, TYPE_COMMENT_BOX, TYPE_REGULAR_TEXT_BOX, TYPE_NUMERICAL_TEXT_BOX, TYPE_TERNARY]
CSV_WRITE_AS_MULTIPLE_COLUMNS = [TYPE_MULTI_CHOICE, TYPE_MULTIPLE_CHOICE_DELIMITED]
CSV_WRITE_MULTI_VALUE_IN_ONE_COL_DELIMITER = "|"
