# CoralNet Crawler

**CoralNet Crawler** is a utility toolkit developed as part of the ReefNet project. It automates the process of collecting annotated underwater imagery from [CoralNet](https://coralnet.ucsd.edu), including source metadata, annotations, and image files. This forms the foundation of large-scale coral reef datasets used for machine learning-based reef classification and monitoring.

➡️ For more details, visit the ReefNet project homepage: [https://reefnet-project.github.io/reefnet-2025/](https://reefnet-project.github.io/reefnet-2025/)

---

## Table of Contents
- [Overview](#overview)
- [Project Structure](#project-structure)
- [File Descriptions](#file-descriptions)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Ethical Use](#ethical-use)
- [Citing This Work](#citing-this-work)
- [Contributors](#contributors)
- [License](#license)

---

## Overview

The CoralNet Crawler provides scripts for:

1. **Scraping Source Data**  
   Extract metadata and image counts from valid CoralNet sources.

2. **Downloading Annotations**  
   Authenticate via CoralNet and retrieve point annotations for each source.

3. **Downloading Images**  
   Download and verify images associated with each source.

---

## Project Structure

```bash
coralnet_crawler/
├── output/
│   └── Great_Barrier_Reef/
│       └── images/
├── metadata/
│   └── Great_Barrier_Reef_annotations.csv
├── sources.csv
├── sources_data.csv
├── .env
├── get_sources_data.py
├── scrape_annotations.py
├── scrape_labelsets.py
├── scrape_metadata.py
├── scrape.py
```

---

## File Descriptions

- **`get_sources_data.py`** — Scrapes general source info (URLs, image count) from `sources.csv` → `sources_data.csv`. This script is the first step and gathers all necessary metadata for subsequent scripts.
- **`scrape_annotations.py`** — Downloads annotations per source after login; logs to `scrape_annotations.log`
- **`scrape_labelsets.py`** — Downloads labelset CSV files for each source; saved under `metadata/<source_name>/labelset.csv`
- **`scrape_metadata.py`** — Scrapes and saves metadata including image counts and source URLs to `metadata/<source_name>/metadata_all.csv`
- **`scrape.py`** — Downloads and verifies image files; logs activity to `scrape_logs.log`
- **`sources.csv`** — Input list of CoralNet sources to process; sources marked `yes` under the `Valid` column are processed
- **`.example.env`** — Template for environment variables; copy to `.env` and populate with your CoralNet login credentials
- **`tasks.md`** — Notes and todos for internal tracking

---

## Setup and Installation

1. **Clone the Repository**
```bash
git clone https://github.com/ReefNet-Project/coralnet_crawler.git
cd coralnet_crawler
```

2. **Install Requirements**
```bash
pip install pandas requests beautifulsoup4 python-dotenv
```

3. **Configure Environment Variables**
```bash
cp .example.env .env
# Then edit .env with your CoralNet login credentials:
USERNAME=your_username
PASSWORD=your_password
```

4. **Prepare Sources File**
Example `sources.csv`:
```csv
source_id,name,Valid
12345,Great_Barrier_Reef,yes
67890,Red_Sea,yes
```

---

## Usage

### 1. Scrape Source Data
```bash
python get_sources_data.py
```
Outputs `sources_data.csv`

### 2. Download Annotations
```bash
python scrape_annotations.py
```
Downloads annotations into `metadata/` subfolders

### 3. Download Images
```bash
python scrape.py
```
Downloads image files into `output/<source_name>/images`

### 4. Download Labelsets
```bash
python scrape_labelsets.py
```
Downloads labelset CSVs into `metadata/<source_name>/labelset.csv`

### 5. Scrape Metadata
```bash
python scrape_metadata.py
```
Collects full metadata into `metadata/<source_name>/metadata_all.csv`

---

## Configuration

- Ensure `sources.csv` has the `Valid` column marked `yes` for sources to be processed
- Credentials must be defined in the `.env` file
- Output directories are created automatically

---

## Logging

- `scrape_annotations.log` — Logs annotation download progress
- `scrape_logs.log` — Logs image download progress and errors

---

## Troubleshooting

- **Login Errors** — Check `.env` values and network access
- **Download Failures** — Inspect logs for timeouts, bad links, or retries
- **Missing Files** — Confirm that CSVs are formatted and paths are correct

---

## Ethical Use

Please use this crawler responsibly:

- Comply with [CoralNet Terms of Service](https://coralnet.ucsd.edu/terms/)
- Avoid overwhelming the server with too many requests
- Add artificial delays in scripts if scraping in bulk

---

## Citing This Work

If you use this script or any data processed with it in your work, please cite our paper:

```bibtex
@article{battach2025reefnet,
  title={ReefNet: A Large-scale, Taxonomically Enriched Dataset and Benchmark for Coral Reef Classification},
  author={Battach, Yahia and Felemban, Abdulwahab and Khan, Faizan Farooq and Radwan, Yousef A. and Li, Xiang and Silva, Luis and Suka, Rhonda and Gonzalez, Karla and Marchese, Fabio and Williams, Ivor D. and Jones, Burton H. and Beery, Sara and Benzoni, Francesca and Elhoseiny, Mohamed},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2025}
}
```

📘 Full citation and project details at: [https://reefnet-project.github.io/reefnet-2025/](https://reefnet-project.github.io/reefnet-2025/)

---

## Contributor 
- [Yahia Battach](https://github.com/shakesBeardZ/) — Creator and Maintainer

---

## License

This project is licensed under the [CC BY 4.0](LICENSE). You are free to use, modify, and distribute it with attribution.

---
