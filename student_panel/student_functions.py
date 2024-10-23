import fitz  # PyMuPDF 
import cv2
import numpy as np
import gridfs
from db import get_db
from bson import ObjectId
import os

def upload_exam_submission(student_id, exam_id, file_path, filename):
    try:
        if not os.path.exists(file_path):
            return False, "File does not exist."
        doc = fitz.open(file_path)
        db = get_db()
        fs = gridfs.GridFS(db)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            if pix.n == 4:
                cv_img = cv2.cvtColor(img_data, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                cv_img = cv2.cvtColor(img_data, cv2.COLOR_RGB2BGR)
            else:
                cv_img = img_data
            if cv2.Laplacian(cv_img, cv2.CV_64F).var() < 50:
                return False, "Image quality is too low on page {}".format(page_num + 1)
        with open(file_path, "rb") as f:
            file_id = fs.put(f, filename=f"{student_id}_{exam_id}.pdf")
        db.submissions.insert_one({
            "student_id": student_id,
            "exam_id": exam_id,
            "file_id": file_id,
            "filename": filename,
            "status": "submitted"
        })
        return True, "PDF uploaded successfully."
    except Exception as e:
        return False, str(e)
