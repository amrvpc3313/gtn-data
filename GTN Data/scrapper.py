import tkinter as tk
from tkinter import filedialog, messagebox
import os


from functions import scrape_amazon  

def browse_destination():
    """Open a file dialog for the user to select a folder."""
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_path.set(folder_selected)

def start_scraping():
    """Start scraping based on user inputs."""
    try:
        pages = int(pages_entry.get())
        if pages <= 0:
            raise ValueError("Number of pages must be greater than 0.")
    except ValueError as e:
        messagebox.showerror("Input Error", "Please enter a valid number of pages.")
        return

    product = product_entry.get().strip()
    if not product:
        messagebox.showerror("Input Error", "Please enter a product to search for.")
        return

    file_name = file_name_entry.get().strip()
    if not file_name:
        messagebox.showerror("Input Error", "Please enter a valid file name.")
        return

    folder = output_path.get().strip()
    if not folder:
        messagebox.showerror("Input Error", "Please select a destination folder.")
        return

    output_file = os.path.join(folder, file_name)
    search_url = f"https://www.amazon.com/s?k={'+'.join(product.split())}"

    
    try:
        scrape_amazon(search_url, max_pages=pages, output_file=output_file)
        messagebox.showinfo("Success", f"Scraping complete! Data saved to {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


root = tk.Tk()
root.title("Amazon Scraper")


output_path = tk.StringVar()


tk.Label(root, text="Amazon Scraper", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)

tk.Label(root, text="Product to search for:").grid(row=1, column=0, sticky="e", padx=10, pady=5)
product_entry = tk.Entry(root, width=40)
product_entry.grid(row=1, column=1, columnspan=2, pady=5)

tk.Label(root, text="Number of pages to scrape:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
pages_entry = tk.Entry(root, width=10)
pages_entry.grid(row=2, column=1, sticky="w", pady=5)

tk.Label(root, text="Output file name (with .csv):").grid(row=3, column=0, sticky="e", padx=10, pady=5)
file_name_entry = tk.Entry(root, width=40)
file_name_entry.grid(row=3, column=1, columnspan=2, pady=5)

tk.Label(root, text="Save to folder:").grid(row=4, column=0, sticky="e", padx=10, pady=5)
tk.Entry(root, textvariable=output_path, width=40).grid(row=4, column=1, pady=5)
tk.Button(root, text="Browse", command=browse_destination).grid(row=4, column=2, pady=5)

tk.Button(root, text="Start Scraping", command=start_scraping, bg="green", fg="white").grid(row=5, column=0, columnspan=3, pady=20)


root.mainloop()