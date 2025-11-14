# Version 2
# Author: Jagjamin

import qbittorrentapi
import datetime
import os
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

hostvar = tk.StringVar
portvar = tk.IntVar
uservar = tk.StringVar
passvar = tk.StringVar
closevar = tk.IntVar
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
    "total torrents": 1,
    "downloading torrents": 1,
    "seeding torrents": 1,
    "closest torrents": 0,
    "update rate": 1000
}

if os.path.exists("settings.json"):
    print("settings found")
else:
    with open("settings.json", "w") as json_file:
        json.dump(settings, json_file, indent=4)

def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}bytes"

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
    torrent_total = tt.get()
    torrent_downloading = td.get()
    torrent_seeding = ts.get()
    closest_torrents = close_int.get()
    update_speed = updaterate.get()

    global settings
    settings = {
        "total size": total_size,
        "remaining size": remaining_size,
        "download speed": download_speed,
        "torrent total": torrent_total,
        "torrent downloading": torrent_downloading,
        "torrent seeding": torrent_seeding,
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
    torrent_total=data["torrent total"]
    torrent_downloading=data["torrent downloading"]
    torrent_seeding=data["torrent seeding"]
    closest_torrents=data["closest torrents"]
    update_speed=data["update rate"]
    m.delete("1.0", tk.END)
    m.insert("1.0", "Total Size is: ")
    m.insert(tk.END, total_size)
    m.insert(tk.END,"\nRemaining Size is: ")
    m.insert(tk.END, remaining_size )
    m.insert(tk.END,"\nDownload Speed is: ")
    m.insert(tk.END, download_speed)
    m.insert(tk.END,"\nTotal Torrent is: ")
    m.insert(tk.END, torrent_total)
    m.insert(tk.END,"\nDownloading Torrent is: ")
    m.insert(tk.END, torrent_downloading)
    m.insert(tk.END,"\nSeeding Torrent is: ")
    m.insert(tk.END, torrent_seeding)
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

def clear_screen():
    if os.name == "nt":
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def populate():
    global display
    headings = createheadings()
    print(headings)
    display.configure(columns=headings)
    for i in headings:
        display.heading(i, text=i)

def display_main():
    global running
    try:
        qbt_client = qbittorrentapi.Client(**hostdict)
        qbt_client.auth_log_in()
    except:
        messagebox.showinfo("Error", "Authorization Error: Change host settings")
        switch_button.config(text = "Start", bg = "green")
        running = False
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

def update_tree():
    global running
    if running is True:
        for item in display.get_children():
            display.delete(item)

        new_data = display_main()
        rows = list(new_data.values())

        display.insert("","end", values=rows)
        display.after(settings["update rate"], update_tree)
    else:
        display.after(settings["update rate"], update_tree)

def torrent_soonest():
    global running
    qbt_client = qbittorrentapi.Client(**hostdict)
    if running is True:
        log = 0
        for item in soonest_torrent.get_children():
            soonest_torrent.delete(item)
        for torrent in qbt_client.torrents_info(sort="eta", reverse=False):
            if torrent.dlspeed > 0 and log < close_int.get():
                soonest_list=[torrent.name, format_bytes(torrent.size), format_bytes(torrent.amount_left), torrent.num_seeds, torrent.num_leechs, datetime.timedelta(seconds=torrent.eta)]
                soonest_torrent.insert("", "end", values=soonest_list)
                log+=1
        soonest_torrent.after(settings["update rate"], torrent_soonest)
    else:
        soonest_torrent.after(settings["update rate"], torrent_soonest)

def torrent_info():
    global running
    torrent_total = tt.get()
    torrent_downloading = td.get()
    torrent_stalled = ts.get()
    qbt_client = qbittorrentapi.Client(**hostdict)
    if running is True:
        widget_display = []
        if torrent_total is True:
            total=0
            for torrent in qbt_client.torrents_info():
                total+=1
            widget_display.append("\nTotal number of torrents: ")
            widget_display.append(total)
        if torrent_downloading is True:
            total=0
            for torrent in qbt_client.torrents_info():
                if torrent.state == "downloading":
                    total+=1
                if torrent.state == "forcedDL":
                    total+=1
            widget_display.append("\nNumber of Downloading Torrents: ")
            widget_display.append(total)
        if torrent_stalled is True:
            total=0
            for torrent in qbt_client.torrents_info():
                if torrent.state == "uploading":
                    total+=1
                if torrent.state == "forcedUP":
                    total+=1
            widget_display.append("\nNumber of Seeding Torrents: ")
            widget_display.append(total)
        torrent_widget.delete("1.0", tk.END)
        for i in widget_display:
            torrent_widget.insert(tk.END, i)
        torrent_widget.after(settings["update rate"], torrent_info)

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

def switch():
    global running
    if running:
        switch_button.config(text = "Start", bg = "Green")
        running = False
    else:
        switch_button.config(text = "Stop", bg = "Red")
        running = True
        update_tree()
        torrent_info()
        torrent_soonest()

root = tk.Tk() # Main window
root.title("qBitTorrent Live Monitoring")
root.geometry("1920x1080")
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

# Creating content for live monitoring frame
live_widget=tk.Text(live_frame, wrap="word")
live_widget.pack(expand=True, fill="both")

columns = createheadings()
display = ttk.Treeview(live_widget, columns=columns, show="headings")
for i in createheadings():
    display.heading(i, text=i)
    display.column(i, anchor="center", width=10)
display.pack(padx=10,pady=10,fill="both",expand=True)

# Soonest torrent frame
soonest_frame=ttk.Frame(live_frame)
soonest_frame.pack(expand=True, fill="both")
soonest_torrent=ttk.Treeview(soonest_frame, columns=("Torrent Name", "Torrent Size", "Amount Remaining", "Seeds", "Peers", "ETA"), show="headings")
soonest_headings=["Torrent Name", "Torrent Size", "Amount Remaining", "Seeds", "Peers", "ETA"]
for i in soonest_headings:
    soonest_torrent.heading(i, text=i)
    soonest_torrent.heading(i, anchor="w")
soonest_torrent.pack(padx=10, pady=10, expand=True, fill="both")

# Content for torrent info subframe
torrent_widget=tk.Text(live_frame, wrap="word")
torrent_widget.pack(padx=10, pady=10, expand=True, fill="both")

# monitoring tab buttons
sub_live_frame = ttk.Frame(live_frame)
sub_live_frame.pack(expand=True, anchor="center", fill="x")
switch_button = tk.Button(sub_live_frame, text = "Start", command = switch, bg = "green", height=5, width=15, font = ("Helvetica", 15, "bold"))
switch_button.pack(padx=10, side="left")

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
tt = tk.BooleanVar(value=settings["torrent total"])
td = tk.BooleanVar(value=settings["torrent downloading"])
ts = tk.BooleanVar(value=settings["torrent seeding"])
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
total_torrents = ttk.Checkbutton(options_frame, text="Show total torrent count", variable=tt)
total_torrents.grid(row=0, column=1, sticky="W", padx=20, pady=5)
downloading_torrents = ttk.Checkbutton(options_frame, text="Show downloading torrent count", variable=td)
downloading_torrents.grid(row=1, column=1, sticky="W", padx=20, pady=5)
seeding_torrents = ttk.Checkbutton(options_frame, text="Show seeding torrent count", variable=ts)
seeding_torrents.grid(row=2, column=1, sticky="W", padx=20, pady=5)
closest_torrents_label = ttk.Label(options_frame, text="Soonest Torrents Display Amount")
closest_torrents_label.grid(row=3, column=0, sticky="W", padx=20, pady=5)
closest_torrents_entry = ttk.Entry(options_frame, textvariable=close_int)
closest_torrents_entry.grid(row=3, column=0, sticky="W", padx=300, pady=5)
update_speed_label = ttk.Label(options_frame,text="Update rate in milliseconds")
update_speed_label.grid(row=4, column=0, sticky="W",  padx=20, pady=5)
update_speed_entry = ttk.Entry(options_frame, textvariable=updaterate)
update_speed_entry.grid(row=4, column=0, sticky="W", padx=300, pady=5)
settings_submit_button = tk.Button(options_frame, text="Save Settings", width=20, height=5, command = lambda : submit_settings(settings_check_box))
settings_submit_button.grid(row=5)
settings_check_button = tk.Button(options_frame, text="Check current settings", width=20, height=5, command = lambda : open_settings(settings_check_box))
settings_check_button.grid(row=6)
settings_check_box = tk.Text(options_frame, height=10)
settings_check_box.grid(row=7)
root.mainloop()

