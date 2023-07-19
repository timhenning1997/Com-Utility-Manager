import binascii
import traceback
from datetime import datetime

import libscrc
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QCheckBox, QTextEdit, QLineEdit, QPushButton, QComboBox, \
    QWidget, QMessageBox

from AbstractWindow import AbstractWindow
from SerialParameters import SerialParameters


class WindowTerminal(AbstractWindow):
    def __init__(self, hubWindow):
        super().__init__(hubWindow, "Terminal")
        self.resize(400, 400)

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)

        self.autoscrollCheckbox = QCheckBox("Autoscroll")
        self.autoscrollCheckbox.setChecked(True)
        self.autoscrollCheckbox.adjustSize()

        self.timestampCheckbox = QCheckBox("Zeitstempel anzeigen")
        self.timestampCheckbox.adjustSize()

        self.portstampCheckbox = QCheckBox("Port anzeigen")
        self.portstampCheckbox.adjustSize()

        self.maxLinesCheckbox = QCheckBox("Clamp lines")
        self.maxLinesCheckbox.setChecked(True)
        self.maxLinesCheckbox.adjustSize()

        options2Layout = QHBoxLayout()
        options2Layout.addWidget(self.autoscrollCheckbox)
        options2Layout.addWidget(self.timestampCheckbox)
        options2Layout.addWidget(self.portstampCheckbox)
        options2Layout.addWidget(self.maxLinesCheckbox)
        options2Layout.addStretch()

        self.lineEdit = QLineEdit()
        self.lineEdit.returnPressed.connect(self.sendData)
        self.sendButton = QPushButton("Senden")
        self.sendButton.clicked.connect(self.sendData)
        self.sendBytesCombobox = QComboBox()
        self.sendBytesCombobox.addItem("Send as string")
        self.sendBytesCombobox.addItem("Send as byte")
        self.sendBytesCombobox.addItem("Send as 0F35 command")
        self.newLineCharCombobox = QComboBox()
        self.newLineCharCombobox.setFixedWidth(65)
        self.newLineCharCombobox.addItem("None      |Kein Zeilenende")
        self.newLineCharCombobox.addItem("NL           |Neue Zeile")
        self.newLineCharCombobox.addItem("CR           |Zeilenumbruch")
        self.newLineCharCombobox.addItem("NL&CR   |Sowhol CR als auch NL")

        sendLayout = QHBoxLayout()
        sendLayout.addWidget(self.lineEdit)
        sendLayout.addWidget(self.sendBytesCombobox)
        sendLayout.addWidget(self.newLineCharCombobox)
        sendLayout.addWidget(self.sendButton)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.textEdit)
        mainLayout.addLayout(options2Layout)
        mainLayout.addLayout(sendLayout)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    def receiveData(self, serialParameters: SerialParameters, data, dataInfo):
        line = ""
        if self.timestampCheckbox.isChecked() or self.portstampCheckbox.isChecked():
            line += "|"
        if self.timestampCheckbox.isChecked():
            line += datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        if self.portstampCheckbox.isChecked():
            line += " " + serialParameters.port
        if line != "":
            line += " ->| "
        try:
            rawData = data.decode('utf-8')
            line += rawData
        except:
            line += str(data) + "\n"

        self.textEdit.append(line.strip('\n\r'))
        if self.maxLinesCheckbox.isChecked():
            plainText = self.textEdit.toPlainText()
            if len(plainText) > 15000:
                self.textEdit.setPlainText(plainText[-14000:])
        if self.autoscrollCheckbox.isChecked():
            self.textEdit.moveCursor(QTextCursor.End)

    def sendData(self):
        if self.sendBytesCombobox.currentText() == "Send as byte":
            data = self.lineEdit.text().encode('utf-8')
        elif self.sendBytesCombobox.currentText() == "Send as string":
            data = self.lineEdit.text()
        elif self.sendBytesCombobox.currentText() == "Send as 0F35 command":
            byte = self.lineEdit.text()
            try:
                checkSum = str(hex(libscrc.modbus(binascii.unhexlify(str(byte))))[2:6].rjust(4,'0'))
                data = "0F35" + str(byte) + str(checkSum)
                #data = data.encode('utf-8')
                #print(data)   # Testausgabe um zu schauen, welches Datenformat herauskommt
                data = binascii.unhexlify(str(data))
                #print("Befehl: 0F35")
                #print("Byte: " + str(byte))
                #print("CheckSum: " + str(checkSum))
                #print("_______________________")
                #print("Sending: " + str(data))   # Testausgabe um zu schauen, welches Datenformat herauskommt
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Send Commandbyte Error")
                msg.setText("There is an error with sending the command bytes")
                msg.setInformativeText(str(e))
                msg.setDetailedText(str(traceback.format_exc()))
                msg.exec_()
                return
        self.lineEdit.setText("")
        if self.newLineCharCombobox.currentText() == "Neue Zeile (NL)":
            data += b'\n'
        if self.newLineCharCombobox.currentText() == "Zeilenumbruch (CR)":
            data += b'\r'
        if self.newLineCharCombobox.currentText() == "Sowhol CR als auch NL":
            data += b'\r\n'
        self.sendSerialData(data)

    def save(self):
        serializedDict = {}
        serializedDict["lineEditText"] = self.lineEdit.text()
        serializedDict["autoscroll"] = self.autoscrollCheckbox.isChecked()
        serializedDict["timestamp"] = self.timestampCheckbox.isChecked()
        serializedDict["portstamp"] = self.portstampCheckbox.isChecked()
        serializedDict["maxlines"] = self.maxLinesCheckbox.isChecked()
        serializedDict["sendBytes"] = self.sendBytesCombobox.currentText()
        serializedDict["newlinechar"] = self.newLineCharCombobox.currentText()
        return serializedDict

    def load(self, data):
        self.lineEdit.setText(data["lineEditText"])
        self.autoscrollCheckbox.setChecked(data["autoscroll"])
        self.timestampCheckbox.setChecked(data["timestamp"])
        self.portstampCheckbox.setChecked(data["portstamp"])
        self.maxLinesCheckbox.setChecked(data["maxlines"])
        self.sendBytesCombobox.setCurrentText(data["sendBytes"])
        self.newLineCharCombobox.setCurrentText(data["newlinechar"])
