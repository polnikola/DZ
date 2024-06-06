import serial
import struct
import wave
import os
import numpy as np
from scipy.signal import chirp
from scipy.io.wavfile import write

dict = {
    "HELP" : "Выводит все команды",
    "LOAD" : "Выбирает wav файл на сервере",
    "INFO" : "Выводит фреймрейт и количество отсчетов",
    "SAMP" : "Передает сэмплы на клиент",
    "QUIT" : "Разрывает соединение",
    "*IDN?" : "Эхо сервера",
    "SPEC" : "Выводит спектрограмму файла",
    "OSCI" : "Выводит осциллограмму"
 }

def Generate_wav(name, time,ratio):
    if ratio > 1:
        return False
    interval_length1 = time * ratio
    interval_length2 = time * (1-ratio)
    sampleRate = 44100 
    startFreq = 20000
    stopFreq = 20
    t1 = np.linspace(0, interval_length1, int(sampleRate * (interval_length1)))
    t2 = np.linspace(0, interval_length2, int(sampleRate * (interval_length2)))
    w1 = chirp(t1, f0=startFreq, f1=stopFreq, t1=interval_length1, method='linear')
    w2 = chirp(t2, f0=stopFreq, f1=startFreq, t1=interval_length2, method='quadratic')
    w = np.concatenate((w1, w2), axis=0)
    write(name, sampleRate, (w*(2**15)).astype(np.int16))
    return True

class ComPort():
    Connected = False
    def Connect(self, portName, baudRate, byteSize = 8, stopBits = 1):
        if(not self.Connected):
            print("Попытка установить соединение", portName)
            try:
                self.port = serial.Serial(port=portName, baudrate=baudRate, bytesize=byteSize, stopbits=stopBits)
                self.Connected = True
            except serial.SerialException:
                print("Проверьте првильность установки параметров")
            except:
                print("Вознкла другая ошибка")
            finally:
                print(("Соединение установлено" if self.Connected else "Соединение не установлено"))

    def Disconnect(self):
        self.port.close()

    def Send(self, data):
        if(self.Connected):
            if(type(data) is str):
                print("Отправка сообщения", data)
                self.port.write(data.encode('utf-8')+ b"Nikita")
                print("Успешно отправлено")
            else:
                print("Отправка сообщения")
                self.port.write(data+ b"Nikita")
                print("Успешно отправлено")
        else:
            print("Device is not connected")
        
    def ReceiveBytes(self):
        if(self.Connected):
            print("Ожидание ответа...")
            resp = self.port.read_until(expected=b"Nikita")
            resp = resp[:-6]
            print("Ответ получен")
            return resp
        else:
            print("Device is not connected")
            return b""

    def ReceiveStr(self):
        resp = self.ReceiveBytes()
        return resp.decode('utf-8')

def handle_client_connection(ser,port):
    print("Accepted connection on COM port")

    while True:
        try:
            request = ser.ReceiveStr()
            if not request:
                break
            command = request.split()
            if command[0] == "LOAD":
                if len(command) != 2:
                    ser.Send(b"ERROR: Invalid LOAD command format\n")
                    continue
                filename = command[1]
                if not os.path.exists(filename):
                    ser.Send(b"ERROR: File not found\n")
                    continue
                try:
                    global wav_file
                    wav_file = wave.open(filename, 'rb')
                    ser.Send(b"OK: File loaded\n")
                except wave.Error:
                    ser.Send(b"ERROR: Invalid WAV file\n")

            elif command[0] == "HELP":
                if len(command) == 2:
                    ser.Send(dict.get(command[1],"нет такой комманды") + '\n')
                else:
                    response = ""
                    keys = dict.keys()
                    for a in keys:
                        response += a + "\n"
                    ser.Send(response)
                continue
            elif command[0] == "INFO":
                if 'wav_file' not in globals():
                    ser.Send(b"ERROR: No file loaded\n")
                    continue
                try:
                    rate = wav_file.getframerate()
                    frames = wav_file.getnframes()
                    ser.Send(f"INFO: Rate={rate} Frames={frames}\n")
                except wave.Error:
                    ser.Send(b"ERROR: Could not read file info\n")
            elif command[0] == "GNRT":
                if len(command) < 4:
                    ser.Send(b"ERROR: Fill all arguments(name, time, fall_%, rise_%)\n")
                    continue
                else:
                    name = command[1]
                    time = float(command[2])
                    ratio = float(command[3])
                    if Generate_wav(name, time,ratio) == True:
                        ser.Send(b"Success\n")
                        continue
                    else: 
                        ser.Send(b"Something went wrong\n")
                        continue
            elif command[0] == "SAMP":
                if 'wav_file' not in globals():
                    ser.Send(b"ERROR: No file loaded\n")
                    continue
                try:
                    wav_file.rewind()
                    rate = wav_file.getframerate()
                    ser.Send(rate.to_bytes(16, byteorder='big'))
                    frames = wav_file.readframes(wav_file.getnframes())
                    ser.Send(frames)
                    framecount = wav_file.getnframes()
                    ser.Send(framecount.to_bytes(16, byteorder='big'))
                    channels = wav_file.getnchannels()
                    ser.Send(channels.to_bytes(16, byteorder='big'))
                except wave.Error as e:
                    ser.Send(b"ERROR: Could not read samples\n")

            elif command[0] == "*IDN?":
                ser.Send(f"You are on the server {port}\n")
            elif command[0] == "QUIT":
                ser.close()
                print("Connection closed")
                break
            else:
                ser.Send(b"ERROR: Unknown command\n")

        except Exception as e:
            ser.Disconnect()
            print("Connection closed")
            break

def start_server(port):
    ser = ComPort()
    ser.Connect(port,115200)
    print(f"Listening on {port}")

    handle_client_connection(ser,port)

if __name__ == "__main__":
    start_server("COM3")  # Укажите ваш COM порт
