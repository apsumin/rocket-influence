from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from managers.pages import Pages

app = FastAPI()
app.mount("/docs", StaticFiles(directory="docs"), name="docs")


#encoderV7 = SentenceTransformer(MODEL7)

pages   = Pages ()



@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=f"{pages.root()}")


# if __name__ == "__main__":
#
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

