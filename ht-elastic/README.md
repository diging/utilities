# Script to index HathiTrust metadata into Elasticsearch

## How to use this script

The script indexes json metadata files retrieved from HathiTrust into Elasticsearch. It should be called as follows
`python ht-elastic.py [arguments]`

The following arguments can be passed:
  - `--input` or `-i` (required): The absolute path to the input file. 
  - `--host` or `-h`: The host name of the Elasticsearch instance used to index the input file. Defaults to `localhost`.
  - `--port` or `-p`: The port of the Elasticsearch instance used to index the input file. Defaults to `9200`.
  
  ## What are the other files?
  
  There are two other files needed for this script:
  - `requirements.txt`: Requirements file that can be passed into pip to install needed requirements.
  - `mapping.json`: Mapping file send to Elasticsearch that defines how metadata should be indexed.
