// Caltech ME72 2024
// Wayne Botzky

#include <Wire.h>
#include <SoftwareSerial.h>
#include "RoboClaw.h"

//See limitations of Arduino SoftwareSerial
SoftwareSerial serial(10, 11);
RoboClaw roboclaw(&serial, 10000);

#define address 0x80


void setup() {
  // Join I2C bus as slave with address 8
  Wire.begin(0x8);

  // Call receiveEvent when data received
  Wire.onReceive(receiveEvent);

  roboclaw.begin(38400);
  roboclaw.ForwardM1(address, 0);
  roboclaw.ForwardM2(address, 0);
  Serial.begin(9600);
}

// Function that executes whenever data is received from master
void receiveEvent(int howMany) {
  while (Wire.available()) {  // loop through all but the last
    char c = Wire.read();     // receive byte as a character

    // Check if the value is a hexadecimal number greater than 0x1000
    unsigned int value = (unsigned int)c;
    Serial.println(value);
    // MOTOR ONE FORWARD
    if (value < 1000) { roboclaw.ForwardM1(address, value); }     
    // MOTOR ONE REVERSE
    else if (value = 65508) { roboclaw.BackwardM1(address, 20); }

    // MOTOR OTWONE REVERSE
    else if (value = 65532) { roboclaw.ForwardM2(address, 20); }
    else if (value = 65484) { roboclaw.BackwardM2(address, 20); }
    
    else if (value = 65512) { roboclaw.BackwardM2(address, 0); }

    
    // MOTOR ONE STOP --> send 64

    // MOTOR TWO FORWARD
    //else if (1000 < value && value < 2000){ roboclaw.ForwardM2(address, value - 1000); }

   // MOTOR TWO STOP
    //else if (value = 1000) { roboclaw.ForwardM2(address, 192); }

    // MOTOR TWO REVERSE
    //else if (3000 <= value && value < 4000){ roboclaw.ForwardM2(address, -(value - 3000)); }
  }
}
void loop() {
  delay(100);
}