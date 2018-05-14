/*
   Feb 22, 2018
   Simulates GPS reading
*/

#include <SoftwareSerial.h>

// GPIO
#define TX       4
#define RX       8

/* Time interval */
int year = 2018;
int month = 2;
int day = 26;
int hour = 15;
int minute = 4;
int second = 0;

SoftwareSerial port (RX, TX);

struct sGPS {
  int _minutes = 20;
  double _long = 10.12;
  double _lat = 10.21;
};

#define BUFFER 100
sGPS GPS[BUFFER];

/* Programs Starts */
void setup ()
{
  Serial.begin(115200);       // DEBUG
  Serial.println("START");  // DEBUG

  // Start Serial COM with PI
  port.begin(9600);

  pinMode(RX, INPUT);
  pinMode(TX, OUTPUT);

}

/* Program Loop */
void loop ()
{
  
  String message;
  /* Message from RPI */
  if (port.available())
  {
    message = port.readString();
    Serial.println("\nGOT: " + message);
    if (message == "TIME")
      port.println(getTime());
    if (message == "GPS")
      port.println(getTime() + ";" + String(random(0, 100)) + ";" + String(random(0, 100)));
  }
  if (Serial.available())
    port.println(Serial.readString());
  delay(1000);
  second++;
  checkOverflow();
}

void checkOverflow()
{
  if (second >= 60)
  {
    second -= 60;
    minute ++;
  }
  if (minute >= 60)
  {
    minute -= 60;
    hour ++;
  }
  if (hour >= 24)
  {
    hour -= 24;
    day ++;
  }
  if (day >= 30)
  {
    day -= 30;
    month ++;
  }
}


String getTime()
{
  return String(year) + "_" + String(month) + "_" + String(day)
         + "_"  + String(hour) + ":" + String(minute) + ":" + String(second);
}

void populateGPS(sGPS*)
{
  
}


