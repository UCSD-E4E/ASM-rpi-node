#define POLY 0x1021
#include <stdlib.h>
#include <PDM.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>

uint8_t data_circle[64 * 1024];
typedef struct circ_bbuf_
{
  uint8_t *buffer; //constant pointer to an array of bytes in which the value being pointed to can change but not the pointer (1024 bytes+1 flag)
  int head;
  int tail;
  int maxlen;
} circ_bbuf_t;

#define CIRCULAR_BUFFER_LEN 64 * 1024
#define CIRCULAR_BUFFER_TYPE uint8_t
typedef struct CircularBuffer_
{
  CIRCULAR_BUFFER_TYPE data[CIRCULAR_BUFFER_LEN];
  size_t head;
  size_t tail;
  size_t len;
} CircularBuffer_t;

typedef struct __attribute__((packed)) AudioDataInput_
{
  uint8_t audversion;
  uint8_t num_channels;
  uint16_t samplesperchann;
  uint64_t audtime;
  uint8_t databuff[1024]; //holds bytes not samples
} AudioDataInput_t;

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

void CB_init(CircularBuffer_t *pDesc)
{
  pDesc->head = 0;
  pDesc->tail = 0;
  pDesc->len = CIRCULAR_BUFFER_LEN;
  memset(pDesc->data, 0, CIRCULAR_BUFFER_LEN * sizeof(CIRCULAR_BUFFER_TYPE));
}

size_t CB_count(CircularBuffer_t *pDesc)
{
  if (NULL == pDesc)
  {
    return 0;
  }
  return pDesc->head - pDesc->tail;
}

int CB_full(CircularBuffer_t *pDesc)
{
  if (NULL == pDesc)
  {
    return 0;
  }
  return ((pDesc->head - pDesc->tail) >= pDesc->len) ? 1 : 0;
}

int CB_empty(CircularBuffer_t *pDesc)
{
  if (NULL == pDesc)
  {
    return 0;
  }
  return ((pDesc->head - pDesc->tail) == 0) ? 1 : 0;
}

int CB_push(CircularBuffer_t *pDesc, CIRCULAR_BUFFER_TYPE byte)
{
  size_t headOffset;

  if (NULL == pDesc)
  {
    return 0;
  }

  if (1 == CB_full(pDesc))
  {
    return 0;
  }

  headOffset = pDesc->head & (pDesc->len - 1);
  pDesc->data[headOffset] = byte;
  pDesc->head += 1;
  return 1;
}

int CB_pop(CircularBuffer_t *pDesc, CIRCULAR_BUFFER_TYPE *pData, size_t nElem)
{
  size_t tailOffset;
  size_t bytesRight;
  if (NULL == pDesc)
  {
    return 0;
  }
  if (NULL == pData)
  {
    return 0;
  }
  if (nElem == 0)
  {
    return 1;
  }
  if (nElem > pDesc->len)
  {
    return 0;
  }
  if (1 == CB_empty(pDesc))
  {
    return 0;
  }

  tailOffset = pDesc->tail & (pDesc->len - 1);
  bytesRight = pDesc->len - tailOffset;
  if (nElem < bytesRight)
  {
    memcpy(pData, &pDesc->data[tailOffset], nElem * sizeof(CIRCULAR_BUFFER_TYPE));
    pDesc->tail += nElem;
  }
  else
  {
    memcpy(pData, &pDesc->data[tailOffset], bytesRight * sizeof(CIRCULAR_BUFFER_TYPE));
    memcpy(&pData[bytesRight], pDesc->data, (nElem - bytesRight) * sizeof(CIRCULAR_BUFFER_TYPE));
    pDesc->tail += nElem;
  }
  return 1;
}

int circ_buff_push(circ_bbuf_t *c, uint8_t data)
{
  volatile int next;
  next = c->head + 1; //next is where the head will point to after this write
  if (next >= c->maxlen)
    next = 0;
  if (next == c->tail) //if the head +1 == tail, circular buffer is full
    return -1;
  c->buffer[c->head] = data; //load data and then move
  c->head = next;
  return 0; //return success to indiciate successful push
}

int circ_buff_pop(circ_bbuf_t *c, uint8_t *data)
{
  int next;
  if (c->head == c->tail) //if the head == tail, we don't have any data
    return -1;
  next = c->tail + 1; //next is where tail will point to after this read
  if (next >= c->maxlen)
    next = 0;

  *data = c->buffer[c->tail]; //read data and then move
  c->tail = next;             //tail to next offset
  return 0;                   //return success to indiciate successful push
}

void genAudiopayload(AudioDataPacket_t *audpacket)
{
  audpacket->audpayload.audversion = 0x01;
  audpacket->audpayload.num_channels = 2;
  audpacket->audpayload.samplesperchann = 256;
  audpacket->audpayload.audtime = 0;
}

void setAudioHeader(AudioDataPacket_t *audiopacket)
{
  audiopacket->audsync_char1 = 0xE4;
  audiopacket->audsync_char2 = 0xEB;
  for (int i = 0; i < 16; i++)
  {
    audiopacket->audsourceUUID[i] = 0;
    audiopacket->audtargetUUID[i] = 0;
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

uint32_t encodeAudioSensorPacket(AudioDataPacket_t *audiodata)
{
  uint16_t crc, headcrc;
  uint8_t *pByte, *pCksum;
  headcrc = crc16((uint8_t *)audiodata, 38);
  pCksum = (uint8_t *)&headcrc;
  pByte = (uint8_t *)&audiodata->audhead_check;
  pByte[0] = pCksum[1];
  pByte[1] = pCksum[0];

  crc = crc16((uint8_t *)audiodata, sizeof(AudioDataPacket_t) - 2);
  pCksum = (uint8_t *)&crc;
  pByte = (uint8_t *)&audiodata->audchecksum;
  pByte[0] = pCksum[1];
  pByte[1] = pCksum[0];
}

void setcirclebuff(circ_bbuf_t *c)
{
  c->buffer = data_circle;
  c->head = 0;
  c->tail = 0;
  c->maxlen = 64*1024;
  memset(c->buffer, 0xAA, c->maxlen);
}

AudioDataPacket_t Audiosensor_packet;
circ_bbuf_t circlebuff;
CircularBuffer_t testBuffer, *pTestBuffer = &testBuffer;

void setup()
{
  setcirclebuff(&circlebuff);
  Serial.begin(9600);
  while (!Serial)
    ;

  PDM.setBufferSize(1024);
  PDM.onReceive(onPDMdata);
  if (!PDM.begin(1, 16000))
  {
    Serial.println("failed");
    while (1)
      ;
  }

  CB_init(pTestBuffer);
}

#define SER_BLOCK_DELAY_MS 10
uint32_t putBlock(void *pData, uint32_t nBytes)
{
  size_t bufferLen;
  size_t bytesToWrite;
  size_t bytesRemaining = nBytes;
  uint8_t *pBytes = (uint8_t *)pData;

  while (bytesRemaining > 0)
  {
    bufferLen = 16;
    bytesToWrite = bytesRemaining > bufferLen ? bufferLen : bytesRemaining;
    Serial.write(pBytes, bytesToWrite);
    pBytes += bytesToWrite;
    bytesRemaining -= bytesToWrite;
    delay(SER_BLOCK_DELAY_MS);
  }
  return nBytes;
}

volatile int circle_buff_check = 0;
/**
/equals -1 if push function had an error
/equals 1 if sampleBuffer fills successfully
**/

void loop()
{
  int nCounts;
  int i;
  CIRCULAR_BUFFER_TYPE nBytes;
  int retval;

  Serial.print("nCounts: ");
  nCounts = CB_count(pTestBuffer);
  Serial.print(nCounts);
  Serial.print("\r\n");

  i = 0;
  while(1)
  {
     Serial.print("Head: ");
     Serial.print(circlebuff.head);
     Serial.print(", Tail: ");
     Serial.print(circlebuff.tail);
    retval = circ_buff_pop(&circlebuff, &nBytes);
 //   Serial.print("Count ");
 //   Serial.print(i);
//    Serial.print(": ");
//    Serial.print(nBytes);
//    Serial.print("\r\n");
    i++;
    if(retval)
    {
      break;
    }
  }

  // for (i = 0; i < nCounts; i++)
  // {
  //   Serial.print("\tCount ");
  //   Serial.print(i);
  //   Serial.print(": ");
  //   CB_pop(pTestBuffer, &nBytes, 1);
  //   Serial.print(nBytes);
  //   Serial.print("\r\n");
  // }
  // for (int i = 0; i < 512; i++)
  // {
  //    Serial.println(circlebuff.buffer[i]);
  //   // Serial.println(sampleBuffer[i]);
  // }
  //This prints all 0s for buffer in the circlebuff, but if we move the push function here then there are values in circlebuff.

  // if (circle_buff_check == -1) //if the push function does not work
  // {
  //   Serial.print("fat error");
  //   ;
  // }

  // if (circle_buff_check == 1) //read out circle buff into packet
  // {
  //   for (int j = 0; j < 1024; j++)
  //   {
  //     if (circ_buff_pop(&circlebuff, &Audiosensor_packet.audpayload.databuff[j]))
  //       ; //returns 0 on success
  //     {
  //       Serial.print("fat error #2"); //circlebuffer was empty
  //     }
  //   }

  //   genAudiopayload(&Audiosensor_packet);
  //   setAudioHeader(&Audiosensor_packet);
  //   encodeAudioSensorPacket(&Audiosensor_packet);
  //   // putBlock(&Audiosensor_packet, sizeof(Audiosensor_packet));

  //   //for(int i = 0; i <1024; i++) {
  //   //    Serial.println(Audiosensor_packet.audpayload.databuff[i]);
  //   //    Serial.println(circlebuff.buffer[i]);}
  //   //	Serial.println(sampleBuffer[i]);
  // }

  // circle_buff_check = 0;
  delay(100);
}

void onPDMdata()
{
  uint8_t sampleBuffer[1024];
  int bytesAvailable = PDM.available();
  PDM.read(sampleBuffer, bytesAvailable);

  for (int i = 0; i < bytesAvailable & i < 1024; i++)
  {
    // if (circ_buff_push(&circlebuff, (uint8_t)sampleBuffer[i])) //returns 0 on success
    // {
    //   circle_buff_check = -1;
    // }
    CB_push(pTestBuffer, sampleBuffer[i]);
    circ_buff_push(&circlebuff, sampleBuffer[i]);
  }
  circle_buff_check = 1;
}
