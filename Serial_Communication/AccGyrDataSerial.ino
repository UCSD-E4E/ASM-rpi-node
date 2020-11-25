#include <Arduino_LSM9DS1.h>
void setup() {
	Serial.begin(9600);
	IMU.begin();
}

void loop() {
	float acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z;
	if (IMU.accelerationAvailable()) {
		IMU.readAcceleration(acc_x, acc_y, acc_z);
		Serial.print("Accelerometer sample rate = ");
		Serial.print(IMU.accelerationSampleRate());
		Serial.println("Acc_x = ");
		Serial.println(acc_x);
		Serial.println("Acc_y = ");
		Serial.println(acc_y);
		Serial.println("Acc_z = ");
		Serial.println(acc_z);
	}

	if (IMU.gyroscopeAvailable()) {
		IMU.readGyroscope(gyr_x, gyr_y, gyr_z);
		Serial.print("Gyrosccope sample rate = ");
		Serial.print(IMU.gyroscopeSampleRate());
		Serial.println("Gyr_x = ");
		Serial.println(gyr_x);
		Serial.println("Gyr_y = ");
		Serial.println(gyr_y);
		Serial.println("Gyr_z = ");
		Serial.println(gyr_z);
	}
}
