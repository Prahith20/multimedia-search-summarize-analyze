# Multimedia Semantic Search

An application that enables lightweight semantic search capabilities across multimedia content including images, text, and videos. The system leverages Google's Gemini Pro Vision for image and video analysis, OpenAI's GPT-3.5 for text processing, and All-MiniLM-L6-v2 for generating vector embeddings, making it easier to find relevant media using natural language queries, as well as image/video uploads.

## Features

- Semantic search across multiple media types
- Summarize the uploaded media and ask questions about the details in it
- Image and video content analysis
- Experiment with the prompts in the video analysis pipeline. The generated text is viewable in a Streamlit window
- Cloud storage integration

## Technologies Used

- **APIs and Embeddings**
  - OpenAI API for text processing
  - Gemini API for image and video analysis
  - All-MiniLM-L6-v2 for vector embeddings

- **Storage and Search**
  - Google Cloud Storage for media storage for Gemini Inference
  - AWS S3 for storing media after uploading and embedding images/videos, which is later used for retrieval with search
  - ChromaDB for vector storage and search

## Setup and Installation

1. **Clone the Repository**
```bash
git clone [repository-url]
cd Multimedia-semantic-search
```

2. **Set Up Python Environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Credentials in config.py**
Update the following credentials in `config.py`:
```python
configs = {
    "image_url": "your-s3-bucket-url-for-images",
    "video_url": "your-s3-bucket-url-for-videos",
    "hugging_face_api_key": "your-huggingface-api-key",
    "openai_api_key": "your-openai-api-key",
    "vertexai_project_id": "your-project-id-in-vertexai",
    "GCS_bucket_name": "your-bucket-name-in-GCS",
    "AWS_bucket_name": "your-bucket-name-in-AWS",
    "AWS_access_key": "your-AWS-access-key",
    "AWS_secret_key": "your-AWS-secret-key",
    "AWS_region": "your-AWS-region",
    "google_service_account_json": "path-to-your-service-account-key.json"
}
```

5. **Set Up Google Cloud CLI and Authentication**
a. Install Google Cloud CLI:
   - Download and install from: https://cloud.google.com/sdk/docs/install

b. Initialize Google Cloud CLI:
```bash
gcloud init
```
- Select or create a Google Cloud project
- Choose your default region and zone

c. Configure Application Default Credentials:
```bash
gcloud auth application-default login
```

d. Enable Required APIs:
```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
```

6. **Set Up Google Cloud Service Account**
- Place your Google Cloud service account JSON key file in the root directory
- Update the `config.py` file with the correct file name

## Running the Application

1. **Start the Flask Server**
```bash
python app.py
```
The server will start on `http://localhost:5000`

2. **Start the Streamlit Server**
```bash
streamlit run streamlit_window.py
```
The Streamlit interface will be available at `http://localhost:8501`

3. **Access the Application**
Visit `http://localhost:5000` in your web browser to access the main application. From there, you can navigate to:

- **Search**: Upload images and videos to build your searchable collection. Then search through your uploads using an image, video, or text query
- **Summary**: Upload an image or video to generate a summary and chat with an AI bot about the details in the media
- **Video Analysis**: Upload a video to generate analysis, transcripts, and more. You can customize the text generation by modifying the prompt and generation configurations in the `analyse_video` function within `Gemini_api.py`

## Note
Make sure all API keys and credentials are properly configured before running the application. The system requires an active internet connection for API calls to OpenAI, Gemini, and cloud storage services. 