/*
   Date: Apr 11. 2018
   Simlator program
   Imitates commands send by Pi
*/

#include <SoftwareSerial.h>

// Command list
#define INTERVAL_CMD   "INTERVAL"
#define HANDSHAKE_CMD  "OK"
#define GPS_LOG_CMD    "GPS_LOG"
#define GPS_DUMP_CMD   "GPS_DUMP"
#define GPS_ERASE_CMD  "GPS_ERASE"
#define TIME_CMD       "TIME"
#define SLEEP_CMD      "SLEEP"
#define DELIM          "_"


SoftwareSerial Arduino(2, 3);       // RX and TX for RPI COM

void setup()
{
  Arduino.begin(19200);
  Serial.begin(115200);

}

void loop()
{
  char buff[100]; memset(buff, '\0', sizeof(buff));
  String msg;
  
  Serial.println("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n --- Commands --- ");
  Serial.println(INTERVAL_CMD);
  Serial.println(HANDSHAKE_CMD);
  Serial.println(GPS_LOG_CMD);
  Serial.println(GPS_DUMP_CMD);
  Serial.println(GPS_ERASE_CMD);
  Serial.println(TIME_CMD);
  Serial.println(SLEEP_CMD);
  Serial.println("Enter command:");

  while(!Serial.available());

  msg = Serial.readString();
  Serial.println(msg);
  // Flush buffer
  Arduino.readString();
  // Send command
  Arduino.print(msg);

  Serial.println(" --- Response --- ");
  uint32_t start = millis();
  while(millis() - start < 20 * 1000)
  {
    // if millis() or timer wraps around, we'll just reset it
    if (start > millis())  start = millis();
    
    if(Arduino.available())
    {
      memset(buff, '\0', sizeof(buff));
      readString(buff, sizeof(buff));
      Serial.println(buff);
      break;
    }
  }

}


/*
   Function to read incomming serial string
*/
void readString (char* buff, int len)
{
  String msg;
  msg = Arduino.readString();
  strcpy(buff, msg.c_str());
}
