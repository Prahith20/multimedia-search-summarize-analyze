from google.cloud import storage
import os
from config import *

BUCKET_NAME = configs["GCS_bucket_name"]

storage_client = storage.Client.from_service_account_json(configs["google_service_account_json"])

def upload_image_to_GCS(file):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(file.filename)
    file.stream.seek(0)
    blob.upload_from_file(file.stream)
    return None

def upload_video_to_GCS(file):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(file.filename)
    file.stream.seek(0)
    blob.upload_from_file(file.stream)
    return None

def upload_frames_to_GCS(folder_path):
    bucket = storage_client.bucket(BUCKET_NAME)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')):  # Add more extensions if needed
            file_path = os.path.join(folder_path, filename)
            blob = bucket.blob(filename)  # Use filename as blob name
            blob.upload_from_filename(file_path)  # Upload the file
            print(f'Uploaded {filename} to {BUCKET_NAME}/{filename}')

def del_frames_in_GCS(folder_path):
    bucket = storage_client.bucket(BUCKET_NAME)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')):  # Add more extensions if needed
            #file_path = os.path.join(folder_path, filename)
            blob = bucket.blob(filename)  # Use filename as blob name
            blob.delete()  # Delete the file
            print(f'Deleted {filename} from {BUCKET_NAME}/{filename}')

