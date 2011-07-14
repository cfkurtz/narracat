# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Common constants
# -----------------------------------------------------------------------------------------------------------------

import os, sys

# specify base path in command-line argument, or leave blank to use path where script is located

# narracat expects to find files in these folders:
#	base
#		config
#			narracat_config.py (optional; if not specified will use one where main script is found)
#		data
#			data.csv (required)
#			labels.csv (required)
#			themes.csv (optional)
#			(narracat will write pickle.txt here)
#		output
#			(narracat will write lots of files here)
			
if len(sys.argv) > 1: 
	BASE_PATH = sys.argv[1]
else:
	BASE_PATH = os.path.dirname(sys.argv[0])
print 'Starting narracat with Base Path"', BASE_PATH, '"'

DATA_PATH = BASE_PATH + os.sep + "data" + os.sep
if not os.path.exists(DATA_PATH):
	os.mkdir(DATA_PATH)

# default file names - can override in local narracat_config file
PICKLE_FILE_NAME = "pickle.txt"
DATA_FILE_NAME = "data.csv"
LABELS_FILE_NAME = "labels.csv"
DATA_HAS_THEMES = True
THEMES_FILE_NAME = "themes.csv"

CONFIG_PATH = BASE_PATH + os.sep + "config" + os.sep
if os.path.exists(CONFIG_PATH) and os.path.exists("%s%snarracat_config.py" % (os.sep, CONFIG_PATH)):
	sys.path.insert(0, CONFIG_PATH) 
	print '... Using configuration file narracat_config.py at %s' % CONFIG_PATH
else:
	pass
	print '... Using default configuration file narracat_config.py'
from narracat_config import *

# default file names - can override in local narracat_config file
DATA_FILE_PATH = DATA_PATH + DATA_FILE_NAME
LABELS_FILE_PATH = DATA_PATH + LABELS_FILE_NAME
THEMES_FILE_PATH = DATA_PATH + THEMES_FILE_NAME

if DATA_HAS_SLICES:
	OUTPUT_PATH = BASE_PATH + os.sep + "output by " + SLICE_QUESTION_ID + os.sep
else:
	OUTPUT_PATH = BASE_PATH + os.sep + "output" + os.sep
if not os.path.exists(OUTPUT_PATH):
	os.mkdir(OUTPUT_PATH)