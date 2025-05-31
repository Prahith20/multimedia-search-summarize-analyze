import chromadb
from chromadb.utils import embedding_functions
import pandas as pd
from config import configs

#Connect to Chroma DB
client = chromadb.Client()
#print('out main')
'''def get_client():
    #chroma_client = chromadb.HttpClient(host=configs['host'], port=configs['port'])
    #print(chroma_client.collections())
    chroma_client = chromadb.Client()

    return chroma_client'''

#Get embeddings function
def get_embedding_func(model_name=configs['embeddings_model']):
    huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
        api_key=configs['hugging_face_api_key'],
        model_name=model_name
    )
    return huggingface_ef

#Get or Create a collection
def create_or_get_collection(client=None,collection_name=configs['collection_name'],embedding_function = None):
    try:
        print('Cd')
        collection = client.get_or_create_collection(name=collection_name, embedding_function=embedding_function,metadata={"hnsw:space": "cosine"})
    except Exception as e:
        print(e)
        
    return collection

#Read Excel
def read_excel(path=configs['excel_path']):
    df = pd.read_excel(path)
    return df

#insert records
def insert_to_vdb(df):
    print(df.head())
    try:
        #create client
        #client = get_client()

        #create embedding function
        embedding_function = get_embedding_func()

        #get collection
        collection = create_or_get_collection(client=client,collection_name=configs['collection_name'],embedding_function=embedding_function)
        print(collection.count())
        #texts
        documents = df['Text'].tolist()
        metadata = df.drop('Text', axis = 1).to_dict(orient = 'records')
        #print(client.heartbeat())
        num_of_records = df.shape[0]
        print(num_of_records)
        current_records = collection.count() #get currect records present in the DB
        ids = range(current_records,current_records+num_of_records)
        ids = [str(id) for id in ids]
        print(ids)
        
        
        #add records
        collection.add(documents=documents,ids=ids,metadatas = metadata)
        print(collection.count())
    except Exception as e:
        print(e)

#search
def vector_search(query_e,collection_name=configs['collection_name']):
    #create client
    #client = get_client()

    #create embedding function
    embedding_function = get_embedding_func()

    #get collection
    collection = client.get_or_create_collection(name=collection_name,embedding_function=embedding_function,metadata={"hnsw:space": "cosine"})

    #get results
    results = collection.query(
        query_texts=query_e, 
        n_results= configs["K"]
    )
    images = []
    for img in results["metadatas"][0]:
        images.append(img['Image Name'])
    return images
#if __name__ == "__main__":
    #print('in main')
    #client = chromadb.Client()
    #df = pd.read_excel("output.xlsx")
    #print(df.head())
    #insert_to_vdb(df)

    #print(vector_search("monkey"))



