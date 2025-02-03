import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from functions import scrape_amazon_asins

def start_scraping():
    asins = []

    # Check if manual entries exist
    asins.extend([entry.get().strip() for entry in asin_entries if entry.get().strip()])
    
    # Load ASINs from the TXT file if provided
    if txt_file_path.get():
        try:
            with open(txt_file_path.get(), mode="r", encoding="utf-8") as file:
                lines = file.readlines()
                if not lines or lines[0].strip().lower() != "asin":
                    messagebox.showerror("Error", "The TXT file must start with a header 'ASIN'.")
                    return
                asins.extend(line.strip() for line in lines[1:] if line.strip())
        except Exception as e:
            messagebox.showerror("Error", f"Could not read TXT file: {e}")
            return

    if not asins:
        messagebox.showwarning("Warning", "Please enter at least one ASIN.")
        return

    output_file = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv")],
        title="Save Output File"
    )
    if not output_file:
        return

    try:
        scrape_amazon_asins(asins, output_file)
        messagebox.showinfo("Success", f"Scraping completed. Data saved to {os.path.basename(output_file)}.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def add_asin_field():
    entry = tk.Entry(main_frame, font=("Arial", 12), relief="solid", width=40)
    entry.pack(pady=5)
    asin_entries.append(entry)

def browse_txt():
    file_path = filedialog.askopenfilename(
        filetypes=[("Text Files", "*.txt")],
        title="Select ASIN TXT File"
    )
    if file_path:
        txt_file_path.set(file_path)

# Initialize the app
app = tk.Tk()
app.title("Amazon ASIN Scraper")
app.geometry("500x600")

header = tk.Label(app, text="Amazon ASIN Scraper", font=("Arial", 18, "bold"))
header.pack(pady=10)

main_frame = tk.Frame(app)
main_frame.pack(pady=20)

# TXT file selection
txt_file_path = tk.StringVar()
txt_frame = tk.Frame(app)
txt_frame.pack(pady=10)

txt_label = tk.Label(txt_frame, text="TXT File (optional):", font=("Arial", 12))
txt_label.pack(side=tk.LEFT, padx=5)

txt_entry = tk.Entry(txt_frame, textvariable=txt_file_path, font=("Arial", 12), width=25, relief="solid")
txt_entry.pack(side=tk.LEFT, padx=5)

browse_button = tk.Button(txt_frame, text="Browse", command=browse_txt, font=("Arial", 12), bg="#FF9800", fg="white")
browse_button.pack(side=tk.LEFT, padx=5)

# Manual ASIN entry
asin_entries = []
add_asin_field()

add_button = tk.Button(app, text="+ Add ASIN", command=add_asin_field, font=("Arial", 12), bg="#4CAF50", fg="white", width=15)
add_button.pack(pady=10)

# Scrape button
scrape_button = tk.Button(app, text="Scrape Data", command=start_scraping, font=("Arial", 12), bg="#2196F3", fg="white", width=15)
scrape_button.pack(pady=10)

app.mainloop()