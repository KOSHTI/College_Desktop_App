import tkinter as tk
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

        scrollbar = Scrollbar(self.root)
        scrollbar.place(relx=0.1, rely=0.5,x=100, relheight=0.75, anchor="w")

        self.pdf_listbox = Listbox(self.root, yscrollcommand=scrollbar.set, font=("Arial", 12))
        self.pdf_listbox.place(relx=0.01, rely=0.5, anchor="w", width=200, height=600)

        scrollbar.config(command=self.pdf_listbox.yview)

        # Frame for displaying PDF content
        self.pdf_frame = tk.Label(self.root)
        self.pdf_frame.place(relx=0.2, rely=0.2,x=20, relwidth=0.75, relheight=0.70)

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
            self.pdf_listbox.select_set(0)
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
                pdf_image = Image.open(pdf_image_path)
                pdf_image = pdf_image.resize((700, 900), Image.Resampling.LANCZOS)  # Resize as needed
                pdf_photo = ImageTk.PhotoImage(pdf_image)
                self.pdf_frame.config(image=pdf_photo)
                self.pdf_frame.image = pdf_photo
        except ValueError:
            messagebox.showerror("Error", "Selected item is not valid.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")

    def review_exam_submissions(self):
        
        select_item = self.pdf_listbox.get(tk.ACTIVE)
        if select_item:
            # Extract the username and filename from the selected item
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
