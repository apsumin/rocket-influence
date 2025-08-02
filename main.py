import os



from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


from fastapi.middleware.cors import CORSMiddleware


CODE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(CODE_DIR)


S__TATIC_DIR = os.path.join(ROOT_DIR, "static")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/api/search")
async def read_item(q: str, t: str, neural: bool = True):
    return {
        "result": 1
    }


