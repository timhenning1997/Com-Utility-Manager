import serial


class SerialParameters:
    def __init__(self, port=None, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False,
                 write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None, rts=None, dtr=None,
                 local_echo=False, appendCR=False, appendLF=False, readTextIndex="read_line", readBytes=1,
                 readUntil='', readUntilAscii=0, DTR=False, maxShownSignalRate=10, Kennbin = "", Kennung = "", autoReconnect = False,
                 showFaultyData = False, saveTimestamp = True, recordBufferSize = 0, alwaysSave = False, alwaysSaveBuffer = 100):
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
        self.rts = rts
        self.dtr = dtr
        self.readTextIndex = readTextIndex
        self.readBytes = readBytes
        self.readUntil = readUntil
        self.readUntilAscii = readUntilAscii
        self.DTR = DTR
        self.maxShownSignalRate = maxShownSignalRate  # Hz
        self.Kennbin = Kennbin
        self.Kennung = Kennung
        self.autoReconnect = autoReconnect
        self.showFaultyData = showFaultyData
        self.saveTimestamp = saveTimestamp
        self.recordBufferSize = recordBufferSize        # useful for faster write speeds to disc
        self.alwaysSave = alwaysSave
        self.alwaysSaveBuffer = alwaysSaveBuffer

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
            "rts": self.rts,
            "dtr": self.dtr,
            "readTextIndex": self.readTextIndex,
            "readBytes": self.readBytes,
            "readUntil": self.readUntil,
            "readUntilAscii": self.readUntilAscii,
            "DTR": self.DTR,
            "maxShownSignalRate": self.maxShownSignalRate,
            "local_echo": self.local_echo,
            "appendCR": self.appendCR,
            "appendLF": self.appendLF,
            "autoReconnect": self.autoReconnect,
            "showFaultyData": self.showFaultyData,
            "saveTimestamp": self.saveTimestamp,
            "recordBufferSize": self.recordBufferSize,
            "alwaysSave": self.alwaysSave,
            "alwaysSaveBuffer": self.alwaysSaveBuffer
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
        self.rts = data["rts"]
        self.dtr = data["dtr"]
        self.readTextIndex = data["readTextIndex"]
        self.readBytes = data["readBytes"]
        self.readUntil = data["readUntil"]
        self.readUntilAscii = data["readUntilAscii"]
        self.DTR = data["DTR"]
        self.maxShownSignalRate = data["maxShownSignalRate"]
        self.local_echo = data["local_echo"]
        self.appendCR = data["appendCR"]
        self.appendLF = data["appendLF"]
        self.autoReconnect = data["autoReconnect"]
        self.showFaultyData = data["showFaultyData"]
        self.saveTimestamp = data["saveTimestamp"]
        self.recordBufferSize = data["recordBufferSize"]
        self.alwaysSave = data["alwaysSave"]
        self.alwaysSaveBuffer = data["alwaysSaveBuffer"]
