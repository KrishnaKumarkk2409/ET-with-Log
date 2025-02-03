import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import openai
import os
# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY') 

# Define the scope for the API
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

# Load the credentials.json file
creds = ServiceAccountCredentials.from_json_keyfile_name("googlekey.json", scope)

# Authorize the client
client = gspread.authorize(creds)

# Ask the user to input the tab (worksheet) name
tab_name = input("Please enter the exact name of the tab (worksheet) in the Google Sheet: ")

# Open the Google Sheet by name
sheet = client.open("ZohoKB").worksheet(tab_name)

# Fetch all records (rows) from the specified tab (worksheet)
data = sheet.get_all_records()

# Filter the data to only keep 'Leaf name' and 'Leaf Link' columns
leaf_data = [{'Leaf name': row['Leaf name'], 'Leaf Link': row['Leaf Link']} for row in data]

# Set up headless browser options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Initialize the browser
driver = webdriver.Chrome(options=chrome_options)

# Function to scrape text from a given URL
def scrape_text(url):
    try:
        driver.get(url)
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        main_content = soup.find('div', {'class': 'ArticleDetailLeftContainer__box'})
        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
            return text
        else:
            return ""
    except Exception as e:
        return ""

# Function to chunk the text into smaller pieces
def chunk_text(text, chunk_size=800):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Function to embed text using OpenAI's Embedding API
def embed_text_openai(text):
    try:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response["data"][0]["embedding"]
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

# Function to save embeddings to a JSON file
import os
import json

def save_embeddings_to_json(embeddings, file_count):
    # Define the folder name
    folder_path = "Chunks"
    
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)
    
    # Construct the full file path
    file_name = f"embeddings_batch_{file_count}.json"
    file_path = os.path.join(folder_path, file_name)
    
    try:
        # Save the embeddings to the specified folder
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(embeddings, json_file, ensure_ascii=False, indent=4)
        print(f"Saved {len(embeddings)} embeddings to {file_path}")
    except Exception as e:
        print(f"Error saving embeddings to JSON: {e}")


# Function to log extraction status in Google Sheet
def log_to_gsheet(row_number, log_status, num_chunks, timestamp):
    try:
        sheet.update_cell(row_number, len(data[0]) + 1, log_status)
        sheet.update_cell(row_number, len(data[0]) + 2, num_chunks)
        sheet.update_cell(row_number, len(data[0]) + 3, timestamp)
        print(f"Updated log for row {row_number}: {log_status}, {num_chunks}, {timestamp}")
    except Exception as e:
        print(f"Error updating log in Google Sheet: {e}")

# Main function to scrape, chunk, and generate embeddings from Google Sheet data
def scrape_chunk_and_embed(leaf_data):
    embeddings_batch = []
    row_count = 0
    file_count = 1
    id_counter = 1

    root_name = "root_name_placeholder"
    root_link = "root_link_placeholder"
    p1_name = "p1_name_placeholder"
    p1_link = "p1_link_placeholder"
    p2_name = "p2_name_placeholder"
    p2_link = "p2_link_placeholder"
    p3_name = "p3_name_placeholder"
    p3_link = "p3_link_placeholder"
    p4_name = "p4_name_placeholder"
    p4_link = "p4_link_placeholder"

    for idx, leaf in enumerate(leaf_data, start=2):
        leaf_name = leaf.get('Leaf name')
        leaf_link = leaf.get('Leaf Link')

        if leaf_link and leaf_link != 'No Leaf Link':
            print(f"Scraping data from: {leaf_link}")
            scraped_text = scrape_text(leaf_link)

            if scraped_text:
                chunks = chunk_text(scraped_text, chunk_size=800)
                print(f"Data for {leaf_name} broken into {len(chunks)} chunks.")
                log_status = "YES"
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_to_gsheet(idx, log_status, len(chunks), timestamp)

                for chunk in chunks:
                    embedding = embed_text_openai(chunk)
                    if embedding:
                        embeddings_batch.append({
                            "id": id_counter,
                            "combined_chunk": f"Root: {root_name}\nP1: {p1_name}\nP2: {p2_name}\nP3: {p3_name}\nP4: {p4_name}\nLeaf: {leaf_name}\nChunk: {chunk}",
                            "embedding": embedding,
                            "metadata": {
                                "root_name": root_name,
                                "root_link": root_link,
                                "p1_name": p1_name,
                                "p1_link": p1_link,
                                "p2_name": p2_name,
                                "p2_link": p2_link,
                                "p3_name": p3_name,
                                "p3_link": p3_link,
                                "p4_name": p4_name,
                                "p4_link": p4_link,
                                "leaf_name": leaf_name,
                                "leaf_link": leaf_link
                            }
                        })
                        id_counter += 1
                        row_count += 1

                        if row_count >= 200:
                            save_embeddings_to_json(embeddings_batch, file_count)
                            file_count += 1
                            row_count = 0
                            embeddings_batch = []
                    else:
                        print(f"Error in embedding for chunk from {leaf_name}")
            else:
                log_status = "NO"
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_to_gsheet(idx, log_status, 0, timestamp)
        else:
            log_status = "NO"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_to_gsheet(idx, log_status, 0, timestamp)

    if embeddings_batch:
        save_embeddings_to_json(embeddings_batch, file_count)

# Call the main function
scrape_chunk_and_embed(leaf_data)

# Close the browser
driver.quit()
