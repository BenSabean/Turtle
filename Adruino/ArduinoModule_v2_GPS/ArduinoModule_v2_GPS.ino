/*
   DcPi Arduino Module
   Apr 8, 2018
   version: 2

   Program for Arduino Nano controller
   Control recording and shutdown cycles
   Reads GPS date-time and location

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
#define GPS_LOG    "GPS_LOG"
#define GPS_DUMP   "GPS_DUMP"
#define GPS_ERASE  "GPS_ERASE"
#define TIME       "TIME"
#define SLEEP      "SLEEP"
#define DURATION   "DURATION"
#define DELIM      "_"

// GPIO
#define SWITCH    13
#define MOSFET    2
#define PI_CHECK  4
#define GPS_RX    10
#define GPS_TX    11
#define VALVE     9

/* COM Setup */
SoftwareSerial GPS_COM(GPS_RX, GPS_TX); // RX and TX for GPS COM

/* GPS Setup */
Adafruit_GPS GPS (&GPS_COM);

/* Time interval */
// In Minutes (H*60 + M)
// Default 8:00 to 18:00
volatile int Start = 480, End = 1140, Now = 481;
// Mission duration in minutes
// Default: 2 days = 48 h = 2880 minutes
// Timer used to keep track of changes in mission duration
volatile int Duration = 2880, prevNow = 0, Timer = -2; // Timer changes two time in beginning


///////////////////////////////////////////
//                                       //
//                SETUP                  //
//                                       //
///////////////////////////////////////////

void setup ()
{
  // Start RPi COM with PI
  Serial.begin(19200); // Need to be faster than GPS (9600)
  Serial.println("\nSTARTED");    // DEBUG

  /* GPIO setup */
  pinMode(SWITCH, INPUT);
  pinMode(PI_CHECK, INPUT);
  pinMode(7, INPUT);  // On first prototype TX and D7 shorted
  pinMode(MOSFET, OUTPUT);
  pinMode(VALVE, OUTPUT);

  // Turn on Pi
  digitalWrite(MOSFET, LOW);
  // Keep Valve Closed
  digitalWrite(VALVE, LOW);

  // GPS initialization commands
  GPS_init();
}

///////////////////////////////////////////
//                                       //
//                LOOP                   //
//                                       //
///////////////////////////////////////////
void loop ()
{
  /* Variables */
  char message[50], slong[10], slat[10];  memset(message, NULL, sizeof(message));
  bool Awake = digitalRead(PI_CHECK);     // Get Pi status
  bool Switch = digitalRead(SWITCH);      // Get ]Switch status

  //
  //  Checking messages from GPS
  //
  GPS_update();

  //
  // Keeping track of mission time every minute
  //
  if (prevNow != Now)
  {
    Timer ++;
    prevNow = Now;
  }

  //
  //  Checking for Mission end and Triggering Valve
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
      get_time_interval(message); // Pi submits Time Interval
      //Serial.println("Start: " + String(Start) + " Now: " + String(Now) + " End: " + String(End));
    }

    //
    // Pi requested current time
    //
    else if (strcmp(message, TIME) == 0)
    {
      get_time_string(message);
      Serial.println(message);  // Pi requested Time String
    }

    //
    // GPS start logging data command
    //
    else if (strcmp(message, GPS_LOG) == 0)
    {
      if (GPS_log() == 0)
        Serial.println(HANDSHAKE);
    }

    //
    // Pi requested dumping of GPS data
    //
    else if (strcmp(message, GPS_DUMP) == 0)
    {
      GPS_dump();
      Serial.println(HANDSHAKE);
    }

    //
    // Erasing stored GPS data
    //
    else if (strcmp(message, GPS_ERASE) == 0)
    {
      GPS.sendCommand(PMTK_LOCUS_ERASE_FLASH);
      Serial.println(HANDSHAKE);
    }

    //
    // Checking Mission Duration
    //
    else if (strcmp(message, DURATION) == 0)
    {
      Serial.println(Timer);
    }

  }

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
      // SLEEP //
      if (Now > End || Now < Start)
      {
        // Tell Pi to Sleep
        Serial.println(SLEEP);
      }
      // AWAKE //
      else
      {
        // Turn Pi Power ON
        digitalWrite(MOSFET, LOW);
      }
    }
    //  Pi is OFF //
    else
    {
      // AWAKE //
      if (Now > Start && Now < End)
      {
        // Turn Pi Power ON
        digitalWrite(MOSFET, LOW);
      }
      // SLEEP //
      else
      {
        // Turn Pi Power OFF
        digitalWrite(MOSFET, HIGH);
      }
    }
  }
  //
  //  SWITCH OFF
  //
  else
  {
    //  Pi is ON //
    if (Awake)
    {
      // Tell Pi to Sleep
      Serial.println(SLEEP);
    }
    //  Pi is OFF //
    else
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
  int _start = -1, _end = 9999;
  char *p;

  // Extracting INTERVAL
  p = strtok(message, "_");
  if (p != NULL)
  {
    // Extracting first time
    p = strtok(NULL, "_");
    sscanf(p, "%d", &_start);
  }
  if (p != NULL)
  {
    // Extracting second time
    p = strtok(NULL, "_");
    sscanf(p, "%d", &_end);
  }

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
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_10HZ);   // 1 Hz update rate
  // Request updates on antenna status, comment out to keep quiet
  //GPS.sendCommand(PGCMD_ANTENNA);
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
  Starting GPS logging with number of retries
*/
int GPS_log()
{
  for (int retry = 10; retry > 0; retry --)
  {
    if (GPS.LOCUS_StartLogger()) return 0;
    delay(200);
  }
  return 1;
}

/*
   Dumps the contants of GPS Log file to RPi port
*/
void GPS_dump()
{
  char buff[19];                    // Shift buffer to check for end of dump
  char end[] = "$PMTK001,622,3*36"; // Dump finished command
  bool keep_loop = true;
  memset(buff, '\0', sizeof(buff));

  // Disable regular data transvers
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_OFF);
  // Flush buffer
  GPS_COM.readString();
  // Command to start dumping
  GPS.sendCommand("$PMTK622,1*29");

  // Safe loop to dump GPS data - will exit after 3 minutes regardless
  uint32_t start = millis();
  while (keep_loop && (millis() - start) < 180 * 1000)
  {
    // If millis timer overflow happens
    if (start > millis()) start = millis();

    if (GPS_COM.available())
    {
      // Reading new caracter from GPS
      buff[17] = GPS_COM.read();
      // Sending to RPI
      Serial.print(buff[17]);
      // Shifting shift register Left
      for (int i = 0; i < 17; i++) buff[i] = buff[i + 1];
      // Comparing each char in shifting reg. with output string
      // When one character is not equal, keeps looping 
      keep_loop = false;
      for (int i = 0; i < 17; i++)
        if (buff[i] != end[i]) keep_loop = true;
    }
  }
  Serial.println();
  // Enable regular data transfers
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_10HZ);   // 1 Hz update rate
}
