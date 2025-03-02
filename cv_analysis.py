import os
import re
import json
import fitz 
import pytesseract
import pdf2image
import docx
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

LLM_API_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_API_KEY = "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"

class CVInfo(BaseModel):
    name: str
    email: str
    phone: str
    education: list
    experience: list
    skills: list
    projects: list
    certifications: list

class ChatbotRequest(BaseModel):
    filename: str
    message: str

async def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_document = fitz.open(pdf_path)
    for page in pdf_document:
        text += page.get_text("text")
    
    if not text.strip():
        images = pdf2image.convert_from_path(pdf_path)
        text = " ".join([pytesseract.image_to_string(img) for img in images])
    
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_information(text):
    name = re.search(r"(?:(Mr|Ms|Dr)\.?\s+)?([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)", text)
    email = re.findall(r'\S+@\S+', text)
    phone = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    skills = re.findall(r"\b(JavaScript|Python|Angular|React|SQL|Java|C\+\+|Node\.js|AI|ML)\b", text, re.I)

    return {
        "name": name.group() if name else "",
        "email": email[0] if email else "",
        "phone": phone[0] if phone else "",
        "education": [], 
        "experience": [], 
        "skills": list(set(skills)),
        "projects": [],
        "certifications": []
    }

def refine_with_llm(cv_text):
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [{"role": "user", "content": f"Extract structured CV data: {cv_text}"}],
        "max_tokens": 200
    }
    response = requests.post(LLM_API_URL, json=payload, headers=headers)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

def save_to_json(cv_data, filename):
    os.makedirs("cv_storage", exist_ok=True)
    filepath = os.path.join("cv_storage", f"{filename}.json")
    with open(filepath, "w", encoding="utf-8") as json_file:
        json.dump(cv_data, json_file, indent=4)
    return filepath

@app.post("/upload_cv/")
async def upload_cv(file: UploadFile = File(...)):
    file_path = f"temp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = await extract_text_from_pdf(file_path) if file.filename.endswith(".pdf") else extract_text_from_docx(file_path)
    extracted_info = extract_information(text)
    structured_data = refine_with_llm(text)
    
    json_path = save_to_json(structured_data, file.filename.split('.')[0])
    
    os.remove(file_path)
    return {"message": "CV processed successfully", "json_path": json_path}

@app.get("/list_cvs/")
def list_cvs():
    files = [f.replace(".json", "") for f in os.listdir("cv_storage") if f.endswith(".json")]
    return {"cvs": files}

@app.post("/chatbot/")
def chatbot_query(request: ChatbotRequest):
    filepath = os.path.join("cv_storage", f"{request.filename}.json")

    #print("File path full:", filepath)
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    
    with open(filepath, "r", encoding="utf-8") as json_file:
        cv_data = json_file.read() 
        #print("File content:", cv_data) 
    
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [{"role": "user", "content": f"Based on the following CV data, {cv_data}, answer this query: {request.message}"}],
        "max_tokens": 200
    }
    response = requests.post(LLM_API_URL, json=payload, headers=headers)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")

@app.get("/")
async def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
