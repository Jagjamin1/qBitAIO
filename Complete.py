# Version 1.5
# Author: Jagjamin

import qbittorrentapi
import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

hostvar = tk.StringVar
portvar = tk.IntVar
uservar = tk.StringVar
passvar = tk.StringVar
running = False


if os.path.exists("host.json"):
    with open("host.json", "r") as file:
        hostdict = json.load(file)
else: hostdict = {
    "host": "localhost",
    "port": 8080,
    "username": "admin",
    "password": "password"
}

if os.path.exists("host.json"):
    print("host settings found")
else:
    with open("host.json", "w") as json_file:
        json.dump(hostdict, json_file, indent=4)

if os.path.exists("settings.json"):
    with open("settings.json", "r") as file:
        settings = json.load(file)
else: settings = {
    "total size": 1,
    "remaining size": 1,
    "download speed": 1,
    "closest torrents": 0,
    "update rate": 1000
}

if os.path.exists("settings.json"):
    print("settings found")
else:
    with open("settings.json", "w") as json_file:
        json.dump(settings, json_file, indent=4)

def submit(m):
    host = host_entry.get()
    port = port_entry.get()
    username = username_entry.get()
    password = pass_entry.get()

    global hostdict
    hostdict = {
        "host": host,
        "port": int(port),
        "username": username,
        "password": password
    }
    try:
        with open("host.json", "w") as json_file:
            json.dump(hostdict, json_file, indent=4)
        m.delete("1.0", tk.END)
        m.insert(tk.END, "Settings Updated")
    except IOError:
        m.delete("1.0", tk.END)
        m.insert(tk.END, "Error updating")

def submit_settings(m):
    total_size = tsb.get()
    remaining_size = rsb.get()
    download_speed = dsb.get()
    closest_torrents = close_int.get()
    update_speed = updaterate.get()

    global settings
    settings = {
        "total size": total_size,
        "remaining size": remaining_size,
        "download speed": download_speed,
        "closest torrents": int(closest_torrents),
        "update rate": int(update_speed)
    }
    try:
        with open("settings.json", "w") as json_file:
            json.dump(settings, json_file, indent=4)
        m.delete("1.0", tk.END)
        m.insert(tk.END, "Settings Updated")
        populate()
    except IOError:
        m.delete("1.0", tk.END)
        m.insert(tk.END, "Error updating")

def openjson(m):
    with open("host.json", "r") as file:
        data = json.load(file)
    host=data["host"]
    port=data["port"]
    username=data["username"]
    password=data["password"]
    m.delete("1.0", tk.END)
    m.insert("1.0", "Host is: ")
    m.insert(tk.END,host)
    m.insert(tk.END,"\nPort is: ")
    m.insert(tk.END,port )
    m.insert(tk.END,"\nUsername is: ")
    m.insert(tk.END, username)
    m.insert(tk.END, "\nPassword is: ")
    m.insert(tk.END, password)

def open_settings(m):
    with open("settings.json", "r") as file:
        data = json.load(file)
    total_size=data["total size"]
    remaining_size=data["remaining size"]
    download_speed=data["download speed"]
    closest_torrents=data["closest torrents"]
    update_speed=data["update rate"]
    m.delete("1.0", tk.END)
    m.insert("1.0", "Total Size is: ")
    m.insert(tk.END, total_size)
    m.insert(tk.END,"\nRemaining Size is: ")
    m.insert(tk.END, remaining_size )
    m.insert(tk.END,"\nDownload Speed is: ")
    m.insert(tk.END, download_speed)
    m.insert(tk.END, "\nSoonest torrents shown is: ")
    m.insert(tk.END, closest_torrents)
    m.insert(tk.END, "\nUpdate rate is:")
    m.insert(tk.END, update_speed)
    m.insert(tk.END, "ms")


def format_bytes(size):
    # 2**10 = 1024
    power = 2 ** 10
    n = 0
    power_labels = {0: '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}bytes"

def populate():
    global display
    headings = createheadings()
    print(headings)
    display.configure(columns=headings)
    for i in headings:
        display.heading(i, text=i)

def display_main():
    try:
        qbt_client = qbittorrentapi.Client(**hostdict)
        qbt_client.auth_log_in()
    except:
        messagebox.showinfo("Error", "Authorization Error: Change host settings")
    totalsize=0
    remaining=0
    speed=0
    with open("settings.json", "r") as file:
        data = json.load(file)
    for torrent in qbt_client.torrents_info():
        totalsize=totalsize+torrent.size
        remaining=remaining+torrent.amount_left
        speed=speed+torrent.dlspeed
    totalsize = format_bytes((totalsize))
    remaining = format_bytes(remaining)
    speed = format_bytes(speed)
    display_dict = {}
    if data.get("total size") == True:
        display_dict.update({"Total Size" : totalsize})
    if data.get("remaining size") == True:
        display_dict.update({"Remaining Amount" : remaining})
    if data.get("download speed") == True:
        display_dict.update({"Download Speed" :speed + "/s"})
    return display_dict

def createheadings():
    with open("settings.json", "r") as file:
        data = json.load(file)
    headings = []
    if data.get("total size") == True:
        headings.append("Total Size")
    if data.get("remaining size") == True:
        headings.append("Remaining Amount")
    if data.get("download speed") == True:
        headings.append("Download Speed")
    return headings


def startlive():
    global running
    running = True
    update_tree()

def update_tree():
    for item in display.get_children():
        display.delete(item)

    new_data = display_main()
    rows = list(new_data.values())

    display.insert("","end", values=rows)
    display.after(settings["update rate"], update_tree)

def jsongui():
    HostWindow = tk.Tk()
    HostWindow.geometry("800x600")
    HostWindow.title("Host Settings")
    global hostvar
    hostvar = tk.StringVar()
    global portvar
    portvar = tk.StringVar()
    global usernamevar
    usernamevar = tk.StringVar()
    global passwordvar
    passwordvar = tk.StringVar()
    global login
    login = {}
    hostlabel = tk.Label(HostWindow, text="Host IP address", width=30)
    hostlabel.pack()
    hostentry = tk.Entry(HostWindow, width=25, textvariable= hostvar)
    hostentry.insert(tk.END, "localhost")
    hostentry.pack()
    portlabel = tk.Label(HostWindow,text="Port number", width=30)
    portlabel.pack()
    portentry = tk.Entry(HostWindow, width=25, textvariable= portvar)
    portentry.insert(tk.END, 8080)
    portentry.pack()
    usernamelabel = tk.Label(HostWindow, text="Username", width=30)
    usernamelabel.pack()
    usernameentry = tk.Entry(HostWindow, width=25, textvariable= usernamevar)
    usernameentry.insert(tk.END, "admin")
    usernameentry.pack()
    passwordlabel = tk.Label(HostWindow, text="Password", width=30)
    passwordlabel.pack()
    passwordentry = tk.Entry(HostWindow, width=25, textvariable= passwordvar)
    passwordentry.insert(tk.END, "adminadmin")
    passwordentry.pack()
    submitbutton = tk.Button(HostWindow, text="Save Settings", width=25, height=5, bg="white", fg="black", command = submit)
    submitbutton.pack()
    testbutton = tk.Button(HostWindow, text="View Settings", width=25, height=5, bg="white", fg="black", command = lambda: openjson(testtext))
    testbutton.pack()
    testtext= tk.Text(HostWindow, height=10, width=50)
    testtext.pack()
    HostWindow.mainloop()
    return True


def test_host(m):
    try:
        qbt_client = qbittorrentapi.Client(**hostdict)
        qbt_client.auth_log_in()
        m.delete("1.0",tk.END)
        m.insert(tk.END, "Login Success")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        m.delete("1.0", tk.END)
        m.insert("1.0", "Unexpected Error")


root = tk.Tk() # Main window
root.title("qBitTorrent Live Monitoring")
root.geometry("800x600")
root.resizable(True, True)

notebook = ttk.Notebook(root) # Notebook within main window
notebook.pack(fill="both", expand=1) # Make notebook fill window

live_frame = ttk.Frame(notebook) # Tab for live monitoring
host_frame = ttk.Frame(notebook) # Tab for host setting
options_frame = ttk.Frame(notebook) # Tab for options

# Add tabs to the notebook
notebook.add(live_frame, text="Monitoring")
notebook.add(host_frame, text="Host Settings")
notebook.add(options_frame, text="General Settings")

# Creating content for live monitoring tab
live_widget=tk.Text(live_frame, wrap="word")
live_widget.pack(expand=True, fill="both")
sub_live_frame = ttk.Frame(live_frame)
sub_live_frame.pack(expand=True, anchor="center")
populate_button = tk.Button(sub_live_frame, text="Populate Headers", command = populate, height=5, width=15)
populate_button.pack(padx=10, side="left")
start_button = tk.Button(sub_live_frame, text="Start", command = startlive, height=5, width=15)
start_button.pack(padx=10, side="left")
columns = createheadings()
display = ttk.Treeview(live_widget, columns=columns, show="headings")
for i in createheadings():
    display.heading(i, text=i)
    display.column(i, anchor="center", width=80)
display.pack(padx=10,pady=10,fill="both",expand=True)

#Creating content for Host Setting tab
host_label = ttk.Label(host_frame, text="Host IP")
host_label.pack(pady=10)
host_entry = ttk.Entry(host_frame, textvariable= hostvar, exportselection=False)
host_entry.insert(tk.END, hostdict["host"])
host_entry.pack()
port_label = ttk.Label(host_frame, text="Host Port Number")
port_label.pack(pady=10)
port_entry = ttk.Entry(host_frame, textvariable= portvar, exportselection=False)
port_entry.insert(tk.END, hostdict["port"])
port_entry.pack()
username_label = ttk.Label(host_frame, text="Username")
username_label.pack(pady=10)
username_entry = ttk.Entry(host_frame, textvariable= uservar, exportselection=False)
username_entry.insert(tk.END, hostdict["username"])
username_entry.pack()
pass_label = ttk.Label(host_frame, text="Password")
pass_label.pack(pady=10)
pass_entry = ttk.Entry(host_frame, textvariable= passvar, exportselection=False)
pass_entry.insert(tk.END, hostdict["password"])
pass_entry.pack()
submit_button = tk.Button(host_frame, text="Save Settings", width=25, height=5, command = lambda : submit(check_box))
submit_button.pack()
check_button = tk.Button(host_frame, text="Check current settings", width=25, height=5, command = lambda : openjson(check_box))
check_button.pack()
test_button = tk.Button(host_frame, text="test", command = lambda : test_host(check_box), height=5, width=15)
test_button.pack()
check_box = tk.Text(host_frame)
check_box.pack()

#Creating content for Options tab
tsb = tk.BooleanVar(value=settings["total size"])
rsb = tk.BooleanVar(value=settings["remaining size"])
dsb = tk.BooleanVar(value=settings["download speed"])
close_int = tk.IntVar(value=settings["closest torrents"])
updaterate = tk.IntVar(value=settings["update rate"])
options_frame.columnconfigure(0, weight=1)
options_frame.columnconfigure(1, weight=1)
options_frame.columnconfigure(2, weight=1)
total_size_button = ttk.Checkbutton(options_frame, text="Total Size", variable=tsb)
total_size_button.grid(row=0, column=0, sticky="W", padx=20, pady=5)
remaining_size_button = ttk.Checkbutton(options_frame, text="Remaining Size", variable=rsb)
remaining_size_button.grid(row=1, column=0, sticky="W", padx=20,pady=5)
total_download_speed = ttk.Checkbutton(options_frame, text="Total Download Speed", variable=dsb)
total_download_speed.grid(row=2, column=0, sticky="W", padx=20, pady=5)
closest_torrents_label = ttk.Label(options_frame, text="Soonest Torrents Display Amount")
closest_torrents_label.grid(row=3, column=0, padx=20, pady=5)
closest_torrents_entry = ttk.Entry(options_frame, textvariable=close_int)
closest_torrents_entry.grid(row=3, column=1, padx=20, pady=5)
update_speed_label = ttk.Label(options_frame,text="Update rate in milliseconds")
update_speed_label.grid(row=4, column=0, padx=20, pady=5)
update_speed_entry = ttk.Entry(options_frame, textvariable=updaterate)
update_speed_entry.grid(row=4, column=1, padx=20, pady=5)
settings_submit_button = tk.Button(options_frame, text="Save Settings", width=25, height=5, command = lambda : submit_settings(settings_check_box))
settings_submit_button.grid(row=5)
settings_check_button = tk.Button(options_frame, text="Check current settings", width=25, height=5, command = lambda : open_settings(settings_check_box))
settings_check_button.grid(row=6)
settings_check_box = tk.Text(options_frame)
settings_check_box.grid(row=7)
root.mainloop()

