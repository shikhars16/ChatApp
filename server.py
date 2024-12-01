import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

# Dictionary to manage rooms and their clients
rooms = {"general": []}
addresses = {}

def broadcast(message, room_name, exclude_client=None):
    """Send a message to all clients in a specific room except the excluded one."""
    if room_name in rooms:
        for client in rooms[room_name]:
            if client != exclude_client:
                try:
                    client.send(message)
                except Exception as e:
                    print(f"Error broadcasting message: {e}")
                    rooms[room_name].remove(client)

def handle_client(client):
    """Handle a single client connection."""
    try:
        client.send("Enter your name:".encode("utf8"))
        name = client.recv(1024).decode("utf8").strip()

        if not name:
            client.close()
            return

        client.send("Enter room name (or type 'create:<room_name>' to create one):".encode("utf8"))
        room_request = client.recv(1024).decode("utf8").strip()

        # Create a new room if requested
        if room_request.startswith("create:"):
            room_name = room_request.split(":", 1)[1].strip()
            if room_name not in rooms:
                rooms[room_name] = []
            else:
                client.send(f"Room {room_name} already exists.".encode("utf8"))
        else:
            room_name = room_request

        # Check if the room exists
        if room_name not in rooms:
            client.send(f"Room {room_name} does not exist. Disconnecting.".encode("utf8"))
            client.close()
            return

        # Add client to the room
        rooms[room_name].append(client)
        addresses[client] = (name, room_name)

        # Notify the room
        join_message = f"{name} has joined the room {room_name}."
        broadcast(join_message.encode("utf8"), room_name, exclude_client=client)
        print(join_message)

        while True:
            try:
                message = client.recv(1024).decode("utf8")
                if message == "#quit":
                    farewell_message = f"{name} has left the room {room_name}."
                    print(farewell_message)
                    broadcast(farewell_message.encode("utf8"), room_name)
                    rooms[room_name].remove(client)
                    client.close()
                    break
                else:
                    # Broadcast the message to the room
                    broadcast(f"{name}: {message}".encode("utf8"), room_name, exclude_client=client)
            except Exception as e:
                print(f"Error handling client {name}: {e}")
                break
    finally:
        # Clean up after the client disconnects
        if client in rooms.get(room_name, []):
            rooms[room_name].remove(client)
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
