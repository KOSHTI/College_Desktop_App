import tkinter as tk
import fitz  # PyMuPDF
import os
from tkinter import messagebox, Scrollbar, Listbox, Canvas, Frame, IntVar
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
        self.A4_WIDTH = 271
        self.A4_HEIGHT = 300
        self.PDF_STORAGE_FOLDER = os.path.join(os.path.dirname(__file__), "pdf_submissions")
        if not os.path.exists(self.PDF_STORAGE_FOLDER):
            os.makedirs(self.PDF_STORAGE_FOLDER)
        self.root.bind("<Configure>", self.resize_background)

        self.image_references = []
        self.is_editing = False
        self.selected_symbol = None  # Default to no symbol
        self.symbol_var = IntVar(value=0)  # 0 for no symbol, 1 for check, 2 for cross
        self.symbol_positions = {}

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

        # Title label
        self.title_label = tk.Label(self.root, text="Welcome, Admin Dashboard", font=("Helvetica", 24, "bold"), bg="#2C3333", fg="#FFD700")
        self.title_label.place(relx=0.5, rely=0.07, anchor="center")

        # Listbox for PDFs
        scrollbar = Scrollbar(self.root)
        scrollbar.place(relx=0.26, rely=0.53, x=100, relheight=0.75, anchor="w")
        self.pdf_listbox = Listbox(self.root, yscrollcommand=scrollbar.set, font=("Arial", 12))
        self.pdf_listbox.place(relx=0.01, rely=0.53, anchor="w", width=400, height=600)
        scrollbar.config(command=self.pdf_listbox.yview)

        # Populate the listbox with uploaded PDFs
        self.load_uploaded_pdfs()

        # Edit button (initially visible)
        self.edit_button = tk.Button(self.root, text="Edit", font=("Arial", 12, "bold"), bg="#3de1a0", fg="#151c18", command=self.start_editing)
        self.edit_button.place(relx=0.85, rely=0.94, anchor="se", width=100, height=30)

        # Save button (initially hidden)
        self.save_button = tk.Button(self.root, text="Save", font=("Arial", 12, "bold"), bg="#e0c1cd", fg="#151c18", command=self.review_exam_submissions)
        self.save_button.place(relx=0.85, rely=0.94, anchor="se", width=100, height=30)
        self.save_button.place_forget()

        # Cancel button (initially hidden)
        self.cancel_button = tk.Button(self.root, text="Cancel", font=("Arial", 12, "bold"), bg="#e0c1cd", fg="#151c18", command=self.cancel_editing)
        self.cancel_button.place(relx=0.75, rely=0.94, anchor="se", width=100, height=30)
        self.cancel_button.place_forget()

        # Radiobuttons for symbol selection
        self.symbol_label = tk.Label(self.root, text="Select Symbol:", bg="#2C3333", fg="#FFFFFF", font=("Arial", 12))
        self.symbol_label.place(relx=0.9, rely=0.15, anchor="ne")

        self.check_symbol_rb = tk.Radiobutton(self.root, text="✔", variable=self.symbol_var, value=1, bg="#31d2f0")
        self.cross_symbol_rb = tk.Radiobutton(self.root, text="✘", variable=self.symbol_var, value=2, bg="#31d2f0")
        
        self.check_symbol_rb.place(relx=0.9, rely=0.2, anchor="ne")
        self.cross_symbol_rb.place(relx=0.9, rely=0.25, anchor="ne")

        # Bind listbox selection
        self.pdf_listbox.bind("<<ListboxSelect>>", self.on_select)

        # Frame for PDF display with ScrollableFrame
        self.pdf_frame = Frame(self.root, width=self.A4_WIDTH, height=self.A4_HEIGHT)
        self.pdf_frame.place(relx=0.35, rely=0.2, x=20, relwidth=0.44, relheight=0.70)

        # Canvas for PDF display
        self.pdf_canvas = Canvas(self.pdf_frame)
        self.pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        self.scrollbar = Scrollbar(self.pdf_frame, orient="vertical", command=self.pdf_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a frame inside the canvas to hold the PDF images
        self.pdf_display_frame = Frame(self.pdf_canvas)
        self.pdf_canvas.create_window((0, 0), window=self.pdf_display_frame, anchor="nw")

        # Link the scrollbar and canvas
        self.pdf_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Update the scroll region when the frame is resized
        self.pdf_display_frame.bind("<Configure>", lambda e: self.pdf_canvas.configure(scrollregion=self.pdf_canvas.bbox("all")))

        # Logout button
        self.logout_button = tk.Button(self.root, text="Logout", font=("Arial", 12, "bold"), bg="#e14b67", fg="#f4f3eb", command=self.logout)
        self.logout_button.place(relx=0.90, rely=0.10, anchor="se", width=100, height=30)

        # Automatically select and display the first item
        if self.pdf_listbox.size() > 0:
            self.pdf_listbox.select_set(0)  # Select first item
            self.load_pdf()

    def start_editing(self):
        self.is_editing = True
        self.edit_button.place_forget()
        self.save_button.place(relx=0.85, rely=0.94, anchor="se", width=100, height=30)
        self.cancel_button.place(relx=0.75, rely=0.94, anchor="se", width=100, height=30)

    def cancel_editing(self):
        if self.is_editing:
            self.is_editing = False
            self.save_button.place_forget()
            self.cancel_button.place_forget()
            self.edit_button.place(relx=0.85, rely=0.96, anchor="se", width=100, height=30)
            self.load_admin_panel()

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
            select_item = self.pdf_listbox.get(tk.ACTIVE)
            username, filename = select_item.split(" - Filename: ")
            success, pdf_image_path = review_submission(self.admin_id, filename)
            if success:
                self.display_all_pages(pdf_path=pdf_image_path)
            else:
                self.clear_pdf_display()
        except ValueError:
            messagebox.showerror("Error", "Selected item format is not valid.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def display_all_pages(self, pdf_path):
        # Clear previous images
        for widget in self.pdf_display_frame.winfo_children():
            widget.destroy()

        self.image_references = []  # Reset image references
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"File '{pdf_path}' not found.")

            doc = fitz.open(pdf_path)

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()

                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img = img.resize((500, 700), Image.Resampling.LANCZOS)
                tk_image = ImageTk.PhotoImage(img)

                label = tk.Label(self.pdf_display_frame, image=tk_image)
                label.image = tk_image  # Keep a reference to avoid garbage collection
                label.pack()

                # Bind click event for placing symbols
                label.bind("<Button-1>", lambda e, page_num=page_num: self.place_symbol(e, page_num))

                self.image_references.append(tk_image)

            # Adjust scrollbar after images are added
            self.pdf_canvas.configure(scrollregion=self.pdf_canvas.bbox("all"))

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while displaying PDF: {e}")

    def place_symbol(self, event, page_num):
        if not self.is_editing:
            messagebox.showwarning("Editing Disabled", "You need to be in editing mode to place symbols.")
            return

        # Retrieve selected symbol from symbol_var
        symbol_value = self.symbol_var.get()
        symbol = "✔" if symbol_value == 1 else "✘" if symbol_value == 2 else None
        if not symbol:
            messagebox.showwarning("Select Symbol", "Please select a symbol to place.")
            return

        x, y = event.x, event.y

        # Display symbol on the GUI
        symbol_label = tk.Label(self.pdf_display_frame, text=symbol, font=("Arial", 24),
                                bg="white", fg="green" if symbol == "✔" else "red")
        symbol_label.place(x=x, y=y)

        # Save the symbol position and details for saving in PDF later
        if not hasattr(self, 'symbols_to_place'):
            self.symbols_to_place = []
        self.symbols_to_place.append({"symbol": symbol, "x": x, "y": y, "page_num": page_num})


    def clear_pdf_display(self):
        for widget in self.pdf_display_frame.winfo_children():
            widget.destroy()

    def review_exam_submissions(self):
        if not self.is_editing:
            messagebox.showwarning("Editing Disabled", "Enable editing to save.")
            return

        try:
            selected_item = self.pdf_listbox.get(tk.ACTIVE)
            _, filename = selected_item.split(" - Filename: ")
            pdf_path = os.path.join(self.PDF_STORAGE_FOLDER, filename)

            # Save PDF with symbols
            edited_pdf_path = self.save_edited_pdf_with_symbols(pdf_path)
            print(f"Edited PDF saved at path: {edited_pdf_path}")

            if not os.path.exists(edited_pdf_path):
                raise FileNotFoundError(f"Edited PDF not found at path: {edited_pdf_path}")

            # Save the edited PDF to MongoDB
            save_result = self.save_edited_pdf(self.admin_id, filename, edited_pdf_path)
            if save_result:
                messagebox.showinfo("Saved", "Your changes have been saved to the database.")
            else:
                raise Exception("Failed to save to the database.")

            self.cancel_editing()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save edited PDF: {e}")


    def save_edited_pdf_with_symbols(self, pdf_path):
        edited_pdf_path = os.path.join(self.PDF_STORAGE_FOLDER, f"edited_{os.path.basename(pdf_path)}")
        doc = fitz.open(pdf_path)

        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Assume self.symbols_to_place is a list of dictionaries with the structure:
                # {"symbol": "✔" or "✘", "x": int, "y": int, "page_num": int}
                for symbol_info in getattr(self, 'symbols_to_place', []):
                    if symbol_info["page_num"] == page_num:
                        symbol = symbol_info["symbol"]
                        x, y = symbol_info["x"], symbol_info["y"]

                        # Define symbol properties
                        font_size = 24
                        color = (0, 1, 0) if symbol == "✔" else (1, 0, 0)  # Green for check, red for cross
                        
                        # Place symbol as text at specified (x, y) position
                        page.insert_text((x, y), symbol, fontname="helv", fontsize=font_size, color=color)

            doc.save(edited_pdf_path)
            print(f"PDF successfully saved at: {edited_pdf_path}")
        except Exception as e:
            print(f"Error while saving PDF: {e}")
            raise
        finally:
            doc.close()
        
        return edited_pdf_path
    
    def save_edited_pdf(self, admin_id, filename, edited_pdf_path):
        import gridfs
        from db import get_db  # Assuming this is how you connect to your MongoDB

        db = get_db()  # Establish database connection
        fs = gridfs.GridFS(db)

        try:
            # Read the edited PDF file
            with open(edited_pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()

            # Save the PDF in GridFS
            file_id = fs.put(pdf_data, filename=filename, metadata={"admin_id": admin_id, "status": "reviewed"})
            print(f"File saved to MongoDB with file ID: {file_id}")

            # Update the submission's status in the database
            db.submissions.update_one(
                {"filename": filename, "status": "submitted"},
                {"$set": {"status": "reviewed", "file_id": file_id}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving PDF to MongoDB: {e}")
            return False

    
    def logout(self):
        self.root.quit()  # or root.destroy() to exit

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
