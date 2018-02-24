/*
   Feb 16, 2018
   Timer program to trigger a valve
*/

#include "LowPower.h"

// GPIO
#define VALVE 4

//////////////////////////////////////////////////////////
//                                                      //
//     Change time interval for the timer (hours)       //
//                                                      //
#define TIME_INTERVAL 48  // In Hours                   //
//                                                      //
//////////////////////////////////////////////////////////

int seconds = 0, minutes = 0, hours = 0;

/* Programs Starts */
void setup ()
{
  Serial.begin(9600);       // DEBUG
  Serial.println("START");  // DEBUG
  // Configure the Valve pin
  pinMode(VALVE, OUTPUT);
  digitalWrite(VALVE, LOW);
}

/* Program Loop */
void loop ()
{
  LowPower.idle(SLEEP_8S, ADC_OFF, TIMER2_OFF, TIMER1_OFF, TIMER0_OFF, SPI_OFF, USART0_OFF, TWI_OFF);
  update_time();
  // Check Time
  if ( hours >= TIME_INTERVAL)
  {
    // DEBUG
    Serial.println("RELEASE");
    // DEBUG
    digitalWrite(VALVE, HIGH);  // Trigger Release Valve
    while (1);                  // Mission accomplished
  }
  // DEBUG
  Serial.println(String(hours) + ":" + String(minutes) + ":" + String(seconds));
  // DEBUG
}

/* Updates time in 8s intervals */
void update_time()
{
  seconds += 8;
  // Seconds overflow
  if (seconds >= 60) {
    seconds -= 60;
    minutes += 1;
  }
  // Minutes overflow
  if (minutes >= 60) {
    minutes -= 60;
    hours += 1;
  }
}

