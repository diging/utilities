# Metadata matcher script

This script is used for matching journal articles and metadata. Requires Python 3.6+ and [`pandas`](https://pypi.org/project/pandas/)

## Configuration

Set the following configurations in `config.py`

* `DIRECTORY` - Path to the parent folder containing all relevant files
* `METADATA_FILE` - Path to journal metadata file: supports `.xlsx` and `.csv` files
* `TEXT_FILES_FOLDER` - Folder containing all the raw journal article text files. Supports nested folder structure
* `NOT_FOUND_FOLDER` - Path to an empty folder. All the unmatched raw text files will be copied here
* `FOUND_METADATA` - Path to the target metadata file: supports `.csv`. This is a copy of `METADATA_FILE`, prepended with 3 columns: **raw text** of the matched file, **path** of the matched file, and **matching score**.
* Set the `FLAG_USE_ABSTRACT = True` for including the ***abstract*** column in the matching process.

### Matching authors

The script supports two types of parsing authors from metadata file. 

1. Authors are listed in a single column. 
    * Example: `Yu, Zhongtang; Morrison, Mark`.
    * Set `META_AUTHOR_SINGLE_FIELD = True` for this case
    * Use `META_AUTHOR_SINGLE_SEPARATOR` to set the separator character
2. Authors are listed in multiple column.
    * Example: `AuthorFirstName1`, `AuthorLastName1`, `AuthorFirstName2`, `AuthorLastName2`, ... etc.
    * Set `META_AUTHOR_SINGLE_FIELD = False` for this case

## Run Script

After setting all configurations in `config.py`, run the following command:

```
python run_script.py
```

### Features

* The script overwrites the `FOUND_METADATA` file on every match. You can interrupt the program at any point. 
    * **Note**: If you interrupt the program while `FOUND_METADATA` file is being saved, the program will still finish saving and quit automatically (unless you forcefully try to stop it again).
* If `FOUND_METADATA` file already exists, the script will exclude the files already matched! This can be used as a ***checkpoint*** feature.

## Scoring

The current scoring schema is as follows:

### 1. Without Abstract (FLAG_USE_ABSTRACT = False)

```
title      - 30
authors    - 20
pmid       -  5
pmcid      -  5

Cutoff     - 50
```

### 2. With Abstract (FLAG_USE_ABSTRACT = True)

```
abstract   - 40
title      - 30
authors    - 20
pmid       -  5
pmcid      -  5

Cutoff     - 70
```