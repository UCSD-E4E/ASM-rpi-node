#define POLY 0x1021
#include <Arduino_LSM9DS1.h>
#include <PDM.h>
#include <stdlib.h>
#include <string.h>

volatile uint8_t data_circle[1025];
typedef struct circ_bbuf_
{
  volatile uint8_t *buffer;
  volatile int head;
  volatile int tail;
  volatile int maxlen; 
} circ_bbuf_t;

typedef struct __attribute__((packed)) AudioDataInput_
{
  uint8_t audversion;
  uint8_t num_channels;
  uint16_t samplesperchann;
  uint64_t audtime;
  uint8_t databuff[1024];
}AudioDataInput_t;

typedef struct __attribute__ ((packed)) AudioDataPacket_
{
  uint8_t audsync_char1;
  uint8_t audsync_char2;
  uint8_t audsourceUUID[16];
  uint8_t audtargetUUID[16];
  uint8_t audpacket_class;
  uint8_t audpacket_id;
  uint16_t audpayload_length;
  uint16_t audhead_check;
  AudioDataInput_t audpayload;
  uint16_t audchecksum;
} AudioDataPacket_t;


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

int circ_buff_push(circ_bbuf_t *c, uint8_t data)
{
  volatile int next;
  next = c->head + 1;
 	
  if (next >= c->maxlen)
      next = 0;
  if (next == c->tail) 			
      return -1;
  c -> buffer[c->head] = data; 		
  c -> head = next;
  return 0; 				
}

int circ_buff_pop(circ_bbuf_t *c, uint8_t *data)
{
//  Serial.println("ENTERED THE POP FUNC BBY");

  int next;
  if(c->head == c->tail) 
  {
  Serial.print("HEAD:"); 
  Serial.print("\t");
  Serial.println(c->head);		

  Serial.print("TAIL");
  Serial.print("\t");
  Serial.println(c->tail);
  Serial.println("**********************");
  return -1;
 }

// int next;
//  if (c->head == c->tail) 		
//      return -1;
  next = c->tail +1; 			
  if(next >= c->maxlen)
  {
     next = 0;
  }
  *data = c->buffer[c->tail]; 		
  c -> tail = next; 			
  return 0;
}

void genAudiopayload(AudioDataPacket_t* audpacket) 
{
  audpacket -> audpayload.audversion = 0x01;
  audpacket -> audpayload.num_channels = 2;
  audpacket -> audpayload.samplesperchann = 256;
  audpacket -> audpayload.audtime = 0;
}

void setAudioHeader(AudioDataPacket_t* audiopacket)
{
  audiopacket->audsync_char1 = 0xE4;
  audiopacket->audsync_char2 = 0xEB;
  for (int i =0; i< 16; i++) {
      audiopacket ->audsourceUUID[i] = 0;
      audiopacket ->audtargetUUID[i] = 0;
    }
 
  audiopacket->audpacket_class = 0x04;
  audiopacket->audpacket_id = 0x02;
  audiopacket->audpayload_length = 1036;
}

//Get readings from sensors into the packet structure (generate the payload)
int genIMUpayload(IMUDataPacket_t* packet)
{
     float ax, ay, az, gx, gy, gz, mx, my, mz;
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
     }

     
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

uint32_t encodeAudioSensorPacket(AudioDataPacket_t* audiodata)
{
    uint16_t crc, headcrc;
    uint8_t *pByte, *pCksum;
    headcrc = crc16((uint8_t*)audiodata, 38); 
    pCksum = (uint8_t*) &headcrc;
    pByte = (uint8_t*) &audiodata->audhead_check;
    pByte[0] = pCksum[1];
    pByte[1] = pCksum[0];
   
    crc = crc16((uint8_t*)audiodata, sizeof(AudioDataPacket_t)-2);
    pCksum = (uint8_t*) &crc;
    pByte = (uint8_t*) &audiodata->audchecksum;
    pByte[0] = pCksum[1];
    pByte[1] = pCksum[0];
}

void setcirclebuff (circ_bbuf_t* c) 
{
   c->buffer = data_circle;
   c->head = 0;
   c->tail = 0;
   c->maxlen = 1025;
}

AudioDataPacket_t Audiosensor_packet;
circ_bbuf_t circlebuff;
IMUDataPacket_t IMUsensor_packet;

void setup() {
  setcirclebuff(&circlebuff);
  Serial.begin(9600);
  while(!Serial);

  IMU.begin();
  PDM.setBufferSize(1024);
  PDM.onReceive(onPDMdata);
  if(!PDM.begin(1,16000))
  {
     Serial.println("failed");
     while(1);
  }
}

#define SER_BLOCK_DELAY_MS  10
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


volatile int circle_buff_check = 0;
volatile int pushcheck = 0;

void loop() 
{
  memset(&IMUsensor_packet, 0, 88);
  genIMUpayload(&IMUsensor_packet);
  setIMUHeader(&IMUsensor_packet);
  encodeIMUSensorPacket(&IMUsensor_packet);
  putBlock(&IMUsensor_packet,sizeof(IMUsensor_packet));
  delay(2000);

if (pushcheck == -1) 
  {
      while(1) 
      {Serial.print("Error from Push Function");} 
  }

  if (circle_buff_check == 1 && pushcheck == 0) 
  {
      for(int j = 0; j<1024; j++) 
      {
         int popcheck = circ_buff_pop(&circlebuff, &Audiosensor_packet.audpayload.databuff[j]); 
         if(popcheck == -1)
         {
	     while(1) 
             {
             Serial.println("Error in Pop Function");
             }
         }
      }

    genAudiopayload(&Audiosensor_packet);
    setAudioHeader(&Audiosensor_packet);
    encodeAudioSensorPacket(&Audiosensor_packet);
    putBlock(&Audiosensor_packet, sizeof(Audiosensor_packet));
  }
  else
  {
        while(1) {
	Serial.print("Error in Push or Pop");}
  }
  circle_buff_check = 0;
  delay(2000);
}

void onPDMdata() {
     circle_buff_check = 0;
     pushcheck = 0;
     uint8_t sampleBuffer[1024];
     int bytesAvailable = PDM.available();
     PDM.read(sampleBuffer, bytesAvailable);

    for(int i = 0; i < 1024; i++) 
     {
     	if(circ_buff_push(&circlebuff, sampleBuffer[i])) 
	{
//		pushcheck =  -1;
	}
     }
     circle_buff_check = 1;
} 
  
 
