# COISE - Conflicts Of Interest Search Engine
Tool to search for COI tags in multiple pdf files

- Merge multiple pdfs in one pdf file
- Search for tags in merged pdf file
- Highlight found COI tags in additional pdf file
- Export found COI results into excel file

## Run standalone executable
### Windows

- Download standalone software for windows https://my.pcloud.com/publink/show?code=kZA88MkZOFRFkCiarDS1eYNbf66ohyJXHRDk

- Run COISearchEngine-win.bat in standaalone/win folder

## Install anaconda and python environment

## Windows

- Install ancanonda (https://www.anaconda.com/distribution/#windows)
- Add anaconda/bin path to your system path
- Run COISearchEngine-win-create.bat file to create conda environment and install requierements

## Mac OS

- Install ancanonda (https://docs.anaconda.com/anaconda/install/mac-os/)
- Add anaconda/bin path to your system path
- Run COISearchEngine-mac-create.bat file to create conda environment and install requierements

## Run script

## Windows

- Run COISearchEngine-win-run.bat to run the software

## Mac OS

- Run COISearchEngine-mac-run.bat to run the software

## Install from enviironment.yml

- Open terminal and go to src folder

- ```
  conda env create -f environment.yml
  ```

## Run python script

```python COISearchEngine.py --filepath_seetings ../settings/settings.yml```

## Build standalone executable

- Run COISearchEngine-build.bat script



