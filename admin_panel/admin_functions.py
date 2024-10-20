import fitz  # PyMuPDF
import gridfs
from db import get_db
from tkinter import filedialog

def review_submission(admin_id):
    db = get_db()
    fs = gridfs.GridFS(db)
    
    submission = db.submissions.find_one({"status": "submitted"})
    if not submission:
        return False, "No submissions available."

    file_id = submission["file_id"]
    file_data = fs.get(file_id).read()

    doc = fitz.open(stream=file_data, filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap()
    pix.save("temp.png")

    return True, "PDF loaded for review."

def save_submission(submission_id):
    db = get_db()
    db.submissions.update_one({"_id": ObjectId(submission_id)}, {"$set": {"status": "reviewed"}})
    return True, "Submission reviewed."
