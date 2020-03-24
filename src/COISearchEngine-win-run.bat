@echo off
ECHO Starting COISearchEngine!
call activate env_COISE
call python COISearchEngine.py
call conda deactivate
ECHO Closing COISearchEngine.
PAUSE