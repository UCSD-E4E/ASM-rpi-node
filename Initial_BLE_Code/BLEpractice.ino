#include <ArduinoBLE.h>

BLEService batteryService("1101");
BLEUnsignedCharCharacteristic batteryLevelChar("2102", BLERead | BLENotify);

void setup() {
	Serial.begin(9600);
	while (!Serial);

	if(!BLE.begin()){
		Serial.println("startiing BLE failed");
		while(1);
	}

	BLE.setLocalName("BatteryMonitor");
	BLE.setAdvertisedService(batteryService);
	batteryService.addCharacteristic(batteryLevelChar);
	BLE.addService(batteryService);

	BLE.advertise();
	Serial.println("Bluetooth active, waiting for connection");
}

void loop() {
	BLEDevice central = BLE.central();

	if(central) {
		Serial.print("connected to central: ");
		Serial.println(central.address());

		while(central.connected()){
			//int battery = analogRead(A0);
			//int batteryLevel = map(battery, 0, 1023, 0, 100);
			int batteryLevel = 69;
			//Serial.print ("Battery Level: ");
			Serial.println(batteryLevel);
			batteryLevelChar.writeValue(batteryLevel);
		}
	}
}
