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
#define DURATION   "DURATION"
#define DELIM      "_"
#define PARAM      "PARAM"

// GPIO
#define SWITCH    13
#define MOSFET    2
#define PI_CHECK  4
#define GPS_RX    10
#define GPS_TX    11
#define VALVE     9
#define BATTERY   A0

/* COM Setup */
SoftwareSerial GPS_COM(GPS_RX, GPS_TX); // RX and TX for GPS COM

/* GPS Setup */
Adafruit_GPS GPS (&GPS_COM);

/* Time interval */
// In Minutes (H*60 + M)
// Default 5:00 to 19:00
volatile int Start = 300, End = 1140, Now = 301;
// Mission duration in minutes
// Default: 3 days = 72 h = 4320 minutes
// Timer used to keep track of changes in mission duration
volatile int Duration = 4320, prevNow = 0, Timer = -2; // Timer changes two time in beginning
// Battery monitoring
volatile float Battery = 0;


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
  pinMode(VALVE, OUTPUT);
  pinMode(BATTERY, INPUT);

  // Turn on Pi
  digitalWrite(MOSFET, LOW);
  // Keep Valve Closed
  digitalWrite(VALVE, LOW);

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
  Battery = ((float) analogRead(BATTERY) * 5.0) / 1024.0; // Battery life tracking

  //
  //  Checking messages from GPS & Updating Time
  //
  GPS_update();

  //
  //  Keeping track of mission time every minute
  //
  if (prevNow != Now)
  {
    Timer ++;
    prevNow = Now;
  }

  //
  //  Checking for Mission End & Triggering Release Valve
  //
  if (Timer > Duration)
    digitalWrite(VALVE, HIGH);

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
      Serial.println(message);  // Send Pi gps string
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
      if (Now > End || Now < Start)
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
      if (Now > Start && Now < End)
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
  int _start = -1, _end = 9999, _dur = 20000;
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

  // Extracting DURATION
  p = strtok(NULL, "_");
  if (p == NULL) return 0;
  sscanf(p, "%d", &_dur);

  // Error checking
  if (_start > 0 && _start < 1439 && _end > 0 && _end < 1439 && _dur > 0 && _dur < 15000)
  {
    Serial.println(HANDSHAKE); // Letting Pi know we got data
    // Setting globals
    Start = _start;
    End = _end;
    Duration = _dur;
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
  if (day < 0)
  {
    day += 29;
    month--;
  }
  if (month < 0)
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
   Format: [START]_[NOW]_[END]_[TIMER]_[DURATION]_[BATTERY]
*/
void get_Paramters(char* buff)
{
  char batt[10];
  dtostrf(Battery, 7, 6, batt);

  sprintf(buff, "%d_%d_%d_%d_%d_%s", Start, Now, End, Timer, Duration, batt);
}
