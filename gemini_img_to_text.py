import os
import pandas as pd
from shutil import move
import boto3
from Gemini_api import *
from upload_to_GCS import *
from gemini_requests import *
from config import *

# AWS S3 configuration
AWS_BUCKET_NAME = configs["AWS_bucket_name"]
AWS_ACCESS_KEY = configs["AWS_access_key"]
AWS_SECRET_KEY = configs["AWS_secret_key"]
AWS_REGION = configs["AWS_region"]
AWS_IMAGE_FOLDER = 'images/'
AWS_VIDEO_FOLDER = 'videos/'

def upload_to_s3(folder_path, bucket):

    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)

    # Loop through each file in the folder and upload to S3
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)      
        print(file_path)
        print(file_name)
        s3_client.upload_file(file_path, AWS_BUCKET_NAME, AWS_IMAGE_FOLDER + file_name)

        print(f"Uploaded {file_name} to s3.")

def upload_video_to_s3(folder_path, bucket):

    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)

    # Loop through each file in the folder and upload to S3
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)      
        print(file_path)
        print(file_name)
        s3_client.upload_file(file_path, AWS_BUCKET_NAME, AWS_VIDEO_FOLDER + file_name)

        print(f"Uploaded {file_name} to s3.")

def cleanup_images_folder(images_folder):
    # Delete all files in the "images" folder
    for file_name in os.listdir(images_folder):
        file_path = os.path.join(images_folder, file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")



def process_images_with_gemini(files):
    
    # Set the paths
    
    images_folder = "images"
    unprocessed_folder = os.path.join(images_folder, "unprocessed")
    processed_folder = os.path.join(images_folder, "processed")
    excel_file_path = "output.xlsx"

    results_list = []
    for file in files:
        upload_image_to_GCS(file)
        query_text = gemini_inference(file.filename)
        #print(file.filename, query_text)
        results_list.append({"Image Name": file.filename, "Text": query_text})

    # Convert the list to a DataFrame
    results_df = pd.DataFrame(results_list)
    print('results list', results_list)

    # Append results to the existing Excel file or create a new file if it doesn't exist
    '''if os.path.exists(excel_file_path):
        with pd.ExcelWriter(excel_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            results_df.to_excel(writer, index=False, header=False)
    else:
        results_df.to_excel(excel_file_path, index=False)'''
    results_df.to_excel(excel_file_path, index=False)

    print(f"Results appended to {excel_file_path}")


    # Loop through each image in the unprocessed folder
    for image_name in os.listdir(unprocessed_folder):
        if image_name.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(unprocessed_folder, image_name)
            # Move the processed image to the processed folder
            move(image_path, os.path.join(processed_folder, image_name))

    
    # Upload processed images to S3 bucket
    upload_to_s3(processed_folder, bucket="llava-application-hari")

    # Delete images from the "images" folder
    cleanup_images_folder(processed_folder)

def process_videos_with_gemini(files):
    
    # Set the paths
    
    videos_folder = "videoss"
    unprocessed_folder = os.path.join(videos_folder, "unprocessed")
    processed_folder = os.path.join(videos_folder, "processed")
    excel_file_path = "output.xlsx"
    
    results_list = []
    for file in files:
        upload_video_to_GCS(file)
        query_text = inference_videos(unprocessed_folder+f'\\{file.filename}')
        #print(file.filename, query_text)
        results_list.append({"Video Name": file.filename, "Text": query_text})

    # Convert the list to a DataFrame
    results_df = pd.DataFrame(results_list)
    print('results list', results_list)

    # Append results to the existing Excel file or create a new file if it doesn't exist
    '''if os.path.exists(excel_file_path):
        with pd.ExcelWriter(excel_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            results_df.to_excel(writer, index=False, header=False)
    else:
        results_df.to_excel(excel_file_path, index=False)'''
    results_df.to_excel(excel_file_path, index=False)

    print(f"Results appended to {excel_file_path}")


    # Loop through each image in the unprocessed folder
    for video_name in os.listdir(unprocessed_folder):
        if video_name.endswith(('.mp4')):
            image_path = os.path.join(unprocessed_folder, video_name)
            # Move the processed image to the processed folder
            move(image_path, os.path.join(processed_folder, video_name))

    
    # Upload processed images to S3 bucket
    upload_video_to_s3(processed_folder, bucket="llava-application-hari")

    # Delete images from the "images" folder
    cleanup_images_folder(processed_folder)