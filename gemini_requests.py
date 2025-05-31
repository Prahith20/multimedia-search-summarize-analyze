import uuid
import os
import cv2
import shutil
import openai
import tiktoken
from Gemini_api import *
from upload_to_GCS import *
from config import *

openai.api_key = configs["openai_api_key"]
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def delete_folder(folder_path):
    try:
        # Delete the folder and its contents
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' successfully deleted.")
    except FileNotFoundError:
        print(f"Folder '{folder_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return 

def write_to_file(results):
    uniq_str = uuid.uuid4().hex
    scenes_file_path = uniq_str + "_scenes.txt"
    with open(scenes_file_path, "w") as file:
        for key, value in results.items():
            file.write(f"scene {key}: {value}\n")
    return scenes_file_path

def extract_frames(input_video_path, output_folder):
    print(input_video_path)
    os.makedirs(output_folder, exist_ok=True)
    # Open the video file
    cap = cv2.VideoCapture(input_video_path)
    # Get the frames per second (fps) of the video
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(fps)
    
    # Calculate the interval to capture frames (2 frames per second in this case)
    frame_interval = int(round(fps / 1))
    # Initialize frame counter
    frame_count = 0
    while True:
        ret, frame = cap.read()

        # Break the loop if the video is finished
        if not ret:
            break

        # Save the frame every frame_interval frames
        if frame_count % frame_interval == 0:
            # Generate the filename based on the frame count
            filename = os.path.join(output_folder, f"frame_{frame_count // frame_interval}.jpg")
            print(filename)
            # Save the frame as an image
            cv2.imwrite(filename, frame)

        # Increment the frame counter
        frame_count += 1

    # Release the video capture object
    cap.release()

def summarize_scenes(secene_text_file):
    with open(secene_text_file, "r") as file:
        input_desc = file.read()

    message = f"""
        Using this set of texts describing the frames of a video captured within short intervals of time: {input_desc}. 
        Please summarize the video by considering the video as a whole and not individual images.
    """
    token_length = len(encoding.encode(message))
    if token_length > 4000:
        print(f"The provided input has too many tokens: {token_length}")
        return ""
    # globals()['TOTAL_COST'] += (token_length / 1000) * 0.0015
    payload = [
        {"role": "user", "content": message},
    ]
    try:
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=payload
        )
        response = chat.choices[0].message.content
        return response
    except Exception as e:
        print(e)
        return ""


def inference_videos(input_video_path):
    output_images_path = uuid.uuid4().hex
    
    extract_frames(input_video_path,output_images_path)
    
    upload_frames_to_GCS(output_images_path)
    
    results = {}
    i=0
    for filename in os.listdir(output_images_path):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):  # Check for image file extensions
            img_path = os.path.join(filename)
            #img = cv2.imread(img_path)
            results[i] = gemini_inference(img_path)
            i+=1
    #cv2.destroyAllWindows()
    '''images_list = [os.path.join(output_images_path, file) for file in os.listdir(output_images_path) if os.path.isfile(os.path.join(output_images_path, file))]
    results = {}
    for i,image in enumerate(images_list):
        print(i,image)
        #encoded_image_str = encode_image(image)
        results[i] = gemini_inference(image)'''
    #print(results)
    del_frames_in_GCS(output_images_path)
    delete_folder(output_images_path)
    scenes_file_path = write_to_file(results)
    #video summary
    video_summary = summarize_scenes(scenes_file_path)
    os.remove(scenes_file_path)
    return video_summary