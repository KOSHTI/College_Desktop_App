import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from student_panel.student_functions import upload_exam_submission

class StudentPanel:
    def __init__(self, root, student_id):
        self.root = root
        self.root.geometry("1200x800")
        self.student_id = student_id
        self.root.title("Student Panel")
        self.bg_image = Image.open("static/background.jpg")  # Ensure path is correct
        self.bg_label = None
        self.bg_photo = None  # To avoid garbage collection
        self.root.bind("<Configure>", self.resize_background)
        self.load_student_panel()

    def set_background(self):
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()
        resized_image = self.bg_image.resize((win_width, win_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)
        if not self.bg_label or not self.bg_label.winfo_exists():
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.bg_label.config(image=self.bg_photo)
            self.bg_label.image = self.bg_photo

    def resize_background(self, event):
        self.set_background()

    def load_student_panel(self):
        self.clear_screen()
        self.set_background()

        # Title label for the student dashboard (centered dynamically)
        self.title_label = tk.Label(self.root, text="Welcome, Student's Dashboard", font=("Helvetica", 24, "bold"), bg="#2C3333", fg="#FFD700")
        self.title_label.place(relx=0.5, rely=0.1, anchor="center")  # Centered at the top

        # Upload Exam Submission button (centered dynamically)
        self.upload_button = tk.Button(self.root, text="Upload Exam Submission", font=("Arial", 14, "bold"), bg="#FFD700", fg="#2C3333", command=self.upload_exam_pdf)
        self.upload_button.place(relx=0.5, rely=0.3, anchor="center", width=300, height=50)

        # Check Submission Status button (centered dynamically)
        self.check_status_button = tk.Button(self.root, text="Check Submission Status", font=("Arial", 14, "bold"), bg="#FFD700", fg="#2C3333", command=self.check_submission_status)
        self.check_status_button.place(relx=0.5, rely=0.4, anchor="center", width=300, height=50)

        # Logout button (aligned to the top right)
        self.logout_button = tk.Button(self.root, text="Logout", font=("Arial", 12), bg="#FF5733", fg="white", command=self.logout)
        self.logout_button.place(relx=0.9, rely=0.05, anchor="ne", width=100, height=30)

    def resize_student_panel(self, event):
        """Adjust widget positions dynamically when the window is resized."""
        self.set_background()

        # Adjust title label position dynamically
        self.title_label.place_configure(relx=0.5, rely=0.1, anchor="center")

        # Adjust upload button position dynamically
        self.upload_button.place_configure(relx=0.5, rely=0.3, anchor="center", width=300, height=50)

        # Adjust check status button position dynamically
        self.check_status_button.place_configure(relx=0.5, rely=0.4, anchor="center", width=300, height=50)

        # Adjust logout button position dynamically
        self.logout_button.place_configure(relx=0.9, rely=0.05, anchor="ne", width=100, height=30)


    def upload_exam_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        exam_id = "exam1"  # Example exam ID
        success, message = upload_exam_submission(self.student_id, exam_id, file_path)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def check_submission_status(self):
        messagebox.showinfo("Status", "Exam Status: Exam PDF Submitted")

    def logout(self):
        confirm_logout = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm_logout:
            self.root.destroy()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
