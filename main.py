# main.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import hashlib
import json

from supabase import create_client, Client
from qdrant_client import QdrantClient, models

# import sqlalchemy as sa
# from sqlalchemy import create_engine, select, Column, Integer, String, Boolean, Table, MetaData
# from sqlalchemy.ext.declarative import declarative_base


from sentence_transformers import SentenceTransformer
from datetime import datetime
app = FastAPI()
app.mount("/docs", StaticFiles(directory="docs"), name="docs")

GITHUB="https://github.com/apsumin/rocket-influence"
SUPABASE= "https://supabase.com/dashboard/project/dfkeshhcxzqdafjfnxyx"
QDRANT="https://15af0a7f-12ff-481f-88fe-6da3734e8c13.us-east4-0.gcp.cloud.qdrant.io:6333/dashboard#/collections"

supabase_url: str = "https://dfkeshhcxzqdafjfnxyx.supabase.co"
supabase_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRma2VzaGhjeHpxZGFmamZueHl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyMzY3MTYsImV4cCI6MjA2NTgxMjcxNn0.EHxmcTzQ13c-j-6awsKp3fQVY8BUJVNdJNEc3OAl1Eo"

supabase: Client = create_client(supabase_url, supabase_key)

QDRANT_URL = "https://15af0a7f-12ff-481f-88fe-6da3734e8c13.us-east4-0.gcp.cloud.qdrant.io:6333"  # http://localhost:6333 for local instance
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.aXa8OyzTkUKWUccpB2SiRfl5S-WdwzI-MuGkgaMmN1Y"  # None for local instance

RT_VIDEOTRANSCRIBTION_TABLE = "rt_videotranscribtion"

__IS_VECTORIZED__="is_vectorized"
__TEXT__="text"


qdrant = QdrantClient(QDRANT_URL, api_key=QDRANT_API_KEY)

VERSION="1.0.0.5"
MODEL="paraphrase-multilingual-MiniLM-L12-v2"
INFO=f"Rocket Influence Middleware server. v{VERSION}"
COLLECTION = "rocket-influence"
USING = "descriptions"
FOLDER = "./ri"
HTML = """
    <style>
      table, th, td {
        border: 0.5px solid;
        border-collapse: collapse;
      }
      tr:nth-child(odd) {
        background-color: lightgray;
      }
      tr:nth-child(even) {
        background-color: white;
      }
      .my-table {
        width: 100%;
        border: 0.5px solid;
        border-collapse: collapse;
      }
      .my-table_2 {
        width: 60%;
        border: 0.5px solid;
        border-collapse: collapse;
      }
      .col-10 {
        width: 10%;
        vertical-align: top;
      }
      .col-30 {
        width: 30%;
        vertical-align: top;
      }
      .col-20 {
        width: 20%;
        vertical-align: top;
      }

      .col-50 {
        width: 50%;
        vertical-align: top;
      }
      .col-60 {
        width: 60%;
        vertical-align: top;
      }
    </style>
    <body>
"""
encoder = SentenceTransformer(MODEL)


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

def debug(m):
    print(f"{datetime.now()}:{m}")


@app.get("/", response_class=HTMLResponse)

async def read_root():
    html = HTML
    html += f"<h3>{INFO}</h3>"
    html += f"<h3>{MODEL}</h3>"
    html += """
            <table class="my-table">
                <tr>
                    <td class="col-30">Supabase URL</td>
                    <td class="col-60">Qdrant URL</td>
                    <td class="col-30">GitHub Repository URL</td>
                </tr>
    """
    html += f"<tr><td class='col-30'><a href=\"{SUPABASE}\">{SUPABASE}</a></td><td class='col-60'><a href=\"{QDRANT}\">{QDRANT}</a></td><td class='col-30'><a href=\"{GITHUB}\">{GITHUB}</a></td></tr>"
    html += "</table>"

    html += """
            <br>
            <table class="my-table_2">
                <tr>
                    <td class="col-20">API</td>
                </tr>
    """
    html += f"<tr><td class='col-30'><a href=\"/api/v2/reload\">/api/v2/reload</a></td></tr>"
    html += f"<tr><td class='col-30'><a href=\"/api/search?q=%22%22\">/api/search</a></td></tr>"
    html += f"<tr><td class='col-30'><a href=\"/api/search/verify?q=%22%22\">/api/search/verify</a></td></tr>"
    html += f"<tr><td class='col-30'><a href=\"/api/v2/qdrant/verify/list\">/api/v2/qdrant/verify/list</a></td></tr>"

    html += """
                </table>
        """
    html += """
            <br>
            <table class="my-table_2">
                <tr>
                    <td class="col-30">Call #1</td>
                    <td class="col-30">Call #2</td>
                </tr>

                <tr>
                    <td class="col-30">
                        <img src="/docs/call_1.jpg" alt="Call #1" style="width:450px;height:470px;"/>
                    </td>
                    <td class="col-30">
                        <img src="/docs/call_2.jpg" alt="Call #2" style="width:450px;height:470px;"/>
                    </td>
                </tr>
            </table>
    """
    html += """
            </body>
       """
    return HTMLResponse(content=f"{html}")


# @app.get("/api/reload", response_class=HTMLResponse)
# async def reload():
#     debug("starting reload...")
#     start = datetime.now()
#     try:
#         with open(f'{FOLDER}/normalizer.json', 'r') as file:
#             normalizer = json.load(file)
#             tables = list(map(lambda item: item["table"], normalizer))
#
#             for item in normalizer:
#                 try:
#                     if "neq" in item:
#                         response = (
#                             supabase.table(item["table"]).select("*")
#                             #.neq(item["neq"]["column"], item["neq"]["value"].encode(encoding='utf-8', errors='strict'))
#                             .neq(item["neq"]["column"], "Ошибка")
#                             .execute()
#                         )
#                     else:
#                         response=(
#                             supabase.table(item["table"]).select("*")
#                             .execute()
#                         )
#                     data = response.data
#                     if  data:
#                         file_path = f"./ri/{item['table']}.json"
#                         with open(file_path, 'w') as json_file:
#                             json.dump(data, json_file, indent=4)
#
#                 except Exception as e:
#                     print(e)
#
#     except Exception as e:
#         print(e)
#
#     debug("normalizing...")
#     __documents__ = []
#     try:
#         with open(f'{FOLDER}/normalizer.json', 'r') as file:
#             normalizer = json.load(file)
#
#             for item in normalizer:
#                 debug(item["table"])
#                 with open(f'{FOLDER}/{item["table"]}.json', 'r') as file:
#                     document = json.load(file)
#                     for d in document:
#                         __item__ = {}
#                         for m in item["map"]:
#                             __item__[m["to"]] = d[m["from"]]
#                             if "verify_for_null" in m:
#                                 if m["verify_for_null"] == True:
#                                     if __item__[m["to"]] is None:
#                                         __item__[m["to"]] = ""
#
#                         if verify_null_values(__item__):
#                             __documents__.append(__item__)
#         __documents__ = remove_null_values(__documents__)
#
#         with open(f'{FOLDER}/normalized.json', 'w') as json_file:
#             json.dump(__documents__, json_file, indent=4)
#
#     except json.JSONDecodeError:
#         return HTMLResponse(content="Error: Could not decode JSON from the file.")
#     except Exception as e:
#         return HTMLResponse(content=f"{e}")
#
#     try:
#         if not qdrant.collection_exists(COLLECTION):
#             qdrant.create_collection(
#                 collection_name=COLLECTION,
#                 vectors_config={
#                     USING:models.VectorParams(
#                         size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
#                         distance=models.Distance.COSINE,
#                 )
#                 }
#             )
#     except Exception as e:
#         return HTMLResponse(content=f"{e}")
#
#     debug("vectorizing...")
#     try:
#         points = []
#         for doc in __documents__:
#             id = generate_unique_id(doc["url"])
#             points.append(
#                 models.PointStruct(
#                     id=id,
#                     vector={
#                         USING: encoder.encode(f"{doc['blogger']}. {doc['description']}").tolist()
#                     },
#                     payload=doc
#                 )
#             )
#         # Point 32491be8-43bd-03c5-f64d-f91382321804
#         debug("reloading...")
#         qdrant.upsert(
#             collection_name=COLLECTION,
#             points=points,
#             wait=False
#         )
#         end = datetime.now()
#         html=HTML
#         html+=f"<h3>{INFO}</h3>"
#         html+=f"<h3>{MODEL}</h3>"
#
#         html+=f"<h4><a href=\"{QDRANT_URL}/dashboard#/collections\">{QDRANT_URL}</a></h4>"
#         #html += f"<h3>{start}-{end}</h3>"
#         html += f"<h4>{len(__documents__)} points vectorized and loaded in  {(end - start).seconds} second(s).</h4>"
#
#         html+="""
#                 <table class="my-table">
#                     <tr>
#                         <td class="col-20">URL</td>
#                         <td class="col-20">Blogger</td>
#                         <td class="col-60">Description</td>
#                     </tr>
#         """
#         for doc in __documents__:
#             html += f"<tr><td class='col-20'><a href=\"{doc['url']}\">{doc['url']}</a></td><td class='col-20'>{doc['blogger']}</td><td class='col-60'>{doc['description']}</td></tr>"
#
#         html += """
#                 </table>
#             </body>
#         """
#         return HTMLResponse(content=html)
#     except Exception as e:
#         return HTMLResponse(content=f"{e}")

# # Option 1: Using SQLAlchemy ORM
# Base = declarative_base()
#
# class VideoTranscribtion(Base):
#     __tablename__ = 'rt_VideoTranscribtion'
#     id = Column(Integer, primary_key=True)
#     text = Column(String)
#     is_vectorized = Column(Boolean)



@app.get("/api/v2/reload")
async def reload2():
    debug("starting reload...")
    try:
        response = (
            supabase.table(RT_VIDEOTRANSCRIBTION_TABLE).select("*")
            .eq(__IS_VECTORIZED__, False)
            .not_.is_(__TEXT__, 'null')
            .execute()
        )
    except Exception as e:
        return {"status": f"{str(e)}"}

    data = response.data
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
        return {"status": f"{str(e)}"}

    if data:
        points = []
        for row in data:
            try:
                id = row["id"]
                points.append(
                    models.PointStruct(
                        id=id,
                        vector={
                            USING: encoder.encode(f"{row['text']}").tolist()
                        },
                        payload=row
                    )
                )
            except Exception as e:
                return {"status": f"{str(e)}"}

        debug("reloading...")
        qdrant.upsert(
            collection_name=COLLECTION,
            points=points,
            wait=False
        )
        try:
            ids = [row["id"] for row in data]
            response = supabase.table(RT_VIDEOTRANSCRIBTION_TABLE).update(
                {__IS_VECTORIZED__: "true"}  # Same value for all
            ).in_("id", ids).execute()

            response = [row for row in data]
            return response

        except Exception as e:
            return {"status": f"{str(e)}"}

        # file_path = f"./ri/{RT_VIDEOTRANSCRIBTION_TABLE}.json"
        # with open(file_path, 'w') as json_file:
        #      json.dump(data, json_file, indent=4)
    return {"status": "ok"}







@app.get("/api/search")
async def read_item(q: str, neural: bool = True):
    debug("quering...")
    hits = qdrant.query_points(
        using=USING,
        collection_name=COLLECTION,
        query=encoder.encode(q).tolist(),
        limit=10,
        with_vectors=True
    ).points

    sorted_hits = sorted(hits, key=lambda item: item.score, reverse=True)
    response=[]
    for hit in sorted_hits:
        response.append({"score:":hit.score,"payload":hit.payload})
    return response


@app.get("/api/v2/qdrant/list", response_class=HTMLResponse)
async def list():
    return HTMLResponse(content="")



@app.get("/api/search/verify", response_class=HTMLResponse)
async def read_verify(q: str):
    debug("verification quering...")
    start = datetime.now()
    hits = qdrant.query_points(
        using=USING,
        collection_name=COLLECTION,
        query=encoder.encode(q).tolist(),
        limit=200,
        with_vectors=True
    ).points

    sorted_hits = sorted(hits, key=lambda item: item.score, reverse=True)
    response=[]
    for hit in sorted_hits:
        response.append({"score:":hit.score,"payload":hit.payload})

    end = datetime.now()
    html = HTML
    html += f"<h3>{INFO}</h3>"
    html += f"<h4><a href=\"/\">Home</a></h4>"
    html += f"<h4><a href=\"{QDRANT_URL}/dashboard#/collections\">{QDRANT_URL}</a></h4>"
    html += f"<h4>{q} {(end-start).microseconds/1000}ms</h4>"
    #html += f"<h4>{(end-start).microseconds/1000}ms</h4>"

    html += """
            <table class="my-table">
                <tr>
                    <td class="col-10">Score</td>
                    <td class="col-20">URL</td>
                    <td class="col-60">Description</td>
                </tr>
    """
    for hit in sorted_hits:
        html += f"<tr><td class='col-10'>{hit.score}</td><td class='col-20'><a href=\"{hit.payload['url']}\">{hit.payload['url']}</a></td><td class='col-20'>{hit.payload['text']}</td></tr>"
    html += """
                </table>
            </body>
        """
    return HTMLResponse(content=html)


# if __name__ == "__main__":
#      import uvicorn
#      uvicorn.run(app, host="0.0.0.0", port=8000)
