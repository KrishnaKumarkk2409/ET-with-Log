Here’s a `README.md` for your project based on the provided files:

---

# ZohoKB Embedding & Pinecone Integration

This repository provides a Python-based solution to scrape data from a Google Sheet, process it into chunks, generate OpenAI embeddings, and upload the results to Pinecone for vector search. The application involves extracting relevant data from web links, generating embeddings, and managing vector data in a scalable manner.

## Project Structure

- **ET with Log.py**: Main script to scrape data from a Google Sheet, generate embeddings using OpenAI, and log the status to the Google Sheet.
- **LOAD.py**: Script for loading generated embeddings from JSON files and upserting them to Pinecone.
- **requirement.txt**: Python dependencies required to run the project.
- **.env**: Environment variables configuration for sensitive keys (e.g., Pinecone API key).

## Features

- **Google Sheets Integration**: Fetch data from Google Sheets using the `gspread` library and process it based on the tab name.
- **Web Scraping**: Use Selenium and BeautifulSoup to scrape content from provided URLs.
- **Text Chunking**: Split scraped text into smaller chunks for embedding generation.
- **OpenAI Embeddings**: Generate text embeddings using OpenAI's API for vectorization.
- **Pinecone Integration**: Upsert embeddings to Pinecone for storage and search.
- **Logging**: Logs the status of scraping and embedding generation back to the Google Sheet for tracking.

## Installation

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/ZohoKB-Embedding.git
cd ZohoKB-Embedding
```

### Step 2: Install Dependencies

Install the required dependencies listed in `requirement.txt`:

```bash
pip install -r requirement.txt
```

### Step 3: Set Up Environment Variables

1. **Create an `.env` file** in the project directory with the following variables:
   ```env
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_INDEX_HOST=your-pinecone-index-host
   OPENAI_API_KEY=your-openai-api-key
   ```

2. **Google Sheets Setup**:
   - Create a service account in Google Cloud and download the `googlekey.json` credentials.
   - Share the Google Sheet (`ZohoKB`) with the service account email provided in the `googlekey.json` file.

### Step 4: Google Sheet Setup

Create a Google Sheet named `ZohoKB` and ensure it has a column for:
- **Leaf name**: The name of the data leaf.
- **Leaf Link**: The URL of the content to scrape.

### Step 5: Run the Scripts

- **Run `ET with Log.py`** to scrape data, generate chunks, create embeddings, and log the status in the Google Sheet:
  ```bash
  python ET with Log.py
  ```

- **Run `LOAD.py`** to load the generated embeddings from the `Chunks` folder and upsert them to Pinecone:
  ```bash
  python LOAD.py
  ```

## Workflow Overview

1. **Scraping**:
   - The script fetches all records from the Google Sheet and extracts the links.
   - It then uses Selenium to scrape data from the given URLs.

2. **Chunking**:
   - The scraped text is split into smaller chunks (default size 800 words) to fit into OpenAI's embedding model.

3. **Embedding Generation**:
   - Each chunk of text is embedded using OpenAI's Embedding API.

4. **Saving and Uploading Embeddings**:
   - The embeddings are saved as JSON files in the `Chunks` folder.
   - The `LOAD.py` script is used to load the embeddings and upsert them to Pinecone for storage and efficient vector search.

## Example Output

After running the scripts, embeddings will be stored in the `Chunks` folder as JSON files, and the Google Sheet will be updated with the scraping and embedding statuses.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README provides a comprehensive overview of the setup, installation, and functionality of your project. Let me know if you'd like to adjust or expand any sections!
