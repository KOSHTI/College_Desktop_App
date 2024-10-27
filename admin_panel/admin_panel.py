import tkinter as tk
import fitz  # PyMuPDF
import os
from tkinter import messagebox, Scrollbar, Listbox
from PIL import Image, ImageTk
from admin_panel.admin_functions import get_uploaded_pdfs, review_submission


class AdminPanel:
    def __init__(self, root, admin_id):
        self.root = root
        self.root.geometry("1200x800")
        self.admin_id = admin_id
        self.root.title("Admin Panel")
        self.bg_image = Image.open("static/background.jpg")
        self.bg_label = None
        self.bg_photo = None  # To avoid garbage collection
        self.PDF_STORAGE_FOLDER = os.path.join(os.path.dirname(__file__), "pdf_submissions")
        if not os.path.exists(self.PDF_STORAGE_FOLDER):
            os.makedirs(self.PDF_STORAGE_FOLDER)
        self.root.bind("<Configure>", self.resize_background)
        self.load_admin_panel()

        self.pdf_frame = tk.Frame(self.root, width=400, height=1200)
        self.pdf_frame.place(relx=0.2, rely=0.2, x=20, relwidth=0.75, relheight=0.70)

        self.pdf_canvas = tk.Canvas(self.pdf_frame, width=400, height=600)
        self.pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        self.scrollbar = tk.Scrollbar(self.pdf_frame, orient=tk.VERTICAL, command=self.pdf_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to work with the scrollbar
        self.pdf_canvas.config(yscrollcommand=self.scrollbar.set)
        self.pdf_canvas.bind("<Configure>", lambda e: self.pdf_canvas.config(scrollregion=self.pdf_canvas.bbox("all")))

        # Create a frame inside the canvas where the PDF images will be displayed
        self.pdf_display_frame = tk.Frame(self.pdf_canvas)
        self.pdf_canvas.create_window((0, 0), window=self.pdf_display_frame, anchor="nw")

        # Keep track of displayed images to prevent garbage collection
        self.image_references = []

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

        scrollbar = Scrollbar(self.root)
        scrollbar.place(relx=0.1, rely=0.5, x=100, relheight=0.75, anchor="w")

        self.pdf_listbox = Listbox(self.root, yscrollcommand=scrollbar.set, font=("Arial", 12))
        self.pdf_listbox.place(relx=0.01, rely=0.5, anchor="w", width=200, height=600)

        scrollbar.config(command=self.pdf_listbox.yview)

        # Populate the listbox with uploaded PDFs
        self.load_uploaded_pdfs()

        # Save Submissions button (centered dynamically)
        self.review_button = tk.Button(self.root, text="Save", font=("Arial", 12, "bold"), bg="#3de1a0", fg="#151c18", command=self.review_exam_submissions)
        self.review_button.place(relx=0.95, rely=0.95, anchor="se", width=100, height=50)

        # Logout button (aligned to the top right)
        self.logout_button = tk.Button(self.root, text="Logout", font=("Arial", 12, "bold"), bg="#FF5733", fg="white", command=self.logout)
        self.logout_button.place(relx=0.9, rely=0.05, anchor="ne", width=100, height=30)

        # Bind listbox selection
        self.pdf_listbox.bind("<<ListboxSelect>>", self.on_select)

        # Automatically select and display the first item
        if self.pdf_listbox.size() > 0:
            self.pdf_listbox.select_set(1)
            self.load_pdf()

    def load_uploaded_pdfs(self):
        pdfs = get_uploaded_pdfs()
        if not pdfs:
            messagebox.showinfo("No Submissions", "There are no PDF submissions at this moment.")
        else:
            self.pdf_listbox.delete(0, tk.END)

            for pdf in pdfs:
                display_text = f"Username: {pdf['username']} - Filename: {pdf['filename']}"
                self.pdf_listbox.insert(tk.END, display_text)

    def on_select(self, event):
        self.load_pdf()

    def load_pdf(self):
        try:
            select_item = self.pdf_listbox.get(tk.ACTIVE)  # Get the selected item
            username, filename = select_item.split(" - Filename: ")  # Split the username and filename
            success, pdf_image_path = review_submission(self.admin_id, filename)
            if success:
                self.display_all_pages(pdf_path=pdf_image_path)
            else:
                self.clear_pdf_display()  # Clear if there's no valid submission
        except ValueError:
            messagebox.showerror("Error", "Selected item format is not valid.")
        except Exception as e:
            pass

    def display_all_pages(self, pdf_path):
        # Clear the PDF frame before displaying new pages
        for widget in self.pdf_display_frame.winfo_children():
            widget.destroy()

        self.image_references.clear()  # Clear previous image references

        try:
            doc = fitz.open(pdf_path)  # Open the PDF

            # Loop through the pages and display them in the Canvas
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()  # Convert the page to an image

                # Convert PyMuPDF pixmap to a PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # Resize the image to fit within the frame (if needed)
                img = img.resize((500, 700), Image.Resampling.LANCZOS)

                # Convert PIL image to ImageTk format for Tkinter
                tk_image = ImageTk.PhotoImage(img)

                # Create a label to hold the image
                label = tk.Label(self.pdf_display_frame, image=tk_image)
                label.pack()

                # Store a reference to avoid garbage collection
                self.image_references.append(tk_image)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")

    def review_exam_submissions(self):
        select_item = self.pdf_listbox.get(tk.ACTIVE)
        if select_item:
            try:
                _, filename = select_item.split(" - Filename: ")
                success, message = review_submission(self.admin_id, filename)
                if success:
                    messagebox.showinfo("Success", message)
                else:
                    messagebox.showerror("Error", message)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load submission: {str(e)}")
        else:
            messagebox.showerror("Error", "No PDF selected.")

    def logout(self):
        confirm_logout = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm_logout:
            self.root.destroy()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def clear_pdf_display(self):
        for widget in self.pdf_display_frame.winfo_children():
            widget.destroy()
