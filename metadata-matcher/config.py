import os
import logging

# =============================================================================
# CONFIGURATION
#
# You can override the configuration using environment variables
# Example:
#   $ export DIRECTORY = "/Users/user/Documents"
#   $ export METADATA_FILE="path/to/meta/file.xlsx"
# =============================================================================

## Paths
DIRECTORY = "."
METADATA_FILE = "metadata/Cleaned Data 1900-2017.xlsx"
TEXT_FILES_FOLDER = "files"
NOT_FOUND_FOLDER = "not_found"
FOUND_METADATA = "found.csv"

## Scoring
SCORE_TITLE = 30
SCORE_AUTHORS = 20
SCORE_PMID = 5
SCORE_PMCID = 5
SCORE_ABSTARCT = 40
CUT_OFF_WITHOUT_ABSTRACT = 50
CUT_OFF_WITH_ABSTRACT = 70

## Misc
FLAG_USE_ABSTRACT = False
TEXT_FILES_DEFAULT_ENCODING = "utf-8" # Fallback encoding if script is unable to auto-detect
TEXT_FILES_GLOB = "**/*.txt"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%m/%d/%Y %I:%M:%S %p"
LOG_LEVEL = logging.getLevelName("INFO")

## Column names currently present in the metadata file
META_COL_TITLE = "Title"
META_COL_ABSTRACT = "Abstract"
META_COL_PMID = "PMID"
META_COL_PMCID = "PMCID"

## How the authors are parsed
META_AUTHOR_SINGLE_FIELD = False
META_AUTHOR_SINGLE_SEPARATOR = ";"
META_AUTHOR_SINGLE_COL = "Authors"

# If `META_AUTHOR_SINGLE_FIELD=False`,
# we assume the authors are present in multiple columns
# Example ->
#   `AuthorFirstName1`, `AuthorLastName1`, `AuthorFirstName2`, `AuthorLastName2`, ... etc.
#   upto `META_AUTHOR_COL_LIMIT` authors
META_AUTHOR_COL_FIRST_NAME_PREFIX = "AuthorFirstName"
META_AUTHOR_COL_LAST_NAME_PREFIX = "AuthorLastName"
META_AUTHOR_COL_LIMIT = 10

## Column names appended for matched text files
META_COL_TEXT_FILE_PATH = "Text file"
META_COL_SCORE = "Score"
META_COL_RAW_TEXT = "Raw text"

# =============================================================================
# DO NOT EDIT BELOW
# =============================================================================
config = {
    "parent_dir": os.environ.get("DIRECTORY", DIRECTORY),
    "metadata": os.environ.get("METADATA_FILE", METADATA_FILE),
    "text_files_folder": os.environ.get(
        "TEXT_FILES_FOLDER", TEXT_FILES_FOLDER
    ),
    "destination_not_found": os.environ.get(
        "NOT_FOUND_FOLDER", NOT_FOUND_FOLDER
    ),
    "destination_found": os.environ.get("FOUND_METADATA", FOUND_METADATA),
    "scoring": {
        "title": os.environ.get("SCORE_TITLE", SCORE_TITLE),
        "authors": os.environ.get("SCORE_AUTHORS", SCORE_AUTHORS),
        "pmid": os.environ.get("SCORE_PMID", SCORE_PMID),
        "pmcid": os.environ.get("SCORE_PMCID", SCORE_PMCID),
        "abstract": os.environ.get("SCORE_ABSTARCT", SCORE_ABSTARCT),
        "cut_off_without_abstract": os.environ.get("CUT_OFF_WITHOUT_ABSTRACT", CUT_OFF_WITHOUT_ABSTRACT),
        "cut_off_with_abstract": os.environ.get("CUT_OFF_WITH_ABSTRACT", CUT_OFF_WITH_ABSTRACT),
    },
    "text_files_default_encoding": os.environ.get("TEXT_FILES_DEFAULT_ENCODING", TEXT_FILES_DEFAULT_ENCODING),
    "text_files_glob": os.environ.get("TEXT_FILES_GLOB", TEXT_FILES_GLOB),
    "use_abstract": os.environ.get("FLAG_USE_ABSTRACT", FLAG_USE_ABSTRACT),
    "log_format": os.environ.get("LOG_FORMAT", LOG_FORMAT),
    "log_date_format": os.environ.get("LOG_DATE_FORMAT", LOG_DATE_FORMAT),
    "log_level": os.environ.get("LOG_LEVEL", LOG_LEVEL),
    "columns": {
        "title": os.environ.get("META_COL_TITLE", META_COL_TITLE),
        "abstract": os.environ.get("META_COL_ABSTRACT", META_COL_ABSTRACT),
        "pmid": os.environ.get("META_COL_PMID", META_COL_PMID),
        "pmcid": os.environ.get("META_COL_PMCID", META_COL_PMCID),
        "text_file": os.environ.get(
            "META_COL_TEXT_FILE_PATH", META_COL_TEXT_FILE_PATH
        ),
        "score": os.environ.get("META_COL_SCORE", META_COL_SCORE),
        "raw_text": os.environ.get("META_COL_RAW_TEXT", META_COL_RAW_TEXT),
        "author_single": os.environ.get("META_AUTHOR_SINGLE_FIELD", META_AUTHOR_SINGLE_FIELD),
        "author_single_sep": os.environ.get("META_AUTHOR_SINGLE_SEPARATOR", META_AUTHOR_SINGLE_SEPARATOR),
        "author_single_col": os.environ.get("META_AUTHOR_SINGLE_COL", META_AUTHOR_SINGLE_COL),
        "author_col_first": os.environ.get("META_AUTHOR_COL_FIRST_NAME_PREFIX", META_AUTHOR_COL_FIRST_NAME_PREFIX),
        "author_col_last": os.environ.get("META_AUTHOR_COL_LAST_NAME_PREFIX", META_AUTHOR_COL_LAST_NAME_PREFIX),
        "author_col_limit": os.environ.get("META_AUTHOR_COL_LIMIT", META_AUTHOR_COL_LIMIT)
    },
}
