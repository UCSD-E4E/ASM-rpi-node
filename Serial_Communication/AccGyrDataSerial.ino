#include <Arduino_LSM9DS1.h>

struct IMUdata {
	float acc_x;
	float acc_y;
	float acc_z;
	float gyr_x:
	float gyr_y;
	float gyr_z;
};

IMUdata IMUdata;

void setup() {
	Serial.begin(9600);
	IMU.begin();
}

void loop() {
	if (IMU.accelerationAvailable()) {
		IMU.readAcceleration(IMUdata.acc_x, IMUdata.acc_y, IMUdata.acc_z); //this writes to the struct 
		//Serial.print("Accelerometer sample rate = ");
		//Serial.print(IMU.accelerationSampleRate());
		Serial.println("Acc_x = ");
		Serial.println(IMUdata.acc_x);
		Serial.println("Acc_y = ");
		Serial.println(IMUdata.acc_y);
		Serial.println("Acc_z = ");
		Serial.println(IMUdata.acc_z);
	}

	if (IMU.gyroscopeAvailable()) {
		IMU.readGyroscope(IMUdata.gyr_x, IMUdata.gyr_y, IMUdata.gyr_z); //writes to the struct
		//Serial.print("Gyrosccope sample rate = ");
		//Serial.print(IMU.gyroscopeSampleRate());
		Serial.println("Gyr_x = ");
		Serial.println(IMUdata.gyr_x);
		Serial.println("Gyr_y = ");
		Serial.println(IMUdata.gyr_y);
		Serial.println("Gyr_z = ");
		Serial.println(IMUdata.gyr_z);
	}
}
