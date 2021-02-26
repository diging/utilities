import re
import chardet
from math import isnan
from pathlib import Path
import shutil
import logging

from utils import Sheet


class MetadataEntries:
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
        self.scoring = config["scoring"]
        self.scanned_files = []  # Files already scanned, retrieved from checkpoint

    def match(self):
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

            text_content = self._get_text_content(text_file)

            # Enumerate each row in metadata sheet
            for article_meta in self.sheet.articles:
                if self.use_abstract:
                    cutoff = self.scoring["cut_off_with_abstract"]
                else:
                    cutoff = self.scoring["cut_off_without_abstract"]

                score = self._get_score_for_text(text_content, article_meta)
                if score >= cutoff:
                    existing_score = self.sheet.get_score_for_article(article_meta["index"])
                    if score > existing_score:
                        logging.info("Found match")
                        self._found_match(text_file, article_meta, score)
                        match_found = True
                        break

            if not match_found:
                logging.info("No match found")
                self._copy_file_not_found(text_file)
            else:
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

    def _get_score_for_text(self, text_content, article_meta):
        # Match contents of `text_content` and `article_meta`
        data_normalized = self._normalize(text_content)

        pmid = article_meta["pmid"]
        pmcid = article_meta["pmcid"]
        abstract = article_meta["abstract"]
        title = article_meta["title"]

        # Scoring
        score = 0
        if title and self._normalize(title) in data_normalized:
            score += self.scoring["title"]
        if pmid and pmid in text_content:
            score += self.scoring["pmid"]
        if pmcid and pmcid in text_content:
            score += self.scoring["pmcid"]
        if self.use_abstract and abstract and self._normalize(abstract) in data_normalized:
            score += self.scoring["abstract"]

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
            score += self.scoring["authors"] * author_match_percentage

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

    def _get_text_content(self, text_file):
        with open(text_file, 'rb') as f:
            size_to_read = self._get_file_size_to_read(text_file)
            data = f.read(size_to_read)
            encoding, confidence = self._get_text_encoding(data)
            if confidence > 0.7:
                try:
                    data = str(data, encoding=encoding)
                    return data
                except UnicodeDecodeError:
                    encoding = self.config["text_files_default_encoding"]
            else:
                encoding = self.config["text_files_default_encoding"]
            
            data = str(data, encoding=encoding)
            return data

    def _get_text_encoding(self, raw_data):
        result = chardet.detect(raw_data)
        return result['encoding'], result['confidence']

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
    metadata_entries = MetadataEntries(config=config)
    metadata_entries.match()
