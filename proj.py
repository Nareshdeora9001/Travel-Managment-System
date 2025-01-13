import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

# Database setup
def setup_database():
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    # Create itineraries table
    c.execute('''
        CREATE TABLE IF NOT EXISTS itineraries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            destination TEXT NOT NULL,
            country TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            budget_per_person REAL NOT NULL,
            number_of_travelers INTEGER NOT NULL,
            rating INTEGER DEFAULT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

# User registration
def register_user():
    username = simpledialog.askstring("Register", "Enter username:")
    password = simpledialog.askstring("Register", "Enter password:", show='*')
    
    if username and password:
        conn = sqlite3.connect('travel.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Registration", "User registered successfully!")
        except sqlite3.IntegrityError:
            messagebox.showwarning("Registration", "Username already exists!")
        conn.close()

# Add a new itinerary
def add_itinerary():
    global user_id  # Make user_id global to access it in this function
    if user_id is None:
        messagebox.showwarning("Login", "You must log in first.")
        return
    
    destination = simpledialog.askstring("New Itinerary", "Enter the destination:")
    country = simpledialog.askstring("Destination country", "Enter the Country Name:")
    travel_date = simpledialog.askstring("Travel Date", "Enter the travel date (YYYY-MM-DD):")
    return_date = simpledialog.askstring("Return Date", "Enter the return date (YYYY-MM-DD):")
    budget_per_person = simpledialog.askfloat("Budget per person", "Enter the budget per person:")
    number_of_travelers = simpledialog.askinteger("Number of Travelers", "Enter the number of travelers:", minvalue=1)

    if all([destination, country, travel_date, return_date, budget_per_person is not None, number_of_travelers is not None]):
        conn = sqlite3.connect('travel.db')
        c = conn.cursor()
        c.execute("INSERT INTO itineraries (user_id, destination, country, travel_date, return_date, budget_per_person, number_of_travelers) VALUES (?, ?, ?, ?, ?, ?, ?) ",
                  (user_id, destination, country, travel_date, return_date, budget_per_person, number_of_travelers))
        conn.commit()
        load_itineraries(user_id)
        conn.close()
    else:
        messagebox.showwarning("Input Error", "Please fill in all fields.")

# Load itineraries from the database
def load_itineraries(user_id):
    listbox.delete(0, tk.END)
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    c.execute("SELECT * FROM itineraries WHERE user_id = ?", (user_id,))
    itineraries = c.fetchall()
    for itinerary in itineraries:
        rating = itinerary[8] if itinerary[8] is not None else "No rating"
        total_cost = itinerary[6] * itinerary[7]  # budget_per_person * number_of_travelers
        listbox.insert(tk.END, f"{itinerary[0]}: {itinerary[2]} | Country: {itinerary[3]} | Travel Date: {itinerary[4]} | Return Date: {itinerary[5]} | Budget: {itinerary[6]} | Travelers: {itinerary[7]} | Total Cost: {total_cost:.2f} | Rating: {rating}")
    conn.close()

# Delete selected itinerary
def delete_itinerary():
    selected_itinerary_index = listbox.curselection()
    if selected_itinerary_index:
        itinerary_info = listbox.get(selected_itinerary_index)
        itinerary_id = itinerary_info.split(':')[0]  # Extract ID for deletion
        conn = sqlite3.connect('travel.db')
        c = conn.cursor()
        c.execute("DELETE FROM itineraries WHERE id = ?", (itinerary_id,))
        conn.commit()
        conn.close()
        load_itineraries(user_id)  # Keep track of current user_id
    else:
        messagebox.showwarning("Delete Itinerary", "Please select an itinerary to delete.")

# Update rating for selected itinerary
def update_rating():
    selected_itinerary_index = listbox.curselection()
    if selected_itinerary_index:
        itinerary_info = listbox.get(selected_itinerary_index)
        itinerary_id = itinerary_info.split(':')[0]  # Extract ID for updating
        rating = simpledialog.askinteger("Rate Your Journey", "Enter your rating (1-5):", minvalue=1, maxvalue=5)
        
        if rating is not None:
            conn = sqlite3.connect('travel.db')
            c = conn.cursor()
            c.execute("UPDATE itineraries SET rating = ? WHERE id = ?", (rating, itinerary_id))
            conn.commit()
            conn.close()
            load_itineraries(user_id)  # Keep track of current user_id
    else:
        messagebox.showwarning("Update Rating", "Please select an itinerary to rate.")

# User login
def login_user():
    global user_id  # Make user_id global to access it across functions
    username = simpledialog.askstring("User Login", "Enter your username:")
    password = simpledialog.askstring("User Login", "Enter your password:", show='*')
    
    conn = sqlite3.connect('travel.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()

    if user:
        user_id = user[0]
        load_itineraries(user_id)
        messagebox.showinfo("Login", "Logged in successfully!")
    else:
        messagebox.showwarning("Login", "Invalid username or password.")
    
    conn.close()

# Create the main application window
root = tk.Tk()
root.title("Travel Management System")

# Create GUI components
frame = tk.Frame(root)
frame.pack(pady=10)

listbox = tk.Listbox(frame, width=200, height=10)
listbox.pack()

register_button = tk.Button(frame, text="Register User", command=register_user)
register_button.pack(side=tk.LEFT, padx=10)

login_button = tk.Button(frame, text="Login User", command=login_user)
login_button.pack(side=tk.LEFT)

itinerary_button = tk.Button(frame, text="Add Itinerary", command=add_itinerary)
itinerary_button.pack(side=tk.LEFT)

delete_button = tk.Button(frame, text="Delete Itinerary", command=delete_itinerary)
delete_button.pack(side=tk.LEFT)

rate_button = tk.Button(frame, text="Rate Itinerary", command=update_rating)
rate_button.pack(side=tk.LEFT, padx=10)

# Global variable to store user_id
user_id = None

# Initialize database
setup_database()

# Run the application
root.mainloop()