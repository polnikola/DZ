import serial
import struct
import wave
import os


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
    start_server("COM5")  # Укажите ваш COM порт
