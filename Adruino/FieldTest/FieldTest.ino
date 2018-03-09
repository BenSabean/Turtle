/*
   March 3, 2018
   Program to for Arduino Nano controller
   Control recording and shutdown cycles
   Reads RTC date-time and locations
*/

#include <Wire.h>
#include <SoftwareSerial.h>
#include <Adafruit_GPS.h>
#include "RTClib.h"

///////////////////////////////////////////
//                                       //
//            DECLARATIONS               //
//                                       //
///////////////////////////////////////////

#define PI_BOOT_DELAY_S     1     // Delay for Pi to boot up In seconds
#define PI_SHUTDOWN_DELAY_S 1     // Delay for Pi to shutdown In seconds

#define SERIAL_RETRY        5     // Attemps to get serial value
#define SERIAL_TIMEOUT_S    1     // Waiting time for response from Pi

// Command list
#define INTERVAL_CMD   "INTERVAL"
#define HANDSHAKE_CMD  "OK"
#define GPS_CMD        "GPS"
#define TIME_CMD       "TIME"
#define SLEEP_CMD      "SLEEP"
#define DELIM          "_"

// GPIO
#define SWITCH    13
#define PI_TX     4
#define PI_RX     8
#define MOSFET    6
#define PI_CHECK  10

/* COM Setup */
SoftwareSerial RPi(PI_RX, PI_TX);       // RX and TX for RPI COM

/* RTC object */
RTC_DS3231 rtc;

/* Time interval */
// In Minutes (H*60 + M)
// Default 8:00 to 18:00
volatile int Start = 480, End = 1439, Now = 481;

/* GPS Data Containers */
volatile float Long = 0, Lat = 0;

///////////////////////////////////////////
//                                       //
//                SETUP                  //
//                                       //
///////////////////////////////////////////
void setup ()
{
  // Serial for DEBUG setup
  Serial.begin(115200);       // DEBUG
  Serial.println("START");    // DEBUG
  // Start Serial COM with PI
  RPi.begin(56700);

  /* RTC Code */
  Wire.begin();
  if (! rtc.begin())
  {
    //Serial.println("Couldn't find RTC");
    while (1);
  }
  // Uncomment to set Time for RTC
  // setTime();

  /* GPIO setup */
  pinMode(SWITCH, INPUT);
  pinMode(PI_CHECK, INPUT);
  pinMode(MOSFET, OUTPUT);

  digitalWrite(MOSFET, HIGH);
}

///////////////////////////////////////////
//                                       //
//                LOOP                   //
//                                       //
///////////////////////////////////////////
void loop ()
{
  /* Variables */
  char message[100], slong[10], slat[10];  memset(message, NULL, 100);
  bool Awake = digitalRead(PI_CHECK);
  bool Switch = digitalRead(SWITCH);
  DateTime now = rtc.now();
  Now = now.hour() * 60 + now.minute();

  //-------- Check for messages from Pi -------
  if (RPi.available())
  {
    // Reading new message
    readString(message, sizeof(message));

    Serial.print("GOT: "); Serial.println(message);

    if (strcmp(message, INTERVAL_CMD) == 0)
    {
      get_time_interval(message);   // Pi submits Time Interval
      // DEBUG
      Serial.println("Start = " + String(Start) + " Now = " + String(Now) + " End = " + String(End));
      // DEBUG
    }
    else if (strcmp(message, TIME_CMD) == 0)
    {
      get_time_string(message);
      send_RPi(message);  // Pi requested Time String
    }
    else if (strcmp(message, GPS_CMD) == 0)
    {
      // GPS Format: int[Time]_float[Long]_float[Lat] (ex:820_104.44421_41.23342)
      dtostrf(Long, 10, 7, slong);
      dtostrf(Lat, 10, 7, slat);
      sprintf(message, "%d_%s_%s", Now, slong, slat);
      send_RPi(message);
    }
  }
  //--------------------------------------------

  //-------------- Mission Timing --------------

  if (Switch)   // 1. SWITCH ON //
  {
    if (Awake)      // 2. Pi is ON //
    {
      // 3. Time to Sleep //
      if (Now > End || Now < Start)
      { // SLEEP YES //
        Serial.println("Sending SLEEP");
        send_RPi(SLEEP_CMD);
        delay(1 * 1000);
      }
      else // 3. Time to be Awake //
      {
        digitalWrite(MOSFET, LOW); // Turn Pi Power ON
      }
    }
    else            // 2. Pi is OFF //
    {
      // 3. Time to WakeUp //
      if (Now > Start && Now < End)
      {
        // Turn Pi Power ON
        digitalWrite(MOSFET, LOW);
      }
      else  // 3. Time to Sleep //
      {
        // Turn Pi Power OFF
        digitalWrite(MOSFET, HIGH);

      }
    }
  }// -----------------------
  else  // 1. SWITCH OFF //
  {
    if (Awake)     // 2. Pi is ON //
    { // Tell Pi to Sleep
      // DEBUG
      Serial.println("Sending SLEEP");
      send_RPi(SLEEP_CMD);
      delay(1 * 1000);
    }
    else            // 2. Pi is OFF //
    {
      digitalWrite(MOSFET, HIGH);
    }
  }
  //--------------------------------------------
}

///////////////////////////////////////////
//                                       //
//              FUNCTIONS                //
//                                       //
///////////////////////////////////////////

/*
  Sends command and receives start-end times
  Format: INTERVAL_[FIRST]_[SECOND] in minutes (ex: 480_1439)
*/
int get_time_interval(char* message)
{
  int _start, _end;

  strtok(message, "_");
  sscanf(strtok(NULL, "_"), "%d", &_start);
  sscanf(strtok(NULL, "_"), "%d", &_end);

  // Error checking
  if (_start > 0 && _start < 1439 && _end > 0 && _end < 1439)
  {
    RPi.println(HANDSHAKE_CMD); // Letting Pi know we got data
    Start = _start;
    End = _end;
    return 0; // break out of the loop
  }
  return 1;
}

/*
  Send command to Pi + HandShake
  0 - HandShake success
  1 - HandShake failed
*/
void send_RPi(char* _msg)
{
  unsigned long _strt, _delta;
  char message[10];

  for (uint8_t i = 0; i < SERIAL_RETRY; i++)
  {
    RPi.println(_msg);    // Send Data command
    // Waiting for handshake
    _strt = millis();
    _delta = millis() - _strt;
    while (_delta < (SERIAL_TIMEOUT_S * 1000))
    {
      if (RPi.available())
      {
        readString(message, 10);
        if (strcmp(message, HANDSHAKE_CMD) == 0) break;
      }
      _delta = abs(millis() - _strt);
    }
  }
}

/*
  Returns a Date-Time String
  Format: YYYY_MM_DD_hh_mm
*/
void get_time_string(char* buff)
{
  DateTime now = rtc.now();
  sprintf(buff, "%d_%d_%d_%d:%d:%d", now.year(), now.month(), now.day(), now.hour(), now.minute(), now.second());
}

/*
   Set RTC time to system upload time
*/
void setTime()
{
  if (rtc.lostPower())
  {
    Serial.println("RTC lost power, lets set the time!");
    // following line sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }
}

/*
   Function to read incomming serial string
*/
void readString (char* buff, int len)
{
  for (uint8_t i = 0; (RPi.available() > 0) && i < len; i++)
    buff[i] = RPi.read();
}

