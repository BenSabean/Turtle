/*
   Feb 24, 2018
   Program to for Arduino Nano controller
   Control recording and shutdown cycles
   Reads GPS date-time and locations
*/

#include <SoftwareSerial.h>
#include <Adafruit_GPS.h>

///////////////////////////////////////////
//                                       //
//            DECLARATIONS               //
//                                       //
///////////////////////////////////////////

#define PI_BOOT_DELAY_S     60    // Delay for Pi to boot up In seconds
#define PI_SHUTDOWN_DELAY_S 1     // Delay for Pi to shutdown In seconds

#define SERIAL_RETRY        10    // Attemps to get serial value
#define SERIAL_TIMEOUT_S    1     // Waiting time for response from Pi

#define GPS_UPDATE_S       1      // GPS reading update interval 

// Command list
#define INTERVAL_CMD   "INTERVAL"
#define HANDSHAKE_CMD  "OK"
#define GPS_CMD        "GPS"
#define TIME_CMD       "TIME"
#define SLEEP_CMD      "SLEEP"
#define DELIM          "_"

// GPIO
#define SWITCH  13
#define PI_TX    4
#define PI_RX    5
#define GPS_TX   2
#define GPS_RX   3
#define MOSFET   6
#define PI_CHECK 8

/* COM Setup */
SoftwareSerial RPi(PI_RX, PI_TX);       // RX and TX for RPI COM
SoftwareSerial GPS_COM(GPS_RX, GPS_TX); // RX and TX for GPS COM

/*    GPS Setup    */
Adafruit_GPS GPS (&GPS_COM);
#define GPSECHO  false            // Dont listen to raw GPS data

/* Time interval */
// In Minutes (H*60 + M)
// Default 8:00 to 18:00
volatile int Start = 480, End = 1080, Now = 481;

/* GPS Data Containers */
volatile float Long, Lat;

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
  RPi.begin(9600);
  // GPS initialization commands
  GPS_init();
  // GPIO setup
  pinMode(SWITCH, INPUT);
  pinMode(PI_CHECK, INPUT);
  pinMode(MOSFET, OUTPUT);
  // Turn Pi Power ON
  digitalWrite(MOSFET, HIGH);
  delay(PI_BOOT_DELAY_S * 1000);  // Delay for PI to turn on

  // DEBUG
  Serial.println("Start = " + String(Start) + "\n" + "End = " + String(End));
  // DEBUG
}

///////////////////////////////////////////
//                                       //
//                LOOP                   //
//                                       //
///////////////////////////////////////////
void loop ()
{
  /* Variables */
  String message;
  bool Awake = digitalRead(PI_CHECK);
  bool Switch = digitalRead(SWITCH);
  int gps_start = 1;

  // Update GPS values every interval
  if ((millis() - gps_start) > GPS_UPDATE_S * 1000)
  {
    GPS_update();
    gps_start = millis();
  }

  // Check for messages from Pi
  if (RPi.available())
  {
    message = RPi.readString();    // Get message

    // Pi submits Time Interval
    if (message == INTERVAL_CMD) get_time_interval();

    // Pi requested Time String
    if (message == TIME_CMD)      send_RPi(get_time_string());

    // Pi requested GPS
    if (message == GPS_CMD)
    {
      // GPS Format: int[Time]_float[Long]_float[Lat] (ex:820_104.44421_41.23342)
      send_RPi(String(Now) + DELIM + String(Long) + DELIM + String(Lat));
    }
  }

  // Checking for system ON/OFF switch first
  if (Switch)
  {
    // Sleep wake cycle
    if (Awake)               // Pi is ON //
    { // Time to Sleep
      if (Now > End) send_RPi(SLEEP_CMD);
    }
    else                     // Pi is OFF //
    {
      delay(PI_SHUTDOWN_DELAY_S * 1000);
      // Turn Pi Power OFF
      digitalWrite(MOSFET, LOW);
      // Time to wake up
      if (Now > Start && Now < End)
      {
        // Turn Pi Power ON
        digitalWrite(MOSFET, HIGH);
        delay(PI_BOOT_DELAY_S * 1000);  // Delay for PI to turn on
      }
    }
  }
  else  // Switch indicator is OFF
  {
    if (Awake)               // Pi is ON //
    { // Tell Pi to Sleep
      send_RPi(SLEEP_CMD);
    }
    else                     // Pi is OFF //
    {
      delay(PI_SHUTDOWN_DELAY_S * 1000);
      // Turn Pi Power OFF
      digitalWrite(MOSFET, LOW);
    }
  }
}

///////////////////////////////////////////
//                                       //
//              FUNCTIONS                //
//                                       //
///////////////////////////////////////////

/* GPS initialization commands */
void GPS_init()
{
  // Start Serial COM with GPS
  GPS.begin(9600);
  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  // uncomment this line to turn on only the "minimum recommended" data
  //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  // Set the update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
  // Request updates on antenna status, comment out to keep quiet
  GPS.sendCommand(PGCMD_ANTENNA);
  // do not call the interrupt function COMPA anymore
  TIMSK0 &= ~_BV(OCIE0A);
  delay(1000);
  // Ask for firmware version
  GPS_COM.println(PMTK_Q_RELEASE);
}

/* Update GPS Values */
void GPS_update()
{
  // New message from the GPS
  if (GPS.newNMEAreceived())
  {
    // DEBUG
    Serial.println("GPS: " + String(GPS.lastNMEA()));   // this also sets the newNMEAreceived() flag to false
    // Parsing
    if (GPS.parse(GPS.lastNMEA()))   // this also sets the newNMEAreceived() flag to false
    {
      // Saving time in buffer
      Now = GPS.hour * 60 + GPS.minute;
      // Saving Location
      Long = GPS.latitudeDegrees;
      Lat = GPS.longitudeDegrees;

      // DEBUG
      Serial.println("Now = " + String(Now));
      Serial.println("Long = " + String(Long));
      Serial.println("Lat = " + String(Lat));
      Serial.println("Fix = " + String((int)GPS.fix));
      Serial.println("Qual = " + String((int)GPS.fixquality));
      Serial.println("Sat = " + String((int)GPS.satellites));
      Serial.println("Speed = " + String(GPS.speed));
      // DEBUG
    }
  }
}

/*
  Sends command and receives start-end times
  Format: [FIRST]_[SECOND] in minutes (ex: 480_1439)
*/
void get_time_interval()
{
  int _strt, _start, _end;
  String message;

  for (uint8_t i = 0; i < SERIAL_RETRY; i++)
  {
    RPi.println(INTERVAL_CMD);      // Send Interval command
    // Safe loop to listen for serial
    _strt = millis();
    while (millis() - _strt < (SERIAL_TIMEOUT_S * 1000))
    {
      if (RPi.available())
      {
        message = RPi.readString();   // Getting message
        // DEBUG
        Serial.println("GOT: " + message);
        // DEBUG
        sscanf(message.c_str(), "%d_%d", &_start, &_end);
        // Error checking
        if (_start > 0 && _start < 1439 && _end > 0 && _end < 1439)
        {
          Start = _start;
          End = _end;
          RPi.println(HANDSHAKE_CMD); // Letting Pi know we got data
          return; // break out of the loop
        }
      }
    }
  }
}

/*
  Send command to Pi + HandShake
  0 - HandShake success
  1 - HandShake failed
*/
int send_RPi(String _msg)
{
  int _strt;
  String message;

  for (uint8_t i = 0; i < SERIAL_RETRY; i++)
  {
    RPi.println(_msg);    // Send Data command
    // Waiting for handshake
    _strt = millis();
    while (millis() - _strt < (SERIAL_TIMEOUT_S * 1000))
    {
      if (RPi.available())
      {
        if (RPi.readString() == HANDSHAKE_CMD)
          return 0;
      }
    }
  }
  return 1;
}

/*
  Returns a Date-Time String
  Format: YYYY_MM_DD_hh_mm
*/
String get_time_string()
{
  return String("20" + String(GPS.year) + DELIM + String(GPS.month) + DELIM
                + String(GPS.day) + DELIM + String(GPS.hour) + DELIM + String(GPS.minute));
}
