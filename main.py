# main.py
from fastapi import FastAPI
import os
import hashlib
import json
from supabase import create_client, Client
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

app = FastAPI()

supabase_url: str = "https://dfkeshhcxzqdafjfnxyx.supabase.co"
supabase_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRma2VzaGhjeHpxZGFmamZueHl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyMzY3MTYsImV4cCI6MjA2NTgxMjcxNn0.EHxmcTzQ13c-j-6awsKp3fQVY8BUJVNdJNEc3OAl1Eo"

supabase: Client = create_client(supabase_url, supabase_key)

QDRANT_URL = "https://15af0a7f-12ff-481f-88fe-6da3734e8c13.us-east4-0.gcp.cloud.qdrant.io:6333"  # http://localhost:6333 for local instance
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.aXa8OyzTkUKWUccpB2SiRfl5S-WdwzI-MuGkgaMmN1Y"  # None for local instance

qdrant = QdrantClient(QDRANT_URL, api_key=QDRANT_API_KEY)

encoder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def generate_unique_id(url):
    return hashlib.md5(url.encode()).hexdigest()

def remove_null_values(data):
    """
    Recursively removes keys with None values from a dictionary (JSON object).
    """
    if isinstance(data, dict):
        return {k: remove_null_values(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_null_values(elem) for elem in data if elem is not None]
    else:
        return data

def verify_null_values(data):
    if isinstance(data, dict):
        for k, v in data.items():
            if v is None:
                return False
    return True


@app.get("/")
async def read_root():
    return {"message": "Rocket Influence Custom REST API v1.0.0.0 server is up!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/reload")
async def reload():
    tables = ["YouTube Transkrib", "Transkrib_TikTok","transkrib_insta"]
    for item in tables:
        try:
            response=(
                supabase.table(item).select("*")
                .execute()
            )
            data = response.data
            if  data:
                file_path = f"./ri/{item}.json"
                with open(file_path, 'w') as json_file:
                    json.dump(data, json_file, indent=4)

        except Exception as e:
            print(e)
    FOLDER = "./ri"
    __documents__ = []
    try:
        with open(f'{FOLDER}/normalizer.json', 'r') as file:
            normalizer = json.load(file)

            for item in normalizer:
                print(item["table"])
                with open(f'{FOLDER}/{item["table"]}.json', 'r') as file:
                    document = json.load(file)
                    for d in document:
                        __item__ = {}
                        for m in item["map"]:
                            __item__[m["to"]] = d[m["from"]]
                        if verify_null_values(__item__):
                            __documents__.append(__item__)
        __documents__ = remove_null_values(__documents__)

        with open(f'{FOLDER}/normalized.json', 'w') as json_file:
            json.dump(__documents__, json_file, indent=4)

    except json.JSONDecodeError:
        return ("{Error: Could not decode JSON from the file.}")
    except Exception as e:
        print(f"{e}")

    COLLECTION = "rocket-influence"
    USING="descriptions"
    try:
        if not qdrant.collection_exists(COLLECTION):
            qdrant.create_collection(
                collection_name=COLLECTION,
                vectors_config={
                    USING:models.VectorParams(
                        size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
                        distance=models.Distance.COSINE,
                )
                }
            )
    except Exception as e:
        return (f"{e}")

    try:
        points = []
        for doc in __documents__:
            id = generate_unique_id(doc["url"])
            points.append(
                models.PointStruct(
                    id=id,
                    vector={
                        USING: encoder.encode(doc["description"]).tolist()
                    },
                    payload=doc
                )
            )
        # Point 32491be8-43bd-03c5-f64d-f91382321804
        qdrant.upsert(
            collection_name=COLLECTION,
            points=points,
            wait=True
        )
    except Exception as e:
        return (f"{e}")

    return {"status": "ok"}

@app.get("/api/search")
async def read_item(q: str, neural: bool = True):
    return {
        "result":q
    }



# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
