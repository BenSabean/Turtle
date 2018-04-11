/*
   DcPi Arduino Module
   Apr 8, 2018
   version: 2

   Program for Arduino Nano controller
   Control recording and shutdown cycles
   Reads GPS date-time and location
*/

#include <SoftwareSerial.h>
#include <Adafruit_GPS.h>

///////////////////////////////////////////
//                                       //
//            DECLARATIONS               //
//                                       //
///////////////////////////////////////////

#define PI_BOOT_DELAY_S     1     // Delay for Pi to boot up In seconds
#define PI_SHUTDOWN_DELAY_S 2     // Delay for Pi to shutdown In seconds

#define SERIAL_RETRY        5     // Attemps to get serial value
#define SERIAL_TIMEOUT_S    2     // Waiting time for response from Pi

// Command list
#define INTERVAL_CMD   "INTERVAL"
#define HANDSHAKE_CMD  "OK"
#define GPS_LOG_CMD    "GPS_LOG"
#define GPS_DUMP_CMD   "GPS_DUMP"
#define GPS_ERASE_CMD  "GPS_ERASE"
#define TIME_CMD       "TIME"
#define SLEEP_CMD      "SLEEP"
#define DELIM          "_"

// GPIO
#define SWITCH    13
#define PI_TX     4
#define PI_RX     3
#define MOSFET    2
#define PI_CHECK  6
#define GPS_RX    10
#define GPS_TX    11

/* COM Setup */
SoftwareSerial RPi(PI_RX, PI_TX);       // RX and TX for RPI COM
SoftwareSerial GPS_COM(GPS_RX, GPS_TX); // RX and TX for GPS COM

/* GPS Setup */
Adafruit_GPS GPS (&GPS_COM);

/* Time interval */
// In Minutes (H*60 + M)
// Default 8:00 to 18:00
volatile int Start = 480, End = 1400, Now = 481;

///////////////////////////////////////////
//                                       //
//                SETUP                  //
//                                       //
///////////////////////////////////////////
void setup ()
{
  // Serial for DEBUG setup
  Serial.begin(115200);       // DEBUG
  Serial.println("\nSTARTED");    // DEBUG

  // Start Serial COM with PI
  RPi.begin(19200); // Need to be faster than GPS

  // GPS initialization commands
  GPS_init();

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
  char message[50], slong[10], slat[10];  memset(message, NULL, sizeof(message));
  bool Awake = digitalRead(PI_CHECK);     // Get Pi status
  bool Switch = digitalRead(SWITCH);      // Get ]Switch status

  RPi.listen(); // Listen for software serial 1 - Pi

  //-------- Check for messages from Pi -------
  if (RPi.available())
  {
    // Reading new message
    readString(message, sizeof(message));

    Serial.print("GOT: "); Serial.println(message);

    // Pi transmits mission interval
    if (strstr(message, INTERVAL_CMD) != NULL)
    {
      get_time_interval(message);   // Pi submits Time Interval
    }
    // Pi requested current time
    else if (strcmp(message, TIME_CMD) == 0)
    {
      get_time_string(message);
      send_RPi(message);  // Pi requested Time String
    }
    // GPS start logging data command
    else if (strcmp(message, GPS_LOG_CMD) == 0)
    {
      GPS_log();
    }
    // Pi requested dumping of GPS data
    else if (strcmp(message, GPS_DUMP_CMD) == 0)
    {
      GPS_dump();
    }
    // Erasing stored GPS data
    else if (strcmp(message, GPS_ERASE_CMD) == 0)
    {
      GPS.sendCommand(PMTK_LOCUS_ERASE_FLASH);
    }
  }

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
        delay(2 * 1000);
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
        delay(PI_SHUTDOWN_DELAY_S * 1000);
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
      delay(2 * 1000);
    }
    else            // 2. Pi is OFF //
    {
      delay(PI_SHUTDOWN_DELAY_S * 1000);
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
int send_RPi(char* _msg)
{
  unsigned long whenToStop;
  char message[10];
  memset(message, '\0', sizeof(message));
  bool done = false;

  for (uint8_t i = 0; (i < SERIAL_RETRY) && (done == false); i++)
  {
    RPi.println(_msg);    // Send Data command
    // Waiting for handshake
    whenToStop = millis () + (SERIAL_TIMEOUT_S * 1000);
    while ( (millis() < whenToStop) && (done == false) )
    {
      if (RPi.available() > 0)
      {
        readString(message, 10);
        if (strcmp(message, HANDSHAKE_CMD) == 0) done = true;
      }
    }
  }
  return 1;
}

/*
  Returns a Date-Time String
  Format: YYYY_MM_DD_hh_mm
*/
void get_time_string(char* buff)
{
  GPS_update();
  sprintf(buff, "%04d_%02d_%02d_%02d:%02d:%02d", GPS.year, GPS.month, GPS.day, GPS.hour, GPS.minute, GPS.seconds);
}

/*
   Function to read incomming serial string
*/
void readString (char* buff, int len)
{
  String msg;
  msg = RPi.readString();
  strcpy(buff, msg.c_str());
}

/*
   GPS initialization commands
*/
void GPS_init()
{
  // Start Serial COM with GPS
  GPS.begin(9600);
  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
  //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  // uncomment this line to turn on only the "minimum recommended" data
  //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  // uncomment to keep gps quiet
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_OFF);
  // Set the update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
  // Request updates on antenna status, comment out to keep quiet
  //GPS.sendCommand(PGCMD_ANTENNA);
  // Disable Interrups
  TIMSK0 &= ~_BV(OCIE0A);
  delay(1000);
}

/*
   Update GPS Values
*/
void GPS_update()
{
  GPS_COM.listen(); // Listen for softwareserial 2 - GPS
  // Start receiving data
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  // Waiting for message to come through
  delay(1000);
  // Reading input
  GPS.read();
  // New message from the GPS
  if (GPS.newNMEAreceived())
  {
    // DEBUG
    //Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false
    // Parsing
    GPS.parse(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false
  }
  // Disable updates
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_OFF);
  RPi.listen(); // Listen for softwareserial 1 - Pi
}

/*
  Starting GPS logging with number of retries
*/
void GPS_log()
{
  GPS_COM.listen(); // Listen for softwareserial 2 - GPS
  for(int retry = 0; retry < 5; retry ++)
  {
    Serial.print("Starting logging....");
    if (GPS.LOCUS_StartLogger()) break;
    else  Serial.println(" no response :(");
    delay(500);
  }
  RPi.listen(); // Listen for softwareserial 1 - Pi
}

void GPS_dump()
{
  GPS_COM.listen(); // Listen for softwareserial 2 - GPS
  ;
  RPi.listen(); // Listen for softwareserial 1 - Pi
}



