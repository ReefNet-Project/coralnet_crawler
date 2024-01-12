# CoralNet Scraper

## Intro

this repo contains scripts to help scrape images from https://coralnet.ucsd.edu/ for research purposes, the scripts deal only with the open sources images that are publicly accissible, this project fits into the efforts of a research project aimed to use AI to automatically identify corals. 

## Details

to run the script

1. first that you have all the modules used inside the files like pandas and beautiful soup ...etc.
2. prepare a csv file called sources that contains the list of valid sources for download
3. run get_sources_data.py to gather the necessary information about all sources from coralnet website and save it into sources_data.csv
4. run scrape.py to download all images