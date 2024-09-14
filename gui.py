import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import stock  # Ensure stock.py and gui.py are in the same directory
import time

class StockFetcherGUI:
    def __init__(self, root):
        """
        A class to create a graphical user interface (GUI) for fetching stock information.

        The GUI is built using the tkinter library and provides an iOS-like appearance. 
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
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        # Configure the window style to resemble iOS
        self.root.configure(bg="#f0f0f0")

        # Title label
        self.title_label = tk.Label(root, text="Stock Information Fetcher", font=("Helvetica", 16), bg="#f0f0f0")
        self.title_label.pack(pady=10)

        # Output directory selection
        self.output_dir = tk.StringVar()
        self.output_dir.set("Choose output directory")

        self.output_button = tk.Button(
            root,
            text="Choose Output Directory",
            command=self.choose_output_dir,
            bg="#007AFF",
            fg="white",
            activebackground="#0051a8",
            activeforeground="white"
        )
        self.output_button.pack(pady=5)

        self.output_label = tk.Label(root, textvariable=self.output_dir, bg="#f0f0f0")
        self.output_label.pack()

        # Progress bar
        self.progress = tk.IntVar()
        self.progress_bar = tk.Scale(
            root,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=300,
            variable=self.progress,
            state='disabled',
            bg="#f0f0f0"
        )
        self.progress_bar.pack(pady=10)

        # Start fetching button
        self.start_button = tk.Button(
            root,
            text="Start Fetching",
            command=self.start_fetching,
            width=20,
            bg="#34C759",
            fg="white",
            activebackground="#28a745",
            activeforeground="white"
        )
        self.start_button.pack(pady=10)

    def choose_output_dir(self):
        """
        Opens a file dialog to choose the output directory.
        """
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def start_fetching(self):
        """
        Disables the 'Start Fetching' button, disables the output directory button, 
        enables the progress bar, and starts the fetching process in a new thread.
        """
        if self.output_dir.get() == "Choose output directory":
            messagebox.showwarning("Warning", "Please select an output directory first.")
            return

        # Disable buttons and enable progress bar
        self.start_button.config(state=tk.DISABLED)
        self.output_button.config(state=tk.DISABLED)
        self.progress_bar.config(state='normal')
        self.progress.set(0)

        # Start the fetching process in a separate thread to avoid blocking the GUI
        threading.Thread(target=self.run_fetch).start()

    def run_fetch(self):
        """
        Runs the fetching process and updates the progress bar.
        """
        try:
            # Set the output directory
            stock.set_output_directory(self.output_dir.get())

            # Simulate progress (replace with actual progress updates from stock.py)
            for i in range(101):
                time.sleep(0.05)  # Simulate work
                self.update_progress(i)

            # Run the data fetching process
            stock.run_fetching()

            # Notify the user upon successful completion
            self.show_message("Success", "Stock data fetching completed successfully.")
        except Exception as e:
            # Notify the user if an error occurs
            self.show_message("Error", f"An error occurred:\n{str(e)}")
        finally:
            # Re-enable buttons and disable the progress bar
            self.start_button.config(state=tk.NORMAL)
            self.output_button.config(state=tk.NORMAL)
            self.progress_bar.config(state='disabled')
            self.progress.set(0)

    def update_progress(self, value):
        """
        Updates the progress bar in the main thread.

        Args:
            value (int): The new value for the progress bar.
        """
        self.root.after(0, lambda: self.progress.set(value))

    def show_message(self, title, message):
        """
        Displays a message box to the user.

        Args:
            title (str): The title of the message box.
            message (str): The message to display.
        """
        self.root.after(0, lambda: messagebox.showinfo(title, message))


if __name__ == "__main__":
    root = tk.Tk()
    app = StockFetcherGUI(root)
    root.mainloop()
