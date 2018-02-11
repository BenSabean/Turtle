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

  /* // UNCOMMENT TO SET TIME
    if (rtc.lostPower())
    {
    Serial.println("RTC lost power, lets set the time!");
    // following line sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
    }
  */

  pinMode(SWITCH, INPUT);
  pinMode(MOSFET, OUTPUT);

  // MOSFET is off - PI is off
  digitalWrite(MOSFET, LOW);
}

/* Program Loop */
void loop ()
{
  /* Variables */
  int start_time = get_start_time();
  int end_time = get_end_time();
  int current_time = get_current_time();
  int switch_pin = digitalRead(SWITCH);
  String message;

  /* Reporting time back to PI */
  if (port.available())
  {
    message = port.readString();
    Serial.println("GOT: " + message);
    if (message == "TIME")
    {
      // Sending the time
      port.println(get_time_string());
      Serial.println(get_time_string());
    }
  }

  /* Keeping track of shutdown cycle */
  if (current_time > start_time && current_time < end_time)
  {
    if (switch_pin)
    {
      Serial.println("MOSFET ON");
      digitalWrite(MOSFET, HIGH);
    }
    else
    {
      Serial.println("MOSFET OFF");
      digitalWrite(MOSFET, LOW);
    }
  }
  else if (current_time > end_time)
  {
    /* Sending sleep command */
    port.println("SLEEP");
    Serial.println("Entering sleep mode");
    delay(60000);
    digitalWrite(MOSFET, LOW);
  }
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

/* Return full date-time string */
String get_time_string ()
{
  DateTime now = rtc.now();
  String date_time =  String(now.year()) + "-";
  date_time +=        String(now.month()) + "-";
  date_time +=        String(now.day()) + "-";
  date_time +=        String(now.hour()) + "-";
  date_time +=        String(now.minute());
  return date_time;
}

