from fastapi import APIRouter, UploadFile, File, Form,Header,Depends
from fastapi.responses import JSONResponse
from datetime import datetime
import os
from PyPDF2 import PdfReader
import shutil
from app.database import textbook_collection
from bson import ObjectId
from fastapi import HTTPException
from collections import defaultdict
from pymongo import ASCENDING
from .jwt_utils import get_current_user_from_header ,require_admin


    
    

router = APIRouter()
router = APIRouter(prefix="/api/textbook", tags=["Text Book"])


# @router.get("/me")
# async def read_my_profile(current_user: dict = Depends(get_current_user_from_header)):
#     # current_user = {'user_id': ..., 'email': ...}
#     return {"message": "Current user fetched successfully", "user": current_user}




BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "textbooks")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)




@router.post("/upload-textbook")
async def upload_textbook(class_name: int = Form(...),subject: str = Form(...),part: str = Form(...),file: UploadFile = File(...),current_admin: dict = Depends(require_admin)):
    filename = os.path.basename(file.filename)
    file_location = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    textbook_data = {
        "class_name": class_name,
        "subject": subject,
        "part": part,
        "file_name": filename,
        "file_path": file_location, 
        "file_url": f"http://localhost:8001/static/textbooks/{filename}",
        "uploaded_at": datetime.utcnow(),
        "uploaded_by": current_admin["user_id"]
    }
    result = await textbook_collection.insert_one(textbook_data)

    return JSONResponse({
        "message": "Textbook uploaded successfully",
        "id": str(result.inserted_id),"file_url": textbook_data["file_url"]})




@router.get("/textbooksnames/{class_name}")
async def get_textbooks_grouped(class_name: int):
    cursor = textbook_collection.find({"class_name": class_name})
    grouped_data = defaultdict(list)
    async for book in cursor:
        grouped_data[book["subject"]].append({
            "id": str(book["_id"]),
            "part": book["part"],
            "file_name": book["file_name"],
            "file_url": book["file_url"],
            "uploaded_at": book["uploaded_at"]
        })
    result = []
    for subject, parts in grouped_data.items():
        result.append({"subject": subject,"parts": parts})
    return result





@router.get("/textbooksshowbyclass/{class_name}")
async def get_textbooks(class_name: int):
    textbooks = []
    cursor = textbook_collection.find({"class_name": class_name})

    async for book in cursor:
        textbooks.append({
            "id": str(book["_id"]),
            "class_name": book["class_name"],
            "subject": book["subject"],
            "part": book["part"],
            "file_name": book["file_name"],
            "file_url": book["file_url"],
            "uploaded_at": book["uploaded_at"]
        })

    return textbooks


@router.get("/textbookbysubject/{class_subject}")
async def get_textbooks(class_subject: str):
    textbooks = []
    cursor = textbook_collection.find({"subject": class_subject}).sort("part", ASCENDING)

    async for book in cursor:
        textbooks.append({
            "id": str(book["_id"]),
            "class_name": book["class_name"],
            "subject": book["subject"],
            "part": book["part"],
            "file_name": book["file_name"],
            "file_url": book["file_url"],
            "uploaded_at": book["uploaded_at"]})
    return textbooks





@router.delete("/delete-textbook/{textbook_id}")
async def delete_textbook(textbook_id: str):
    
    book = await textbook_collection.find_one({"_id": ObjectId(textbook_id)})
    
    if not book:
        raise HTTPException(status_code=404, detail="Textbook not found")
    
    import os
    file_path = book.get("file_path")
    
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    await textbook_collection.delete_one({"_id": ObjectId(textbook_id)})

    return {
        "message": "Textbook deleted successfully"
    }






BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@router.get("/textbooks_with_pagecount/{class_name}")
async def get_textbooks_with_pages(class_name: int):
    textbooks = []
    cursor = textbook_collection.find({"class_name": class_name})

    async for book in cursor:
        file_path = os.path.join(BASE_DIR, book["file_path"])
        page_count = 0

        if os.path.exists(file_path):
            try:
                pdf = PdfReader(file_path)
                page_count = len(pdf.pages)
            except Exception as e:
                print(f"Error reading PDF {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")

        textbooks.append({
            "subject": book["subject"],
            "part": book["part"],
            "page_count": page_count
        })

    return textbooks