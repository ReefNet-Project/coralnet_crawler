# CoralNet Scraper

## Intro

This code is provided as part of the ReefNet project, and specifically the ReerNet paper submitted to NeurIPS Dataset and Benchmark track 2025, find details here: [link](https://reefnet-project.github.io/reefnet-2025/)

this repo contains scripts to help scrape images from https://coralnet.ucsd.edu/ for research purposes, the scripts deal only with the public sources images that are publicly accissible, this project fits into the efforts of a research project aimed to use AI to automatically identify corals. 

## Details

to run the script

1. first that you have all the modules used inside the files like pandas and beautiful soup ...etc.
2. prepare a csv file called sources that contains the list of valid sources for download
3. run get_sources_data.py to gather the necessary information about all sources from coralnet website and save it into sources_data.csv
4. run scrape.py to download all images
5. to run scarpe_annotations.py you need to make copy of .example.env and rename it .env and put your credentials in it then you can run it to download all annotations.