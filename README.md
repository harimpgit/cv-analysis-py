**CV Analysis System**

**Overview**
This is a CV analysis system built using FastAPI. It extracts information from CVs (PDF, Word), stores structured data, and allows querying via a chatbot interface powered by an LLM (llama-3.3 via openrouter.ai).

**Features**
•	Upload CVs (PDF, DOCX)
•	Extract key information (name, email, phone, skills, experience, education, etc.)
•	Store structured data in JSON format
•	Query CV details using an AI-powered chatbot
•	Web-based UI for interaction

**Setup Instructions**

**Prerequisites**
•	Python 3.10+
•	Poppler (for pdf2image)(https://github.com/oschwartz10612/poppler-windows/releases)
•	Tesseract OCR (for OCR extraction)(https://github.com/UB-Mannheim/tesseract/wiki)
•	Ensure both Poppler and Tesseract are added to the system PATH

**Installation**
1.	Clone the repository:
2.	git clone https://github.com/harimpgit/cv-analysis-py.git
3.	cd cv-analysis-system

4.	Create a virtual environment and activate it:
5.	python -m venv venv  
6.	source venv\Scripts\activate  

7.	Install dependencies:
8.	pip install -r requirements.txt  

9.	Set up environment variables:
    Copy .env.example to .env

10.	Start the FastAPI server:
11.	uvicorn main:app --reload  

12.	Open your browser and navigate to:
13.	http://127.0.0.1:8000  

**API Endpoints**
•	POST /upload_cv/ - Uploads and processes a CV
•	GET /list_cvs/ - Lists available CVs
•	POST /chatbot/ - Queries the chatbot about a selected CV
•	GET / - Serves the web-based UI

**Testing**
To run tests:
pytest tests/ 
