from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify
import os
from flask_cors import CORS
from Gemini_api import *
from upload_to_GCS import *
from gemini_requests import *
from chat import *
#from vectorDB import vector_search, insert_to_vdb
from gemini_img_to_text import *
from config import *

import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path = './chromadb')
embedding_function = embedding_functions.HuggingFaceEmbeddingFunction(
        api_key=configs['hugging_face_api_key'],
        model_name=configs['embeddings_model']
    )
collection = client.get_or_create_collection(name=configs['image_collection'], embedding_function=embedding_function,metadata={"hnsw:space": "cosine"})
video_collection = client.get_or_create_collection(name=configs['video_collection'], embedding_function=embedding_function,metadata={"hnsw:space": "cosine"})

def insert_to_vdb(df):
    print('v0',df.head())
    try:
        print('v1',collection.count())
        #texts
        documents = df['Text'].tolist()
        metadata = df.drop('Text', axis = 1).to_dict(orient = 'records')
        #print(client.heartbeat())
        num_of_records = df.shape[0]
        print('v2',num_of_records)
        current_records = collection.count() #get current records present in the DB
        ids = range(current_records,current_records+num_of_records)
        ids = [str(id) for id in ids]
        print('v3',len(documents), len(ids), len(metadata))
        print(documents, ids)
        #add records
        collection.add(documents=documents,ids=ids,metadatas = metadata)
        print('v4',collection.count())
    except Exception as e:
        print(e)

def insert_to_video_vdb(df):
    print('v0',df.head())
    try:
        print('v1',video_collection.count())
        #texts
        documents = df['Text'].tolist()
        metadata = df.drop('Text', axis = 1).to_dict(orient = 'records')
        #print(client.heartbeat())
        num_of_records = df.shape[0]
        print('v2',num_of_records)
        current_records = video_collection.count() #get currect records present in the DB
        ids = range(current_records,current_records+num_of_records)
        ids = [str(id) for id in ids]
        print('v3',len(documents), len(ids), len(metadata))
        print(documents, ids)
        #add records
        video_collection.add(documents=documents,ids=ids,metadatas = metadata)
        print('v4',video_collection.count())
    except Exception as e:
        print(e)


#search
def vector_search(query_e):
    #get results
    results = collection.query(
        query_texts=query_e, 
        n_results= configs["K"]
    )
    images = []
    for img in results["metadatas"][0]:
        images.append(img['Image Name'])
    return images

def vector_search_for_video(query_e):
    #get results
    results = video_collection.query(
        query_texts=query_e, 
        n_results= configs["K"]
    )
    videos = []
    for vid in results["metadatas"][0]:
        videos.append(vid['Video Name'])
    return videos


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'images/unprocessed/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
UPLOAD_VIDEOS_FOLDER = "videos"
app.config['UPLOAD_VIDEOS'] = UPLOAD_VIDEOS_FOLDER

STATIC_UPLOAD_FOLDER = "uploads"
app.config['STATIC_UPLOAD_FOLDER'] = STATIC_UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_VIDEOS_FOLDER, exist_ok=True)
os.makedirs(STATIC_UPLOAD_FOLDER, exist_ok=True)

UPLOAD_VIDEO_FOLDER = 'videoss/unprocessed/'
app.config['UPLOAD_VIDEO_FOLDER'] = UPLOAD_VIDEO_FOLDER
os.makedirs(UPLOAD_VIDEO_FOLDER, exist_ok=True)

def read_excel(path=configs['excel_path']):
    df = pd.read_excel(path)
    return df

def search_image(query_text):
    images = vector_search(query_text)

    IMAGE_URL = configs['image_url']

    result_paths = [IMAGE_URL+img for img in images]
    print('Image paths returned from vdb')
    return result_paths

def search_video(query_text):
    videos = vector_search_for_video(query_text)

    VIDEO_URL = configs['video_url']

    result_paths = [VIDEO_URL+vid for vid in videos]
    print('Video paths returned from vdb')
    return result_paths

def allowed_file(file_name):
    if file_name.endswith(('.jpg', '.jpeg', '.png','.jfif')):
        return True
    else:
        return False
    
def allowed_video_file(file_name):
    if file_name.endswith(('.mp4')):
        return True
    else:
        return False

def search_with_image(image_path):
    text = gemini_inference(image_path)
    return text

def handle_image_upload():
    uploaded_image = request.files['image_file']
    filena = uploaded_image.filename
    if uploaded_image and allowed_file(filena):  # Define allowed_file function
        filename = secure_filename(uploaded_image.filename)
        upload_folder = os.path.join(os.getcwd(), 'uploads')
        uploaded_image_path = os.path.join(upload_folder, filename)
        uploaded_image.save(uploaded_image_path)

        upload_image_to_GCS(uploaded_image)
        # Call the inference_with_image function and return query_text
        query_text = search_with_image(filena)
        print(query_text)
        return query_text, uploaded_image_path

    return None, None


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summary')
def summary():
    return render_template('summary.html')

@app.route('/image-upload-for-summary')
def image_upload_for_summary():
    return render_template('image_upload_for_summary.html')

@app.route('/video-upload-for-summary')
def video_upload_for_summary():
    return render_template('video_upload_for_summary.html')

@app.route('/upload_image_for_summary', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Upload the file to GCS
    upload_image_to_GCS(file)
    
    # Save the image
    #file_path = os.path.join('uploads', file.filename)
    file_path = os.path.join(app.config['STATIC_UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    description = gemini_inference(file.filename)
    #description = 'Dummy description'
    
    print(file_path)
    return jsonify({'description': description, 'image_url': file_path})

@app.route('/upload_video_for_summary', methods=['POST'])
def upload_video():
    
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    
    if file.filename == '':
        return "No selected file"

    if file:
        # Save the uploaded file to the 'videos' folder
        #file_path = os.path.join('uploads', file.filename)
        file_path = os.path.join(app.config['STATIC_UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        # Call inference function with the file path
        result = inference_videos(file_path)
        #result = 'Dummy description'
        print(result)
        
        return jsonify({'description': result, 'video_url': file_path})


@app.route('/chat_with_image', methods=['POST'])
def chat_with_image():
    data = request.json
    question = data.get('question')
    description = data.get('description')

    answer = image_chat(description, question)  # Call your function to get the response
    return jsonify({'answer': answer})

@app.route('/chat_with_video', methods=['POST'])
def chat_with_video():
    data = request.json
    question = data.get('question')
    description = data.get('description')

    answer = video_chat(description, question)  # Call your function to get the response
    return jsonify({'answer': answer})

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/image-search')
def image_upload():
    return render_template('image_search.html')

@app.route('/video-search')
def video_upload():
    return render_template('video_search.html')

@app.route('/upload_images', methods=['POST'])
def upload_images():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')

    if not files:
        return jsonify({'error': 'No files provided'}), 400
    print(request.files)
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    
    process_images_with_gemini(files.copy())
    df = pd.read_excel(configs['excel_path'])
    insert_to_vdb(df)
    os.remove(configs['excel_path'])
    

    return jsonify({'message': 'Sucessfully Processed all images'}), 200


@app.route('/image_search', methods=['GET', 'POST'])
def image_search():
    images = []
    uploaded_image = None

    if request.method == 'POST':
        # Get text input from the form
        if request.form['search_text']!='':
            search_text =  request.form['search_text']
            print('Text search: ',search_text)
        else:
            print(request.files['image_file'].filename)
            if request.files['image_file'].filename!='' and not request.files['image_file'].filename.endswith(".mp4"):
                search_text,uploaded_image = handle_image_upload()
                print('Image search: ',search_text)
                uploaded_image = uploaded_image.split("\\")[-1]
                uploaded_image = "uploads/"+uploaded_image
                print(uploaded_image)
            else:
                # Save the uploaded file to the 'videos' folder
                file_path = os.path.join(app.config['UPLOAD_VIDEOS'], request.files['image_file'].filename)
                request.files['image_file'].save(file_path)

                # Call inference function with the file path
                result = inference_videos(file_path)
                
                search_text = result
                
        # Call the search function
        images = search_image(search_text)
    print(images)
    return images


@app.route('/upload_videos', methods=['POST'])
def upload_videos():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')

    if not files:
        return jsonify({'error': 'No files provided'}), 400
    print(request.files)
    '''for file in files:
        if file and allowed_video_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_VIDEO_FOLDER'], filename))'''

    # Save the uploaded file to the 'videos' folder
    file_path = os.path.join(app.config['UPLOAD_VIDEO_FOLDER'], request.files['files'].filename)
    request.files['files'].save(file_path)
    process_videos_with_gemini(files.copy())
    df = pd.read_excel(configs['excel_path'])
    insert_to_video_vdb(df)
    os.remove(configs['excel_path'])
    

    return jsonify({'message': 'Sucessfully Processed all videos'}), 200


@app.route('/video_search', methods=['GET', 'POST'])
def video_search():
    images = []
    uploaded_image = None

    if request.method == 'POST':
        # Get text input from the form
        if request.form['search_text']!='':
            search_text =  request.form['search_text']
            print('Text search: ',search_text)
        else:
            print(request.files['image_file'].filename)
            if request.files['image_file'].filename!='' and not request.files['image_file'].filename.endswith(".mp4"):
                search_text,uploaded_image = handle_image_upload()
                print('Image search: ',search_text)
                uploaded_image = uploaded_image.split("\\")[-1]
                uploaded_image = "uploads/"+uploaded_image
                print(uploaded_image)
            else:
                # Save the uploaded file to the 'videos' folder
                file_path = os.path.join(app.config['UPLOAD_VIDEOS'], request.files['image_file'].filename)
                request.files['image_file'].save(file_path)

                # Call inference function with the file path
                result = inference_videos(file_path)
                
                search_text = result
                
        # Call the search function
        videos = search_video(search_text)

    return videos

@app.route('/video_analysis', methods=['GET','POST'])
def video_analysis():
    result_text = ""
    flag=False
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']

        if file.filename == '':
            return 'No selected file', 400

        upload_video_to_GCS(file)
        result_text = analyse_video(file.filename)
        print(result_text)
        with open('example.txt', 'w') as file:
            file.write(result_text)
            
        flag=True
    #use redirect
    return render_template('video_analysis.html', flag=flag)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)