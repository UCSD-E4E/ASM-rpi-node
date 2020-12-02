#include <PDM.h>
#include <Arduino_LSM9DS1.h>

short sampleBuffer[256];
volatile int samplesRead;

struct IMUdata {
	float acc_x;
	float acc_y;
	float acc_z;
	float gyr_x;
	float gyr_y;
	float gyr_z;
}IMUdata;


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
	if(samplesRead) {
		for(int i = 0; i < samplesRead; i++) {
			Serial.write(sampleBuffer[i]);
		}
		samplesRead = 0;
	}

	if (IMU.accelerationAvailable()) {
		IMU.readAcceleration(IMUdata.acc_x, IMUdata.acc_y, IMUdata.acc_z);
		Serial.write(IMUdata.acc_x);
		Serial.write(IMUdata.acc_y);
		Serial.write(IMUdata.acc_z);
	}

	if (IMU.gyroscopeAvailable()) {
		IMU.readGyroscope(IMUdata.gyr_x, IMUdata.gyr_y, IMUdata.gyr_z);
		Serial.write(IMUdata.gyr_x);
		Serial.write(IMUdata.gyr_y);
		Serial.write(IMUdata.gyr_z);
	}

	delay(9900000000000);
}

void onPDMdata() {
	int bytesAvailable = PDM.available();
	PDM.read(sampleBuffer, bytesAvailable);
	samplesRead = bytesAvailable / 2;
} 
