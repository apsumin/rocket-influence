# main.py
HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Qdrant Test</title>
    <style>
        body {
            font-family: Verdana, Geneva, sans-serif;
            background-color: #f5f5f5;
            font-size: 12px; /* Optional: Set a base font size */
        }
        .form-container {
            background-color: #D3D3D3;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 40%;
            max-width: 500px;
        }
        h2 {
            color: #333;
            margin-top: 0;
            margin-bottom: 12px;
            text-align: center;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        select, input[type="text"] {
            width: 100%;
            padding: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 12px;
            box-sizing: border-box;
            transition: border-color 0.3s;
        }
        select:focus, input[type="text"]:focus {
            outline: none;
            border-color: #4a90e2;
            box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
        }
        .button-container {
            position: relative;
        }
        button {
            background-color: #4a90e2;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 12px;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #357abd;
        }
        button:active {
            background-color: #2968a3;
        }
        h4 {
            color: blue;
            margin-bottom: 10px;
        }
        
        /* Class for red headings */
        .red-text {
            color: red;
        }
        
        /* Class for green headings */
        .green-text {
            color: green;
        }
        
        /* Spinner Styles */
        .spinner {
            display: none;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            position: absolute;
            top: 50%;
            left: 50%;
            margin-left: -10px;
            margin-top: -10px;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        /* Overlay to prevent interaction during submission */
        .overlay {
            display: none;
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.7);
            z-index: 10;
            border-radius: 8px;
        }
       
        table, th, td {
            font-family: Verdana, Geneva, sans-serif;
            font-size: 12px; /* Optional: Set a base font size */

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
      .col-5 {
        width: 5%;
        vertical-align: top;
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
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('testForm');
            const submitButton = document.getElementById('submitButton');
            const spinner = document.getElementById('spinner');
            const overlay = document.getElementById('overlay');
            
            const using = document.getElementById('using');
            const query_text = document.getElementById('query_text');
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                // Show spinner and overlay
                spinner.style.display = 'block';
                overlay.style.display = 'block';
                submitButton.disabled = true;
                
                // Get form data
                const formData = new FormData(form);
                const urlParams = new URLSearchParams(formData);
                const url = `/api/v3/search/verify?${urlParams.toString()}`;

                fetch(url)
                .then(response => response.text())
                .then(html => {
                    
                    document.querySelector('body').innerHTML = html;
                    spinner.style.display = 'none';
                    overlay.style.display = 'none';
                    submitButton.disabled = false;
                   
                    query_text.value = formData.get ('query_text');
                    for (let i = 0; i < using.options.length; i++) {
                        if (using.options[i].value === formData.get('using')) {
                            using.selectedIndex = i;
                            break;
                        }
                    }
                })
            });
        });
    </script>
    <body>
"""


from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import hashlib
import json
import re

from supabase import create_client, Client
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct

from sentence_transformers import SentenceTransformer
from datetime import datetime


#from fastembed import TextEmbedding
#from fastembed import TextEmbedding, LateInteractionTextEmbedding, SparseTextEmbedding
#from transformers import AutoTokenizer, AutoModelForMaskedLM
#import torch
import numpy as np
from itertools import chain

app = FastAPI()
app.mount("/docs", StaticFiles(directory="docs"), name="docs")


GITHUB	    ="https://github.com/apsumin/rocket-influence"
SUPABASE    ="https://supabase.com/dashboard/project/dfkeshhcxzqdafjfnxyx"
QDRANT	    ="https://15af0a7f-12ff-481f-88fe-6da3734e8c13.us-east4-0.gcp.cloud.qdrant.io:6333/dashboard#/collections"

supabase_url: str = "https://dfkeshhcxzqdafjfnxyx.supabase.co"
supabase_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRma2VzaGhjeHpxZGFmamZueHl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyMzY3MTYsImV4cCI6MjA2NTgxMjcxNn0.EHxmcTzQ13c-j-6awsKp3fQVY8BUJVNdJNEc3OAl1Eo"

supabase: Client = create_client(supabase_url, supabase_key)

QDRANT_URL = "https://15af0a7f-12ff-481f-88fe-6da3734e8c13.us-east4-0.gcp.cloud.qdrant.io:6333"  
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.aXa8OyzTkUKWUccpB2SiRfl5S-WdwzI-MuGkgaMmN1Y" 

RT_VIDEOTRANSCRIBTION_TABLE ="rt_videotranscribtion"
__IS_VECTORIZED__           ="is_vectorized"
__TEXT__                    ="text"
__IS_VECTORIZED_V2__        ="is_vectorized_v2"

qdrant = QdrantClient(QDRANT_URL, api_key=QDRANT_API_KEY, timeout=180)

VERSION     ="1.0.1.0"
INFO        =f"Rocket Influence Middleware server. v{VERSION}"
COLLECTION  = "rocket-influence"
USING       ="descriptions"
FOLDER      ="./ri"



HYBRID_COLLECTION = "rocket-influence-hybrid"

#MODEL	="ai-forever/ru-en-RoSBERTa"
#MODEL	="jinaai/jina-embeddings-v3"
MODEL  	="paraphrase-multilingual-MiniLM-L12-v2"
#MODEL  	="gemini-embedding-001"


DESCRIPTION_VECTOR="description"
TITLE_VECTOR="title"
TEXT_VECTOR="text"

encoder = SentenceTransformer(MODEL)

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s\-.,;:!?]', '', text)
    return text or "none"

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
    html += f"<tr><td class='col-30'><a href=\"/api/v3/reload\">/api/v3/reload</a></td></tr>"
    html += f"<tr><td class='col-30'><a href=\"/api/v2/search/verify?q=%22%22\">/api/v2/search/verify</a></td></tr>"
    html += f"<tr><td class='col-30'><a href=\"/api/v3/search/verify?using=title&query_text=Обзор домов в Подмосковье\">/api/v3/search/verify</a></td></tr>"

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



@app.get("/api/v3/reload")
async def reload3():
    try:

        response = (
            supabase.table(RT_VIDEOTRANSCRIBTION_TABLE).select("*")
            .eq(__IS_VECTORIZED_V2__, False)
            .not_.is_(__TEXT__, 'null')
            .limit  (500)
            .execute()
        )
    except Exception as e:
        return {"status": f"{str(e)}"}
    data = response.data
    if data:
        # titles          = [preprocess_text(f"{row['title']}") for row in data]
        # descriptions    = [preprocess_text(f"{row['description']}") for row in data]
        # texts           = [preprocess_text(f"{row['text']}") for row in data]
        try:
            if not qdrant.collection_exists(HYBRID_COLLECTION):
                qdrant.create_collection(
                    collection_name=HYBRID_COLLECTION,
                    vectors_config={
                        DESCRIPTION_VECTOR: models.VectorParams(
                            size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
                            distance=models.Distance.COSINE,
                        ),
                        TITLE_VECTOR: models.VectorParams(
                            size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
                            distance=models.Distance.COSINE,
                        ),
                        TEXT_VECTOR: models.VectorParams(
                            size=encoder.get_sentence_embedding_dimension(),  # Vector size is defined by used model
                            distance=models.Distance.COSINE,
                        ),
                    }
                )
            points = []
            for row in data:
                points.append(
                        models.PointStruct(
                            id=row["id"],
                            vector={
                                DESCRIPTION_VECTOR: encoder.encode(preprocess_text(f"{row['description']}")).tolist(),
                                TITLE_VECTOR: encoder.encode(preprocess_text(f"{row['title']}")).tolist(),
                                TEXT_VECTOR: encoder.encode(preprocess_text(f"{row['text']}")).tolist()
                            },
                            payload=row
                        )
                )
            qdrant.upload_points(collection_name=HYBRID_COLLECTION,points=points, wait=False)

            ids = [row["id"] for row in data]
            response = supabase.table(RT_VIDEOTRANSCRIBTION_TABLE).update(
                {__IS_VECTORIZED_V2__: "true"}  # Same value for all
            ).in_("id", ids).execute()

            response = [{"id":row["id"],"title":row["title"],"description":row["description"]} for row in data]
            return response

        except Exception as e:
            return {"status": f"{str(e)}"}

@app.get("/api/v3/search/verify", response_class=HTMLResponse)
async def search3(using: str, query_text: str):
    start = datetime.now()
    query = encoder.encode(query_text).tolist()

    if using == "all":
        try:
            batch = qdrant.query_batch_points(
                collection_name=HYBRID_COLLECTION,
                requests=[
                    models.QueryRequest(
                        query=query,
                        using=TITLE_VECTOR,
                        with_payload=True,
                        limit=20,
                    ),
                    models.QueryRequest(
                        query=query,
                        using=DESCRIPTION_VECTOR,
                        with_payload=True,
                        limit=20,
                    ),
                    models.QueryRequest(
                        query=query,
                        using=TEXT_VECTOR,
                        with_payload=True,
                        limit=20,
                    )
                ]
            )
            results = list(chain.from_iterable([response.points for response in batch]))
        except Exception as e:
            return {"status": f"{str(e)}"}
    else:
        results = qdrant.query_points(
            using=using,
            collection_name=HYBRID_COLLECTION,
            query=query,
            limit=20,
            with_vectors=False
        ).points

    __sorted = sorted(results, key=lambda item: item.score, reverse=True)
    end = datetime.now()
    html = HTML
    html += f"<h3>{INFO}</h3>"
    html += f"<h4><a href=\"/\">Home</a></h4>"
    html += f"<h4><a href=\"{QDRANT_URL}/dashboard#/collections\">{QDRANT_URL}</a></h4>"
    html += f"<h4>{MODEL}</h4>"

    html += """
        <div class="form-container">
        <h2>Test Qdrant Search</h2>
        <form id="testForm" action="/api/v3/search/verify" method="get">
            <div class="form-group">
                <label for="category">Embedded Vector to use for semantic search:</label>
                <select id="using" name="using" required>
    """
    options = [{"value":"title", "text":"Video Title"},
               {"value":"description", "text":"Video Description"},
               {"value":"text", "text":"Video Transcription"},
               {"value":"all", "text": "All Vectors Above Combined"}
    ]
    choice=using
    for option in options:
        if option["value"] == using:
            html += f"<option selected value='{option['value']}'>{option['text']}</option>"
            choice=option['text']
        else:
            html += f"<option value='{option['value']}'>{option['text']}</option>"


    html+= """
                </select>
            </div>
            <div class="form-group">
                <label for="query_text">Query or Prompt Text to use for semantic search:</label>
                <input type="text" id="query_text" name="query_text" placeholder="Please, enter search query..." required
    """
    html += f" value='{query_text}'>"
    html += """
            </div>
            <div class="button-container">
                <button type="submit" id="submitButton">Submit</button>
                <div id="spinner" class="spinner"></div>
            </div>
        </form>
        <div id="overlay" class="overlay"></div>
    </div>
    """
    html += f"<h4 class='green-text'>{choice}:</h4><h4> {query_text}: {(end-start).microseconds/1000}ms</h4>"
    #html += f"<h4>{(end-start).microseconds/1000}ms</h4>"

    html += """
        <table class="my-table">
        <tr>
            <td class="col-5">Score</td>
            <td class="col-10">Video Title</td>
            <td class="col-20">Video Description</td>
            <td class="col-60">Video Transcription</td>
        </tr>
    """
    try:
        for hit in __sorted:
            if using == "all":
                html += f"<tr><td class='col-5'>{hit.score}</td><td class='col-10'>{hit.payload['title']}</td><td class='col-20'>{hit.payload['description']}</td><td class='col-60'>{hit.payload['text'][:2048]}...</td></tr>"
            else:
                if using == "text":
                    html += f"<tr><td class='col-5'>{hit.score}</td><td class='col-10'>{hit.payload['title']}</td><td class='col-20'>{hit.payload['description']} {hit.payload['url']}</td><td class='col-60'>{hit.payload['text'][:2048]}...</td></tr>"
                else:
                    html += f"<tr><td class='col-5'>{hit.score}</td><td class='col-10'>{hit.payload['title']}</td><td class='col-20'>{hit.payload['description']} {hit.payload['url']}</td><td class='col-60'>{hit.payload['text'][:2048]}.....</td></tr>"

    except Exception as e:
        return HTMLResponse(content=f"status: {str(e)}")

    html += """
                 </table>
             </body>
     """
    return HTMLResponse(content=html)

@app.get("/api/v2/search/verify", response_class=HTMLResponse)
async def verify_v2(q: str):
    start = datetime.now()
    results = qdrant.query_points(
        using=USING,
        collection_name=COLLECTION,
        query=encoder.encode(q).tolist(),
        limit=10,
        with_vectors=True
    ).points
    __sorted=sorted(results, key=lambda item: item.score, reverse=True)

    end = datetime.now()
    html = HTML
    html += f"<h3>{INFO}</h3>"
    html += f"<h4><a href=\"/\">Home</a></h4>"
    html += f"<h4><a href=\"{QDRANT_URL}/dashboard#/collections\">{QDRANT_URL}</a></h4>"
    html += f"<h4>{q}: {(end-start).microseconds/1000}ms</h4>"
    #html += f"<h4>{(end-start).microseconds/1000}ms</h4>"

    html += """
        <table class="my-table">
        <tr>
            <td class="col-5">Score</td>
            <td class="col-10">Title</td>
            <td class="col-20">Description</td>
            <td class="col-60">Text</td>
        </tr>
    """
    try:
        for hit in __sorted:
            html += f"<tr><td class='col-5'>{hit.score}</td><td class='col-10'>{hit.payload['title']}</td><td class='col-20'>{hit.payload['description']}</td><td class='col-60'>{hit.payload['text']}</td></tr>"

    except Exception as e:
        return HTMLResponse(content=f"status: {str(e)}")

    html += """
                </table>
            </body>
    """
    return HTMLResponse(content=html)





# if __name__ == "__main__":
#      import uvicorn
#      uvicorn.run(app, host="0.0.0.0", port=8000)


