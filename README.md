# COISE - Conflicts Of Interest Search Engine
Tool to search for COIs tags in multiple pdf files, merge all pdfs in one pdf file, highlight found COIs in additional pdf and export found COI results in excel file.

## Run standalone executable
### Windows

- Download standalone software for windows https://my.pcloud.com/publink/show?code=kZA88MkZOFRFkCiarDS1eYNbf66ohyJXHRDk

- Run COISearchEngine-win.bat

### Mac OS

- Download standalone software for mac os https://my.pcloud.com/publink/show?code=kZkQ8MkZaw8m59aVkMbOuN5vt2Hv45fWStGy

- Run COISearchEngine-win.bat

## Install python environment
python COISearchEngine.py --filepath_seetings H:/cloud/cloud_data/Projects/COISE/settings/settings.yml

## Run python script

```python COISearchEngine.py --filepath_seetings ../settings/settings.yml```

## Build standalone executable
- Run COISearchEngine-build.bat script

## Install conda environment

- Create conda environment with src/environments.yml file

```py
conda env create --name env_COISE --file=environments.yml
```







