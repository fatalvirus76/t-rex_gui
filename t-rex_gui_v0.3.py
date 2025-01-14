import os
import subprocess
import json
import threading
from tkinter import Tk, StringVar, ttk, Button, messagebox, Text, Scrollbar
from tkinter import filedialog

# Initialize the main application window
root = Tk()
root.title("T-Rex Miner GUI")

# Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Dictionary to track options
options = {}

# Variable to store the selected settings file path
settings_file = ""

# Helper function to add options to a tab
def add_option(tab, label, key, entry_type, choices=None):
    var = StringVar()
    label_widget = ttk.Label(tab, text=label)
    label_widget.pack(anchor="w", pady=5)

    if entry_type == 'text':
        entry_widget = ttk.Entry(tab, textvariable=var)
        entry_widget.pack(anchor="w", pady=5)
    elif entry_type == 'dropdown' and choices:
        var.set(choices[0])  # Set default value
        dropdown_widget = ttk.OptionMenu(tab, var, *choices)
        dropdown_widget.pack(anchor="w", pady=5)
    
    options[key] = var

# Function to read and display output from the process in real-time
def read_output(process, widget):
    try:
        for stdout_line in iter(process.stdout.readline, ""):
            widget.insert("end", stdout_line)
            widget.yview("end")
        for stderr_line in iter(process.stderr.readline, ""):
            widget.insert("end", stderr_line)
            widget.yview("end")
        process.stdout.close()
        process.stderr.close()
        process.wait()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to run the T-Rex miner
def run_trex(mode="run"):
    # Base command
    command = ["./t-rex"]

    if mode == "benchmark":
        command.append("-B")

    # Gather options
    for key, var in options.items():
        value = var.get().strip()
        if value:  # Add option only if it's not empty
            command.append(key)
            command.append(value)

    # Run the command and capture the output in real-time
    try:
        global process
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)

        # Clear the debug window before new output
        debug_text.delete(1.0, "end")

        # Start a separate thread to read the output from stdout and stderr
        output_thread = threading.Thread(target=read_output, args=(process, debug_text))
        output_thread.daemon = True
        output_thread.start()

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to stop the T-Rex process
def stop_trex():
    try:
        subprocess.run(["killall", "-9", "t-rex"])
        debug_text.insert("end", "T-Rex mining process stopped.\n")
        debug_text.yview("end")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to stop T-Rex: {e}")

# Function to save the options to a JSON file
def save_options():
    if not settings_file:
        messagebox.showwarning("Warning", "No settings file selected. Please select a file to save.")
        return

    try:
        # Create a dictionary of current options
        options_dict = {key: var.get() for key, var in options.items()}
        with open(settings_file, 'w') as f:
            json.dump(options_dict, f, indent=4)
        messagebox.showinfo("Success", f"Settings saved to {settings_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings: {e}")

# Function to load the options from a JSON file
def load_options():
    if not settings_file:
        messagebox.showwarning("Warning", "No settings file selected. Please select a file to load.")
        return

    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                options_dict = json.load(f)
            # Populate the options with the saved values
            for key, value in options_dict.items():
                if key in options:
                    options[key].set(value)
            messagebox.showinfo("Success", "Settings loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")
    else:
        messagebox.showwarning("Warning", "Settings file not found.")

# Function to select a settings file using file dialog
def select_settings_file():
    global settings_file
    settings_file = filedialog.askopenfilename(
        title="Select Settings File", 
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if settings_file:
        messagebox.showinfo("File Selected", f"Settings file selected: {settings_file}")

# Create General tab
general_tab = ttk.Frame(notebook)
notebook.add(general_tab, text="General")

# Define algorithm choices for dropdown
algorithms = [
    "autolykos2", "blake3", "etchash", "ethash", "firopow",
    "kawpow", "mtp", "mtp-tcr", "multi", "octopus",
    "progpow", "progpow-veil", "progpow-veriblock", "progpowz", "tensority"
]

# Add General options
add_option(general_tab, "Algorithm (-a, --algo)", "-a", 'dropdown', algorithms)
add_option(general_tab, "Coin (--coin)", "--coin", 'text')
add_option(general_tab, "Mining Pool URL (-o, --url)", "-o", 'text')
add_option(general_tab, "Username (-u, --user)", "-u", 'text')
add_option(general_tab, "Password (-p, --pass)", "-p", 'text')
add_option(general_tab, "Worker Name (-w, --worker)", "-w", 'text')
add_option(general_tab, "Number of Retries (-r, --retries)", "-r", 'text')
add_option(general_tab, "Retry Pause (-R, --retry-pause)", "-R", 'text')
add_option(general_tab, "Network Timeout (-T, --timeout)", "-T", 'text')
add_option(general_tab, "Time Limit (--time-limit)", "--time-limit", 'text')

# Create Debug tab
debug_tab = ttk.Frame(notebook)
notebook.add(debug_tab, text="Debug")

# Add a Text widget for displaying debug information
debug_text = Text(debug_tab, wrap="word", height=20, width=80)
debug_text.pack(pady=10)

# Create Mining Info tab
mining_info_tab = ttk.Frame(notebook)
notebook.add(mining_info_tab, text="Mining Info")

# Add a Text widget for displaying mining info (could be used for further info about mining)
mining_info_text = Text(mining_info_tab, wrap="word", height=20, width=80)
mining_info_text.pack(pady=10)

# Create API tab
api_tab = ttk.Frame(notebook)
notebook.add(api_tab, text="API")

# Add API options
add_option(api_tab, "API Bind HTTP (--api-bind-http)", "--api-bind-http", 'text')
add_option(api_tab, "Enable HTTPS (--api-https)", "--api-https", 'text')
add_option(api_tab, "API Key (--api-key)", "--api-key", 'text')
add_option(api_tab, "API Read-Only (--api-read-only)", "--api-read-only", 'text')
add_option(api_tab, "Generate API Key (--api-generate-key)", "--api-generate-key", 'text')
add_option(api_tab, "API Webserver Cert (--api-webserver-cert)", "--api-webserver-cert", 'text')
add_option(api_tab, "API Webserver Private Key (--api-webserver-pkey)", "--api-webserver-pkey", 'text')

# Create Benchmark tab
benchmark_tab = ttk.Frame(notebook)
notebook.add(benchmark_tab, text="Benchmark")

# Add Benchmark options
add_option(benchmark_tab, "Benchmark Mode (-B, --benchmark)", "-B", 'text')
add_option(benchmark_tab, "Benchmark Epoch (--benchmark-epoch)", "--benchmark-epoch", 'text')
add_option(benchmark_tab, "Benchmark Block (--benchmark-block)", "--benchmark-block", 'text')

# Create Overclock tab
overclock_tab = ttk.Frame(notebook)
notebook.add(overclock_tab, text="Overclock")

# Add Overclock options
add_option(overclock_tab, "LHR Tune (--lhr-tune)", "--lhr-tune", 'text')
add_option(overclock_tab, "LHR Auto-tune Mode (--lhr-autotune-mode)", "--lhr-autotune-mode", 'text')
add_option(overclock_tab, "LHR Auto-tune Step Size (--lhr-autotune-step-size)", "--lhr-autotune-step-size", 'text')
add_option(overclock_tab, "LHR Auto-tune Interval (--lhr-autotune-interval)", "--lhr-autotune-interval", 'text')
add_option(overclock_tab, "LHR Low Power (--lhr-low-power)", "--lhr-low-power", 'text')
add_option(overclock_tab, "Power Limit (--pl)", "--pl", 'text')
add_option(overclock_tab, "Lock Core Clock (--lock-cclock)", "--lock-cclock", 'text')
add_option(overclock_tab, "Memory Tweak (--mt)", "--mt", 'text')

# Create a frame for buttons to keep them in one row
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

# Add buttons to the frame with side="left" for horizontal arrangement
select_button = Button(button_frame, text="Select Settings File", command=select_settings_file)
select_button.pack(side="left", padx=5)

run_button = Button(button_frame, text="Run", command=lambda: run_trex(mode="run"))
run_button.pack(side="left", padx=5)

benchmark_button = Button(button_frame, text="Benchmark", command=lambda: run_trex(mode="benchmark"))
benchmark_button.pack(side="left", padx=5)

save_button = Button(button_frame, text="Save", command=save_options)
save_button.pack(side="left", padx=5)

load_button = Button(button_frame, text="Load", command=load_options)
load_button.pack(side="left", padx=5)

stop_button = Button(button_frame, text="Stop", command=stop_trex)
stop_button.pack(side="left", padx=5)

quit_button = Button(button_frame, text="Quit", command=root.quit)
quit_button.pack(side="left", padx=5)

# Run the main loop
root.mainloop()
