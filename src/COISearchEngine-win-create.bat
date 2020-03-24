@echo off
ECHO Installing conda environment env_COISE and COISearchEngine
call conda create -n env_COISE python=3.7
call activate env_COISE
call pip install -r requirements.txt
call deactivate env_COISE
ECHO Closing COISearchEngine
PAUSE