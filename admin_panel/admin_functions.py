import os
from bson.objectid import ObjectId
import fitz  # PyMuPDF for reading PDFs
import gridfs
import gridfs.errors
from db import get_db
from tkinter import filedialog

PDF_STORAGE_FOLDER = os.path.join(os.path.dirname(__file__), "pdf_submissions")

# Ensure the directory exists. If not, create it.
if not os.path.exists(PDF_STORAGE_FOLDER):
    os.makedirs(PDF_STORAGE_FOLDER)

def review_submission(admin_id, filename):
    db = get_db()
    fs = gridfs.GridFS(db)
    
    submission = db.submissions.find_one({"status": "submitted", "filename":filename})
    if not submission:
        return False, "No submissions available."

    file_id = submission.get("file_id")
    if not file_id:
        return False, "File ID is missing in submission."
    try:
        file_data = fs.get(file_id).read()
    except gridfs.errors.NoFile:
        return False, "Failed to retrieve the file from the database."

    # doc = fitz.open(stream=file_data, filetype=".pdf")
    pdf_path = os.path.join(PDF_STORAGE_FOLDER, filename)
    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(file_data)

    return True, pdf_path

def save_submission(submission_id):
    db = get_db()
    db.submissions.update_one({"_id": ObjectId(submission_id)}, {"$set": {"status": "reviewed"}})
    return True, "Submission reviewed."

def get_uploaded_pdfs():
    db = get_db()
    submissions = db.submissions.find({"status": "submitted"})
    
    pdf_list = []
    for submission in submissions:
        
        student_id = submission.get("student_id", "No Username")
        filename =  submission.get("filename", "Unknown.pdf")

        if filename:
            pdf_info = {
            "username": student_id,
            "filename": filename
            }
            pdf_list.append(pdf_info)
            # print(f"Found submission: Username: {student_id} - Filename: {filename}")
        else:
            print(f"Missing filename in submission: {submission}")
    
    return pdf_list
