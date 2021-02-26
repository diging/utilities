from math import isnan
import pandas as pd


class ParseException(Exception):
    pass


class Sheet:
    def __init__(self, file_name, col_config, use_abstract=False, append_path_cols=True):
        self.file_name = file_name
        self.col_config = col_config
        self.use_abstract = use_abstract
        self.append_path_cols = append_path_cols
        self.parse_file()

    def parse_file(self):
        # Read metadata file
        if self.file_name.endswith("xlsx") or self.file_name.endswith("xls"):
            self.df = pd.read_excel(self.file_name)
        elif self.file_name.endswith("csv"):
            self.df = pd.read_csv(self.file_name)
        else:
            raise Exception(
                "Metadata file type should be one of .xslsx, .xsl, .csv")

        try:
            self._validate_cols()
        except ParseException as e:
            raise e

        # Iterate rows
        rows = 0
        self.articles = []
        for i, row in self.df.iterrows():
            title = self._parse(row[self.col_config["title"]])
            pmid = self._parse(row[self.col_config["pmid"]])
            pmcid = self._parse(row[self.col_config["pmcid"]])
            abstract = self._parse(
                row[self.col_config["abstract"]]) if self.use_abstract else ""

            authors = []
            # Case 1 --> All authors are in single column
            if self.col_config["author_single"]:
                authors_str = self._parse(
                    row[self.col_config["author_single_col"]])
                if authors_str:
                    authors_split = authors_str.split(
                        self.col_config["author_single_sep"])
                    for author in authors_split:
                        last_name, first_name = author.split(
                            ",")[0], author.split(",")[1]
                        authors.append([last_name, first_name])

            # Case 2 --> Authors are present in separate columns
            #            with common prefix
            else:
                for i in range(1, self.col_config["author_col_limit"] + 1):
                    first_name = row[f"{self.col_config['author_col_first']}{i}"]
                    last_name = row[f"{self.col_config['author_col_last']}{i}"]
                    if isinstance(last_name, str) and isinstance(first_name, str):
                        authors.append([last_name, first_name])
                    else:
                        break

            if title:
                self.articles.append({
                    "title": title,
                    "abstract": " ".join(abstract.split()[:10]) if abstract else None,
                    "pmid": pmid,
                    "pmcid": pmcid,
                    "authors": authors,
                    "index": rows
                })

            rows += 1

        # Add columns - text file path, text, score
        if self.append_path_cols:
            self.df[self.col_config["text_file"]] = ""
            self.df[self.col_config["raw_text"]] = ""
            self.df[self.col_config["score"]] = ""

    def get_matched_files(self):
        col = self.col_config["text_file"]
        matched_files = self.df[~self.df[col].isnull()][col].to_list()
        return matched_files

    def append_found_text_info(self, index, path, raw_text, score):
        self.df.loc[index, self.col_config["text_file"]] = path
        self.df.loc[index, self.col_config["raw_text"]] = raw_text
        self.df.loc[index, self.col_config["score"]] = str(score)

    def save(self, path):
        if self.append_path_cols:
            columns = self.df.columns.to_list(
            )[-3:] + self.df.columns.to_list()[:-3]
        else:
            columns = self.df.columns.to_list()

        self.df.to_csv(
            path,
            columns=columns,
            index=False,
        )

    def get_score_for_article(self, article_index):
        score = self._parse(self.df.loc[article_index, self.col_config["score"]])
        if not score:
            return 0
        return int(float(score)) # To convert "60.0" (str) to 60 (int)

    def get_text_file_for_article(self, article_index):
        return self.df.loc[article_index, self.col_config["text_file"]]

    def _validate_cols(self):
        cols = ['title', 'abstract', 'pmid', 'pmcid']
        for col in cols:
            if self.col_config[col] not in self.df.columns:
                raise ParseException(
                    f"Column {self.col_config[col]} does not exist in the metadata file")

    def _parse(self, field):
        if type(field) is float and not isnan(field):
            return str(int(field))
        if type(field) is str:
            return field
        if type(field) is int:
            return str(field)
