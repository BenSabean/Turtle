#include <Wire.h>  // Library which contains functions to have I2C Communication
#define SLAVE_ADDRESS 0x40 // Define the I2C address to Communicate to Uno

byte response[2]; // this data is sent to PI
volatile short LDR_value; // Global Declaration
const int LDR_pin=A0; //pin to which LDR is connected A0 is analog A0 pin  
void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);
  Wire.begin(SLAVE_ADDRESS); // this will begin I2C Connection with 0x40 address
  Wire.onRequest(sendData); // sendData is funtion called when Pi requests data
  pinMode(LDR_pin,INPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  
delay(1000);
}
void sendData(){
  LDR_value=analogRead(LDR_pin);
  // Arduino returns 10bit data but we need to convert it to 8bit 
  LDR_value=map(LDR_value,0,1023,0,255);
  response[0]=(byte)LDR_value;
  Wire.write(response,2); // return data to PI
}
