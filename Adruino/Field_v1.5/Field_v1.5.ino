/*
   DcPi Arduino Module
   Apr 23, 2018
   version: 1.5 field test

   Program for Arduino Nano controller
   Control recording and shutdown cycles
   Reads GPS date-time and location

   Protocol: Pi sends commands
   reponse either data or string "OK"

   Contact: Arthur Bondar
   Email:   arthur.bondar.1@gmail.com
*/

#include <SoftwareSerial.h>
#include <Adafruit_GPS.h>

///////////////////////////////////////////
//                                       //
//            DECLARATIONS               //
//                                       //
///////////////////////////////////////////

// Command list
#define INTERVAL   "INTERVAL"
#define HANDSHAKE  "OK"
#define GET_GPS    "GPS"
#define TIME       "TIME"
#define SLEEP      "SLEEP"
#define DELIM      "_"
#define PARAM      "PARAM"

// GPIO
#define SWITCH    13
#define MOSFET    2
#define PI_CHECK  4
#define GPS_RX    10
#define GPS_TX    11

  // Months
#define JAN 1
#define FEB 2
#define MAR 3
#define APR 4
#define MAY 5
#define JUN 6
#define JUL 7
#define AUG 8
#define SEP 9
#define _OCT 10
#define NOV 11
#define _DEC 12

/* COM Setup */
SoftwareSerial GPS_COM(GPS_RX, GPS_TX); // RX and TX for GPS COM

/* GPS Setup */
Adafruit_GPS GPS (&GPS_COM);

/* Time interval */
// In Minutes (H*60 + M)
// Default 5:00 to 19:00 -> 300 to 1140
volatile int Start = 0, End = 1500, Now = 1;


///////////////////////////////////////////
//                                       //
//                SETUP                  //
//                                       //
///////////////////////////////////////////

void setup ()
{
  // Start RPi COM with PI
  Serial.begin(19200); // Need to be faster than GPS (9600)

  /* GPIO setup */
  pinMode(SWITCH, INPUT);
  pinMode(PI_CHECK, INPUT);
  pinMode(7, INPUT);  // On first prototype TX and D7 shorted
  pinMode(MOSFET, OUTPUT);

  // Turn on Pi
  digitalWrite(MOSFET, LOW);

  // GPS initialization commands
  GPS_init();
  // Flush serial buffer
  Serial.readString();
}

///////////////////////////////////////////
//                                       //
//                LOOP                   //
//                                       //
///////////////////////////////////////////
void loop ()
{
  char message[100];
  memset(message, NULL, sizeof(message));
  bool Awake = digitalRead(PI_CHECK);     // Get Pi status
  bool Switch = digitalRead(SWITCH);      // Get Switch status

  //
  //  Checking messages from GPS & Updating Time
  //
  GPS_update();

  //
  //  -------- Check for messages from Pi -------
  //
  if (Serial.available())
  {
    // Reading new message
    readString(message, sizeof(message));

    //
    // Pi transmits mission interval
    //
    if (strstr(message, INTERVAL) != NULL)
    {
      scan_time_interval(message); // HANDSHAKE inside the function
    }

    //
    // Pi requested current time
    //
    else if (strcmp(message, TIME) == 0)
    {
      get_time_string(message);
      Serial.println(message);  // send Pi time string
    }

    //
    // Pi requested GPS
    //
    else if (strcmp(message, GET_GPS) == 0)
    {
      get_GPS(message);
      Serial.println(message);  // send Pi gps string
    }

    //
    // Pi requested system status
    //
    else if (strcmp(message, PARAM) == 0)
    {
      get_Paramters(message);
      Serial.println(message);

    }

  } // -------------- END SERIAL --------------

  //
  //  -------------- Mission Timing --------------
  //
  //  SWITCH ON
  //
  if (Switch)
  {
    //  Pi is ON //
    if (Awake)
    {
      // SLEEP TIME //
      if (Now >= End || Now <= Start)
        // Tell Pi to Sleep
        Serial.println(SLEEP);
      // AWAKE TIME //
      else
        // Turn Pi Power ON
        digitalWrite(MOSFET, LOW);
    }
    //  Pi is OFF //
    else
    {
      // AWAKE TIME //
      if (Now >= Start && Now <= End)
        // Turn Pi Power ON
        digitalWrite(MOSFET, LOW);
      // SLEEP TIME //
      else
        // Turn Pi Power OFF
        digitalWrite(MOSFET, HIGH);
    }
  }
  //
  //  SWITCH OFF
  //
  else
  {
    //  Pi is ON //
    if (Awake)
      // Tell Pi to Sleep
      Serial.println(SLEEP);
    //  Pi is OFF //
    else
      // Turn Pi Power OFF
      digitalWrite(MOSFET, HIGH);
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
  Format: INTERVAL_[START]_[END]_[DURATION] in minutes
  Example: INTERVAL_480_1439_2880
*/
int scan_time_interval(char* message)
{
  int _start = -1, _end = 9999;
  char *p;

  // Extracting INTERVAL
  p = strtok(message, "_");
  if (p == NULL) return 0;

  // Extracting START time
  p = strtok(NULL, "_");
  if (p == NULL) return 0;
  sscanf(p, "%d", &_start);

  // Extracting END time
  p = strtok(NULL, "_");
  if (p == NULL) return 0;
  sscanf(p, "%d", &_end);

  // Error checking
  if (_start > 0 && _start < 1439 && _end > 0 && _end < 1439)
  {
    Serial.println(HANDSHAKE); // Letting Pi know we got data
    // Setting globals
    Start = _start;
    End = _end;
    return 0; // break out of the loop
  }
  return 1;
}

/*
  Returns a Date-Time String
  Format: YYYY-MM-DD hh:mm:ss
*/
void get_time_string(char* buff)
{
  int hour = GPS.hour - 3;
  int day = GPS.day;
  int month = GPS.month;
  int year = GPS.year;

  // UTC to Atlantic Time conversion
  if (hour < 0)
  {
    hour += 24;
    day--;
  }


  if (day <= 0)
  {
    month--;
    if(month == JAN)        day += 31;
    else if(month == FEB)   day += 28;
    else if(month == MAR)   day += 31;
    else if(month == APR)   day += 30;
    else if(month == MAY)   day += 31;
    else if(month == JUN)   day += 30;
    else if(month == JUL)   day += 31;
    else if(month == AUG)   day += 31;
    else if(month == SEP)   day += 30;
    else if(month == _OCT)  day += 31;
    else if(month == NOV)   day += 30;
    else if(month == _DEC)  day += 31;
  }
  if (month <= 0)
  {
    month += 12;
    year--;
  }
  sprintf(buff, "%04d-%02d-%02d %02d:%02d:%02d", 2000 + year, month, day, hour, GPS.minute, GPS.seconds);
}

/*
   Function to read incomming RPi string
*/
void readString (char* buff, int len)
{
  String msg;
  msg = Serial.readString();
  strcpy(buff, msg.c_str());
}

/*
   GPS initialization commands
*/
void GPS_init()
{
  // Start RPi COM with GPS
  GPS.begin(9600);
  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
  //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  // uncomment this line to turn on only the "minimum recommended" data
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  // uncomment to keep gps quiet
  //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_OFF);
  // Set the update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
  // Disable Interrups
  TIMSK0 &= ~_BV(OCIE0A);
  delay(1000);
}

/*
   Update GPS Values for time, stored internally
*/
void GPS_update()
{
  int hour = 0;

  // Reading input
  GPS.read();
  // New message from the GPS
  // this also sets the newNMEAreceived() flag to false
  if (GPS.newNMEAreceived())
    GPS.parse(GPS.lastNMEA());

  // Updating current time
  // UTC to Atlantic conversion
  hour = GPS.hour - 3;
  if (hour < 0) hour += 24;
  Now = hour * 60 + GPS.minute;
}

/*
   Sends GPS value to Pi
   Format: [Fix]_[Quality]_[Long]_[Lat]_[Speed]_[Angle]
*/
void get_GPS(char* buff)
{
  char lat[11], lon[11], speed[11], angle[11];

  dtostrf(GPS.latitudeDegrees, 8, 6, lat);
  dtostrf(GPS.longitudeDegrees, 8, 6, lon);
  dtostrf(GPS.speed, 8, 6, speed);
  dtostrf(GPS.angle, 8, 6, angle);

  sprintf(buff, "%d_%d_%s_%s_%s_%s", GPS.fix, GPS.fixquality, lat, lon, speed, angle);
}

/*
   Checking mission parameters to make sure evething on track
   Format: [START]_[NOW]_[END]
*/
void get_Paramters(char* buff)
{
  sprintf(buff, "%d_%d_%d", Start, Now, End);
}
