import pandas as pd
import csv
import re
import requests
import json
import time

# Install required packages
!pip install faiss-cpu sentence-transformers
import faiss
import numpy as np


def cleanup_data(text: str):
    """Clean and normalize text."""
    # Normalize minus signs (U+2212 → hyphen)
    text = text.replace("−", "-")

    # Decode Unicode escapes
    text = text.encode('utf-8').decode('unicode_escape')

    # Remove extra backslashes
    text = text.replace('\\', '')
    
    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Remove leading numbers or bullets
    text = re.sub(r'^\s*\d+(\.\d+)*\s*\.?\s*', '', text, flags=re.MULTILINE)

    # Remove extra empty lines
    text = re.sub(r'\n\s*\n', '\n', text).strip()

    # Remove figure references
    text = re.sub(r"\(Fig\.[^)]*\)", "", text)

    # Remove table references
    text = re.sub(r"\(Table[^)]*\)", "", text)

    # Remove "Refer to Fig. X" references
    text = re.sub(r"Refer to Fig\.[^\s.]*\.?", "", text)

    # Remove "for full review see ..." notes
    text = re.sub(r"\(for full review see[^)]*\)", "", text, flags=re.IGNORECASE)

    return text


def fetch_space_biology_data_bioc(pmcid: str):
    """Fetch paper JSON data from NCBI BioC API."""
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/{pmcid}/unicode"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching {pmcid}: {response.status_code}")
        return None

    try:
        paper_json = response.json()
    except Exception as e:
        print(f"Failed to parse JSON for {pmcid}: {e}")
        return None
    
    # Avoid overwhelming the server
    time.sleep(1)

    return paper_json


# Load CSV containing PMC links
url = "https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv"
df = pd.read_csv(url)


def get_all_paper_data(df):
    """Extract PMC IDs from the CSV links."""
    paper_metadata = []
    for index, row in df.iterrows():
        match = re.search(r'(PMC\d+)', row['Link'])
        if match:
            pmc_id = match.group(1)
            paper_metadata.append(pmc_id)
    return paper_metadata     


table_metadata_ids = get_all_paper_data(df)


def process_space_biology_data(metada_json_data):
    """
    Process BioC JSON data and merge all paragraphs under each subheader into a single string.
    """
    paragraph_data = metada_json_data[0]["documents"][0]
    passages = paragraph_data['passages']

    grouped_data = {}
    current_l1 = None
    current_l2 = None

    for item in passages:
        passage_text = item["text"]
        t = item['infons']['type']
        text = cleanup_data(passage_text)

        if t == "title_1":
            current_l1 = text
            current_l2 = None
            if current_l1 not in grouped_data:
                grouped_data[current_l1] = {}

        elif t == "title_2":
            current_l2 = text
            if current_l1 and current_l2 not in grouped_data[current_l1]:
                grouped_data[current_l1][current_l2] = ""

        elif t == "paragraph":
            if current_l1:
                if current_l2:
                    # Merge paragraph text under level_2 subsection
                    if grouped_data[current_l1][current_l2]:
                        grouped_data[current_l1][current_l2] += " " + text
                    else:
                        grouped_data[current_l1][current_l2] = text
                else:
                    # Merge paragraph text directly under level_1 (no subsection)
                    if "main_content" not in grouped_data[current_l1]:
                        grouped_data[current_l1]["main_content"] = text
                    else:
                        grouped_data[current_l1]["main_content"] += " " + text

    return grouped_data


def fetch_all_nasa_metadata_info(metadata_list):
    """
    Fetch and process all papers from the PMC metadata list.
    Returns a list of processed JSON data.
    """
    metadata_raw_json_response_list = []

    for metadata_id in metadata_list:
        raw_json_data = fetch_space_biology_data_bioc(metadata_id)
        if raw_json_data:
            space_engine_processed_data = process_space_biology_data(raw_json_data)
            metadata_raw_json_response_list.append(space_engine_processed_data)
            print(f"Processed {metadata_id}")

    return metadata_raw_json_response_list  


# Fetch all data
metadata_raw_json_response_list = fetch_all_nasa_metadata_info(table_metadata_ids)

# Save processed data to file
if metadata_raw_json_response_list:
    with open('grouped_papers1.json', 'w', encoding='utf-8') as f:
        json.dump(metadata_raw_json_response_list, f, indent=2, ensure_ascii=False)
    print("\nSaved to grouped_papers1.json")


