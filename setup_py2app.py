"""
How to bundle NarraCat for Mac

1. Install py2app
2. Remove the build and dist folders under the NarraCat source folder
3. Open Terminal
4. Cd to the directory where NarraCat.py is found
5. Run this command

        python setup_py2app.py py2app
        
6. The app should be in the dist folder. Test it.

How to bundle NarraCat for Windows

1. Install 

"""

from setuptools import setup

APP = ['NarraCat.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

