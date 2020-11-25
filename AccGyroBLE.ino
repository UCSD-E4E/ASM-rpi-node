#include "Arduino.h"
#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

#define BLE_BUFFER_SIZES	20
#define BLE_DEVICE_NAME 	"Arduino Nano 33 BLE Sense"
#define BLE_LOCAL_NAME		"Gyrosccope BLE"


BLEService BLEGyroscope("590d65c7-3a0a-4023-a05a-6aaf2f22441c");
BLEUnsignedCharCharacteristic gyroscopeXBLE("0004", BLERead | BLENotify);
BLEUnsignedCharCharacteristic gyroscopeYBLE("0005", BLERead | BLENotify);
BLEUnsignedCharCharacteristic gyroscopeZBLE("0006", BLERead | BLENotify);

void setup() {
	Serial.begin(115200);
	while(!Serial);
	Serial.print("Arduino is awake");

	if(!BLE.begin()) {
		while(1);
	}

	BLE.setLocalName(BLE_LOCAL_NAME);
	BLE.setAdvertisedService(BLEGyroscope);

	BLEGyroscope.addCharacteristic(gyroscopeXBLE);
	BLEGyroscope.addCharacteristic(gyroscopeYBLE);
	BLEGyroscope.addCharacteristic(gyroscopeZBLE);
		
	BLE.addService(BLEGyroscope);
	BLE.advertise();
	Serial.print("Advertising...");

	IMU.begin();
}

void loop() {
	BLEDevice central = BLE.central();
	if(central) {
		float x,y,z;

		if(central)  {
			Serial.print("Central connected.");
			
			while(central.connected()) {
				if(IMU.gyroscopeAvailable()) {
					IMU.readGyroscope(x,y,z);
				//	gyroscopeXBLE.writeValue(x);
				//	gyroscopeYBLE.writeValue(y);
				//	gyroscopeZBLE.writeValue(z);
					gyroscopeXBLE.writeValue(1);
					gyroscopeYBLE.writeValue(2);
					gyroscopeZBLE.writeValue(3);
					
				//	Serial.print(gyroscopeXBLE);
				}
			}
		}
	}
}
