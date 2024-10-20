import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from authentication.auth_manager import login_user
from admin_panel.admin_panel import AdminPanel
from student_panel.student_panel import StudentPanel

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1200x800")
        self.root.title("College Management System")

        # Load the background image
        self.bg_image = Image.open("static/UI.jpg")  # Ensure this path points to your background image
        self.bg_photo = None
        self.bg_label = None

        self.root.bind("<Configure>", self.resize_background)  # Bind window resize event
        self.load_login_screen()

    def set_background(self):
        """Set the background image based on window size."""
        win_width = self.root.winfo_width()
        win_height = self.root.winfo_height()

        # Resize the background image to match window size
        resized_image = self.bg_image.resize((win_width, win_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)

        # If the background label doesn't exist, create it
        if not self.bg_label or not self.bg_label.winfo_exists():
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            # Update the background image on resize
            self.bg_label.config(image=self.bg_photo)
            self.bg_label.image = self.bg_photo  # Keep reference to avoid garbage collection

    def resize_background(self, event):
        """Adjust the background image size and reposition elements dynamically when the window is resized."""
        self.set_background()

        # Adjust title label position dynamically
        self.title_label.place_configure(relx=0.5, y=50, anchor="n")

        # Adjust username label and entry
        self.username_label.place_configure(relx=0.4, rely=0.3, anchor="e")
        self.username_entry.place_configure(relx=0.4, rely=0.3, anchor="w", width=200)

        # Adjust password label and entry
        self.password_label.place_configure(relx=0.4, rely=0.4, anchor="e")
        self.password_entry.place_configure(relx=0.4, rely=0.4, anchor="w", width=200)

        # Adjust login button
        self.student_login_button.place_configure(relx=0.5, rely=0.5, anchor="center", width=100, height=40)

    def load_login_screen(self):
        self.clear_screen()

        # Set the background image first
        self.set_background()

        # Title label for the login screen (placed dynamically in the upper middle)
        self.title_label = tk.Label(self.root, text="Welcome to College Management System", font=("Helvetica", 24, "bold"), bg="#2C3333", fg="#FFD700")
        self.title_label.place(relx=0.5, y=50, anchor="n")  # Centered at the top middle

        # Username label and entry (placed dynamically)
        self.username_label = tk.Label(self.root, text="Username : ", font=("Arial", 14), bg="#2C3333", fg="white")
        self.username_label.place(relx=0.4, rely=0.3, anchor="e")  # Adjust relx/rely for centering

        self.username_entry = tk.Entry(self.root, font=("Arial", 14))
        self.username_entry.place(relx=0.4, rely=0.3, anchor="w", width=200)  # Entry box next to the label

        # Password label and entry (similar logic)
        self.password_label = tk.Label(self.root, text="Password : ", font=("Arial", 14), bg="#2C3333", fg="white")
        self.password_label.place(relx=0.4, rely=0.4, anchor="e")

        self.password_entry = tk.Entry(self.root, show="*", font=("Arial", 14))
        self.password_entry.place(relx=0.4, rely=0.4, anchor="w", width=200)

        # Student Login button
        self.student_login_button = tk.Button(self.root, text="Student Login", font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", command=self.authenticate_user)
        self.student_login_button.place(relx=0.5, rely=0.55, anchor="center", width=200, height=50)

    def authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        success, role = login_user(username, password)

        if success:
            if role == "admin":
                self.load_admin_panel()
            elif role == "student":
                self.load_student_panel()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")

    def load_admin_panel(self):
        self.clear_screen()
        admin_panel = AdminPanel(self.root, admin_id="admin123")

    def load_student_panel(self):
        self.clear_screen()
        student_panel = StudentPanel(self.root, student_id="student123")

    def clear_screen(self):
        """Remove all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()
