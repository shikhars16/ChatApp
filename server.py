import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

clients = []
addresses = {}

def broadcast(message, exclude_client=None):
    """Send a message to all clients except the excluded one."""
    for client in clients:
        if client != exclude_client:
            try:
                client.send(message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")

def handle_client(client):
    """Handle a single client connection."""
    try:
        name = client.recv(1024).decode("utf8").strip()
        if not name:
            client.close()
            return

        # Broadcast message when a new client joins
        join_message = f"{name} has joined the chat."
        broadcast(join_message.encode("utf8"))
        print(join_message)

        clients.append(client)
        addresses[client] = name

        while True:
            try:
                message = client.recv(1024).decode("utf8")
                if message == "#quit":
                    farewell_message = f"{name} left the chat."
                    print(farewell_message)
                    broadcast(farewell_message.encode("utf8"))
                    clients.remove(client)
                    client.close()
                    break
                else:
                    # Broadcast the message without extra formatting
                    broadcast(f"{name}: {message}".encode("utf8"))
            except Exception as e:
                print(f"Error handling client {name}: {e}")
                break
    finally:
        if client in clients:
            clients.remove(client)
        if client in addresses:
            del addresses[client]

def accept_connections():
    """Accept new client connections."""
    while True:
        client, client_address = server.accept()
        print(f"New connection: {client_address}")
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

# Start the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)
print("Server started, waiting for connections...")
accept_connections()
