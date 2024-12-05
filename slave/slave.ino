// Caltech ME72 2024
// Wayne Botzky

#include <Wire.h>
#include <SoftwareSerial.h>
#include "RoboClaw.h"

//See limitations of Arduino SoftwareSerial
SoftwareSerial serial(10,11);	
RoboClaw roboclaw(&serial,10000);

#define address 0x80

 
void setup() {
  // Join I2C bus as slave with address 8
  Wire8.begin(0x8);
  Wire9.begin(0x9);
  
  // Call receiveEvent when data received                
  Wire8.onReceive(receiveEvent8);
  Wire9.onReceive(receiveEvent9);

  roboclaw.begin(38400);
  roboclaw.ForwardM1(address, 0);
  roboclaw.ForwardM2(address, 0);
}
 
// Function that executes whenever data is received from master
void receiveEvent8(int howMany) {
  while (Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character


     // Check if the value is a hexadecimal number greater than 0x1000
    unsigned int value = (unsigned int)c;

    roboclaw.ForwardM1(address, value); // Start Motor1 forward with the specified speed

  }
}
void receiveEvent9(int howMany) {
  while (Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character


     // Check if the value is a hexadecimal number greater than 0x1000
    unsigned int value = (unsigned int)c;

    roboclaw.ForwardM2(address, value); // Start Motor1 forward with the specified speed
    

  }
}
void loop() {
  delay(100);
}