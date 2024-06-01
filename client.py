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
    framecount = client.ReceiveBytes()
    channels = client.ReceiveBytes()
    return samplerate, data,framecount,channels

def plot_spectrogram(samples, rate):
    # samples = np.frombuffer(samples, dtype=np.uint16)
    samples = [struct.unpack('h', samples[i:i+2])[0] for i in range(0, len(samples), 2)]
    samplerate = int.from_bytes(rate, byteorder='big')
    plt.specgram(samples, NFFT=1024, Fs=samplerate, noverlap=512)
    plt.title("Spectrogram")
    plt.ylabel("Frequency (Hz)")
    plt.xlabel("Time (s)")
    plt.show()

def plot_oscil(samples,rate,framecount):
    # Получение временного массива
    samples = [struct.unpack('h', samples[i:i+2])[0] for i in range(0, len(samples), 2)]
    framecount = int.from_bytes(framecount, byteorder='big')
    rate = int.from_bytes(rate, byteorder='big')
    duration = framecount / rate
    time = np.linspace(0., duration, framecount)
    xf = np.linspace(0.0, (1/rate * len(samples)), len(samples),endpoint=True,retstep=False, dtype=None,axis = 0)
    plt.title('Осциллограмма WAV файла')
    plt.xlabel('Время (с)')
    plt.ylabel('Амплитуда')
    plt.plot(xf,samples, color = 'green')
    plt.show()

def plot_spectrum(samples,rate,framecount,channels,N):
    samples = [struct.unpack('h', samples[i:i+2])[0] for i in range(0, len(samples), 2)]
    framecount = int.from_bytes(framecount, byteorder='big')
    rate = int.from_bytes(rate, byteorder='big')
    channels = int.from_bytes(channels, byteorder='big')
    if N == 0:
        N = framecount
    # Если данные стерео, выбрать один канал
    if channels == 2:
        samples = samples[:, 0]  # Выбор первого канала
    # Проверка, что N не превышает длину данных
    if not (N > framecount):
        # Получение первых N отсчетов
        samples = samples[:N]
        # Выполнение FFT
        fft_data = np.fft.fft(samples)
        fft_data = np.abs(fft_data)  # Амплитуды
        freqs = np.fft.fftfreq(N, 1/rate)  # Частоты
        # Поскольку FFT возвращает спектр, симметричный относительно нуля, берем только положительные частоты
        pos_mask = freqs >= 0
        freqs = freqs[pos_mask]
        fft_data = fft_data[pos_mask]
        # Построение спектра
        plt.figure(figsize=(10, 4))
        plt.plot(freqs, fft_data)
        plt.title('Спектр сигнала')
        plt.xlabel('Частота (Гц)')
        plt.ylabel('Амплитуда')
        plt.grid(True)
        plt.show()
    else:
        print("В файле меньше отсчетов чем ввел пользователь\n")

def main():
    port = "COM4"  # Укажите ваш COM-порт
    baudrate = 115200
    sample_rec = False

    client = ComPort()
    client.Connect(port,baudrate)
    time.sleep(1)  # Дать время для инициализации порта

    while True:
        raw = input("Enter command: ")
        request = raw.split()
        command = request[0]
        raw = raw.strip()
        if not raw:
            continue
        if command == "QUIT":
            send_command(client, raw)
            client.Disconnect()
            break
        if command == "SPGM":
            if sample_rec:
                plot_spectrogram(samples, rate)
            else:
                print("No samples")
            continue
        if command == "OSCI":
            if sample_rec:
                plot_oscil(samples, rate,framecount)
            else:
                print("No samples")
            continue
        if command == "SPEC":
            if not sample_rec:
                print("No samples")
                continue 
            if len(request) != 2:
                print("Не введено количество сэмплов, строю спектр по всем отсчетам")
                plot_spectrum(samples,rate,framecount,channels,N=0)
            elif len(request) == 2:
                plot_spectrum(samples,rate,framecount,channels,N=int(request[1]))
            continue        
        send_command(client, raw)
        if command.startswith("SAMP"):
            print("Receiving samples...")
            rate, samples,framecount,channels = receive_samples(client)
            print("Samples received")
            sample_rec = True
            continue
        else:
            print(server_response(client))

if __name__ == "__main__":
    main()
