#include <PDM.h>
#include <Arduino_LSM9DS1.h>

short sampleBuffer[256];
volatile int samplesRead;


void setup() {
	Serial.begin(9600);
	while(!Serial);
	PDM.onReceive(onPDMdata);

	if(!PDM.begin(1, 16000)) {
		Serial.print("Failed to start PDM");
		while(1);
	}
	
	IMU.begin();
}

void loop() {
	float accx, accy, accz, gyrx, gyry, gyrz;
	if (IMU.accelerationAvailable()) {
		IMU.readAcceleration(accx, accy, accz);
		byte *ax = (byte*) &accx;
		byte *ay = (byte*) &accy;
		byte *az = (byte*) &accz;
		Serial.write(ax, 4);
		Serial.write(ay, 4);
		Serial.write(az, 4);
	}

	if (IMU.gyroscopeAvailable()) {
		IMU.readGyroscope(gyrx, gyry, gyrz);
		byte *gx = (byte*) &gyrx;
		byte *gy = (byte*) &gyry;
		byte *gz = (byte*) &gyrz;
		Serial.write(gx, 4);
		Serial.write(gy, 4);
		Serial.write(gz, 4);
	}
	
	if(samplesRead) {
		for(int j = 0; j < samplesRead; j++) {
			byte *mic = (byte*) &sampleBuffer[j];
			Serial.write(mic, sizeof(samplesRead));
		}
	}
	samplesRead = 0;
}

void onPDMdata() {
	int bytesAvailable = PDM.available();
	PDM.read(sampleBuffer, bytesAvailable);
	samplesRead = bytesAvailable / 2;
} 
