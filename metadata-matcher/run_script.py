import re
from math import isnan
from pathlib import Path
import shutil
import logging

from utils import Sheet


class Journal:
    def __init__(self, config):
        self.parent_dir = Path(config["parent_dir"])
        self.metadata = self.parent_dir / config["metadata"]
        self.folder = self.parent_dir / config["text_files_folder"]
        self.destination_not_found = self.parent_dir / \
            config["destination_not_found"]
        self.destination_found = self.parent_dir / config["destination_found"]
        self.use_abstract = config["use_abstract"]
        self.files = []  # Will hold files to be matched
        self.config = config
        self.scanned_files = []  # Files already scanned, retrieved from checkpoint

    def search(self):
        self._scan_metadata()
        self._scan_folder()
        self._perform_match()

    def _scan_folder(self):
        """
        Scan for the text files, retrieve the full paths
        """
        folder_path = Path(self.folder)
        logging.info(
            f"Scanning for '{self.config['text_files_glob']}' files inside '{folder_path}'")

        text_files = list(folder_path.glob(self.config["text_files_glob"]))
        logging.info(
            f"Found {len(text_files)} '{self.config['text_files_glob']}' files")

        if self.scanned_files:
            # Exclude scanned files
            for text_file in text_files:
                if str(text_file) not in self.scanned_files:
                    self.files.append(text_file)
        else:
            self.files = text_files

    def _scan_metadata(self):
        """
        Scan metadata sheet, retrieve all articles
        """
        if self.destination_found.exists():
            # Resume from checkpoint
            logging.info(
                f"Found existing checkpoint metadata - '{self.destination_found}'")
            logging.info(f"Scanning metadata - '{self.destination_found}'")
            self.sheet = Sheet(
                str(self.destination_found),
                self.config['columns'], 
                use_abstract=self.use_abstract, 
                append_path_cols=False
            )
            self.scanned_files = self.sheet.get_matched_files()
        else:
            logging.info(f"Scanning metadata - '{self.metadata}'")
            self.sheet = Sheet(
                str(self.metadata), self.config['columns'], use_abstract=self.use_abstract)
        
        logging.info(
            f"Found {len(self.sheet.articles)} rows inside the metadata sheet")

    def _perform_match(self):
        """
        Match metadata and text files
        """
        logging.info("Starting metadata matching")

        # Enumerate all text files
        for i, text_file in enumerate(self.files):
            logging.info(
                f"Scanning File ({i + 1}/{len(self.files)}) {text_file}")
            match_found = False

            # Enumerate each row in metadata sheet
            for article_meta in self.sheet.articles:
                cutoff = 70 if self.use_abstract else 50
                score = self._get_score_for_text(text_file, article_meta)
                if score >= cutoff:
                    logging.info("Found match")
                    self._found_match(text_file, article_meta, score)
                    match_found = True
                    break

            if not match_found:
                logging.info("No match found")
                self._copy_file_not_found(text_file)

            try:
                self._save_metadata()
            except KeyboardInterrupt:
                logging.info("Detected program shutdown signal")
                self._save_metadata()
                quit()

    def _save_metadata(self):
        logging.info(
            f"Saving matched files metadata to '{self.destination_found}'")
        self.sheet.save(self.destination_found)
        logging.info(
            f"Successfully saved matched files metadata to '{self.destination_found}'")

    def _get_score_for_text(self, text_file, article_meta):
        # Match contents of `text_file` and `article_meta`
        with open(text_file, encoding='utf8') as f:
            size_to_read = self._get_file_size_to_read(text_file)
            data = f.read(size_to_read)
            data_normalized = self._normalize(data)

            pmid = article_meta["pmid"]
            pmcid = article_meta["pmcid"]
            abstract = article_meta["abstract"]
            title = article_meta["title"]

            # Scoring
            score = 0
            if title and self._normalize(title) in data_normalized:
                score += 30
            if pmid and pmid in data:
                score += 5
            if pmcid and pmcid in data:
                score += 5
            if self.use_abstract and abstract and self._normalize(abstract) in data_normalized:
                score += 40

            if len(article_meta["authors"]) > 0:
                # Match all authors
                author_matches = 0
                for author in article_meta["authors"]:
                    first_name = self._normalize(author[0])
                    last_name = self._normalize(author[1])

                    if f"{last_name}{first_name}" in data_normalized:
                        author_matches += 1
                    elif f"{first_name}{last_name}" in data_normalized:
                        author_matches += 1

                author_match_percentage = author_matches / \
                    len(article_meta["authors"])
                score += 20 * author_match_percentage

            return score

    def _found_match(self, text_file, article_meta, score):
        with open(text_file, encoding='utf8') as f:
            data = f.read()
            raw_text = data.replace("\n", " ")
            self.sheet.append_found_text_info(
                article_meta["index"], text_file, raw_text, score
            )

    def _copy_file_not_found(self, text_file):
        # Copy `text_file` to `self.destination_not_found` folder
        shutil.copyfile(
            text_file,
            Path(self.destination_not_found) / Path(text_file).name
        )

    def _get_file_size_to_read(self, text_file):
        """
        Get the size (in bytes) of the `text_file` to read.
            * <=3000 bytes: read whole file
            * >3000 bytes <=6000 bytes: read 2/3rd of the file
            * >6000 bytes: read 1/3rd of the file
        """
        size = text_file.stat().st_size
        if size <= 3000:
            return size
        elif size > 3000 and size <= 6000:
            return int(size * 2 / 3)
        else:
            return int(size / 3)

    def _normalize(self, text):
        """
        remove all non-characters, convert to lowercase
        """
        return re.sub(r"\W", "", text.lower())


if __name__ == "__main__":
    from config import config

    logging.basicConfig(
        format=config["log_format"],
        datefmt=config["log_date_format"],
        level=config["log_level"]
    )
    journal = Journal(config=config)
    journal.search()
