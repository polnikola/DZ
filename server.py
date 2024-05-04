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
        try: command = client_socket.recv(1024).decode().split(" ")
        except socket.error:
            continue
        if command[0] == "LOAD":
            try: filename = command[1]
            except IndexError:
                client_socket.sendall("BAD".encode())
                continue
            wave_file, sample_rate, num_frames = load_wav_file(filename)
            if wave_file:
                client_socket.sendall("OK".encode())
                data = wave_file.readframes(num_frames)
                send_data(client_socket, data)
                wave_file.close()
                command = client_socket.recv(1024).decode()
                if command == "INFO":
                    send_data(client_socket, struct.pack("!II", sample_rate, num_frames))
                elif command == "SPEC":
                     send_data(client_socket, struct.pack("!I", sample_rate))
                else:
                     client_socket.sendall(b"ERROR")
            else:
                client_socket.sendall(b"ERROR: File not found")
        elif command[0] == "*IDN?":
            port = client_socket.getsockname()[1]
            response = f"You're on server port {port}"
            client_socket.sendall(response.encode())
        elif command[0] == "INFO":
            response = "No file loaded"
            client_socket.sendall(response.encode())
            continue
        else:
            client_socket.sendall(b"ERROR: Invalid command")

# Основная функция сервера
def server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    while True:
        try: client_socket, addr = server_socket.accept()
        except socket.error:
            pass
        else:
            print(f"Connected to {addr[0]}:{addr[1]}")
            handle_client(client_socket)
            client_socket.close()
            print("connection closed")

# Запуск серверa

server("localhost", 9999)
