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
    if (value < 1000) { // MOTOR ONE FORWARD
      roboclaw.ForwardM1(address, value);  // Start Motor1 forward with the specified speed
    } 
    
    else if (1000 < value && value < 2000){ // MOTOR TWO FORWARD
      roboclaw.ForwardM2(address, value - 1000);  // Start Motor1 forward with the specified speed
    }
      
    else if (2000 < value && value < 3000){ // MOTOR ONE REVERSE
      roboclaw.ForwardM1(address, -(value - 2000));  // Start Motor1 forward with the specified speed
    }
      
    else if (3000 < value && value < 4000){ // MOTOR TWO REVERSE
      roboclaw.ForwardM2(address, -(value - 3000));  // Start Motor1 forward with the specified speed
    }
  }
}
void loop() {
  delay(100);
}