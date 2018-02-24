/*
   Feb 24, 2018
   Program to test Adafruit Ultimate GPS module
*/

#include <SoftwareSerial.h>
#include <Adafruit_GPS.h>

///////////////////////////////////////////
//                                       //
//            DECLARATIONS               //
//                                       //
///////////////////////////////////////////

// GPIO
#define SWITCH  13
#define PI_TX    4
#define PI_RX    5
#define GPS_TX   2
#define GPS_RX   3
#define MOSFET   6

SoftwareSerial RPi(PI_RX, PI_TX);       // RX and TX for RPI COM
SoftwareSerial GPS_COM(GPS_RX, GPS_TX); // RX and TX for GPS COM

/*    GPS Setup    */
Adafruit_GPS GPS (&GPS_COM);
#define GPSECHO  false            // Dont listen to raw GPS data

/* Time interval */
int start, end;

///////////////////////////////////////////
//                                       //
//                SETUP                  //
//                                       //
///////////////////////////////////////////
void setup ()
{
  // Serial for DEBUG setup
  Serial.begin(115200);       // DEBUG
  Serial.println("START");  // DEBUG
  // Start Serial COM with PI
  RPi.begin(9600);
  // GPS initialization commands 
  GPS_init();
  // GPIO setup
  pinMode(SWITCH, INPUT);
  pinMode(MOSFET, OUTPUT);
  // MOSFET is off - PI is off
  digitalWrite(MOSFET, LOW);
}
// I dont know why I need this
uint32_t timer = millis();


///////////////////////////////////////////
//                                       //
//                LOOP                   //
//                                       //
///////////////////////////////////////////
void loop ()
{
  bool success = false;

  success = GPS_update();

  // if millis() or timer wraps around, we'll just reset it
  if (timer > millis())  timer = millis();

    // approximately every 2 seconds or so, print out the current stats
  if (millis() - timer > 2000) 
  { 
    timer = millis(); // reset the timer
    GPS_print();
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
  // Disable Interrups
  TIMSK0 &= ~_BV(OCIE0A);
  delay(1000);
  // Ask for firmware version
  GPS_COM.println(PMTK_Q_RELEASE);
}

/* Update GPS Values */
bool GPS_update()
{
  // New message from the GPS
  if (GPS.newNMEAreceived()) 
  {
    // DEBUG
    Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false
    // Parsing
    if (!GPS.parse(GPS.lastNMEA()))   // this also sets the newNMEAreceived() flag to false
      return 1;  // we can fail to parse a sentence in which case we should just wait for another
    else 
      return 0;
  }
}

/* DEBUG printing GPS Values */
void GPS_print()
{
  Serial.print("\nTime: ");
  Serial.print(GPS.hour, DEC); Serial.print(':');
  Serial.print(GPS.minute, DEC); Serial.print(':');
  Serial.print(GPS.seconds, DEC); Serial.print('.');
  Serial.println(GPS.milliseconds);
  Serial.print("Date: ");
  Serial.print(GPS.day, DEC); Serial.print('/');
  Serial.print(GPS.month, DEC); Serial.print("/20");
  Serial.println(GPS.year, DEC);
  Serial.print("Fix: "); Serial.print((int)GPS.fix);
  Serial.print(" quality: "); Serial.println((int)GPS.fixquality); 
  if (GPS.fix) 
  {
    Serial.print("Location: ");
    Serial.print(GPS.latitude, 4); Serial.print(GPS.lat);
    Serial.print(", "); 
    Serial.print(GPS.longitude, 4); Serial.println(GPS.lon);
    Serial.print("Location (in degrees, works with Google Maps): ");
    Serial.print(GPS.latitudeDegrees, 4);
    Serial.print(", "); 
    Serial.println(GPS.longitudeDegrees, 4);
    
    Serial.print("Speed (knots): "); Serial.println(GPS.speed);
    Serial.print("Angle: "); Serial.println(GPS.angle);
    Serial.print("Altitude: "); Serial.println(GPS.altitude);
    Serial.print("Satellites: "); Serial.println((int)GPS.satellites);
  }
}