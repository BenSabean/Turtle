/*
   Feb 7, 2018
   Program to for Arduino Nano controller
   Samples the time from RTC DS3231 and starts/stops
   the operation of Raspberry pi
*/

#include <Wire.h>
#include "RTClib.h"

#define SWITCH  13
#define SLEEP   4
#define MOSFET  6

RTC_DS3231 rtc;

/* Time interval */
int start_hour  = 8,  start_min = 30;
int end_hour    = 18, end_min   = 0;

/* Programs Starts */
void setup ()
{
  Serial.begin(9600);
  Serial.println("START");
  
  Wire.begin();
  
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  if (rtc.lostPower()) {
    Serial.println("RTC lost power, lets set the time!");
    // following line sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }
  
  pinMode(SWITCH, INPUT);
  pinMode(SLEEP, OUTPUT);
  pinMode(MOSFET, OUTPUT);

  // MOSFET is off
  digitalWrite(MOSFET, LOW);
  // SLEEP signal is low
  digitalWrite(SLEEP, LOW);
}

/* Programs Loop */
void loop ()
{
  int start_time = get_start_time();
  int end_time = get_end_time();
  int current_time = get_current_time();
  int switch_pin = digitalRead(SWITCH);
  Serial.println(current_time);
  
  if (current_time > start_time && current_time < end_time)
  {
    if (switch_pin) digitalWrite(MOSFET, HIGH);
  }
  else if (current_time > end_time)
  {
    digitalWrite(SLEEP, HIGH);
    delay(60000);
    digitalWrite(MOSFET, LOW);
  }
  delay(10000);
}

/* Returns current time */
int get_current_time ()
{
  DateTime now = rtc.now();
  int time_minutes = (now.hour() * 60) + now.minute();
  return time_minutes;
}

/* Returns start recording time */
int get_start_time ()
{
  int time_minutes;
  time_minutes = (start_hour * 60) + start_min;
  return time_minutes;
}

/* Returns end recording time */
int get_end_time ()
{
  int time_minutes;
  time_minutes = (end_hour * 60) + end_min;
  return time_minutes;
}

