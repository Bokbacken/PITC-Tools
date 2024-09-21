import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import os
import time

# Function to get list of network interfaces
def get_network_interfaces():
    interfaces = sorted(os.listdir('/sys/class/net/'))  # Sort interfaces alphabetically
    return interfaces

# Function to update command preview
def update_command_preview(*args):
    selected_interfaces = [interface for interface, var in interface_vars.items() if var.get()]
    command_parts = []

    if not selected_interfaces:
        command_preview.set("Please select at least one interface.")
        return

    for iface in selected_interfaces:
        iface_command = f"sudo tc qdisc add dev {iface} root netem"

        if 'delay_var' in globals() and delay_var.get():
            delay_time = delay_time_entry.get()
            variation = variation_entry.get()
            correlation = correlation_entry.get()
            delay_command = f"delay {delay_time}ms" if delay_time else ""
            if variation:
                delay_command += f" {variation}ms"
            if correlation:
                delay_command += f" {correlation}%"
            iface_command += " " + delay_command.strip()

        if 'loss_var' in globals() and loss_var.get():
            loss_pct = loss_pct_entry.get()
            correlation = loss_corr_entry.get()
            loss_command = f"loss {loss_pct}%" if loss_pct else ""
            if correlation:
                loss_command += f" {correlation}%"
            iface_command += " " + loss_command.strip()

        if 'duplicate_var' in globals() and duplicate_var.get():
            duplicate_pct = duplicate_pct_entry.get()
            if duplicate_pct:
                iface_command += f" duplicate {duplicate_pct}%"

        if 'corrupt_var' in globals() and corrupt_var.get():
            corrupt_pct = corrupt_pct_entry.get()
            if corrupt_pct:
                iface_command += f" corrupt {corrupt_pct}%"

        if 'reorder_var' in globals() and reorder_var.get():
            reorder_pct = reorder_pct_entry.get()
            reorder_corr = reorder_corr_entry.get()
            reorder_command = f"reorder {reorder_pct}%" if reorder_pct else ""
            if reorder_corr:
                reorder_command += f" {reorder_corr}%"
            iface_command += " " + reorder_command.strip()

        if 'rate_limit_var' in globals() and rate_limit_var.get():
            rate = rate_entry.get()
            burst = burst_entry.get()
            latency = latency_entry.get()
            rate_command = f"rate {rate}mbit" if rate else ""
            if burst:
                rate_command += f" burst {burst}kbit"
            if latency:
                rate_command += f" latency {latency}ms"
            iface_command += " " + rate_command.strip()

        if 'gap_var' in globals() and gap_var.get():
            gap_size = gap_size_entry.get()
            if gap_size:
                iface_command += f" gap {gap_size}"

        if 'latency_dist_var' in globals() and latency_dist_var.get():
            mean_delay = mean_delay_entry.get()
            std_dev = std_dev_entry.get()
            dist_file = dist_file_entry.get()
            latency_dist_command = f"delay {mean_delay}ms {std_dev}ms" if mean_delay else ""
            if dist_file:
                latency_dist_command += f" distribution {dist_file}"
            iface_command += " " + latency_dist_command.strip()

        if 'queue_discipline_var' in globals() and queue_discipline_var.get():
            discipline = discipline_entry.get()
            if discipline:
                iface_command += f" qdisc {discipline}"

        command_parts.append(iface_command.strip())

    final_command = '\n'.join(command_parts)
    command_preview.set(final_command)

# Function to execute the command
def execute_command():
    cmd = command_preview.get()
    if "Please select at least one interface." in cmd:
        messagebox.showwarning("Warning", "You must select at least one interface.")
        return

    command_output.insert(tk.END, f"Executing commands:\n{cmd}\n")
    command_output.yview_moveto(1.0)  # Scroll to the bottom

    try:
        for line in cmd.splitlines():
            result = subprocess.run(line, shell=True, check=True, capture_output=True, text=True)
            command_output.insert(tk.END, f"Output: {result.stdout}\n")
            if result.stderr:
                command_output.insert(tk.END, f"Error: {result.stderr}\n")
            command_output.yview_moveto(1.0)  # Scroll to the bottom
        status_label.config(text="Command executed.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to execute command: {e}")
        command_output.insert(tk.END, f"Failed to execute command: {e.stderr}\n")
        command_output.yview_moveto(1.0)  # Scroll to the bottom
        status_label.config(text="Execution failed.")

# Function to execute the command with a timer
def execute_command_with_timer():
    cmd = command_preview.get()
    if "Please select at least one interface." in cmd:
        messagebox.showwarning("Warning", "You must select at least one interface.")
        return

    command_output.insert(tk.END, f"Executing commands with timer:\n{cmd}\n")
    command_output.yview_moveto(1.0)  # Scroll to the bottom

    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        status_label.config(text="Command running...")
        countdown_time = int(timer_entry.get()) * 1000
        root.after(countdown_time, lambda: process.terminate())
        update_timer(countdown_time // 1000)  # Start countdown

        stdout, stderr = process.communicate()
        command_output.insert(tk.END, f"Output: {stdout}\n")
        if stderr:
            command_output.insert(tk.END, f"Error: {stderr}\n")
        command_output.yview_moveto(1.0)  # Scroll to the bottom

    except Exception as e:
        messagebox.showerror("Error", f"Failed to execute command: {e}")
        command_output.insert(tk.END, f"Error: {e}\n")
        command_output.yview_moveto(1.0)  # Scroll to the bottom
        status_label.config(text="Execution failed.")

# Function to update the timer countdown
def update_timer(time_left):
    if time_left > 0:
        timer_status_label.config(text=f"Time left: {time_left} seconds")
        root.after(1000, update_timer, time_left - 1)
    else:
        timer_status_label.config(text="Time's up!")
        abort_command()

# Function to copy command to clipboard
def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(command_preview.get())
    messagebox.showinfo("Info", "Command copied to clipboard.")
def abort_command():
    command_output.insert(tk.END, "Aborting commands...\n")

    for interface, var in interface_vars.items():
        if var.get():
            try:
                # Step 1: Gradually reduce delay and loss (if they were set)
                # This assumes netem parameters are configured before, so we clear them step by step

                # If delay was set, clear it
                clear_delay_command = f"sudo tc qdisc change dev {interface} root netem delay 0ms"
                subprocess.run(clear_delay_command, shell=True, check=True, capture_output=True, text=True)

                # If loss was set, clear it
                clear_loss_command = f"sudo tc qdisc change dev {interface} root netem loss 0%"
                subprocess.run(clear_loss_command, shell=True, check=True, capture_output=True, text=True)

                # Introduce a delay to allow changes to take effect
                time.sleep(0.5)

                # Step 2: Replace the netem qdisc with a benign qdisc like pfifo_fast
                replace_command = f"sudo tc qdisc replace dev {interface} root pfifo_fast"
                subprocess.run(replace_command, shell=True, check=True, capture_output=True, text=True)
                command_output.insert(tk.END, f"Replaced netem with pfifo_fast on {interface}.\n")

                # Introduce a delay to allow packets to be processed under the new qdisc
                time.sleep(0.5)

                # Step 3: Now safely delete the netem qdisc
                delete_command = f"sudo tc qdisc del dev {interface} root netem"
                result = subprocess.run(delete_command, shell=True, check=True, capture_output=True, text=True)
                command_output.insert(tk.END, f"Aborted netem on {interface}.\n")

                if result.stderr:
                    command_output.insert(tk.END, f"Error deleting netem qdisc on {interface}: {result.stderr}\n")

            except subprocess.CalledProcessError:
                command_output.insert(tk.END, f"Failed to abort on {interface}.\n")
                continue  # Ignore errors if netem isn't set

    messagebox.showinfo("Info", "All tc netem configurations have been replaced and removed.")
    status_label.config(text="Aborted.")
    timer_status_label.config(text="")



# Function to add tooltip with delay
def create_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, wraplength=200)
    label.pack()

    def show_tooltip(event):
        if widget.tooltip_id:  # If the tooltip is scheduled, show it
            tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")  # Show tooltip near the mouse pointer
            tooltip.deiconify()
            widget.tooltip_id = None  # Reset the scheduled tooltip

    def hide_tooltip(event):
        tooltip.withdraw()
        widget.tooltip_id = None  # Clear the tooltip schedule

    def schedule_tooltip(event):
        widget.tooltip_id = widget.after(500, lambda: show_tooltip(event))  # Delay of 500ms before showing tooltip

    widget.bind("<Enter>", schedule_tooltip)
    widget.bind("<Leave>", hide_tooltip)
    widget.tooltip_id = None

# Initialize the main window
root = tk.Tk()
root.title("Network Manipulation Tool")

# Interface Selection
interface_frame = tk.LabelFrame(root, text="Select Interfaces to Apply Netem")
interface_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

interface_vars = {}
interfaces = get_network_interfaces()
for idx, iface in enumerate(interfaces):
    var = tk.BooleanVar()
    cb = tk.Checkbutton(interface_frame, text=iface, variable=var, command=update_command_preview)
    cb.grid(row=idx//8, column=idx%8, sticky="w", padx=5)
    interface_vars[iface] = var

# Function Sections
sections = [
    ("Delay", "Adds a fixed delay to all packets, with optional variation and correlation.",
     ["Time (ms):", "Variation (ms):", "Correlation (%):"], [100, "", ""]),
    ("Loss", "Drops a percentage of packets, with optional correlation between drops.",
     ["Loss %:", "Correlation (%):"], [2, ""]),
    ("Duplicate", "Duplicates a percentage of packets.", ["Duplicate %:"], [1]),
    ("Corrupt", "Corrupts a percentage of packets by introducing bit errors.", ["Corrupt %:"], [0.1]),
    ("Reorder", "Reorders a percentage of packets, with optional correlation between reorders.",
     ["Reorder %:", "Correlation (%):"], [25, ""]),
    ("Rate Limit", "Limits the rate of outgoing traffic, allowing bursts up to a specified size and latency.",
     ["Rate (mbit):", "Burst Size (kbit):", "Latency (ms):"], [1, "", ""]),
    #("Gap", "Introduces gaps by sending a burst of packets followed by a pause.", ["Size (packets):"], [10]),
    #("Latency Distribution", "Applies a delay with a specified mean and standard deviation. Optionally uses a custom distribution file.",
    # ["Mean Delay (ms):", "Std Dev (ms):", "Dist. File Path:"], [100, "", ""]),
    #("Queuing Discipline", "Applies a queuing discipline to manage packet queues and control traffic behavior.",
    # ["Discipline:"], ["fq_codel"])
]

row_idx = 1
for section in sections:
    var = tk.BooleanVar()
    frame = tk.LabelFrame(root)  # Frame without text label
    frame.grid(row=row_idx, column=0, padx=5, pady=5, sticky="nsew")
    row_idx += 1

    # Add the tickbox and label in the same row
    cb = tk.Checkbutton(frame, text=f"{section[0]}", variable=var, command=update_command_preview)
    cb.grid(row=0, column=0, sticky="w")
    create_tooltip(cb, section[1])  # Tooltip only on checkbox

    section_vars = []
    column_index = 1  # Start placing parameters from the next column
    for i, param in enumerate(section[2]):
        tk.Label(frame, text=param).grid(row=0, column=column_index, padx=5, pady=5, sticky="w")
        entry = tk.Entry(frame, width=10)
        entry.insert(0, section[3][i])
        entry.grid(row=0, column=column_index + 1, padx=5, pady=5, sticky="w")
        entry.bind("<KeyRelease>", update_command_preview)  # Bind key release to update command preview dynamically
        column_index += 2  # Move to the next set of parameter-entry

        # Provide specific tooltips for each parameter
        if section[0] == "Delay" and "Time" in param:
            create_tooltip(entry, "Inserts constant delay of specified time.")
        elif section[0] == "Delay" and "Variation" in param:
            create_tooltip(entry, "Adds jitter to the delay by varying the constant time +/- the specified time.")
        elif section[0] == "Delay" and "Correlation" in param:
            create_tooltip(entry, "Specifies the correlation between the delay and its variation.")
        elif section[0] == "Loss" and "Loss" in param:
            create_tooltip(entry, "Percentage of packets to drop randomly.")
        elif section[0] == "Loss" and "Correlation" in param:
            create_tooltip(entry, "Correlation in the random packet loss process.")
        elif section[0] == "Duplicate":
            create_tooltip(entry, "Percentage of packets to duplicate.")
        elif section[0] == "Corrupt":
            create_tooltip(entry, "Percentage of packets to corrupt by flipping random bits.")
        elif section[0] == "Reorder" and "Reorder" in param:
            create_tooltip(entry, "Percentage of packets to reorder.")
        elif section[0] == "Reorder" and "Correlation" in param:
            create_tooltip(entry, "Correlation in the reordering of packets.")
        elif section[0] == "Rate Limit" and "Rate" in param:
            create_tooltip(entry, "Maximum transmission rate in megabits per second.")
        elif section[0] == "Rate Limit" and "Burst" in param:
            create_tooltip(entry, "Maximum burst size allowed during transmission, in kilobits.")
        elif section[0] == "Rate Limit" and "Latency" in param:
            create_tooltip(entry, "Latency introduced by traffic shaping, in milliseconds.")
        elif section[0] == "Gap":
            create_tooltip(entry, "Number of packets in each burst before a gap is introduced.")
        elif section[0] == "Latency Distribution" and "Mean Delay" in param:
            create_tooltip(entry, "Average delay time in milliseconds.")
        elif section[0] == "Latency Distribution" and "Std Dev" in param:
            create_tooltip(entry, "Standard deviation of delay time in milliseconds.")
        elif section[0] == "Latency Distribution" and "Dist. File" in param:
            create_tooltip(entry, "Path to custom distribution file to use for latency simulation.")
        elif section[0] == "Queuing Discipline":
            create_tooltip(entry, "The queuing discipline to apply (e.g., 'fq_codel').")

        section_vars.append(entry)

    if section[0] == "Delay":
        delay_var, delay_time_entry, variation_entry, correlation_entry = var, *section_vars
    elif section[0] == "Loss":
        loss_var, loss_pct_entry, loss_corr_entry = var, *section_vars
    elif section[0] == "Duplicate":
        duplicate_var, duplicate_pct_entry = var, *section_vars
    elif section[0] == "Corrupt":
        corrupt_var, corrupt_pct_entry = var, *section_vars
    elif section[0] == "Reorder":
        reorder_var, reorder_pct_entry, reorder_corr_entry = var, *section_vars
    elif section[0] == "Rate Limit":
        rate_limit_var, rate_entry, burst_entry, latency_entry = var, *section_vars
    elif section[0] == "Gap":
        gap_var, gap_size_entry = var, *section_vars
    elif section[0] == "Latency Distribution":
        latency_dist_var, mean_delay_entry, std_dev_entry, dist_file_entry = var, *section_vars
        tk.Label(frame, text="Dist. File Path:").grid(row=1, column=0, padx=5, pady=5, sticky="w")  # Label on new row
        dist_file_entry.grid(row=1, column=1, columnspan=5, padx=5, pady=5, sticky="ew")  # Entry on new row
    elif section[0] == "Queuing Discipline":
        queue_discipline_var, discipline_entry = var, *section_vars

# Command and Execution Controls
command_frame = tk.LabelFrame(root, text="Command Execution")
command_frame.grid(row=row_idx, column=0, padx=5, pady=5, sticky="nsew")
command_preview = tk.StringVar(value="Command will appear here...")
tk.Entry(command_frame, textvariable=command_preview, width=80).grid(row=0, column=0, columnspan=4, padx=5, pady=5)
tk.Label(command_frame, text="Timer (seconds):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
timer_entry = tk.Entry(command_frame, width=5)
timer_entry.insert(0, "10")  # Default value of 10 for the timer
timer_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
tk.Button(command_frame, text="Execute", command=execute_command).grid(row=2, column=0, padx=5, pady=5)
tk.Button(command_frame, text="Execute with Timer", command=execute_command_with_timer).grid(row=2, column=1, padx=5, pady=5)
tk.Button(command_frame, text="Abort", command=abort_command).grid(row=2, column=2, padx=5, pady=5)
tk.Button(command_frame, text="Copy to Clipboard", command=copy_to_clipboard).grid(row=2, column=3, padx=5, pady=5)
status_label = tk.Label(command_frame, text="", fg="green")
status_label.grid(row=3, column=0, columnspan=2, sticky="w")
timer_status_label = tk.Label(command_frame, text="", fg="red")
timer_status_label.grid(row=3, column=2, columnspan=2, sticky="w")

# Command output textbox
command_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10)
command_output.grid(row=row_idx + 1, column=0, padx=5, pady=5, sticky="nsew")

root.columnconfigure(0, weight=1)
command_frame.columnconfigure(1, weight=1)

# Start the main loop
root.mainloop()
