import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import os

# Connection settings
HOST = 'chatapp-cpan226.up.railway.app'
PORT = 12345

# Initialize client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Functions for GUI
def receive_messages():
    """Receive and display messages from the server."""
    while True:
        try:
            message = client_socket.recv(1024).decode("utf8")
            if message == "#quit":
                break
            conversation_box.insert(tk.END, message + "\n")
            conversation_box.yview(tk.END) 
        except OSError:
            break

def send_message():
    """Send a message to the server."""
    message = message_entry.get("1.0", tk.END).strip()
    if not message:
        return  # Ignore empty messages
    
    #send msg to server
    client_socket.send(bytes(message, "utf8"))
    
    try:
        sender = name_entry.get().strip()
        receiver = "All"  # 
        file_exists = os.path.isfile("chat_history.txt")
        with open("chat_history.txt", "a") as file:
            if not file_exists:
                conversation_box.insert(tk.END, "New chat history file created.\n")
            file.write(f"{sender} to {receiver}: {message}\n")
        message_entry.delete("1.0", tk.END) # Clears message entry after sending  
          
    except FileNotFoundError as e:
        conversation_box.insert(tk.END, f"Error: {str(e)}\n")
        print(f"Error: {str(e)}")

    except PermissionError as e:
        conversation_box.insert(tk.END, f"Error: {str(e)}\n")
        print(f"Error: {str(e)}")

    except Exception as e:
        conversation_box.insert(tk.END, f"Error sending message: {str(e)}\n")
        print(f"Error sending message: {str(e)}")
        

def on_closing():
    """Handle the client closing the chat."""
    client_socket.send(bytes("#quit", "utf8"))
    client_socket.close()
    root.destroy()

# GUI setup
root = tk.Tk() # Creates main tkinter window
root.title("Chat Application") # Sets title of window

#name entry 
name_label = tk.Label(root, text="Your Name:")
name_label.grid(row=0, column=0, padx=5, pady=5)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, padx=5, pady=5)

def enter_name():
    """Send the user's name to the server and start the chat."""
    name = name_entry.get().strip()
    if not name:
        return
    client_socket.send(bytes(name, "utf8"))
    """disable name entry feild and enter chat button, enable send button"""
    name_entry.config(state="disabled") 
    send_button.config(state="normal") 
    name_button.config(state="disabled")
    threading.Thread(target=receive_messages, daemon=True).start()

name_button = tk.Button(root, text="Enter Chat", command=enter_name)
name_button.grid(row=0, column=2, padx=5, pady=5)

message_label = tk.Label(root, text="Message:")
message_label.grid(row=1, column=0, padx=5, pady=5)
message_entry = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=30, height=5)
message_entry.grid(row=2, column=1, padx=5, pady=5)

conversation_label = tk.Label(root, text="Conversation:")
conversation_label.grid(row=4, column=0, padx=5, pady=5)
conversation_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
conversation_box.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Bind close event
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
