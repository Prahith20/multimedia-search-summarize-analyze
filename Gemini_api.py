import vertexai
from config import *
from vertexai.generative_models import GenerativeModel, Part

# PROJECT_ID = "your-project-id"
vertexai.init(project=configs["vertexai_project_id"], location="us-central1")

model = GenerativeModel("gemini-1.5-pro-001")
bucket_name = configs["GCS_bucket_name"]

def gemini_inference(filename):
    image_file = Part.from_uri(
        f"gs://{bucket_name}/{filename}", "image/jpeg"
    )

    prompt = "Describe the image in detail in a paragraph, paying special attention to the minute aspects. Consider elements like outfit colors of the subject in the image if any, textures, lighting, and any intricate patterns or small objects present."
    # Query the model
    response = model.generate_content([image_file, prompt])
    print(response)
    return response.text

def analyse_video(filename):

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.1,
        "top_p": 0.2,
    }

    emotion_detection_prompt = """Please analyse the provided video with respect to facial emotions, audio emotions and transcription and identify the main topics discussed throughout. 
        
        ### Instructions ###
        1. For each topic, provide a clear and concise heading along with the corresponding timestamp where the topic begins. Ensure that the headings accurately reflect the content of the video.
        2. Ensure to cover all the topics in video and give proper headings. DONOT combine two or more topics in one heading.
        3. Please provide accurate timestamps for each heading.
        ### Output Format ###
        Heading 1 - [Timestamp sec-sec]
        Heading 2 - [Timestamp sec-sec]

        ### Instructions ###
        2. Donot hallucinate anything from video.
        3. Perform the following tasks for the identified headings with respective timestamps:

        ### Task 1 ###
        Detect and classify the various speaker's facial emotions and give the emotions and facial features of speaker for each heading.
        Format the output properly. Don't add any extra text or symbols like " ''' " and "*".
        ### Output Format ###
        1.Speaker - response
        2.Emotion - response
        3.Facial features - response

        ### Task 2 ###
        For each of the identified above headings identify the speaker's tone, pitch and pace and provide the results.
        Format the output properly. Don't add any extra text or symbols like " ''' " and "*".
        ### Output Format ###
        1.Speaker - response
        2.Tone - response
        3.Pitch - response
        4.Pace - response

        ### Task 3 ###
        For each of the identified above headings transcribe the audio content and analyse the context and tone of the transcribed text.
        Format the output properly. Don't add any extra text or symbols like " ''' " and "*".
        ### Output Format ###
        1.Speaker - response
        2.Context - response
        3.Tone - response
        4.Transcription - response

        ### Task 4 ###
        Compare the facial expressions of the speaker with the tone they used and the content they spoke.
        Format the output properly. Don't add any extra text or symbols like " ''' " and "*".
        Possible emotions:
        Facial emotion labels: happy, sad, angry, surprised, neutral, fearful, disgusted.
        Audio emotion labels: happy, sad, angry, surprised, neutral, fearful, disgusted.
        
        ### Task 5 ###
        Analyse the video to compare the speaker's facial expressions with their tone of voice and the content of their speech. 
        Identify any mismatches or inconsistencies between the facial expressions, tone, and spoken words.
        Provide detailed feedback on how these elements align or conflict with each other, and offer specific suggestions for improving the overall coherence and effectiveness of the presentation.
        Focus on enhancing the emotional impact, clarity, and authenticity of the delivery.
        Format the output properly. Don't add any extra text or symbols like " ''' " and "*".
    """
    prompt1 = "Please analyze the provided video and generate a very detailed summary. Extract even the minute details that might help me with bussiness analytics for a dataset."
    # video_file_uri = "gs://dd-oe-poc/Michael-Lee-oetv.mp4"

    video_file = Part.from_uri(f"gs://{bucket_name}/{filename}", mime_type="video/mp4")

    contents = [video_file, prompt1]
    print('Payload sent for video analysis')
    response = model.generate_content(contents, generation_config = generation_config)
    # formated_response = BeautifulSoup(response.text, 'html.parser')
    # html = markdown.markdown(response.text)
    return response.text
