#define POLY 0x1021
#include <stdlib.h>
#include <PDM.h>
#include<string.h>

volatile uint8_t data_circle[1025];
typedef struct circ_bbuf_
{
  volatile uint8_t *buffer; //constant pointer to an array of bytes in which the value being pointed to can change but not the pointer (1024 bytes+1 flag)
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
   uint8_t databuff[1024];  //holds bytes not samples 
}AudioDataInput_t;

typedef struct __attribute__((packed)) AudioDataPacket_
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


int circ_buff_push(circ_bbuf_t *c, uint8_t data)
{  
  volatile int next;
  next = (c->head) + 1; 			//next is where the head will point to after this write
 
 /** Serial.print("next:");
  Serial.print("\t");

  Serial.println(next);
  Serial.print("INEQUALITY:");
  Serial.print("\t");
  Serial.println(next >= c->maxlen);**/
  if (next >= c->maxlen)
  {
      next = 0;
  }

//  if (next == c->tail)
//  { 			//if the head +1 == tail, circular buffer is full
//	return -1;
//  }

  c -> buffer[c->head] = data; 		//load data and then move
  c -> head = next;
  return 0; 				//return success to indiciate successful push
}

int circ_buff_pop(circ_bbuf_t *c, uint8_t *data)
{
 // Serial.println("ENTERED THE POP FUNC BBY");

  int next;

  if(c->head == c->tail) 
  {
  Serial.print("HEAD:"); 
  Serial.print("\t");
  Serial.println(c->head);		//HEAD IS ALWAYS CHANGING B/C ISR CALLED ANYTIME

  Serial.print("TAIL");
  Serial.print("\t");
  Serial.println(c->tail);
  Serial.println("**********************");
      return -1;
 }

// int next;
//  if (c->head == c->tail) 		//if the head == tail, we don't have any data
//      return -1;
  next = c->tail +1; 			//next is where tail will point to after this read
  if(next >= c->maxlen)
      {next = 0;}
  *data = c->buffer[c->tail]; 		//read data and then move
  c -> tail = next; 			//tail to next offset
  return 0;	 			//return success to indiciate successful push 
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

void setup() {
  setcirclebuff(&circlebuff);
  Serial.begin(9600);
  while(!Serial);

  PDM.setBufferSize(1024);
  PDM.onReceive(onPDMdata);
  if(!PDM.begin(1,16000)) 
  {
     Serial.println("failed");
      while(1);
  }
}

#define SER_BLOCK_DELAY_MS 10
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

/**    for(int i = 0; i < 1024; i++) 
     {
     	if(circ_buff_push(&circlebuff,sampleBuffer[i])) 
	{
		pushcheck =  -1;
	}
     }
     circle_buff_check = 1;
Serial.println("DONE DONE DONE");**/

//Serial.println(circlebuff.head);
//Serial.println(circlebuff.tail);
//Serial.println(pushcheck);

if (pushcheck == -1) 
{
     Serial.print("fat error"); 
}

if (circle_buff_check == 1 && pushcheck == 0) 
{
    for(int j = 0; j<1024; j++) 
    {
       int popcheck = circ_buff_pop(&circlebuff, &Audiosensor_packet.audpayload.databuff[j]);
      //IN THIS BLOCK BELOW, THE IF STATEMENT WOULD BE TRIGGERED, BUT WHEN I PRINT OUT THE VALUES OF 
      //HEAD AND TAIL IN CIRCLEBUFF, THEY AREN'T EQUAL? CHECK PRINT STATEMENTS IN POP FUNCTION.
      //FOR NOW, THIS CODE WORKS AS IF, NOT SURE ABT THE IF STATEMENT BELOW THO?
      // if(circ_buff_pop(&circlebuff,&Audiosensor_packet.audpayload.databuff[j])); 
      // {
      //	  Serial.println("fat error #2"); //circlebuffer was empty
      // }
       if(popcheck == -1)
       {
           Serial.println("faterror#2");
           break;
       }
    }

 genAudiopayload(&Audiosensor_packet);
 setAudioHeader(&Audiosensor_packet);
 encodeAudioSensorPacket(&Audiosensor_packet);
 putBlock(&Audiosensor_packet, sizeof(Audiosensor_packet));
}
circle_buff_check = 0;
delay(100);
}

void onPDMdata() {
     pushcheck = 0;
     uint8_t sampleBuffer[1024];
     int bytesAvailable = PDM.available();
     PDM.read(sampleBuffer, bytesAvailable);

     for(int i = 0; i < 1024; i++) 
     {
     	if(circ_buff_push(&circlebuff,sampleBuffer[i])) 
	{
		pushcheck =  -1;
	}
     }
     circle_buff_check = 1;
}
