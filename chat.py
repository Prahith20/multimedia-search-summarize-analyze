import openai
import tiktoken
from config import *
#Open AI intialization
TOTAL_COST = 0
openai.api_key = configs["openai_api_key"]
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


def openai_api(message):
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

def image_chat(context, question):
    

    message = f"""
        Using this information about an image : {context} . Answer the following question : {question}. 
        If you could not find the answer from the information provided, respond "Sorry I cannot answer that question
        The user is interacting with the image and not the description.
    """
    return openai_api(message)
    
    
def video_chat(context, question):
    message = f"""
        Using this information about a video : {context} . Answer the following question : {question}. 
        If you could not find the answer from the information provided, respond "Sorry I cannot answer that question"
        The user is interacting with the video and not the descriptions.
    """
    return openai_api(message)
    