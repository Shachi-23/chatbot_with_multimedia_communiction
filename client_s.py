import socket
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, simpledialog, colorchooser, Menu
import os
import sys
import subprocess


host = '192.168.139.142'
port = 5000

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
except Exception as e:
    messagebox.showerror("Connection Error", f"Unable to connect to the server.\n{e}")
    sys.exit()

root = tk.Tk()
root.title("Chat Client")


bg_color = "#282c34"  
text_color = "#ffffff" 
button_color = "#005f73"
entry_bg_color = "#2b2b2b"
entry_text_color = "#a9b7c6"

root.configure(bg=bg_color)

client_name = simpledialog.askstring("Name", "Enter your name:", parent=root)
if not client_name:
    sys.exit("Name is required to join the chat.")


name_label = tk.Label(root, text=f"Name: {client_name}", fg=text_color, bg=bg_color, font=("Arial", 12))
name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10)


SENT_TAG = "sent_message"

RECEIVED_TAG = "received_message"

def send_message(message):
    if message: 
       
        if client_name in message:
            update_chat_box(message, tag=SENT_TAG)  
        else:
            full_message = f"{client_name}: {message}" 
            client.send(full_message.encode('utf-8'))
            update_chat_box(full_message, tag=SENT_TAG)  

def send_emoji(emoji_str):
    send_message(emoji_str)

def send_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)
        client.send(f"FILE:{filename}:{filesize}".encode('utf-8'))
        with open(file_path, "rb") as file:
            bytes_read = file.read(4096)
            while bytes_read:
                client.send(bytes_read)
                bytes_read = file.read(4096)

def update_chat_box(message, tag=None):
    chat_box.config(state=tk.NORMAL)
    if tag:
        chat_box.insert(tk.END, message + "\n", tag)  
    else:
        chat_box.insert(tk.END, message + "\n")  
    chat_box.yview(tk.END)
    chat_box.config(state=tk.DISABLED)

def open_file(filename):
    try:
        if sys.platform == "win32":
            os.startfile(filename)
        elif sys.platform == "darwin":
            subprocess.call(('open', filename))
        else:
            subprocess.call(('xdg-open', filename))
    except Exception as e:
        messagebox.showerror("Open File Error", f"Could not open file: {e}")

def receive_messages():
    while True:
        try:
            message = client.recv(4096).decode('utf-8')
            if message.startswith("FILE:"):
                _, filename, filesize = message.split(":")
                filesize = int(filesize)
                filepath = f"received_{filename}"
                with open(filepath, "wb") as file:
                    bytes_received = 0
                    while bytes_received < filesize:
                        bytes_read = client.recv(4096)
                        if not bytes_read:
                            break
                        file.write(bytes_read)
                        bytes_received += len(bytes_read)
                update_chat_box(f"Received file: {filename}", tag=RECEIVED_TAG)
                open_file(filepath)
            else:
                update_chat_box(message, tag=RECEIVED_TAG)
        except Exception as e:
            update_chat_box(f"Error: {e}")
            break

def show_emoji_menu(event):
    emoji_menu.post(event.x_root, event.y_root)

# GUI Layout continued
chat_box = scrolledtext.ScrolledText(root, state='disabled', height=15, width=50, bg=entry_bg_color, fg=entry_text_color)
chat_box.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

message_entry = tk.Entry(root, width=48, bg=entry_bg_color, fg=entry_text_color)
message_entry.grid(row=2, column=0, padx=5, pady=5)

send_button = tk.Button(root, text="Send", command=lambda: send_message(message_entry.get()), bg=button_color, fg=text_color)
send_button.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

send_emoji_button = tk.Button(root, text="Emoji", bg=button_color, fg=text_color)
send_emoji_button.grid(row=3, column=0, padx=5, pady=5)
emoji_menu = Menu(send_emoji_button, tearoff=0)
emoji_menu.add_command(label="😊", command=lambda: send_emoji("😊"))
emoji_menu.add_command(label="😂", command=lambda: send_emoji("😂"))
emoji_menu.add_command(label="😎", command=lambda: send_emoji("😎"))
emoji_menu.add_command(label="❤️", command=lambda: send_emoji("❤️"))
emoji_menu.add_command(label="👍", command=lambda: send_emoji("👍"))
emoji_menu.add_command(label="🙋‍♀️", command=lambda: send_emoji("🙋‍♀️"))
emoji_menu.add_command(label="🤩", command=lambda: send_emoji("🤩"))
emoji_menu.add_command(label="👋🏻", command=lambda: send_emoji("👋🏻"))
emoji_menu.add_command(label="🦚", command=lambda: send_emoji("🦚"))
emoji_menu.add_command(label="😁", command=lambda: send_emoji("😁"))

send_file_button = tk.Button(root, text="Send File", command=send_file, bg=button_color, fg=text_color)
send_file_button.grid(row=3, column=1, padx=5, pady=5)


name_label.config(text=f"Name: {client_name}")


chat_box.tag_configure(SENT_TAG, justify='right', foreground='white')
chat_box.tag_configure(RECEIVED_TAG, justify='left', foreground='lightgreen')

threading.Thread(target=receive_messages, daemon=True).start()

send_emoji_button.bind("<Button-1>", show_emoji_menu)

root.mainloop()
