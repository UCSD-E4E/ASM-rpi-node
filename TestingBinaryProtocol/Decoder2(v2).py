import struct
import uuid
import binascii
import enum
import datetime as dt
import numpy as np
import queue
import serial
import time

packet = bytes.fromhex('')

class binaryPacket:
    def __init__(self, payload: bytes, packetClass: int, packetID: int, sourceUUID: uuid.UUID, destUUID: uuid.UUID):
        self._payload = payload
        self._class = packetClass
        self._id = packetID
        self._source = sourceUUID
        self._dest = destUUID

    def to_bytes(self):
        payloadLen = len(self._payload)
        header = struct.pack("<BB", 0xE4, 0xEB) + \
                 self._source.bytes + \
                 self._dest.bytes + \
                 struct.pack("<BBH", self._class, self._id, payloadLen)
        pktCksum = binascii.crc_hqx(header, 0xFFFF).to_bytes(2, "big")
        msg = header + pktCksum + self._payload
        cksum = binascii.crc_hqx(msg, 0xFFFF).to_bytes(2, "big")
        return msg + cksum

    def getClassIDCode(self):
        return (self._class << 8) | self._id

    def __str__(self):
        string = self.to_bytes().hex().upper()
        length = 4
        return '%s' % ' '.join(string[i:i + length] for i in range(0, len(string), length))

    def __repr__(self):
        return str(self)

    def __eq__(self, packet):
        return self.to_bytes() == packet.to_bytes()

    @classmethod
    def from_bytes(cls, packet: bytes):
        srcUUID, destUUID, pcls, pid, payload = cls.parseHeader(packet)
        return binaryPacket(payload, pcls, pid, uuid.UUID(bytes=srcUUID), uuid.UUID(bytes=destUUID))

    @classmethod
    def parseHeader(cls, packet: bytes):
        if binascii.crc_hqx(packet, 0xFFFF) != 0:
            raise RuntimeError("Checksum verification failed")

        if binascii.crc_hqx(packet[0:0x0028], 0xFFFF) != 0:
            raise RuntimeError("Header checksum verification failed")

        if len(packet) < 0x2A:
            raise RuntimeError("Packet too short!")

        s1, s2, pcls, pid, _ = struct.unpack("<BB16x16xBBH", packet[0:0x26])
        srcUUID = bytes(packet[0x0002:0x0012])
        destUUID = bytes(packet[0x0012:0x0022])
        if s1 != 0xE4 or s2 != 0xEB:
            raise RuntimeError("Not a packet!")
        payload = packet[0x28:-2]
        return srcUUID, destUUID, pcls, pid, payload

    @classmethod
    def matches(cls, packetClass: int, packetID: int):
        return True


class E4E_Data_IMU(binaryPacket):
    __class = 0x04
    __id = 0x00
    __VERSION = 0x01

    def __init__(self, src: uuid.UUID, dest: uuid.UUID, accX, accY, accZ, gyroX, gyroY, gyroZ, magX, magY, magZ,
                 timestamp: dt.datetime = None):
        self.acc = [accX, accY, accZ]
        self.gyro = [gyroX, gyroY, gyroZ]
        self.mag = [magX, magY, magZ]
        if timestamp is None:
            timestamp = dt.datetime.now()
        self.timestamp = timestamp

        payload = struct.pack("<BBQ3f3f3f",
                                   self.__VERSION,
                                   0x00,
                                   int(timestamp.timestamp() * 1e3),
                                   *self.acc,
                                   *self.gyro,
                                   *self.mag)
        super(E4E_Data_IMU, self).__init__(payload, self.__class, self.__id, src, dest)

    @classmethod
    def matches(cls, packetClass: int, packetID: int):
        return packetClass == self.__class and packetID == self.__id

    @classmethod
    def from_bytes(cls, packet: bytes):
        srcUUID, destUUID, pcls, pid, payload = cls.parseHeader(packet)
        ver, _, timestamp_ms, accX, accY, accZ, gyroX, gyroY, gyroZ, magX, magY, magZ = struct.unpack("<BBQ3f3f3f", payload)
        if ver != cls.__VERSION:
            return RuntimeError("Unknown packet version!")

        timestamp = dt.datetime.fromtimestamp(timestamp_ms / 1e3)
        return E4E_Data_IMU(src=uuid.UUID(bytes=srcUUID),
                            dest=uuid.UUID(bytes=destUUID),
                            accX=accX,
                            accY=accY,
                            accZ=accZ,
                            gyroX=gyroX,
                            gyroY=gyroY,
                            gyroZ=gyroZ,
                            magX=magX,
                            magY=magY,
                            magZ=magZ,
                            timestamp=timestamp)


class E4E_Data_Audio_raw8(binaryPacket):
    __class = 0x04
    __id = 0x01
    __VERSION = 0x01

    def __init__(self, audioData: np.ndarray, src: uuid.UUID, dest: uuid.UUID, timestamp: dt.datetime = None):
        assert (len(audioData.shape) == 2)
        nChannels = audioData.shape[0]
        nSamples = audioData.shape[1]
        if timestamp is None:
            timestamp = dt.datetime.now()

        self.audioData = audioData
        payload = struct.pack("<BBHQ",
                              self.__VERSION,
                              nChannels,
                              nSamples,
                              int(timestamp.timestamp() * 1e3))
        for channel in range(nChannels):
            for sampleIdx in range(nSamples):
                payload += struct.pack("<B", int(audioData[channel, sampleIdx]))
        super(E4E_Data_Audio_raw8, self).__init__(payload, self.__class, self.__id, src, dest)

    @classmethod
    def matches(cls, packetClass: int, packetID: int):
        return packetClass == self.__class and packetID == self.__id

    @classmethod
    def from_bytes(cls, packet: bytes):
        srcUUID, destUUID, pcls, pid, payload = cls.parseHeader(packet)
        ver, nChannels, nSamples, timestamp_ms = struct.unpack("<BBHQ", payload[0:0x0C])
        audioBytes = payload[0x0C:]
        assert (len(audioBytes) == nChannels * nSamples)
        idx = 0
        audioData = np.zeros((nChannels, nSamples))
        for channel in range(nChannels):
            for sampleIdx in range(nSamples):
                audioData[channel, sampleIdx] = audioBytes[idx]
                idx += 1
        timestamp = dt.datetime.fromtimestamp(timestamp_ms / 1e3)
        return E4E_Data_Audio_raw8(audioData, uuid.UUID(bytes=srcUUID), uuid.UUID(bytes=destUUID), timestamp)


class E4E_Data_Audio_raw16(binaryPacket):
    __class = 0x04
    __id = 0x02
    __VERSION = 0x01

    def __init__(self, audioData: np.ndarray, src: uuid.UUID, dest: uuid.UUID, timestamp: dt.datetime = None):
        assert (len(audioData.shape) == 2)
        nChannels = audioData.shape[0]
        nSamples = audioData.shape[1]
        if timestamp is None:
            timestamp = dt.datetime.now()

        self.audioData = audioData
        payload = struct.pack("<BBHQ",
                              self.__VERSION,
                              nChannels,
                              nSamples,
                              int(timestamp.timestamp() * 1e3))
        for channel in range(nChannels):
            for sampleIdx in range(nSamples):
                payload += struct.pack("<H", int(audioData[channel, sampleIdx]))
        super(E4E_Data_Audio_raw16, self).__init__(payload, self.__class, self.__id, src, dest)

    @classmethod
    def matches(cls, packetClass: int, packetID: int):
        return packetClass == self.__class and packetID == self.__id

    @classmethod
    def from_bytes(cls, packet: bytes):
        srcUUID, destUUID, pcls, pid, payload = cls.parseHeader(packet)
        ver, nChannels, nSamples, timestamp_ms = struct.unpack("<BBHQ", payload[0:0x0C])
        audioBytes = payload[0x0C:]
        assert (len(audioBytes) == nChannels * nSamples * 2)
        idx = 0
        audioData = np.zeros((nChannels, nSamples))
        for channel in range(nChannels):
            for sampleIdx in range(nSamples):
                audioData[channel, sampleIdx], = struct.unpack("<H", audioBytes[idx * 2: idx * 2 + 2])
                idx += 1
        timestamp = dt.datetime.fromtimestamp(timestamp_ms / 1e3)
        return E4E_Data_Audio_raw16(audioData, uuid.UUID(bytes=srcUUID), uuid.UUID(bytes=destUUID), timestamp)


class E4E_Data_Raw_File_Header(binaryPacket):
    __class = 0x04
    __id = 0xFC
    __VERSION = 0x01

    def __init__(self, fileID: int, filename: str, MIMEType: str, fileSize: int, fileTime: dt.datetime, src: uuid.UUID,
                 dest: uuid.UUID):
        self.fileID = fileID
        self.filename = filename
        self.mimeType = MIMEType
        self.fileSize = fileSize
        self.fileTime = fileTime
        payload = struct.pack("<BBHHQQ",
                              self.__VERSION,
                              fileID,
                              len(filename),
                              len(MIMEType),
                              fileSize,
                              int(fileTime.timestamp() * 1e3))
        payload += filename.encode('ascii')
        payload += MIMEType.encode('ascii')
        super(E4E_Data_Raw_File_Header, self).__init__(payload, self.__class, self.__id, src, dest)

    @classmethod
    def matches(cls, packetClass: int, packetID: int):
        return packetClass == self.__class and packetID == self.__id

    @classmethod
    def from_bytes(cls, packet: bytes):
        srcUUID, destUUID, pcls, pid, payload = cls.parseHeader(packet)
        ver, fileID, filenameLen, mimeTypeLen, fileSize, fileTimestamp = struct.unpack("<BBHHQQ", payload[0:0x16])
        filename = payload[0x16:0x16 + filenameLen].decode()
        mimeType = payload[0x16 + filenameLen:].decode()
        timestamp = dt.datetime.fromtimestamp(fileTimestamp / 1e3)
        return E4E_Data_Raw_File_Header(fileID, filename, mimeType, fileSize, timestamp, uuid.UUID(bytes=srcUUID),
                                        uuid.UUID(bytes=destUUID))


class E4E_Data_Raw_File_CTS(binaryPacket):
    __class = 0x04
    __id = 0xFD
    __VERSION = 0x01

    def __init__(self, fileID: int, ack: bool, src: uuid.UUID, dest: uuid.UUID):
        self.fileID = fileID
        self.ack = ack
        payload = struct.pack("<BBB", self.__VERSION, fileID, int(ack))
        super(E4E_Data_Raw_File_CTS, self).__init__(payload, self.__class, self.__id, src, dest)

    @classmethod
    def matches(cls, packetClass: int, packetID: int):
        return packetClass == self.__class and packetID == self.__id

    @classmethod
    def from_bytes(cls, packet: bytes):
        srcUUID, destUUID, pcls, pid, payload = cls.parseHeader(packet)
        fileID = payload[1]
        if payload[2] == 1:
            ack = True
        else:
            ack = False
        return E4E_Data_Raw_File_CTS(fileID, ack, uuid.UUID(bytes=srcUUID), uuid.UUID(bytes=destUUID))


class E4E_Data_Raw_File_ACK(binaryPacket):
    __class = 0x04
    __id = 0xFE
    __VERSION = 0x01

    def __init__(self, fileID: int, seq: int, ack: bool, src: uuid.UUID, dest: uuid.UUID):
        self.fileID = fileID
        self.seq = seq
        self.ack = ack
        payload = struct.pack("<BBHB", self.__VERSION, fileID, seq, int(ack))
        super(E4E_Data_Raw_File_ACK, self).__init__(payload, self.__class, self.__id, src, dest)

    @classmethod
    def matches(cls, packetClass: int, packetID: int):
        return packetClass == self.__class and packetID == self.__id

    @classmethod
    def from_bytes(cls, packet: bytes):
        srcUUID, destUUID, pcls, pid, payload = cls.parseHeader(packet)
        ver, fileID, seq, ackInt = struct.unpack("<BBHB", payload)
        if ackInt == 1:
            ack = True
        else:
            ack = False
        return E4E_Data_Raw_File_ACK(fileID, seq, ack, uuid.UUID(bytes=srcUUID), uuid.UUID(bytes=destUUID))


class E4E_Data_Raw_File(binaryPacket):
    __class = 0x04
    __id = 0xFF
    __VERSION = 0x01

    def __init__(self, fileID: int, seq: int, blob: bytes, src: uuid.UUID, dest: uuid.UUID):
        self.fileID = fileID
        self.seq = seq
        self.blob = blob
        payload = struct.pack("<BBHQ", self.__VERSION, fileID, seq, len(blob))
        payload += blob
        super(E4E_Data_Raw_File, self).__init__(payload, self.__class, self.__id, src, dest)

    @classmethod
    def matches(cls, packetClass: int, packetID: int):
        return packetClass == self.__class and packetID == self.__id

    @classmethod
    def from_bytes(cls, packet: bytes):
        srcUUID, destUUID, pcls, pid, payload = cls.parseHeader(packet)
        ver, fileID, seq, blobLen = struct.unpack("<BBHQ", payload[0:0x0C])
        blob = payload[0x0C:0x0C + blobLen]
        return E4E_Data_Raw_File(fileID, seq, blob, uuid.UUID(bytes=srcUUID), uuid.UUID(bytes=destUUID))


class binaryPacketParser:
    class State(enum.Enum):
        FIND_SYNC1 = 0
        FIND_SYNC2 = 1
        HEADER = 2
        HEADER_CKSUM = 3
        HEADER_VALIDATE = 4
        PAYLOAD = 5
        CKSUM = 6
        VALIDATE = 7
        RECYCLE = 8

    packetMap = {
        0x0400: E4E_Data_IMU,
        0x0401: E4E_Data_Audio_raw8,
        0x0402: E4E_Data_Audio_raw16,
        0x04FC: E4E_Data_Raw_File_Header,
        0x04FD: E4E_Data_Raw_File_CTS,
        0x04FE: E4E_Data_Raw_File_ACK,
        0x04FF: E4E_Data_Raw_File
    }

    HEADER_LEN = 0x0026

    def __init__(self):
        self.__state = self.State.FIND_SYNC1
        self.__payloadLen = 0
        self.__buffer = None
        self.__data = queue.Queue()

    def parseByte(self, data: int):
        self.__data.put(data)
        while not self.__data.empty():
            retval = self._parseByte()
        return retval

    def _parseByte(self):
        data = self.__data.get_nowait()
#         print("%s: 0x%02x" % (self.__state, data))
        if self.__state is self.State.FIND_SYNC1:
            if data == 0xE4:
                self.__state = self.State.FIND_SYNC2
                self.__buffer = bytearray()
                self.__buffer.append(data)
            return None
        elif self.__state is self.State.FIND_SYNC2:
            if data == 0xEB:
                self.__state = self.State.HEADER
                self.__buffer.append(data)
            else:
                self.__state = self.State.FIND_SYNC1
            return None
        elif self.__state is self.State.HEADER:
            self.__buffer.append(data)
            if len(self.__buffer) == self.HEADER_LEN:
                self.__state = self.State.HEADER_CKSUM
                self.__payloadLen, = struct.unpack('<H', self.__buffer[self.HEADER_LEN - 2:self.HEADER_LEN])
            return None
        elif self.__state is self.State.HEADER_CKSUM:
            self.__buffer.append(data)
            self.__state = self.State.HEADER_VALIDATE
        elif self.__state is self.State.HEADER_VALIDATE:
            self.__buffer.append(data)
            if binascii.crc_hqx(self.__buffer, 0xFFFF) != 0:
                #                 print(self.__buffer.hex())
                #                 print(binascii.crc_hqx(self.__buffer, 0xFFFF).to_bytes(2, "big").hex())
                #                 print("Invalid header")
                # Recycle everything
                self.__state = self.State.FIND_SYNC1
                self.__recycleBuffer = self.__buffer[2:]
                while not self.__data.empty():
                    self.__recycleBuffer.append(self.__data.get_nowait())
                for byte in self.__recycleBuffer:
                    self.__data.put(byte)
            else:
                self.__state = self.State.PAYLOAD
            return None
        elif self.__state is self.State.PAYLOAD:
            self.__buffer.append(data)
            if len(self.__buffer) == self.__payloadLen + self.HEADER_LEN + 2:
                self.__state = self.State.CKSUM
            return None
        elif self.__state is self.State.CKSUM:
            self.__buffer.append(data)
            self.__state = self.State.VALIDATE
            return None
        elif self.__state is self.State.VALIDATE:
            self.__buffer.append(data)
            if binascii.crc_hqx(self.__buffer, 0xFFFF) != 0:
                #                 print(self.__buffer.hex())
                #                 print(binascii.crc_hqx(self.__buffer, 0xFFFF).to_bytes(2, "big").hex())
                raise RuntimeError("Checksum verification failed")
            packetID, = struct.unpack('>H', self.__buffer[0x0022:0x0024])
            self.__state = self.State.FIND_SYNC1
            if packetID not in self.packetMap:
                return binaryPacket.from_bytes(self.__buffer)
            else:
                return self.packetMap[packetID].from_bytes(self.__buffer)

    def parseBytes(self, data: bytes):
        packets = []
        for byte in data:
            self.__data.put(byte)
        while not self.__data.empty():
            retval = self._parseByte()
            if retval is not None:
                  packets.append(retval)
        return packets

if __name__ == '__main__':
#def bestfunction():
    ser = None 
    ser = serial.Serial('/dev/ttyACM0', 9600)
    ser.flush()

    while(True):
        t_end = time.time() + 86400
        now = dt.datetime.now().strftime('%Y-%m-%d-%H-%M')
        csvname = 'IMUaudio'+ now + '.csv'
             
        with open(csvname,'w') as csvFile:
            while time.time() < t_end:
                timestamp = dt.datetime.now()
                csvFile.write(str(timestamp)+'\n')

                parser = binaryPacketParser()
                packets = parser.parseBytes(ser.read(88))
                csvFile.write(str(packets)+'\n\n') 

                packets = parser.parseBytes(ser.read(1078))
                csvFile.write(str(packets)+'\n\n')
