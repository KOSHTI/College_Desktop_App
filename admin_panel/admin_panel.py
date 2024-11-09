import tkinter as tk
import fitz  # PyMuPDF
import os
from tkinter import messagebox, Scrollbar, Listbox, Canvas, Frame, IntVar
from PIL import Image, ImageTk
import io
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
        self.current_pdf_doc = None


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
        self.pdf_listbox = Listbox(self.root, font=("Arial", 12))
        self.pdf_listbox.place(relx=0.01, rely=0.53, anchor="w", width=250, height=600)
        
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
        self.symbol_label = tk.Label(self.root, text="Select Symbol:", bg="#ebdef0", fg="#1b2631", font=("Arial", 12, "bold"))
        self.symbol_label.place(relx=0.9, rely=0.15, anchor="ne")

        self.check_symbol_rb = tk.Radiobutton(self.root, text="✔", variable=self.symbol_var, value=1, bg="#7fb3d5")
        self.cross_symbol_rb = tk.Radiobutton(self.root, text="✘", variable=self.symbol_var, value=2, bg="#7fb3d5")
        
        self.check_symbol_rb.place(relx=0.85, rely=0.2, anchor="ne")
        self.cross_symbol_rb.place(relx=0.88, rely=0.2, anchor="ne")

        # Marking System Table Section
        self.marks_frame = tk.Frame(self.root, bg="#d6eaf8", bd=1, relief="solid")
        self.marks_frame.place(relx=0.95, rely=0.25, anchor="ne")

        # Table Headings
        heading_font = ("Arial", 10, "bold")
        tk.Label(self.marks_frame, text="Que No.", font=heading_font, bg="#aed6f1").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(self.marks_frame, text="Marks per Que.", font=heading_font, bg="#aed6f1").grid(row=0, column=1, padx=5, pady=5)
        tk.Label(self.marks_frame, text="Marks Obtained", font=heading_font, bg="#aed6f1").grid(row=0, column=2, padx=5, pady=5)

        # Updated main_questions_data to hold individual marks for each subquestion
        main_questions_data = {
            1: [2, 3, 4, 2, 1],  # Q1 has 5 subquestions with varying marks [Q1.1=2, Q1.2=3, ..., Q1.5=1]
            2: [5, 3, 2],        # Q2 has 3 subquestions with varying marks [Q2.1=5, Q2.2=3, Q2.3=2]
            3: [4, 2, 3, 1],     # Q3 has 4 subquestions with varying marks [Q3.1=4, Q3.2=2, ..., Q3.4=1]
            # Add more questions with specific marks as needed
        }

        # Adding Rows for Main Questions and Subquestions Dynamically
        self.questions = []  # List to store question data
        row_number = 1
        for question_number, subquestion_marks in main_questions_data.items():
            for subquestion_index, total_marks in enumerate(subquestion_marks, start=1):
                # Create labels for question numbers and total marks for each subquestion
                que_no_label = tk.Label(self.marks_frame, text=f"Q{question_number}.{subquestion_index}", bg="#d6eaf8", font=("Arial", 10))
                que_no_label.grid(row=row_number, column=0, padx=5, pady=5)  # Adjusting row number

                total_marks_label = tk.Label(self.marks_frame, text=str(total_marks), bg="#d6eaf8", font=("Arial", 10))
                total_marks_label.grid(row=row_number, column=1, padx=5, pady=5)

                obtained_entry = tk.Entry(self.marks_frame, width=15)
                obtained_entry.grid(row=row_number, column=2, padx=5, pady=5)

                # Bind the entry field to the update_total_marks function
                obtained_entry.bind("<KeyRelease>", self.update_total_marks)  # Recalculate total marks on key release

                # Append the question and its components to the questions list for further access
                self.questions.append({
                    "que_no": que_no_label,
                    "total_marks": total_marks_label,
                    "obtained_entry": obtained_entry,
                    "max_marks": total_marks  # Store max marks for each subquestion
                })

                row_number += 1  # Move to the next row

        # Adding Total Marks Calculation (Correctly place it in the next available row)
        self.total_marks_var = tk.StringVar()
        self.total_label = tk.Label(self.marks_frame, textvariable=self.total_marks_var, font=("Arial", 10, "bold"), bg="#aed6f1")
        self.total_label.grid(row=row_number, column=1, padx=5, pady=5)

        # Bind listbox selection
        self.pdf_listbox.bind("<<ListboxSelect>>", self.on_select)

        # Frame for PDF display with ScrollableFrame
        self.pdf_frame = Frame(self.root, width=self.A4_WIDTH, height=self.A4_HEIGHT)
        self.pdf_frame.place(relx=0.25, rely=0.2, x=20, relwidth=0.44, relheight=0.70)

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
            self.pdf_listbox.select_set(0)
            self.load_pdf()
    
    def update_total_marks(self, event=None):
        total_obtained  = 0
        total_possible = sum(question["max_marks"] for question in self.questions)  # Sum of all max marks
        for question in self.questions:
            obtained = question["obtained_entry"].get()
            if obtained.isdigit():  # Ensure only valid integers are added
                total_obtained  += int(obtained)
        self.total_marks_var.set(f"{total_obtained}/{total_possible}")

    def start_editing(self):
        # Enter editing mode and open the PDF document once for editing
        self.is_editing = True
        self.edit_button.place_forget()
        self.save_button.place(relx=0.85, rely=0.94, anchor="se", width=100, height=30)
        self.cancel_button.place(relx=0.75, rely=0.94, anchor="se", width=100, height=30)

        # Load the selected PDF to keep it open during editing
        selected_item = self.pdf_listbox.get(tk.ACTIVE)
        _, filename = selected_item.split(" - Filename: ")
        pdf_path = os.path.join(self.PDF_STORAGE_FOLDER, filename)
        self.current_pdf_doc = fitz.open(pdf_path)  # Open the PDF document once

    def cancel_editing(self):
        # Cancel editing and close the PDF document without saving
        if self.is_editing:
            self.is_editing = False
            self.save_button.place_forget()
            self.cancel_button.place_forget()
            self.edit_button.place(relx=0.85, rely=0.96, anchor="se", width=100, height=30)
            if self.current_pdf_doc:
                self.current_pdf_doc.close()  # Close without saving changes
            self.current_pdf_doc = None  # Reset the document reference
            self.load_admin_panel()  # Reload admin panel UI

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

        self.image_references = []
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
                label.bind("<Button-1>", lambda e, page_num=page_num: self.add_symbol(e, page_num))

                self.image_references.append(tk_image)

            self.pdf_canvas.configure(scrollregion=self.pdf_canvas.bbox("all"))

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while displaying PDF: {e}")

    def add_symbol(self, event, page_num):
        if not self.is_editing or not self.current_pdf_doc:
            messagebox.showwarning("Editing Disabled", "You need to be in editing mode to place symbols.")
            return

        symbol_value = self.symbol_var.get()
        symbol_img_path = "correct.png" if symbol_value == 1 else "wrong.png" if symbol_value == 2 else None
        if symbol_img_path is None:
            messagebox.showwarning("Select Symbol", "Please select a symbol to place.")
            return

        try:
            # Load and convert the symbol image to byte stream
            symbol_img = Image.open(symbol_img_path)
            img_byte_arr = io.BytesIO()
            symbol_img.save(img_byte_arr, format="PNG")
            img_byte_arr = img_byte_arr.getvalue()
            
            # Get coordinates and specify rectangle for image placement
            x, y = event.x, event.y
            page = self.current_pdf_doc[page_num]  # Access the current page from the open document
            
            img_rect = fitz.Rect(x, y, x + symbol_img.width, y + symbol_img.height)
            page.insert_image(img_rect, stream=img_byte_arr)

            # Display symbol instantly on the GUI
            tk_image = ImageTk.PhotoImage(symbol_img)
            symbol_label = tk.Label(self.pdf_display_frame, image=tk_image)
            symbol_label.image = tk_image  # Keep a reference to avoid garbage collection
            symbol_label.place(x=x, y=y)

            # Save references to prevent garbage collection of multiple images
            if not hasattr(self, 'displayed_symbols'):
                self.displayed_symbols = []
            self.displayed_symbols.append(symbol_label)

            # Track symbol placement for future reference if needed
            if not hasattr(self, 'symbols_to_place'):
                self.symbols_to_place = []
            self.symbols_to_place.append({"symbol_img_path": symbol_img_path, "x": x, "y": y, "page_num": page_num})

        except Exception as e:
            messagebox.showerror("Error", f"Failed to place symbol: {e}")

    def clear_pdf_display(self):
        for widget in self.pdf_display_frame.winfo_children():
            widget.destroy()

    def review_exam_submissions(self):
        # Save all symbols to the edited PDF and close it
        if not self.is_editing:
            messagebox.showwarning("Editing Disabled", "Enable editing to save.")
            return

        try:
            if self.current_pdf_doc:
                # Finalize and save all changes to a new file
                selected_item = self.pdf_listbox.get(tk.ACTIVE)
                _, filename = selected_item.split(" - Filename: ")
                edited_pdf_path = os.path.join(self.PDF_STORAGE_FOLDER, f"edited_{filename}")
                self.current_pdf_doc.save(edited_pdf_path)
                self.current_pdf_doc.close()  # Close the document after saving
                self.current_pdf_doc = None  # Reset the document reference
                print(f"Edited PDF saved at path: {edited_pdf_path}")

                # Optionally save to MongoDB or further processing
                save_result = self.save_edited_pdf(self.admin_id, filename, edited_pdf_path)
                if save_result:
                    messagebox.showinfo("Saved", "Your changes have been saved to the database.")
                else:
                    raise Exception("Failed to save to the database.")

            self.cancel_editing()  # Exit editing mode

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save edited PDF: {e}")

    def save_edited_pdf_with_symbols(self, pdf_path):
        edited_pdf_path = os.path.join(self.PDF_STORAGE_FOLDER, f"edited_{os.path.basename(pdf_path)}")
        doc = fitz.open(pdf_path)

        try:
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
        from db import get_db
        db = get_db()
        fs = gridfs.GridFS(db)

        try:
            with open(edited_pdf_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()

            file_id = fs.put(pdf_data, filename=filename, metadata={"admin_id": admin_id, "status": "reviewed"})
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
        self.root.quit()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
