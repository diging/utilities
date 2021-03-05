# Metadata matcher script

This script matches metadata entries of articles in a `CSV/XLSX` file, with plain text files containing the content of the articles listed in the metadata file. It does so by comparing certain columns from metadata such as `title` and `authors` (configurable) with the plain text. Each column match is assigned with a score, and if the total score exceeds a cutoff score, it is considerd a match. Requires Python 3.6+.

**Install the dependencies**

```
pip install -r requirements.txt
```

## Configuration

Set the following configurations in `config.py`

* `DIRECTORY` - Path to the parent folder containing metadata file and plain text files. Accepts both relative (to where the script is run from), and absolute path.
* `METADATA_FILE` - Path to article metadata file: supports `.xlsx` and `.csv` files (Relative to `DIRECTORY`).
* `TEXT_FILES_FOLDER` - Folder containing all the raw journal article text files. Supports nested folder structure (Relative to `DIRECTORY`).
* `NOT_FOUND_FOLDER` - Path to an empty folder. All the unmatched raw text files will be copied here (Relative to `DIRECTORY`).
* `FOUND_METADATA` - Path to the target metadata file: supports `.csv`. This is a copy of `METADATA_FILE`, prepended with 3 columns: **raw text** of the matched file, **path** of the matched file, and **matching score** (Relative to `DIRECTORY`).
* Set the `FLAG_USE_ABSTRACT = True` for including the ***abstract*** column in the matching process.

### Matching authors

The script supports two types of parsing authors from metadata file. 

1. Authors are listed in a single column. 
    * Example: `Yu, Zhongtang; Morrison, Mark`.
    * Set `META_AUTHOR_SINGLE_FIELD = True` for this case.
    * Use `META_AUTHOR_SINGLE_SEPARATOR` to set the separator character between multiple authors - `;` in this case.
2. Authors are listed in multiple columns.
    * Example: `AuthorFirstName1`, `AuthorLastName1`, `AuthorFirstName2`, `AuthorLastName2`, ... etc.
    * The number of authors is limited to `10` (i.e. upto `AuthorFirstName10`). This can be changed using the config `META_AUTHOR_COL_LIMIT`.
    * The prefix `AuthorFirstName` and `AuthorLastName` can be changed with the config `META_AUTHOR_COL_FIRST_NAME_PREFIX` and `META_AUTHOR_COL_LAST_NAME_PREFIX` respectively.
    * Set `META_AUTHOR_SINGLE_FIELD = False` for this case.

## Run Script

After setting all configurations in `config.py`, run the following command:

```
python run_script.py
```

### Features

* The script overwrites the `FOUND_METADATA` file on every match. You can interrupt the program at any point by pressing `Control + C`. 
    * **Note**: If you interrupt the program while `FOUND_METADATA` file is being saved, the program will still finish saving and quit automatically (unless you forcefully try to stop it again).
* If `FOUND_METADATA` file already exists, the script will exclude the files already matched! This can be used as a ***checkpoint*** feature.
* You can run `python run_script.py` again to restart the program from the checkpoint.
* For restarting the process from the beginning, either delete the `FOUND_METADATA` file, or provide a different name for `FOUND_METADATA`. 

## Scoring

* `Title` field must match completely - ignoring the case, whitespaces, and special characters.
    - **Example:** `THIS is a sample   -title` and `This is A sample title` are matched.
* First 10 words of the `Abstract` field must match completely - ignoring the case, whitespaces, and special characters.
* `PMID` and `PMCID` fields must match completely.
* `Authors` are matched if either `FirstName LastName` or `LastName FirstName` are matched completely - ignoring the case, whitespaces, and special characters.
    - **Example:** `John Doe` and `DOE, JOHN` are matched.
    - If there are `10` authors, and only `6` are matched, the scoring would be `20 x 0.6 = 14`.

The current scoring schema is as follows:

### 1. Without Abstract (FLAG_USE_ABSTRACT = False)

```
title      - 30
authors    - 20 x percentage of authors matched
pmid       -  5
pmcid      -  5

Cutoff     - 50
```

### 2. With Abstract (FLAG_USE_ABSTRACT = True)

```
abstract   - 40
title      - 30
authors    - 20 x percentage of authors matched
pmid       -  5
pmcid      -  5

Cutoff     - 70
```