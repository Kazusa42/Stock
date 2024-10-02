import tkinter as tk
from tkinter import filedialog, ttk
import threading

from datetime import datetime

import stock  # Ensure stock.py and gui.py are in the same directory

class StockFetcherGUI:
    def __init__(self, root):
        """
        A class to create a graphical user interface (GUI) for fetching stock information.

        The GUI is built using the tkinter library and provides a terminal-like appearance. 
        The interface allows the user to:
    
        - Select an output directory where the fetched stock data will be saved.
        - Start the data-fetching process by clicking the "Start Fetching" button.
        - Receive success or error messages based on the execution of the stock fetching process.
    
        The "Start Fetching" button becomes temporarily disabled while the fetching 
        is in progress and is re-enabled upon completion or failure.
        Args:
            root (tk.Tk): The root Tkinter window.

        Methods:
            - choose_output_dir: Opens a dialog for the user to select the output directory.
            - start_fetching: Initiates the stock fetching process by disabling the button and starting a new thread.
            - run_fetch: Runs the stock fetching process in a separate thread to avoid blocking the GUI.
            - show_message: Displays a message box to inform the user of the outcome (success or error).
        """
        self.root = root
        self.root.title("Stock Information Fetcher")
        self.root.geometry("1000x700")

        # Configure the window style to resemble iOS
        self.root.configure(bg="black")

        # Title label
        self.title_label = tk.Label(
            root,
            text="Stock Information Fetcher",
            font=("JetBrains Mono Light", 32),
            fg="dark green",
            bg="black",
        )
        self.title_label.pack(pady=10)

        # Output directory selection
        self.output_dir = tk.StringVar()
        self.output_dir.set("Output directory is: ")

        self.output_button = tk.Button(
            root,
            text="Choose Output Directory",
            command=self.choose_output_dir,
            font=("JetBrains Mono Thin", 18),
            fg="black",
            bg="dark green",
            relief="flat",
            borderwidth=1,
        )
        self.output_button.pack(pady=5)

        self.output_label = tk.Label(
            root,
            textvariable=self.output_dir,
            font=("JetBrains Mono Thin", 14),
            fg="dark green",
            bg="black",
        )
        self.output_label.pack()

        # Start fetching button
        self.start_button = tk.Button(
            root,
            text="Start Fetching",
            command=self.start_fetching,
            font=("JetBrains Mono Thin", 18),
            fg="black",
            bg="dark green",
            relief="flat",
            borderwidth=1,
        )
        self.start_button.pack(pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            root,
            orient="horizontal",
            length=700,
            mode="determinate",
            variable=self.progress_var,
        )
        self.progress_bar.pack(pady=10)

        # Message box
        self.message_box = tk.Text(
            root,
            height=20,
            width=80,
            bd=5,
            highlightcolor="white",
            highlightbackground="white",
            insertbackground="white",
            font=("JetBrains Mono Thin", 12),
            fg="dark green",
            bg="black",
            relief="flat",
            state="disabled",
        )
        self.message_box.pack(pady=10)
        self.message_box.bind("<Configure>", self.update_widget_length)

        self.progress_callback = lambda x : self.update_progress(x)

    def update_widget_length(self, event):
        text_width = self.message_box.winfo_width()
        self.progress_bar.config(length=text_width)
    
    def choose_output_dir(self):
        """
        Opens a file dialog to choose the output directory.
        """
        directory = filedialog.askdirectory()
        if directory:
            self.show_message("System", f"Set output directory to {directory}.")
            self.output_dir.set(directory)

    def start_fetching(self):
        """
        Disables the 'Start Fetching' button, disables the output directory button, 
        enables the progress bar, and starts the fetching process in a new thread.
        """
        if self.output_dir.get() == "Output directory is: ":
            self.show_message("Warning", "Please select an output directory first.")
            return

        # Disable buttons and enable progress bar
        self.start_button.config(state=tk.DISABLED)
        self.output_button.config(state=tk.DISABLED)
        # self.progress_bar.config(state='normal')
        self.progress_var.set(0.00)

        # Start the fetching process in a separate thread to avoid blocking the GUI
        threading.Thread(target=self.run_fetch).start()

    def run_fetch(self):
        """
        Runs the fetching process and updates the progress bar.
        """
        try:
            # Set the output directory
            stock.set_output_directory(self.output_dir.get())

            # Run the data fetching process
            self.show_message("System", f"Start fetching stock data at {datetime.now().strftime('%Y-%m-%d_%H_%M')}...")
            stock.run_fetching(progress_callback=self.progress_callback)

            # Notify the user upon successful completion
            self.show_message("Success", "Stock data fetching completed successfully.")
        except Exception as e:
            # Notify the user if an error occurs
            self.show_message("Error", f"An error occurred:\n{str(e)}")
        finally:
            # Re-enable buttons and disable the progress bar
            self.start_button.config(state=tk.NORMAL)
            self.output_button.config(state=tk.NORMAL)
            # self.progress_bar.config(state='disabled')
            self.progress_var.set(0)

    def update_progress(self, value):
        """
        Updates the progress bar in the main thread.

        Args:
            value (int): The new value for the progress bar.
        """
        self.root.after(0, lambda: self.progress_var.set(value))

    def show_message(self, title, message):
        """
        Displays a message box to the user.

        Args:
            title (str): The title of the message box.
            message (str): The message to display.
        """
        self.message_box.config(state="normal")
        self.message_box.insert(tk.END, f"[INFO:] {message}\n")
        self.message_box.config(state="disabled")
        self.message_box.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = StockFetcherGUI(root)
    root.mainloop()
