/*
   Feb 7, 2018
   Program to for Arduino Nano controller
   Samples the time from RTC DS3231 and starts/stops
   the operation of Raspberry pi
*/

#include <Wire.h>
#include "RTClib.h"
#include <SoftwareSerial.h>

// GPIO
#define SWITCH  13
#define TX       4
#define RX       8
#define MOSFET   6

RTC_DS3231 rtc;
SoftwareSerial port(RX, TX); // RX and TX

/* Time interval */
int start_hour  = 8,  start_min = 30;
int end_hour    = 20, end_min   = 0;

/* Programs Starts */
void setup ()
{
  Serial.begin(9600);       // DEBUG
  Serial.println("START");  // DEBUG

  // Start Serial COM with PI
  port.begin(9600);

  Wire.begin();

  if (! rtc.begin())
  {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  pinMode(RX, INPUT);
  pinMode(TX, OUTPUT);
}

/* Program Loop */
void loop ()
{
  String message;
  /* Message from RPI */
  if (port.available())
  {
    Serial.println("GOT: " + port.readString());
  }

  if (Serial.available())
  {
    message = Serial.readString();
    Serial.println("SEND: " + message);
    port.println(message);
  }

}


