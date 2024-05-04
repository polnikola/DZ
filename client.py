import socket
import struct
import matplotlib.pyplot as plt
import numpy as np

# Функция для получения данных от сервера
def receive_data(connection):
    length_data = connection.recv(4)
    length = struct.unpack("!I", length_data)[0]
    data = b""
    while len(data) < length:
        packet = connection.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

# Функция для отправки запроса на сервер
def send_request(connection, request):
    connection.sendall(request.encode())

# Функция для построения спектрограммы
def plot_spectrogram(data, sample_rate):
    signal = np.frombuffer(data, dtype=np.int16)
    plt.specgram(signal, Fs=sample_rate)
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    plt.show()

# Основная функция клиента
def client(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    call = input("Введите запрос ")
    send_request(client_socket, call)
    if call[0] == "LOAD":
        response = client_socket.recv(1024).decode()
        if response == "OK":
            client_socket.sendall("OK".decode())
            response = receive_data(client_socket)
            if response.startswith(b"ERROR"):
                print(response.decode())
            else:
                sample_rate, num_frames = struct.unpack("!II", response)
                print(f"Sample Rate: {sample_rate}, Number of Frames: {num_frames}")

                data = receive_data(client_socket)
                if data:
                    plot_spectrogram(data, sample_rate)
                else:
                    print("Failed to receive data from server")
        else:
            print (response.decode())
    else:
        response = client_socket.recv(1024)
        print(response.decode())
    client_socket.close()
    print("connection closed")

# Запуск клиента
client("localhost", 9999)
