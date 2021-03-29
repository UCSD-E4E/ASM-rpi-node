#define POLY 0x1021
#include <time.h>
#include <Arduino_LSM9DS1.h>
#include <stdlib.h>

typedef struct __attribute__((packed)) IMUDataInput_ 
{ 
  uint8_t version1;
  uint8_t reserved;
  uint64_t time1;
  float accx;
  float accy;
  float accz;
  float gyrx;
  float gyry;
  float gyrz; 
  float magx;
  float magy;
  float magz;
} IMUDataInput_t;

typedef struct __attribute__((packed)) IMUDataPacket_ 
{ 
  uint8_t sync_char1;
  uint8_t sync_char2;
  uint8_t sourceUUID[16];
  uint8_t targetUUID[16];
  uint8_t packet_class;
  uint8_t packet_id;
  uint16_t payload_length;
  uint16_t head_check;
  IMUDataInput_t payload;
  uint16_t checksum;
} IMUDataPacket_t; 

//Get readings from sensors into the packet structure (generate the payload)
int genIMUpayload(IMUDataPacket_t* packet)
{
     /**float ax, ay, az, gx, gy, gz, mx, my, mz;
     if(IMU.accelerationAvailable())
     {
        IMU.readAcceleration(ax,ay,az);
        packet -> payload.accx = ax*9.80665;
        packet -> payload.accy = ay*9.80665;
        packet -> payload.accz = az*9.80665;
     }
     else
     {
	return 0;
     }

     if(IMU.gyroscopeAvailable())
     {
        IMU.readGyroscope(gx,gy,gz);
	packet -> payload.gyrx = gx*(PI/180);
        packet -> payload.gyry = gy*(PI/180);
        packet -> payload.gyrz = gz*(PI/180);
     }
     else
     {
	return 0;
     }

     if(IMU.magneticFieldAvailable())
     {
        IMU.readMagneticField(mx,my,mz);
	 packet -> payload.magx = mx;
         packet -> payload.magy = my;
         packet -> payload.magz = mz;
     }
     else
     {
	return 0;
     }**/

 packet -> payload.accx = 1;
 packet -> payload.accy = 2;
 packet -> payload.accz = 3;
 packet -> payload.gyrx = 4;
 packet -> payload.gyry = 5;
 packet -> payload.gyrz = 6;
 packet -> payload.magx = 7;
 packet -> payload.magy = 8;
 packet -> payload.magz = 9;

  packet -> payload.version1 = 0x01;
  packet -> payload.reserved = 0x00;
  packet -> payload.time1 = 0;
}

void setIMUHeader(IMUDataPacket_t* packet)
{
    packet->sync_char1 = 0xE4;
    packet->sync_char2 = 0xEB;
    for (int i =0; i< 16; i++) 
    {
      packet ->sourceUUID[i] = 0;
      packet ->targetUUID[i] = 0;
    }
    packet->packet_class = 0x04;
    packet->packet_id = 0x00;
    packet->payload_length = 46;
}

uint16_t crc16(uint8_t *buffer1, uint32_t len) 
{
    uint32_t i, j;
    uint16_t crc = 0xFFFF;
    for (j = 0; j < len; j++)
    {
        uint8_t next_byte = buffer1[j];
        for (i = 0; i < 8; i++)
        {
            if (((crc & 0x8000) >> 8) ^ (next_byte & 0x80))
            {
                crc = (crc << 1) ^ POLY;
            }
            else
            {
                crc = (crc << 1);
            }
            next_byte <<= 1;
        }
    }
    return crc;
}

uint32_t encodeIMUSensorPacket(IMUDataPacket_t* data)
{
    uint16_t crc, headcrc;
    uint8_t *pByte, *pCksum;
    headcrc = crc16((uint8_t*)data,38); 
    pCksum = (uint8_t*) &headcrc;
    pByte = (uint8_t*) &data->head_check;
    pByte[0] = pCksum[1];
    pByte[1] = pCksum[0];

    crc = crc16((uint8_t*)data, sizeof(IMUDataPacket_t)-2);
    pCksum = (uint8_t*) &crc;
    pByte = (uint8_t*) &data->checksum;
    pByte[0] = pCksum[1];
    pByte[1] = pCksum[0];
} 

IMUDataPacket_t IMUsensor_packet;

void setup() {
  Serial.begin(9600);
  while(!Serial);

  IMU.begin();

}
/**
 * Set this number of milliseconds to wait for buffer to open up
 */
 #define SER_BLOCK_DELAY_MS 10
 /**
  * puts nBytes from pData into Serial w/ block delays to faciliate big writes
  * 
  * @param pData Pointer to the data to write
  * @param nBytes number of bytes to write
  * @return number of bytes written
  */

uint32_t putBlock(void* pData, uint32_t nBytes)
{
  size_t bufferLen;
  size_t bytesToWrite;
  size_t bytesRemaining = nBytes;
  uint8_t* pBytes = (uint8_t*) pData;

  while(bytesRemaining > 0) 
  {
    bufferLen = 16;
    bytesToWrite = bytesRemaining > bufferLen ? bufferLen: bytesRemaining;
    Serial.write(pBytes, bytesToWrite);
    pBytes += bytesToWrite;
    bytesRemaining -= bytesToWrite;
    delay(SER_BLOCK_DELAY_MS);
  }
  return nBytes;
}

//IMUDataPacket_t* pPacket = &IMUsensor_packet;
void loop() {
  
  memset(&IMUsensor_packet, 0, 88);
  genIMUpayload(&IMUsensor_packet);
  setIMUHeader(&IMUsensor_packet);
  encodeIMUSensorPacket(&IMUsensor_packet);
  putBlock(&IMUsensor_packet,sizeof(IMUsensor_packet));
  delay(3000);


  /**Serial.println("sync chars:    ");
  Serial.println(pPacket->sync_char1);
  Serial.println(pPacket->sync_char2);
  Serial.println("UUIDs:    ");
  for(int i = 0; i<16; i++) {
     Serial.print(i);
     Serial.println(pPacket->sourceUUID[i]);
     Serial.println(pPacket->targetUUID[i]);
  }
  Serial.println("Class, ID, Length, Headcheck:    ");
  Serial.println(pPacket->packet_class); //04
  Serial.println(pPacket->packet_id);    //00
  Serial.println(pPacket->payload_length);  //2E
  Serial.println(pPacket->head_check);     
  Serial.println("Version, reserved, time:    ");
  Serial.println(pPacket->payload.version1);
  Serial.println(pPacket->payload.reserved);
  Serial.println(pPacket->payload.time1);
  Serial.println("Acc, mag, gyr:    ");
  Serial.println(pPacket->payload.accx);
  Serial.println(pPacket->payload.accy);
  Serial.println(pPacket->payload.accz);
  Serial.println(pPacket->payload.magx);
  Serial.println(pPacket->payload.magy);
  Serial.println(pPacket->payload.magz);
  Serial.println(pPacket->payload.gyrx);
  Serial.println(pPacket->payload.gyry);
  Serial.println(pPacket->payload.gyrz);
  Serial.println(pPacket->checksum);**/
} 

