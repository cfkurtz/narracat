# -----------------------------------------------------------------------------------------------------------------
# NarraCat: Tools for Narrative Catalysis
# -----------------------------------------------------------------------------------------------------------------
# License: Affero GPL 1.0 http://www.affero.org/oagpl.html
# Google Code Project: http://code.google.com/p/narracat/
# Copyright 2011 Cynthia Kurtz
# -----------------------------------------------------------------------------------------------------------------
# This file:
#
# Main program
# to run this program, type at a command line "python narracat_main.py <base_dir>"
# where <base_dir> 
# -----------------------------------------------------------------------------------------------------------------


from narracat_launcher import *

def main():
		
	root = Tk()
	root.minsize(300,300)
	root.geometry("800x600")
	root.title("NarraCat: Tools for Narrative Catalysis")
	app = NarracatLauncher(master=root, questions=None, participants=None, stories=None)
	app.mainloop()

if __name__ == "__main__":
	main()
	