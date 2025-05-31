import chromadb
from config import configs

chroma_client = chromadb.HttpClient(host=configs['host'], port=configs['port'])
print(chroma_client.list_collections())