import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
from authentication.auth_manager import login_user, register_user
from student_panel.student_panel import StudentPanel
from admin_panel.admin_panel import AdminPanel

class CollegeApp:

    def __init__(self, root):
        self.root = root
        self.root.title("College Exam Management System")
        self.root.geometry("1200x800")  # Set a reasonable starting size
        self.bg_image = Image.open("UI.jpg")  # Load the background image
        self.bg_label = None  # Background label reference
        self.bg_photo = None  # Background photo reference to avoid garbage collection
        self.root.bind("<Configure>", self.resize_background)  # Resize event listener

        self.role = None
        self.username = None

        self.create_login_screen()

    def set_background(self):
        """Function to set the background image based on the current window size."""
        win_width = self.root.winfo_width()  # Get the current window width
        win_height = self.root.winfo_height()  # Get the current window height

        # Resize the background image according to the window size
        resized_image = self.bg_image.resize((win_width, win_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)

        # If the background label doesn't exist, create it
        if not self.bg_label or not self.bg_label.winfo_exists():
            self.bg_label = tk.Label(self.root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            # Update the background image when resizing
            self.bg_label.config(image=self.bg_photo)
            self.bg_label.image = self.bg_photo  # Avoid garbage collection

    def resize_background(self, event):
        """Adjust the background image size when the window is resized."""
        self.set_background()


    def show_login_window(user_type):
        """Show the login window for the selected user type."""
        root = tk.Tk()
        root.geometry("800x600")

        if user_type == "student":
            app = StudentPanel(root)
        elif user_type == "admin":
            app = AdminPanel(root)
        
        root.mainloop()

    def main():
        """Entry point for the application."""
        root = tk.Tk()
        root.title("Choose User Type")
        root.geometry("400x300")

        label = tk.Label(root, text="Choose User Type", font=("Helvetica", 18))
        label.pack(pady=20)

        # Student Login Button
        student_button = tk.Button(root, text="Student Login", command=lambda: [root.destroy(), show_login_window("student")])
        student_button.pack(pady=10)

        # Admin Login Button
        admin_button = tk.Button(root, text="Admin Login", command=lambda: [root.destroy(), show_login_window("admin")])
        admin_button.pack(pady=10)

        root.mainloop()

    def create_acrylic_bg_for_label(self, x, y, width, height):
        """Create a small blurred background for a label to simulate acrylic effect."""
        # Apply a slight Gaussian blur to the background
        blurred_image = self.bg_image.filter(ImageFilter.GaussianBlur(10))
        
        # Add a slight light gray tint by reducing brightness and applying grayish tint
        enhancer = ImageEnhance.Brightness(blurred_image)
        darkened_image = enhancer.enhance(0.8)  # Lighten slightly, maintaining visibility

        # Resize the darkened, blurred background to the required size
        acrylic_bg_image = darkened_image.resize((width, height), Image.Resampling.LANCZOS)
        acrylic_photo = ImageTk.PhotoImage(acrylic_bg_image)

        # Place the image to simulate a semi-transparent, acrylic effect background
        acrylic_label = tk.Label(self.root, image=acrylic_photo, bd=0)
        acrylic_label.place(x=x, y=y, width=width, height=height)
        acrylic_label.image = acrylic_photo  # Keep reference to avoid garbage collection

    def create_login_screen(self):
        """Create the login screen UI."""
        self.clear_screen()

        # Set background image again after clearing screen
        self.set_background()

        # Title
        title_label = tk.Label(self.root, text="Login to College Management System",
                               font=("Arial", 25, "bold"), bg="#2C3333", fg="#FFD700")
        title_label.place(x=350, y=100)

        # Apply acrylic effect for Username label background only
        self.create_acrylic_bg_for_label(390, 190, 130, 40)
        username_label = tk.Label(self.root, text="Username:", font=("Arial", 18), bg="#2C3333", fg="white")
        username_label.place(x=400, y=200)

        # Username Entry
        self.username_entry = tk.Entry(self.root, font=("Arial", 14), highlightbackground="#FFD700", highlightthickness=2)
        self.username_entry.place(x=550, y=200, width=250, height=30)

        # Apply acrylic effect for Password label background only
        self.create_acrylic_bg_for_label(390, 260, 130, 40)
        password_label = tk.Label(self.root, text="Password:", font=("Arial", 18), bg="#2C3333", fg="white")
        password_label.place(x=400, y=270)

        # Password Entry
        self.password_entry = tk.Entry(self.root, show="*", font=("Arial", 14), highlightbackground="#FFD700", highlightthickness=2)
        self.password_entry.place(x=550, y=270, width=250, height=30)

        # Student Login Button
        student_login_button = tk.Button(self.root, text="Student Login", font=("Arial", 14, "bold"),
                                         bg="#FFD700", fg="#2C3333", command=self.login_student)
        student_login_button.place(x=500, y=350, width=200, height=40)

        # Admin Login Button
        admin_login_button = tk.Button(self.root, text="Admin Login", font=("Arial", 14, "bold"),
                                       bg="#FFD700", fg="#2C3333", command=self.login_admin)
        admin_login_button.place(x=500, y=410, width=200, height=40)

        # Register Button
        register_button = tk.Button(self.root, text="Register", font=("Arial", 12, "bold"),
                                    bg="#FF5733", fg="white", command=self.register)
        register_button.place(x=670, y=540, width=100, height=30)

    def login_student(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, role = login_user(username, password)
        if success and role == "student":
            # messagebox.showinfo("Success", "Logged in as Student")
            self.role = role
            self.username = username
            self.load_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Student credentials.")

    def login_admin(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, role = login_user(username, password)
        if success and role == "admin":
            # messagebox.showinfo("Success", "Logged in as Admin")
            self.role = role
            self.username = username
            self.load_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Admin credentials.")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = register_user(username, password)
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

    def load_dashboard(self):
        """Load the student or admin dashboard based on role."""
        self.clear_screen()
        if self.role == "student":
            StudentPanel(self.root, self.username)
        elif self.role == "admin":
            AdminPanel(self.root, self.username)

    def clear_screen(self):
        """Remove all widgets from the root window."""
        for widget in self.root.winfo_children():
            widget.destroy()

# Main Application
if __name__ == "__main__":
    root = tk.Tk()
    app = CollegeApp(root)
    root.mainloop()
