import socket
import struct
import wave
import os
import threading

def send_data(connection, data,framerate):
    connection.sendall(struct.pack("!II", len(data),framerate))
    connection.sendall(data)

def handle_client_connection(client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    

    while True:
        try:
            request = client_socket.recv(1024).decode().strip()
            if not request:
                break

            command = request.split()
            if command[0] == "LOAD":
                if len(command) != 2:
                    client_socket.sendall(b"ERROR: Invalid LOAD command format\n")
                    continue
                filename = command[1]
                if not os.path.exists(filename):
                    client_socket.sendall(b"ERROR: File not found\n")
                    continue
                try:
                    global wav_file
                    wav_file = wave.open(filename, 'rb')
                    client_socket.sendall(b"OK: File loaded\n")
                except wave.Error:
                    client_socket.sendall(b"ERROR: Invalid WAV file\n")

            elif command[0] == "INFO":
                if 'wav_file' not in globals():
                    client_socket.sendall(b"ERROR: No file loaded\n")
                    continue
                try:
                    rate = wav_file.getframerate()
                    frames = wav_file.getnframes()
                    client_socket.sendall(f"INFO: Rate={rate} Frames={frames}\n".encode())
                except wave.Error:
                    client_socket.sendall(b"ERROR: Could not read file info\n")

            elif command[0] == "SAMP":
                if 'wav_file' not in globals():
                    client_socket.sendall(b"ERROR: No file loaded\n")
                    continue
                try:
                    wav_file.rewind()
                    frames = wav_file.readframes(wav_file.getnframes())
                    send_data(client_socket,frames,wav_file.getframerate())
                except wave.Error:
                    client_socket.sendall(b"ERROR: Could not read samples\n")

            elif command[0] == "*IDN?":
                client_socket.sendall(f"You are on server {client_address[0]}:{client_address[1]}\n".encode())
            elif command[0] == "QUIT":
                client_socket.close()
                print("connection closed")
                break
            else:
                client_socket.sendall(b"ERROR: Unknown command\n")
        
        except Exception as e:
            #client_socket.sendall(f"ERROR: {str(e)}\n".encode())
            client_socket.close()
            print("connection closed")
            break

    client_socket.close()

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Listening on {host}:{port}")

    while True:
        client_sock, client_addr = server.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(client_sock, client_addr))
        client_thread.start()
        
if __name__ == "__main__":
    start_server("127.0.0.1", 5000)
