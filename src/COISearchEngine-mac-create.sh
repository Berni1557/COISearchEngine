#!/bin/sh
ECHO "Installing conda environment env_COISE and COISearchEngine"
conda create -n env_COISE python=3.7
source activate env_COISE
pip install -r requirements.txt
deactivate env_COISE
ECHO "Closing COISearchEngine"
PAUSE