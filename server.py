import socket
import wave
import struct
import os

# Функция для загрузки wav файла
def load_wav_file(filename):
    try:
        wave_file = wave.open(filename, 'rb')
        sample_rate = wave_file.getframerate()
        num_frames = wave_file.getnframes()
        return wave_file, sample_rate, num_frames
    except FileNotFoundError:
        return None, None, None

# Функция для отправки данных клиенту
def send_data(connection, data):
    connection.sendall(struct.pack("!I", len(data)))
    connection.sendall(data)

# Функция для обработки запросов клиента
def handle_client(client_socket):
    while True:
        request = client_socket.recv(1024).decode().strip()
        if not request:
            break
        request_parts = request.split()
        command = request_parts[0]

        if command == "LOAD":
            if len(request_parts) < 2:
                client_socket.sendall(b"ERROR: Missing filename")
                continue
            filename = " ".join(request_parts[1:])
            wave_file, sample_rate, num_frames = load_wav_file(filename)
            if wave_file:
                client_socket.sendall("OK".encode())
                if client_socket.recv(1024).decode() == "OK":
                    send_data(client_socket, struct.pack("!II", sample_rate, num_frames))
                    data = wave_file.readframes(num_frames)
                    send_data(client_socket, data)
                    wave_file.close()
            else:
                client_socket.sendall(b"ERROR: File not found")
        elif command == "*IDN?":
            print("1")
            port = client_socket.getsockname()[1]
            response = f"You're on server port {port}"
            client_socket.sendall(response.encode())
        else:
            client_socket.sendall(b"ERROR: Invalid command")

# Основная функция сервера
def server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected to {addr[0]}:{addr[1]}")
        handle_client(client_socket)
        client_socket.close()
        print("connection closed")

# Запуск серверa

server("localhost", 9999)
