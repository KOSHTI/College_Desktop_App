import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from authentication.auth_manager import login_user, register_user
from student_panel.student_panel import StudentPanel
from admin_panel.admin_panel import AdminPanel

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1200x800")
        self.root.title("College Management System")

        # Load the background image
        self.bg_image = Image.open("static/UI.jpg")  # Ensure this path points to your background image
        self.bg_photo = None
        self.bg_label = None
        self.user_type = None

        self.root.bind("<Configure>", self.resize_background)  # Bind window resize event
        self.load_main_screen()

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

        # Check if the current screen has buttons before adjusting their size
        if hasattr(self, 'student_login_button') and self.student_login_button.winfo_exists():
            self.student_login_button.place_configure(relx=0.5, rely=0.4, anchor="center", width=200, height=50)
        
        if hasattr(self, 'admin_login_button') and self.admin_login_button.winfo_exists():
            self.admin_login_button.place_configure(relx=0.5, rely=0.5, anchor="center", width=200, height=50)

        if hasattr(self, 'register_button') and self.register_button.winfo_exists():
            self.register_button.place_configure(relx=0.5, rely=0.6, anchor="center", width=200, height=50)

        if hasattr(self, 'title_label') and self.title_label.winfo_exists():
            self.title_label.place_configure(relx=0.5, y=100, anchor="n")

    def load_main_screen(self):
        self.clear_screen()

        # Set the background image first
        self.set_background()

        # Title label for the main screen
        self.title_label = tk.Label(self.root, text="Welcome to College Management System", font=("Helvetica", 30, "bold"), bg="#2C3333", fg="#FFD700")
        self.title_label.place(relx=0.5, y=100, anchor="n")  # Centered at the top middle

        # Student Login button
        self.student_login_button = tk.Button(self.root, text="Student Login", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=self.load_student_login)
        self.student_login_button.place(relx=0.5, rely=0.4, anchor="center", width=200, height=50)

        # Admin Login button
        self.admin_login_button = tk.Button(self.root, text="Admin Login", font=("Arial", 14, "bold"), bg="#FF6347", fg="white", command=self.load_admin_login)
        self.admin_login_button.place(relx=0.5, rely=0.5, anchor="center", width=200, height=50)


    def load_student_login(self):
        """Load the Student Login panel."""
        self.clear_screen()
        self.set_background()

        # Title label
        self.title_label = tk.Label(self.root, text="Student Login", font=("Helvetica", 24, "bold"), bg="#2C3333", fg="#FFD700")
        self.title_label.place(relx=0.5, y=50, anchor="n")  # Centered at the top middle

        # Username and Password Labels and Entries
        self.create_login_form("student")

    def load_admin_login(self):
        """Load the Admin Login panel."""
        self.clear_screen()
        self.set_background()

        # Title label
        self.title_label = tk.Label(self.root, text="Admin Login", font=("Helvetica", 24, "bold"), bg="#2C3333", fg="#FFD700")
        self.title_label.place(relx=0.5, y=50, anchor="n")  # Centered at the top middle

        # Username and Password Labels and Entries
        self.create_login_form("admin")

    def load_registration(self):
        """Load the Registration panel."""
        self.clear_screen()
        self.set_background()

        # Title label
        self.title_label = tk.Label(self.root, text="User Registration", font=("Helvetica", 24, "bold"), bg="#2C3333", fg="#FFD700")
        self.title_label.place(relx=0.5, y=50, anchor="n")  # Centered at the top middle

        # Registration form fields
        self.create_registration_form()

    def create_login_form(self, user_type):
        """Create common login form for both student and admin."""
        # Username label and entry
        self.username_label = tk.Label(self.root, text="Username: ", font=("Arial", 14), bg="#2C3333", fg="white")
        self.username_label.place(relx=0.4, rely=0.3, anchor="e")

        self.username_entry = tk.Entry(self.root, font=("Arial", 14))
        self.username_entry.place(relx=0.4, rely=0.3, anchor="w", width=200)

        # Password label and entry
        self.password_label = tk.Label(self.root, text="Password: ", font=("Arial", 14), bg="#2C3333", fg="white")
        self.password_label.place(relx=0.4, rely=0.4, anchor="e")

        self.password_entry = tk.Entry(self.root, show="*", font=("Arial", 14))
        self.password_entry.place(relx=0.4, rely=0.4, anchor="w", width=200)

        # Login button
        self.login_button = tk.Button(self.root, text="Login", font=("Arial", 14), bg="#4CAF50" if user_type == "student" else "#FF6347", fg="white", command=lambda: self.authenticate(user_type))
        self.login_button.place(relx=0.5, rely=0.5, anchor="center", width=150, height=40)

        # Create the sign-up label
        Signup_label = tk.Label(root, text="Don't have an account?", fg="black", cursor="hand2", font=("Arial", 10))
        Signup_label.place(relx=0.5, rely=0.6, anchor="e")

        Signup_button = tk.Button(self.root, text="Sign up", font=("Arial", 10), fg="blue", command=self.load_registration)
        Signup_button.place(relx=0.5, rely=0.6, anchor="w")

    def create_registration_form(self):
        """Create registration form fields."""
        # Username
        self.username_label = tk.Label(self.root, text="Username: ", font=("Arial", 14), bg="#2C3333", fg="white")
        self.username_label.place(relx=0.4, rely=0.3, anchor="e")

        self.username_entry = tk.Entry(self.root, font=("Arial", 14))
        self.username_entry.place(relx=0.4, rely=0.3, anchor="w", width=200)

        # Password
        self.password_label = tk.Label(self.root, text="Password: ", font=("Arial", 14), bg="#2C3333", fg="white")
        self.password_label.place(relx=0.4, rely=0.4, anchor="e")

        self.password_entry = tk.Entry(self.root, show="*", font=("Arial", 14))
        self.password_entry.place(relx=0.4, rely=0.4, anchor="w", width=200)

        # User type selection (Radio buttons)
        self.user_type_var = tk.StringVar(value=self.user_type)

        student_radio = tk.Radiobutton(self.root, text="Student", variable=self.user_type_var, value="student", font=("Arial", 12), bg="#2C3333", fg="white")
        student_radio.place(relx=0.4, rely=0.5, anchor="w")

        admin_radio = tk.Radiobutton(self.root, text="Admin", variable=self.user_type_var, value="admin", font=("Arial", 12), bg="#2C3333", fg="white")
        admin_radio.place(relx=0.6, rely=0.5, anchor="w")

        # Register button
        self.register_button = tk.Button(self.root, text="Register", font=("Arial", 14), bg="#1E90FF", fg="white", command=self.register_user)
        self.register_button.place(relx=0.5, rely=0.5, anchor="center", width=150, height=40)

    def authenticate(self, user_type):
        """Authenticate the student or admin user and load the respective panel."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        success, role = login_user(username, password)

        if success:
            self.clear_screen()
            if role == "student" and user_type == "student":
                student_panel = StudentPanel(self.root, student_id=username)
                print(f"Student Panel loaded for {username}")
                # print(student_panel)
            elif role == "admin" and user_type == "admin":
                admin_panel = AdminPanel(self.root, admin_id=username)
                print(f"Admin Panel loaded for {username}")
                # print(admin_panel)
            else:
                messagebox.showerror("Login Failed", f"Invalid role for {user_type} login.")
                self.load_main_screen()
        else:
            messagebox.showerror("Login Failed", f"Invalid {user_type} credentials.")

    def register_user(self):
        """Register the user and show success or error message."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_type =  "student", "admin"

        user_type = self.user_type_var.get()
        success = register_user(username, password, user_type)

        if success:
            messagebox.showinfo("Registration Successful", f"{user_type.capitalize()} has been registered successfully!")
            self.load_main_screen()
        else:
            messagebox.showerror("Registration Failed", f"Failed to register {user_type}. Try again.")

    def clear_screen(self):
        """Remove all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()