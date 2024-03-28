import serial


class SerialParameters:
    def __init__(self, port=None, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False,
                 write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None,
                 local_echo=False, appendCR=False, appendLF=False, readTextIndex="read_line", readBytes=1,
                 readUntil='', DTR=False, maxShownSignalRate=10, Kennbin = "", Kennung = "", autoReconnect = False,
                 showFaultyData = False,recordBufferSize = 0):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.write_timeout = write_timeout
        self.dsrdtr = dsrdtr
        self.inter_byte_timeout = inter_byte_timeout
        self.exclusive = exclusive
        self.readTextIndex = readTextIndex
        self.readBytes = readBytes
        self.readUntil = readUntil
        self.DTR = DTR
        self.maxShownSignalRate = maxShownSignalRate  # Hz
        self.Kennbin = Kennbin
        self.Kennung = Kennung
        self.autoReconnect = autoReconnect
        self.showFaultyData = showFaultyData
        self.recordBufferSize = recordBufferSize        # useful for faster write speeds to disc

        self.local_echo = local_echo
        self.appendCR = appendCR
        self.appendLF = appendLF

        self.currentSignalRate = 0  # Hz
        self.errorCounter = 0

    def serialize(self):
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "bytesize": self.bytesize,
            "parity": self.parity,
            "stopbits": self.stopbits,
            "timeout": self.timeout,
            "xonxoff": self.xonxoff,
            "rtscts": self.rtscts,
            "write_timeout": self.write_timeout,
            "dsrdtr": self.dsrdtr,
            "inter_byte_timeout": self.inter_byte_timeout,
            "exclusive": self.exclusive,
            "readTextIndex": self.readTextIndex,
            "readBytes": self.readBytes,
            "readUntil": self.readUntil,
            "DTR": self.DTR,
            "maxShownSignalRate": self.maxShownSignalRate,
            "local_echo": self.local_echo,
            "appendCR": self.appendCR,
            "appendLF": self.appendLF,
            "autoReconnect": self.autoReconnect,
            "showFaultyData": self.showFaultyData,
            "recordBufferSize": self.recordBufferSize
        }

    def deserialize(self, data):
        self.port = data["port"]
        self.baudrate = data["baudrate"]
        self.bytesize = data["bytesize"]
        self.parity = data["parity"]
        self.stopbits = data["stopbits"]
        self.timeout = data["timeout"]
        self.xonxoff = data["xonxoff"]
        self.rtscts = data["rtscts"]
        self.write_timeout = data["write_timeout"]
        self.dsrdtr = data["dsrdtr"]
        self.inter_byte_timeout = data["inter_byte_timeout"]
        self.exclusive = data["exclusive"]
        self.readTextIndex = data["readTextIndex"]
        self.readBytes = data["readBytes"]
        self.readUntil = data["readUntil"]
        self.DTR = data["DTR"]
        self.maxShownSignalRate = data["maxShownSignalRate"]
        self.local_echo = data["local_echo"]
        self.appendCR = data["appendCR"]
        self.appendLF = data["appendLF"]
        self.autoReconnect = data["autoReconnect"]
        self.showFaultyData = data["showFaultyData"]
        self.recordBufferSize = data["recordBufferSize"]
