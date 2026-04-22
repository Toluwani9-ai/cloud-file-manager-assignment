from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, StreamingResponse

import google.oauth2.id_token
import google.auth.transport.requests

from pymongo import MongoClient
import certifi
from datetime import datetime
import io
import hashlib

from azure.storage.blob import BlobServiceClient

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

firebase_request_adapter = google.auth.transport.requests.Request()


# Mongodb
MONGO_URL = "mongodb+srv://webtechno:FastapiMongo123%21@cluster0.ifvpn.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URL, tlsCAFile=certifi.where())
db = client["fastapi_db"]
users_collection = db["users"]


# AZURE STORAGE (AZURITE)
AZURE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNoqFlqUwJPLlmEtlCDXJ1OUzFT50zjU8xG7t1M9l0=bYf9r5c=;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

CONTAINER_NAME = "files"

try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    try:
        container_client.create_container()
    except:
        pass
    print(" Azure connected")
except Exception as e:
    print(" Azure error:", e)
    container_client = None



def get_user(request: Request):
    id_token = request.cookies.get("token")

    if not id_token:
        return None, RedirectResponse("/?error=Not logged in", status_code=303)

    try:
        user_token = google.oauth2.id_token.verify_firebase_token(
            id_token, firebase_request_adapter
        )
        return user_token, None
    except Exception:
        return None, RedirectResponse("/?error=Session expired, login again", status_code=303)



# Path helper
def get_folder_by_path(root, path):
    if path in ["", "/"]:
        return root

    parts = path.strip("/").split("/")
    current = root

    for part in parts:
        current = next((f for f in current.get("folders", []) if f["name"] == part), None)
        if not current:
            return None

    return current

# HOME
@app.get("/")
async def root(request: Request):
    user_token = None
    error_message = request.query_params.get("error")
    folders = []
    files = []
    current_path = request.query_params.get("path", "/")

    search = request.query_params.get("search")
    sort = request.query_params.get("sort")

    id_token = request.cookies.get("token")

    if id_token:
        try:
            user_token = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter
            )

            email = user_token["email"]

            users_collection.update_one(
                {"email": email},
                {
                    "$set": {"email": email, "last_login": datetime.utcnow()},
                    "$setOnInsert": {
                        "root": {"name": "/", "folders": [], "files": []}
                    }
                },
                upsert=True
            )

            user_data = users_collection.find_one({"email": email})
            root_folder = user_data.get("root", {})
            current_folder = get_folder_by_path(root_folder, current_path)

            if current_folder:
                folders = current_folder.get("folders", [])
                files = current_folder.get("files", [])


                if search:
                    files = [f for f in files if search.lower() in f["name"].lower()]

                if sort == "name":
                    files = sorted(files, key=lambda x: x["name"])
                elif sort == "date":
                    files = sorted(files, key=lambda x: x.get("uploaded_at", ""), reverse=True)


                hash_count = {}
                for f in files:
                    h = f.get("hash")
                    if h:
                        hash_count[h] = hash_count.get(h, 0) + 1

                for f in files:
                    f["is_duplicate"] = hash_count.get(f.get("hash"), 0) > 1

        except Exception:
            error_message = "Session expired, login again"

    return templates.TemplateResponse("main.html", {
        "request": request,
        "user_token": user_token,
        "folders": folders,
        "files": files,
        "current_path": current_path,
        "error_message": error_message
    })


# Create folder
@app.post("/create-folder")
async def create_folder(request: Request, folder_name: str = Form(...), path: str = Form("/")):
    user_token, error = get_user(request)
    if error:
        return error

    email = user_token["email"]

    user_data = users_collection.find_one({"email": email})
    root = user_data["root"]
    current = get_folder_by_path(root, path)

    if not current:
        return RedirectResponse("/?error=Invalid path", status_code=303)

    current["folders"].append({
        "name": folder_name,
        "folders": [],
        "files": []
    })

    users_collection.update_one({"email": email}, {"$set": {"root": root}})
    return RedirectResponse(f"/?path={path}", status_code=303)



# Upload file

@app.post("/upload-file")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    path: str = Form("/"),
    overwrite: str = Form("false")
):
    user_token, error = get_user(request)
    if error:
        return error

    email = user_token["email"]

    content = await file.read()
    file_hash = hashlib.md5(content).hexdigest()

    user_data = users_collection.find_one({"email": email})
    root = user_data["root"]
    current = get_folder_by_path(root, path)

    if not current:
        return RedirectResponse("/?error=Invalid path", status_code=303)

    existing = next((f for f in current.get("files", []) if f["name"] == file.filename), None)

    if existing and overwrite == "false":
        return RedirectResponse(
            f"/?path={path}&error=File exists. Confirm overwrite.",
            status_code=303
        )

    safe_path = path.strip("/")
    blob_name = f"{email}/{safe_path}/{file.filename}" if safe_path else f"{email}/{file.filename}"

    container_client.get_blob_client(blob_name).upload_blob(content, overwrite=True)

    if not existing:
        current["files"].append({
            "name": file.filename,
            "hash": file_hash,
            "size": len(content),
            "type": file.content_type,
            "uploaded_at": datetime.utcnow()
        })

    users_collection.update_one({"email": email}, {"$set": {"root": root}})

    return RedirectResponse(f"/?path={path}", status_code=303)


# Delete file
@app.post("/delete-file")
async def delete_file(request: Request, filename: str = Form(...), path: str = Form("/")):
    user_token, error = get_user(request)
    if error:
        return error

    email = user_token["email"]

    safe_path = path.strip("/")
    blob_name = f"{email}/{safe_path}/{filename}" if safe_path else f"{email}/{filename}"

    container_client.get_blob_client(blob_name).delete_blob()

    user_data = users_collection.find_one({"email": email})
    root = user_data["root"]
    current = get_folder_by_path(root, path)

    if current:
        current["files"] = [f for f in current["files"] if f["name"] != filename]

    users_collection.update_one({"email": email}, {"$set": {"root": root}})

    return RedirectResponse(f"/?path={path}", status_code=303)


# Download file
@app.get("/download-file")
async def download_file(request: Request, filename: str, path: str = "/"):
    user_token, error = get_user(request)
    if error:
        return error

    email = user_token["email"]

    safe_path = path.strip("/")
    blob_name = f"{email}/{safe_path}/{filename}" if safe_path else f"{email}/{filename}"

    data = container_client.get_blob_client(blob_name).download_blob().readall()

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/view-file")
async def view_file(request: Request, filename: str, path: str = "/"):
    user_token, error = get_user(request)
    if error:
        return error

    email = user_token["email"]

    safe_path = path.strip("/")
    blob_name = f"{email}/{safe_path}/{filename}" if safe_path else f"{email}/{filename}"

    blob = container_client.get_blob_client(blob_name)
    data = blob.download_blob().readall()

    # basic type detection
    if filename.endswith((".png", ".jpg", ".jpeg")):
        media_type = "image/jpeg"
    elif filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".txt"):
        media_type = "text/plain"
    else:
        media_type = "application/octet-stream"

    return StreamingResponse(io.BytesIO(data), media_type=media_type)