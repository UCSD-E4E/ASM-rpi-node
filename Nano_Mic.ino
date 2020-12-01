#include <PDM.h>

short sampleBuffer[256];
volatile int samplesRead;

void setup() {
	Serial.begin(9600);
	if (!PDM.begin(1, 16000)) {
		Serial.print("Failed to start PDM");
		while(1);
	}
	
}

void loop() {
	int bytesAvailable = PDM.available();
	int bytesRead = PDM.read(sampleBuffer, bytesAvailable);
	for (int i =0; i < 256; i++) {
		Serial.print(sampleBuffer[i], 6);
		Serial.print(i == 256 -1 ? '\n' : ',');
	}
	samplesRead = bytesRead / 2; //16-bit, 2 bytes per sample
	PDM.end();
}
