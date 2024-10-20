import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from admin_panel.admin_functions import review_submission

class AdminPanel:
    def __init__(self, root, admin_id):
        self.root = root
        self.root.geometry("1200x800")
        self.admin_id = admin_id
        self.root.title("Admin Panel")
        self.bg_image = Image.open("static/background.jpg")  # Path to background image
        self.bg_label = None
        self.bg_photo = None  # To avoid garbage collection
        self.root.bind("<Configure>", self.resize_background)
        self.load_admin_panel()

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

    def load_admin_panel(self):
        self.clear_screen()
        self.set_background()

        # Title label for the admin dashboard (centered dynamically)
        self.title_label = tk.Label(self.root, text="Welcome, Admin Dashboard", font=("Helvetica", 24, "bold"), bg="#2C3333", fg="#FFD700")
        self.title_label.place(relx=0.5, rely=0.1, anchor="center")  # Centered at the top

        # Review Submissions button (centered dynamically)
        self.review_button = tk.Button(self.root, text="Review Submissions", font=("Arial", 14, "bold"), bg="#FFD700", fg="#2C3333", command=self.review_exam_submissions)
        self.review_button.place(relx=0.5, rely=0.3, anchor="center", width=300, height=50)

        # Logout button (aligned to the top right)
        self.logout_button = tk.Button(self.root, text="Logout", font=("Arial", 12, "bold"), bg="#FF5733", fg="white", command=self.logout)
        self.logout_button.place(relx=0.9, rely=0.05, anchor="ne", width=100, height=30)

    def review_exam_submissions(self):
        success, message = review_submission(self.admin_id)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def logout(self):
        confirm_logout = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm_logout:
            self.root.destroy()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
