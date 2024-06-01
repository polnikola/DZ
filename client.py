import serial
import struct
import matplotlib.pyplot as plt
import numpy as np
import time
from server import ComPort

def send_command(client, command):
    client.Send(command + '\n')

def server_response(client):
    response = client.ReceiveStr()
    return response


def receive_samples(client):
    samplerate = client.ReceiveBytes()
    data = client.ReceiveBytes()
    return samplerate, data

def plot_spectrogram(samples, rate):
    # samples = np.frombuffer(samples, dtype=np.uint16)
    samples = [struct.unpack('h', samples[i:i+2])[0] for i in range(0, len(samples), 2)]
    samplerate = int.from_bytes(rate, byteorder='big')
    plt.specgram(samples, NFFT=1024, Fs=samplerate, noverlap=512)
    plt.title("Spectrogram")
    plt.ylabel("Frequency (Hz)")
    plt.xlabel("Time (s)")
    plt.show()

def main():
    port = "COM4"  # Укажите ваш COM-порт
    baudrate = 115200
    sample_rec = False

    client = ComPort()
    client.Connect(port,baudrate)
    time.sleep(1)  # Дать время для инициализации порта

    while True:
        command = input("Enter command: ").strip()
        if not command:
            continue
        if command == "QUIT":
            send_command(client, command)
            client.Disconnect()
            break
        if command == "SPEC":
            if sample_rec:
                plot_spectrogram(samples, rate)
            else:
                print("No samples")
            continue

        send_command(client, command)
        if command.startswith("SAMP"):
            print("Receiving samples...")
            rate, samples = receive_samples(client)
            print("Samples received")
            sample_rec = True
        else:
            print(server_response(client))

if __name__ == "__main__":
    main()
