from supabase import create_client, Client
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct
from qdrant_client.http.models import MatchValue
from qdrant_client.http.models import PayloadSchemaType

from sentence_transformers import SentenceTransformer
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import hashlib
import json
import re
import json

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List



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

RT_VIDEOTRANSCRIPTION_TABLE_V2 	="rt_videotranscription_v2"
__IS_VECTORIZED__           	="is_vectorized"
__TEXT__                    	="text"
__IS_VECTORIZED_V2__        	="is_vectorized_v2"

qdrant = QdrantClient(QDRANT_URL, api_key=QDRANT_API_KEY, timeout=180)

VERSION     ="1.0.1.2"
INFO        =f"Rocket Influence Middleware server. v{VERSION}"
COLLECTION  = "rocket-influence"
USING       ="descriptions"


HYBRID_COLLECTION_V2 = "rocket-influence-hybrid-V2"

MODEL  	="paraphrase-multilingual-MiniLM-L12-v2"

encoder = SentenceTransformer(MODEL)

DESCRIPTION_VECTOR="description"
TITLE_VECTOR="title"
TEXT_VECTOR="text"

@app.get("/api/v4/reload")
async def reload4():

    try:

        response = (
            supabase.table(RT_VIDEOTRANSCRIPTION_TABLE_V2).select("*")
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
            if not qdrant.collection_exists(HYBRID_COLLECTION_V2):
                qdrant.create_collection(
                    collection_name=HYBRID_COLLECTION_V2,
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

        except Exception as e:
            return {"status": f"{str(e)}"}
        try:
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
            qdrant.upload_points(collection_name=HYBRID_COLLECTION_V2, points=points, wait=False)

            ids = [row["id"] for row in data]
            response = supabase.table(RT_VIDEOTRANSCRIPTION_TABLE_V2).update(
                    {__IS_VECTORIZED_V2__: "true"}  # Same value for all
                ).in_("id", ids).execute()

            response = [{"id": row["id"], "title": row["title"], "description": row["description"]} for row in data]
            return response

        except Exception as e:
            return {"status": f"{str(e)}"}

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s\-.,;:!?]', '', text)
    return text or "none"


class QdrantRequestFilter(BaseModel):
    index: str = Field(..., min_length=0, max_length=50, example="channel_name")
    value: str = Field(..., min_length=0, max_length=1024, example="")

class QdrantRequest(BaseModel):
    limit: int = Field(..., gt=0, lt=120, example=30)
    tags: Optional[List[str]] = Field([], example=["technology", "music"])
    filters: Optional[List[QdrantRequestFilter]] = Field([], example=[])


class QdrantResponse(BaseModel):
    status: str = "ok"

# @app.post("/api/v4/search/verify")
# async def verify4post(request: Request):
#     # Get raw body and decode explicitly
#     body = await request.body()
#
#     # Print raw bytes for debugging
#     print(f"Raw bytes: {body}")
#
#     # Decode as UTF-8
#     try:
#         decoded_body = body.decode('utf-8')
#         print(f"Decoded text: {decoded_body}")
#     except UnicodeDecodeError as e:
#         return {"error": f"UTF-8 decoding failed: {e}"}
#
#     return {"status": "ok"}

@app.get("/api/v5/search")
async def search5(request: Request):
    # Get raw body and decode explicitly
    params = dict(request.query_params)
    # Parse JSON
    try:
        request = json.loads(params['q'])
    except json.JSONDecodeError as e:
        return {"status": f"{str(e)}"}

    tags={}
    if len(request["filters"])>0:
        query_filter = models.Filter(must=[models.FieldCondition(key=request["filters"][0]["index"],match=MatchValue(value=request["filters"][0]["value"]) )])
    else:
        query_filter = models.Filter(must=[])

    response=[]
    for tag in request["tags"]:
        try:
            query = encoder.encode(tag).tolist()
            results = qdrant.query_points(
                using=TEXT_VECTOR,
                collection_name=HYBRID_COLLECTION_V2,
                query=query,
                limit=request["limit"],
                query_filter=query_filter,
                with_payload=True
            ).points
            response.append ({"tag":tag,"value":sorted(results, key=lambda item: item.score, reverse=True)})
        except Exception as e:
            return {"status": f"{str(e)}"}

    return response





@app.get("/api/v5/search/verify", response_class=HTMLResponse)
async def verify5(request: Request):

    start = datetime.now()
    end = datetime.now()
    html = HTML
    html += f"<h3>{INFO}</h3>"
    html += f"<h4><a href=\"/\">Home</a></h4>"
    html += f"<h4><a href=\"{QDRANT_URL}/dashboard#/collections\">{QDRANT_URL}</a></h4>"
    #html += f"<h4>{q}: {(end-start).microseconds/1000}ms</h4>"
    html += f"<h4>{start}</h4>"

    html += """
        <div class="form-container">
        <h2>Customer #1 Digital Profile:</h2>
        <form id="testForm" action="/api/v5/search" method="get">
            <div class="form-group">
                <label for="category">Channels:</label>
                <select id="channel_name" name="channel_name">
    """
    for channel in CHANNELS:
        html += f"<option value='{channel['channel_name']}'>{channel['channel_name']}</option>"

    html+= """
                </select>
                <br><br>
            </div>
            <div class="form-group">
                <label for="category">Vectorized Tags:</label>
    """
    for idx, vtag in enumerate(VECTORED_TAGS):
        html += f"<input type='checkbox' id='tag{idx}' name='tag' value='{vtag}'>{vtag}<br>"

    html += """
            </div>
             <div class="button-container">
                <button type="submit" id="submitButton">Submit</button>
                <div id="spinner" class="spinner"></div>
            </div>
            <div id="overlay" class="overlay"></div>
        </form>
    </div>
    <div id="content">
        <p>Content will be loaded here...</p>
    </div>
    </body>
    """
    html += SCRIPT
    return HTMLResponse(content=html)







# @app.get("/api/v4/search/verify")
# async def verify4():
#     request={
#         "limit":10,
#         "tags":[
#             "встреча Путина и Трампа на Аляске",
#             "как построить дом правильно",
#             "что такое Автомобиль",
#             "про криптовалюту и биткоины"
#         ],
#         "filters":[
#             {"index":"channel_name","value":"Blockchain Pro Channel"}
#         ]
#     }
#
#     # try:
#     #     # Create payload indexes
#     #     # qdrant.create_payload_index(
#     #     #     collection_name=HYBRID_COLLECTION_V2,
#     #     #     field_name="channel_name",
#     #     #     field_schema=PayloadSchemaType.KEYWORD
#     #     # )
#     #     # collection_info = qdrant.get_collection(HYBRID_COLLECTION_V2)
#     #     # print("Created indexes:", list(collection_info.config.params.payload_schema.keys()))
#     #
#     #     # qdrant.update_collection(
#     #     #     collection_name=HYBRID_COLLECTION_V2,
#     #     #     payload_schema={"channel_name": PayloadSchemaType.KEYWORD}
#     #     # )
#     # except Exception as e:
#     #     return {"status": f"{str(e)}"}
#
#     tags={}
#     if len(request["filters"])>0:
#         query_filter = models.Filter(must=[models.FieldCondition(key=request["filters"][0]["index"],match=MatchValue(value=request["filters"][0]["value"]) )])
#     else:
#         query_filter = models.Filter(must=[])
#
#     for tag in request["tags"]:
#         try:
#             query = encoder.encode(tag).tolist()
#             tags[tag] = qdrant.query_points(
#                 using=TEXT_VECTOR,
#                 collection_name=HYBRID_COLLECTION_V2,
#                 query=query,
#                 limit=request["limit"],
#                 query_filter=query_filter,
#                 with_payload=True
#             ).points
#         except Exception as e:
#             return {"status": f"{str(e)}"}
#     print(tags)
#     return {"status": "ok"}


HTML = """
    <!DOCTYPE html>
    <html lang="en">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Qdrant Semantic Search</title>
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
            width: 80%;
            max-width: 600px;
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
    <body>
"""

SCRIPT="""
    <script>
    
        const contentDiv = document.getElementById('content');
        function truncateString(str, maxLength, suffix = '...') {
            if (str.length <= maxLength) return str;
            return str.slice(0, maxLength - suffix.length) + suffix;
        }

                    
        document.addEventListener('DOMContentLoaded', function() {
   
            const form = document.getElementById('testForm');
            const submitButton = document.getElementById('submitButton');
            const spinner = document.getElementById('spinner');
            const overlay = document.getElementById('overlay');
            const channel = document.getElementById('channel');
            form.addEventListener('submit', function(e) {
            
                e.preventDefault();
                // Show spinner and overlay
                spinner.style.display = 'block';
                overlay.style.display = 'block';
                submitButton.disabled = true;

                // Get form data
                const formData = new FormData(form);
                const urlParams = new URLSearchParams(formData)
                
                var payload = {"limit":10,"tags":[],"filters":[]}
                for (let [key, value] of formData.entries()) {
                    if (key == "tag" && value.length!=0){
                        payload.tags.push (value)         
                    }
                    if (key == "channel_name" && value.length!=0){
                        payload.filters.push ({"index":key,"value":value})
                    }
                }
                const url = `/api/v5/search?q=${JSON.stringify(payload)}`;
                fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json(); // Parse JSON data
                })
                .then(data => {
                    var html="";
                    data.forEach(tag => {
                            html+=`<h4 class='green-text'>${tag.tag}:</h4>`
                            console.log (tag.tag)
                            html+='<table class="my-table"><tr><td class="col-5">Score</td><td class="col-10">Video Title</td><td class="col-20">URL</td><td class="col-10">Channel</td><td class="col-60">Video Transcription</td></tr>'                            
                            tag.value.forEach(hit => {
                                html+=`<tr><td class='col-5'>${hit.score}</td><td class='col-10'>${hit.payload['title']}</td><td class='col-20'>${hit.payload['url']}</td><td class='col-10'>${hit.payload['channel_name']}</td><td class='col-60'>${truncateString(hit.payload['text'], 2048)}</td></tr>`
                                console.log (hit.score)
                            });
                            html+="</table>"                            
                    });
                    contentDiv.innerHTML    = html;//JSON.stringify(data);
                    spinner.style.display   = 'none';
                    overlay.style.display   = 'none';
                    submitButton.disabled   = false;
                })
                .catch(error => {
                    // Handle errors
                    contentDiv.innerHTML = `<p class="error">Error loading content: ${error.message}</p>`;
                    console.error('Error:', error);
                });
            });
        });
    </script>
"""

OPTIONS = [
    {"value": "title", "text": "Video Title"},
    {"value": "description", "text": "Video Description"},
    {"value": "text", "text": "Video Transcription"},
    {"value": "all", "text": "All Vectors Above Combined"}
]

CHANNELS=[
    {
        "channel_name": ""
    },

    {
    "channel_name": "#ХОЧУКВАРТИРУ"
  },
  {
    "channel_name": "AcademeG"
  },
  {
    "channel_name": "Alan Enileev"
  },
  {
    "channel_name": "Alanya - Жизнь без купюр"
  },
  {
    "channel_name": "Alexander Kondrashov"
  },
  {
    "channel_name": "Alexandra Sokolova - Income Mersin Real Estate"
  },
  {
    "channel_name": "Andrey Burenok"
  },
  {
    "channel_name": "ASATA “BORODA” channel"
  },
  {
    "channel_name": "BitNovosti.com"
  },
  {
    "channel_name": "Blockchain Pro Channel"
  },
  {
    "channel_name": "carwow Русская версия"
  },
  {
    "channel_name": "Clickoncar"
  },
  {
    "channel_name": "Combat Crew"
  },
  {
    "channel_name": "CryptoFateev Ripple XRP Трейдер"
  },
  {
    "channel_name": "CRYPTUS"
  },
  {
    "channel_name": "CSCALP TV"
  },
  {
    "channel_name": "DragtimesInfo"
  },
  {
    "channel_name": "DSC OFF"
  },
  {
    "channel_name": "Era of change finance"
  },
  {
    "channel_name": "forklog"
  },
  {
    "channel_name": "GOOD WOOD Строительство домов"
  },
  {
    "channel_name": "HAMAHA"
  },
  {
    "channel_name": "HomeHunter"
  },
  {
    "channel_name": "Ilia Bondarev"
  },
  {
    "channel_name": "Ivan Zenkevich PRO Cars"
  },
  {
    "channel_name": "JETCAR"
  },
  {
    "channel_name": "Kirill Evans"
  },
  {
    "channel_name": "M2TV - Недвижимость с экспертами"
  },
  {
    "channel_name": "MAJORKA"
  },
  {
    "channel_name": "Mike Supercars TopSpeed (Supercars Miami)"
  },
  {
    "channel_name": "On The Roofs"
  },
  {
    "channel_name": "Pilot Alexander"
  },
  {
    "channel_name": "Prometheus"
  },
  {
    "channel_name": "REPEY - курортная недвижимость"
  },
  {
    "channel_name": "RestProperty Недвижимость в Турции"
  },
  {
    "channel_name": "Samsebeskazal Denis"
  },
  {
    "channel_name": "SEVEN FORCE"
  },
  {
    "channel_name": "smotraTV"
  },
  {
    "channel_name": "The Life of Others"
  },
  {
    "channel_name": "Travel TV Bogdan Bulychev / BogDee"
  },
  {
    "channel_name": "varlamov"
  },
  {
    "channel_name": "VDT l Влог о недвижимости и строительстве"
  },
  {
    "channel_name": "Vitaliy and Liza"
  },
  {
    "channel_name": "Wylsacom"
  },
  {
    "channel_name": "zaRRubin"
  },
  {
    "channel_name": "АВТО ПЛЮС"
  },
  {
    "channel_name": "АНАПЧАНЕ"
  },
  {
    "channel_name": "Антон Воротников"
  },
  {
    "channel_name": "Антон Птушкін"
  },
  {
    "channel_name": "Архитектор Виталий Злобин"
  },
  {
    "channel_name": "Асафьев Стас"
  },
  {
    "channel_name": "Большой тест-драйв"
  },
  {
    "channel_name": "Виктор Садыгов | Москва, Дорогая"
  },
  {
    "channel_name": "Гараж 54"
  },
  {
    "channel_name": "Дима Гордей"
  },
  {
    "channel_name": "ДОМ у МОРЯ"
  },
  {
    "channel_name": "Жекич Дубровский"
  },
  {
    "channel_name": "Игорь Зуевич"
  },
  {
    "channel_name": "ИЛЬДАР АВТО-ПОДБОР"
  },
  {
    "channel_name": "Касё Гасанов"
  },
  {
    "channel_name": "Лиса Рулит"
  },
  {
    "channel_name": "Максим Шелков"
  },
  {
    "channel_name": "Мастерская Синдиката"
  },
  {
    "channel_name": "Маша Себова"
  },
  {
    "channel_name": "МИР НАИЗНАНКУ"
  },
  {
    "channel_name": "Михаил Ширвиндт"
  },
  {
    "channel_name": "Моя Планета"
  },
  {
    "channel_name": "Настя Туман"
  },
  {
    "channel_name": "О НОВОСТРОЙКАХ"
  },
  {
    "channel_name": "Орел и Решка"
  },
  {
    "channel_name": "ПОЕХАВШИЙ"
  },
  {
    "channel_name": "ПриветТачка"
  },
  {
    "channel_name": "Роман Томера"
  },
  {
    "channel_name": "Сергей Смирнов про инвестиции и недвижимость"
  },
  {
    "channel_name": "СЛЕЗЫ САТОШИ"
  },
  {
    "channel_name": "ХОЧУ ДОМОЙ - Путешествия, в которые вы не поедете"
  },
  {
    "channel_name": "Ян Буян - Путешествия"
  }
]


VECTORED_TAGS=[
    "про разработку ИИ",
    "про криптовалюту и биткоины",
    "как правильно и хорошо спланировать дом",
    "про дорогую недвижимость в Дубае",
    "про дорогую недвижимость в Москве",
    "про дорогую недвижимость в Турции",
    "про немецкие автомобили",
    "про японские автомобили",
    "про автомобиль Делориан",
    "про автомобиль Audi A7",
    "новые жилые комплексы в Москве и Подмосковье",
    "про тест драйв немецких автомобилей",
    "про тест драйв японских автомобилей",
    "про тест драйв российских автомобилей",
    "новые жилые комплексы в Москве и Подмосковье",
    "про войну в Украине",
    "встреча Путина и Трампа на Аляске",
    "про сталинские лагеря"
]



# if __name__ == "__main__":
#      import uvicorn
#      uvicorn.run(app, host="0.0.0.0", port=8000)
