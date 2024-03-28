import os
from datetime import datetime
from time import time
from PyQt5.QtCore import *
import serial
from PyQt5.QtWidgets import QMessageBox
from pathlib import Path

from SerialParameters import SerialParameters


import binascii
import libscrc
import numpy as np
import platform


class SerialSignals(QObject):
    # Signals
    receivedData = pyqtSignal(object, object)
    madeConnection = pyqtSignal(object)
    lostConnection = pyqtSignal(object)
    failedSendData = pyqtSignal(object, object)

    startRecording = pyqtSignal(object)
    pauseRecording = pyqtSignal(object)
    stopRecording = pyqtSignal(object)


class SerialThread(QRunnable):
    def __init__(self, serialParameters: SerialParameters):
        super().__init__()
        self.serialParameters = serialParameters
        self.serialArduino = serial.Serial()
        self.serialArduino.port = self.serialParameters.port
        self.serialArduino.baudrate = self.serialParameters.baudrate
        self.serialArduino.bytesize = self.serialParameters.bytesize
        self.serialArduino.parity = self.serialParameters.parity
        self.serialArduino.stopbits = self.serialParameters.stopbits
        self.serialArduino.timeout = self.serialParameters.timeout
        self.serialArduino.xonxoff = self.serialParameters.xonxoff
        self.serialArduino.rtscts = self.serialParameters.rtscts
        self.serialArduino.write_timeout = self.serialParameters.write_timeout
        self.serialArduino.dsrdtr = self.serialParameters.dsrdtr
        self.serialArduino.inter_byte_timeout = self.serialParameters.inter_byte_timeout
        self.serialArduino.exclusive = self.serialParameters.exclusive
        #self.serialArduino.setDTR(self.serialParameters.DTR)

        self.signals = SerialSignals()
        self.is_killed = False
        self.is_paused = False
        self.lostConnectionTimer = -1

        self.recordingStarted = False
        self.record = False
        self.recordFilePath = str(Path(os.getcwd() + "/test.txt"))
        self.lastRefreshTime = 0
        self.failCounter = 0

        self.lastSignalTime = time()
        self.lastRefreshTimeDict = {}

        # useful for faster write speeds to disc
        self.recordBuffer = []
        self.recordBufferSize = serialParameters.recordBufferSize

        if platform.system() == "Linux":
            self.serialArduino.port = "/dev/" + self.serialParameters.port


    @pyqtSlot()  # Decorator function to show that this method is a slot
    def run(self):
        if not self.serialArduino.isOpen():
            try:
                self.serialArduino.open()
                self.signals.madeConnection.emit(self.serialParameters)
            except:
                print("Connecting to: " + self.serialParameters.port + " failed")
                return None

        while not self.is_killed:
            if not self.is_paused:
                try:
                    if self.serialArduino.isOpen():
                        if self.serialParameters.readTextIndex == "read_line":
                            readLine = self.read_line()  # self.serialArduino.readline()
                            if not readLine == b'':
                                #try:
                                #readLine.decode('utf-8')
                                #except UnicodeDecodeError as e:
                                #    if self.lostConnectionTimer == -1:
                                #        self.lostConnectionTimer = datetime.now().timestamp() + 1
                                #    if datetime.now().timestamp() > self.lostConnectionTimer:
                                #        print(e)
                                #        self.signals.lostConnection.emit(self.serialParameters)
                                #        return None
                                #    continue
                                if self.record:
                                    self.recordData([readLine.decode('utf-8').strip()])
                                if "lRT" not in self.lastRefreshTimeDict:
                                    self.lastRefreshTimeDict["lRT"] = 0
                                if time() > self.lastRefreshTimeDict["lRT"] + (
                                        1 / self.serialParameters.maxShownSignalRate):
                                    currentTime = time()
                                    if currentTime - self.lastSignalTime > 0:
                                        self.serialParameters.currentSignalRate = 1 / (currentTime - self.lastSignalTime)
                                    self.lastRefreshTimeDict["lRT"] = time()
                                    self.signals.receivedData.emit(self.serialParameters, readLine)

                                self.lastSignalTime = time()

                        elif self.serialParameters.readTextIndex == "read_bytes":
                            readLine = self.serialArduino.read(self.serialParameters.readBytes)
                            if not readLine == b'':
                                #try:
                                #    readLine.decode('utf-8')
                                #except UnicodeDecodeError as e:
                                #    print(e)
                                #    self.signals.lostConnection.emit(self.serialParameters)
                                #    return None
                                if self.record:
                                    self.recordData([readLine.decode('utf-8').strip()])
                                if "lRT" not in self.lastRefreshTimeDict:
                                    self.lastRefreshTimeDict["lRT"] = 0
                                if time() > self.lastRefreshTimeDict["lRT"] + (
                                        1 / self.serialParameters.maxShownSignalRate):
                                    currentTime = time()
                                    if currentTime - self.lastSignalTime > 0:
                                        self.serialParameters.currentSignalRate = 1 / (
                                                    currentTime - self.lastSignalTime)
                                    self.lastRefreshTimeDict["lRT"] = time()
                                    self.signals.receivedData.emit(self.serialParameters, readLine)

                                self.lastSignalTime = time()
                        elif self.serialParameters.readTextIndex == "read_until":
                            readLine = self.serialArduino.read_until(
                                self.serialParameters.readUntil.encode('utf-8'))  # self.serialParameters.readUntil)
                            if not readLine == b'':
                                try:
                                    readLine.decode('utf-8')
                                except UnicodeDecodeError as e:
                                    print(e)
                                    self.signals.lostConnection.emit(self.serialParameters)
                                    return None
                                if self.record:
                                    self.recordData([readLine.decode('utf-8').strip()])
                                if "lRT" not in self.lastRefreshTimeDict:
                                    self.lastRefreshTimeDict["lRT"] = 0
                                if time() > self.lastRefreshTimeDict["lRT"] + (
                                        1 / self.serialParameters.maxShownSignalRate):
                                    currentTime = time()
                                    if currentTime - self.lastSignalTime > 0:
                                        self.serialParameters.currentSignalRate = 1 / (
                                                currentTime - self.lastSignalTime)
                                    self.lastRefreshTimeDict["lRT"] = time()
                                    self.signals.receivedData.emit(self.serialParameters, readLine)

                                self.lastSignalTime = time()
                        elif self.serialParameters.readTextIndex == "logging_raw":
                            with open('loggingRaw.txt', 'a') as file:
                                readChar = self.serialArduino.read(1)
                                if readChar != b'':
                                    file.write(str(readChar))
                        elif self.serialParameters.readTextIndex == "read_WU_device":
                            if self.serialArduino.read(1) == b'\xaa':
                                if self.serialArduino.read(1) == b'\x55':
                                    Kennbin = self.serialArduino.read(2)
                                    Kennung = int(binascii.hexlify(Kennbin[:1]), 16)
                                    readLine = self.serialArduino.read(2 * Kennung + 2 + 2)
                                    if not readLine == b'':
                                        crc16send = readLine[-2:]
                                        crc16 = libscrc.modbus(Kennbin + readLine[0:-2])
                                        crc_check = crc16 == int(binascii.hexlify(crc16send), 16)

                                        data = []
                                        for n in range(len(readLine) // 2):
                                            data.append(str(binascii.hexlify(readLine[2 * n:2 * n + 2]))[2:6])
                                        singleLine = np.asarray(data)
                                        if not crc_check:
                                            singleLine = np.append(singleLine, '4650')
                                            self.serialParameters.errorCounter += 1
                                            if self.record:
                                                self.failCounter += 1
                                        else:
                                            singleLine = np.append(singleLine, '4f4b')
                                        # if not crc_check:
                                        #     singleLine[-1] = 'aaaa'

                                        if self.record:
                                            self.recordData(singleLine)

                                        if Kennbin not in self.lastRefreshTimeDict:
                                            self.lastRefreshTimeDict[Kennbin] = 0

                                        if time() > self.lastRefreshTimeDict[Kennbin] + (1 / self.serialParameters.maxShownSignalRate):
                                            if self.serialParameters.showFaultyData or crc_check:
                                                currentTime = time()
                                                if currentTime - self.lastSignalTime > 0:
                                                    self.serialParameters.currentSignalRate = 1 / (currentTime - self.lastSignalTime)

                                                self.lastRefreshTimeDict[Kennbin] = time()
                                                self.serialParameters.Kennbin = Kennbin
                                                self.serialParameters.Kennung = Kennung
                                                self.signals.receivedData.emit(self.serialParameters, singleLine)

                                        self.lastSignalTime = time()
                    else:
                        self.signals.lostConnection.emit(self.serialParameters)
                        return None
                except:
                    try:
                        self.signals.lostConnection.emit(self.serialParameters)
                    except:
                        pass
                    return None
            # QApplication.processEvents()
        self.serialArduino.close()
        try:
            self.signals.lostConnection.emit(self.serialParameters)
        except:
            pass

    def startRecordData(self, port, filePath, fileName):
        if not port.upper() == "COM-ALL" and not port.upper() == self.serialParameters.port.upper():
            return None
        if not os.path.exists(filePath):
            return None

        if self.recordingStarted:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Port already recording!")
            msg.setInformativeText('Stop current recording before starting a new one.')
            msg.setWindowTitle("Recording error")
            msg.exec_()
            return

        if filePath[-1] != "/":
            filePath += "/"
        if fileName.strip() == "":
            fileName += datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".txt"
        if port.upper() == "COM-ALL":
            fileName = fileName.split(".")[0] + "_" + str(self.serialParameters.port) + ".txt"
        self.recordFilePath = str(Path(filePath + fileName))

        try:
            with open(self.recordFilePath, 'a') as file:
                pass
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Invalid filename!")
            msg.setInformativeText('Exception: \n' + str(e))
            msg.setWindowTitle("Filename error")
            msg.exec_()
            return None

        self.failCounter = 0
        self.recordingStarted = True
        self.record = True
        self.signals.startRecording.emit(self.serialParameters)

        if self.serialParameters.readTextIndex == "read_WU_device":
            with open(self.recordFilePath, 'a') as file:
                file.write(float.hex(time()) + "\n")

    def stopRecordData(self, port):
        if not port.upper() == "COM-ALL" and not port.upper() == self.serialParameters.port.upper():
            return None

        self.recordingStarted = False
        self.record = False
        self.signals.stopRecording.emit(self.serialParameters)

        if not self.recordingStarted:
            return None

        if self.serialParameters.readTextIndex == "read_WU_device":
            #occurrences = 0
            #with open(self.recordFilePath, 'r') as file:
            #    occurrences = file.read().count("aaaa")
            #with open(self.recordFilePath, 'a') as file:
            #    file.write(float.hex(time()) + "\n")
            #    file.write("FatalError = " + str(occurrences) + "\n")

            with open(self.recordFilePath, 'a') as file:
                file.write(float.hex(time()) + "\n")
                file.write("FatalError = " + str(self.failCounter) + "\n")

    def pauseRecordData(self, port):
        if not port.upper() == "COM-ALL" and not port.upper() == self.serialParameters.port.upper():
            return None
        self.record = False

    def resumeRecordData(self, port):
        if not port.upper() == "COM-ALL" and not port.upper() == self.serialParameters.port.upper():
            return None
        self.record = True

    def writeDataToFile(self, text, port, filePath, fileName):
        if not port.upper() == "COM-ALL" and not port.upper() == self.serialParameters.port.upper():
            return None

        lastRecord = self.record
        self.record = False
        if filePath != "":
            if not os.path.exists(filePath):
                self.record = lastRecord
                return None

            if filePath[-1] != "/":
                filePath += "/"
            if fileName.strip() == "":
                fileName += datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".txt"
            if port.upper() == "COM-ALL":
                fileName = fileName.split(".")[0] + "_" + str(self.serialParameters.port) + ".txt"
            self.recordFilePath = str(Path(filePath + fileName))
            self.failCounter = 0

        if self.serialParameters.readTextIndex == "read_WU_device":
            with open(self.recordFilePath, 'a') as file:
                file.write(text)
        self.record = lastRecord

    def recordData(self, data):
        if self.recordBufferSize == 0:
            with open(self.recordFilePath, 'a') as file:
                file.write(' '.join(data) + "\n")
        elif len(self.recordBuffer) >= self.recordBufferSize:
            self.recordBuffer.append(' '.join(data) + "\n")
            with open(self.recordFilePath, 'a') as file:
                file.write(''.join(self.recordBuffer))
                self.recordBuffer = []
        else:
            self.recordBuffer.append(' '.join(data) + "\n")


    def writeSerial(self, port, data):
        for p in port.split("|"):
            if p.upper() == "COM-ALL" or p.upper() == self.serialParameters.port.upper():
                try:
                    if self.serialArduino.isOpen():
                        self.serialArduino.write(data)
                        self.serialArduino.flush()
                        if self.serialParameters.local_echo:
                            self.signals.receivedData.emit(self.serialParameters, data)
                    else:
                        self.signals.lostConnection.emit(self.serialParameters)
                        return None
                except:
                    self.signals.failedSendData.emit(self.serialParameters, data)
                    return None

    def kill(self, port):
        if port.upper() == "COM-ALL" or port.upper() == self.serialParameters.port.upper():
            self.serialParameters.autoReconnect = False
            self.is_killed = True

    def pause(self, port):
        if port.upper() == "COM-ALL" or port.upper() == self.serialParameters.port.upper():
            self.is_paused = True

    def resume(self, port):
        if port.upper() == "COM-ALL" or port.upper() == self.serialParameters.port.upper():
            self.is_paused = False

    def read_line(self):
        startTime = time()
        byte_str = b''
        while True:
            if self.is_killed or time() - startTime >= self.serialArduino.timeout:
                break
            byte = self.serialArduino.read()
            byte_str += byte
            if byte == b'\n':
                break
        return byte_str
