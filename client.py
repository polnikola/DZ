import socket
import struct
import matplotlib.pyplot as plt
import numpy as np

def send_command(sock, command):
    sock.sendall(command.encode())
def server_response(sock):
    response = sock.recv(1024).decode()
    print (response)

def get_samples(sock):
    samples = b""
    while True:
        part = sock.recv(1024)
        if not part:
            break
        samples += part
        print(part)
    return samples

def receive_samples(connection):
    length_and_rate = connection.recv(8)
    length,samplerate = struct.unpack("!II", length_and_rate)
    data = b""
    while len(data) < length:
        packet = connection.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return samplerate,data

def plot_spectrogram(samples, rate):
    samples = np.frombuffer(samples, dtype=np.int16)
    plt.specgram(samples, NFFT=1024, Fs=rate, noverlap=512)
    plt.title("Spectrogram")
    plt.ylabel("Frequency (Hz)")
    plt.xlabel("Time (s)")
    plt.show()

def main():
    server_ip = "127.0.0.1"
    server_port = 5000
    sample_rec = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, server_port))

        while True:
            command = input("Enter command: ").strip()
            if not command:
                continue

            if command == "QUIT":
                send_command(sock,command)
                sock.close()
                sample_rec = False
                break
            if command == "SPEC":
                if sample_rec:
                    plot_spectrogram(samples, rate)
                else:
                    print("No samples")
                continue
            send_command(sock,command)
            if command.startswith("SAMP"):
                print("Receiving samples...")
                rate,samples = receive_samples(sock)
                print("Samples received")
                sample_rec = True
            else:
                server_response(sock)

if __name__ == "__main__":
    main()
