# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Instructions
# -----------------------------------------------------------------------------------------------------------------

== System requirements

Any operating system will do. 

Regarding hard drive space, the program takes up hardly any itself. The thing is a gnat.
BUT it generates large numbers of large files, especially if you ask a lot of questions. 
I typically end up with an "output" folder between 0.5 and 1.0 GIGAbytes in size. 
So watch out for that. 

As for memory, I'm not sure what the limitations are. 
I have 10 GB of memory on my computer and I've never used it anywhere else. 
It might run slow if you have little memory.

== Installation

First, install python, scipy and matplotlib. 
This page 
    http://www.installationwiki.org/Installing_Matplotlib
has pretty good instructions for doing that. 
 
Next, check out the NarraCat source code from the Google Code site 
    http://code.google.com/p/narracat/

== Using NarraCat

You can open narracat_main.py in your editor and run it from there. 

You can use either IDLE (which comes with python) 
    http://docs.python.org/library/idle.html

or Eclipse:
    http://www.eclipse.org/

or another editor to edit any files you want to change.

OR you can open a terminal window, cd (change directory) to the folder to where you put NarraCat, and type

    python narracat_main.py {BASE_DIR} 

where {BASE_DIR} is the directory where you want NarraCat to read and write files. 

(If you are using an editor, put {BASE_DIR} in the command-line arguments
your editor will use to run narracat_main.py.)

== File locations

NarraCat expects to find files in these locations as it works:

BASE_DIR

... config

... ... narracat_config.py - here you put options specific to your project

... data

... ... data.csv - your data file in CSV format

... ... labels.csv - a description of what is in the data file (see example for format)

... ... themes.csv - optional themes to link stories to themes

... output

... ... (here NarraCat will write LOTS and LOTS of files)

And that's pretty much it!

== Reading data

NarraCat reads preadsheet data in CSV (comma-separated values) format. 
I have read several different data formats in the projects I have used NarraCat for so far, 
and wouldn't you know it, each had its own issues. 

So, the way you read your data is, you give NarraCat a clean, pretty CSV data file, 
and you also give it a clean, pretty "labels" file that tells it what is in the clean, pretty CSV file. 
There are example data and labels files in the examples directory.

== Sample data

In the examples folder there are sample data files you can use to try out NarraCat before
you have your own data to play with.
There are 20 fake stories repeated 3 times (because I ran out of patience making up stories).
Maybe someday somebody will take pity on the repeated stories and make up some more to take their place.

The labels file gives examples of specifying different types of questions.
The themes file gives examples of some themes you might identify in stories.

== Miscellaneous tips

- A good way to get to know the program is to run it with the sample data and then just poke around in the output.
- You can only do cluster analysis on respondents, not stories; and you can only do it if EVERY respondent
is represented by the SAME number of scale values.
- Files are always overwritten when you run the same operation again.
- If you want to consider with and without slices, run once with the DATA_HAS_SLICES flag on and once without.
- If you think you should see more output files, check your settings for how many stories there must be
to be considered as a group and how significant results should be. 

== Unpleasant things

- Normal output appears in the "console" panel on the NarraCat browser. Errors appear wherever you ran
the program from (your programming environment or the command line).
- The console panel thing doesn't update until all operations have completed. Messy, I know. 
Until I fix this I suggest running one operation at a time.
- 

== Bugs, questions, suggestions, help

Please write to cfkurtz at cfkurtz dot com for any of these.