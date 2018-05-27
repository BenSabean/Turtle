// Wire Slave Receiver
// by Nicholas Zambetti <http://www.zambetti.com>

// Demonstrates use of the Wire library
// Receives data as an I2C/TWI slave device
// Refer to the "Wire Master Writer" example for use with this

// Created 29 March 2006

// This example code is in the public domain.


#include <Wire.h>
#include <LowPower.h>

#define DEBUG true
int crc = 0;

void setup() {
  pinMode(A4, INPUT);
  pinMode(A5, INPUT);
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);
  digitalWrite(A4, LOW);
  digitalWrite(A5, LOW);
  Wire.begin(8);                // join i2c bus with address #8
  Wire.onReceive(receiveEvent); // register event
#if DEBUG
  Serial.begin(9600);           // start serial for output
  Serial.println("START");
#endif
}

void loop() {
#if DEBUG
  delay(8000);
#else
  if (Wire.available()) {
    receiveEvent(0);
  }
  // ATmega328P, ATmega168
  LowPower.idle(SLEEP_1S, ADC_OFF, TIMER2_OFF, TIMER1_OFF, TIMER0_OFF,
                SPI_OFF, USART0_OFF, TWI_ON);
#endif
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(int howMany) {
  //digitalWrite(5, HIGH);
#if DEBUG
  Serial.println("Start Packet");

#endif
  crc = 0;
  while (1 < Wire.available()) { // loop through all but the last
    byte op = Wire.read();
    addCrc(op);
    byte len = Wire.read();
    byte b = Wire.read();
    addCrc(b);
#if DEBUG
    Serial.print("BYTE: ");
    Serial.println(b);
#endif

  }
  uint8_t x = Wire.read();
  if (x == crc) digitalWrite(5, HIGH);   // receive byte as an integer
  else digitalWrite(9, HIGH);
#if DEBUG
  Serial.print("Recived CRC: ");
  Serial.println(x);         // print the integer
  Serial.print("Calculated CRC: ");
  Serial.println(crc);
  Serial.println("End Packet");
  delay(2000);
#else
  // ATmega328P, ATmega168
  LowPower.idle(SLEEP_1S, ADC_OFF, TIMER2_OFF, TIMER1_OFF, TIMER0_OFF,
                SPI_OFF, USART0_OFF, TWI_ON);
#endif
  digitalWrite(5, LOW);
  digitalWrite(9, LOW);
}

void addCrc(byte n) {
  for (int i = 0; i < 8; i++) {
    if ((n ^ crc) & 0x80) {
      crc = (crc << 1) ^ 0x31;
    }
    else {
      crc = (crc << 1);
    }
    n = n << 1;
  }
  crc = crc & 0xFF;
}

