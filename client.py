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
    while True:
        call = input("Введите запрос ")
        send_request(client_socket, call)
        call = call[:4]
        if call == "QUIT":
            break
        if call == "LOAD":
            send_request (client_socket,call)
            response = client_socket.recv(1024).decode()
            if response == "OK":
                data = receive_data(client_socket)
                print ("File loaded\n")
                call = input("Введите команду ")
                call = call[:4]
                if call == "SPEC":
                    client_socket.sendall(call.encode())
                    response = client_socket.recv(4)
                    sample_rate = struct.unpack("!I", response)[0]
                    plot_spectrogram(data, sample_rate)
                elif call == "INFO":
                    client_socket.sendall(call.encode())
                    response = receive_data(client_socket)
                    sample_rate, num_frames = struct.unpack("!II", response)
                    print(f"Sample Rate: {sample_rate}, Number of Frames: {num_frames}")
                elif call == "UNLOAD":
                    continue
            else:
                response = receive_data(client_socket)
        else:
            print (client_socket.recv(1024).decode())
    client_socket.close()
    print("connection closed")

# Запуск клиента
client("localhost", 9999)
