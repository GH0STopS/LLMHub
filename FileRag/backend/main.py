from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from starlette.responses import JSONResponse
from ingest import ingest_codebase
from rag_chain import CodeAssistantBot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = [],
    allow_credentials = True,
    allow_headers = ["*"],
    allow_methods = ["*"]
)

# class UploadFile(BaseModel):
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class Query(BaseModel):
    query : str

def secure_filename(filename:str)->str:
    return Path(filename).name
    

@app.post("/uploadFile")
async def uploadFile(file : UploadFile = File(...)):
    file_name = file.filename.split('.')[0]
    if not file_name:
        raise HTTPException(status_code=400, detail="Invaid file")
    dest = UPLOAD_DIR / file_name
    contents = await file.read()
    with open(dest, 'wb') as f:
        f.write(contents)

    ingest_codebase(dest)

    return JSONResponse(
        {"filename": file_name, "size": len(contents)}
    )

@app.post("/query")
async def askBot(query : Query):
    bot = CodeAssistantBot()
    print(query.query)
    res = bot.analyze(query.query)
    if res:
        return JSONResponse(
            {"response":res}
        )
    raise HTTPException(status_code=400, detail="LLM Down!")


    # return {"message":"Hi"}
@app.get("/function")
async def function():
    bot = CodeAssistantBot()
    print("------------hi")
    res = bot.list_functions()
    print(res)
    if res:
        return JSONResponse({
            "response":res
        })
    raise HTTPException(status_code=400, detail="failed")

@app.get("/imports")
async def imports():
    bot = CodeAssistantBot()
    print("------------hi")
    res = bot.list_imports()
    print(res)
    if res:
        return JSONResponse({
            "response":res
        })
    raise HTTPException(status_code=400, detail="failed")

@app.get("/codeSmell")
async def codeSmell():
    bot = CodeAssistantBot()
    print("------------codesmell")
    res = bot.code_smells()
    if res:
        return JSONResponse({
            "response":res
        })
    raise HTTPException(status_code=400, detail="failed")