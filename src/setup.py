from cx_Freeze import setup, Executable

setup(name = "COISearchEngine" ,
      version = "0.1" ,
      description = "" ,
      executables = [Executable("COISearchEngine.py")])

#from setuptools import setup
#
#APP = ['COISearchEngine.py']
#DATA_FILES = []
#OPTIONS = {
# 'iconfile':'logo.icns',
# 'argv_emulation': True,
# 'packages': ['certifi'],
#}
#
#setup(
#    app=APP,
#    data_files=DATA_FILES,
#    options={'py2app': OPTIONS},
#    setup_requires=['py2app'],
#)