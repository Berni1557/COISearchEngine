#!/bin/sh
ECHO "Starting COISearchEngine"
source activate env_COISE
python COISearchEngine.py
conda deactivate
ECHO "Closing COISearchEngine"
PAUSE