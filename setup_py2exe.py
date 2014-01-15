"""
Usage:
    python setup_py2exx.py py2exe
"""

from distutils.core import setup
import py2exe
import numpy

from distutils.filelist import findall
import os
import matplotlib
matplotlibdatadir = matplotlib.get_data_path()
matplotlibdata = findall(matplotlibdatadir)
matplotlibdata_files = []
for f in matplotlibdata:
    dirname = os.path.join('matplotlibdata', f[len(matplotlibdatadir)+1:])
    matplotlibdata_files.append((os.path.split(dirname)[0], [f]))

setup(console=['NarraCat.py'],
      options={'py2exe': {'packages':['matplotlib'],}},
      data_files=matplotlibdata_files
      )

