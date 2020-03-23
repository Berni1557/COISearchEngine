@echo off
TITLE COISearchEngine
ECHO Building COISearchEngine!
call activate env_COISE
call python setup.py build
call conda deactivate
ECHO Closing COISearchEngine.