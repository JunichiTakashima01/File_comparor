import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import time

# Event to control detection stop
detection_event = threading.Event()
detection_thread = None

# Function to handle detection process
def run_detection():
    progress_bar.pack(pady=10)
    progress_bar.start()
    path = path_entry.get()
    text_window.insert(tk.END, f"Detection started on path: {path}\n")
    text_window.see(tk.END)
    
    # Simulate detection work
    result_window.delete(1.0, tk.END)  # Clear previous results
    for i in range(5):
        if detection_event.is_set():
            text_window.insert(tk.END, "Detection stopped by user.\n")
            text_window.see(tk.END)
            break
        time.sleep(1)  # Simulate work
        step_result = f"Result of step {i + 1}\n"
        text_window.insert(tk.END, f"Step {i + 1} completed.\n")
        result_window.insert(tk.END, step_result)
        text_window.see(tk.END)
        result_window.see(tk.END)

    progress_bar.stop()
    progress_bar.pack_forget()
    start_button.config(text="Start Detection")
    detection_event.clear()

# Function to handle button click
def toggle_detection():
    global detection_thread
    if detection_thread is None or not detection_thread.is_alive():
        detection_event.clear()
        start_button.config(text="Stop Detection")
        detection_thread = threading.Thread(target=run_detection)
        detection_thread.start()
    else:
        detection_event.set()
        start_button.config(text="Start Detection")

# Create the main window
root = tk.Tk()
root.title("Detection Interface")
root.geometry("500x600")

# Create the Start/Stop Detection button
start_button = tk.Button(root, text="Start Detection", command=toggle_detection)
start_button.pack(pady=10)

# Create a progress bar (initially hidden)
progress_bar = ttk.Progressbar(root, mode='indeterminate', length=400)

# Create a scrolled text window for logs
log_label = tk.Label(root, text="Log:")
log_label.pack()
text_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=8)
text_window.pack(pady=5)

# Create a scrolled text window for results
result_label = tk.Label(root, text="Results:")
result_label.pack()
result_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=8)
result_window.pack(pady=5)

# Create a path entry label and entry box
path_label = tk.Label(root, text="Path:")
path_label.pack(pady=(10, 0))
path_entry = tk.Entry(root, width=50)
path_entry.pack(pady=5)


# Start the Tkinter event loop
root.mainloop()
