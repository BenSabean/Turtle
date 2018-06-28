/*
   June 22, 2018

   Timing controller program
   Using I2C protocol to interface with Raspberry Pi
   Excepts various commands from the Pi:
   0x01 - Starts sleep timer for the Pi
   0x02 - Triggers release system after a cirtain period of time

   I2C message format:
   [Operation code][msg lenght][Hour][Minute]
   I2C status return:
   [SleepMode][ReleaseMode][BattVoltage]
*/

#include <Wire.h>         // I2C protocol library

#define VALVE       7     // Release MOSFET control (HIGH-ON, LOW-OFF)
#define BATTERY     A1    // Battery Monitor pin
#define WAKEPIN     12    // Pi Power MOSFET control (LOW-ON, HIGH-OFF)
#define ALIVE       11    // Checking Pi Status
#define SLEEP_LED   10    // Sleep mode indicator
#define PCB_LED     13    // LED on the PCB

#define I2C_ADDRESS 0x05
#define SLEEP_CODE  0x01
#define VALVE_CODE  0x02
#define CHECK_CODE  0xAA

#define PI_SHUTDOWN_S 300

volatile uint32_t t_Sleep = 0, Sleep = 0, t_Release = 0, Release = 0, Sec = 0;
volatile bool Sleep_mode = false;
volatile bool Release_mode = false;
volatile bool New_msg = false;
volatile bool LED_state = false;
volatile uint64_t Start = 0;
volatile uint16_t Voltage = 0;

//  INIT //
void setup()
{
  //  GPIO setup  //
  pinMode(VALVE, OUTPUT);
  pinMode(SLEEP_LED, OUTPUT);
  pinMode(PCB_LED, OUTPUT);
  pinMode(BATTERY, INPUT);
  pinMode(ALIVE, INPUT);
  pinMode(A4, INPUT);           // I2C pins setup
  pinMode(A5, INPUT);           // I2C pins setup
  digitalWrite(VALVE, LOW);     // Valve OFF
  // Initial setup
  digitalWrite(SLEEP_LED, LOW);

  //  I2C setup  //
  Wire.begin(I2C_ADDRESS);      // join i2c bus with address
  Wire.onReceive(receiveEvent); // register event
  Wire.onRequest(sendEvent);

  for (uint8_t i = 0; i < 15; i++)
  {
    digitalWrite(PCB_LED, HIGH);     // Valve OFF
    delay(200);
    digitalWrite(PCB_LED, LOW);     // Valve OFF
    delay(200);
  }
  // Trigger the Pi on reset
  triggerPi();

  //  DEBUG  //
  Serial.begin(38400);           // start serial for output
  Serial.println("START");
}

//  MAIN LOOP  //
void loop()
{
  // When message received from i2c //
  if (New_msg == true)
  {
    parseMessage(); // Getting data from I2C register
    New_msg = false;
  }

  // Checking for start of Sleep mode //
  if (Sleep_mode) digitalWrite(SLEEP_LED, HIGH); // Turning indicator ON
  else            digitalWrite(SLEEP_LED, LOW);    // Turning indicator OFF

  // Checking for end of Sleep mode //
  if (Sleep_mode && (t_Sleep >= Sleep))
  {
    Sleep_mode = false;
    t_Sleep = 0;               // Reset sleep timer !
    triggerPi();
    Serial.println("Pi Triggered");
  }

  // Checking for end of Release mode //
  if (Release_mode == true && (t_Release >= Release))
  {
    Release_mode = false;
    t_Release = 0;            // Reset release timer !
    digitalWrite(VALVE, HIGH);  // Turning Pi OFF
    Serial.println("Release valve TRIGGERED!");
  }

  // Check if 1 sec past  //
  if (millis() - Start > 1000)
  {
    Start = millis();                 // reset timer
    Sec++;                            // increment sec counter
    digitalWrite(PCB_LED, LED_state); // flick the LED
    LED_state = (LED_state == true) ? false : true;
    Voltage = analogRead(BATTERY);    // Saving battery Voltage
  }
  // In case of overflow
  if (Start > millis()) Start = millis();

  // Keeping track of time with seconds
  if (Sec >= 60)
  {
    Sec = 0;                          // seconds overflow
    // Sleep mode active
    if (Sleep_mode) t_Sleep ++;
    else t_Sleep = 0;

    // Rlease mode active
    if (Release_mode) t_Release ++;
    else t_Release = 0;

    if (Sleep_mode) Serial.println("Sleep: " + String(t_Sleep + 1) + " out of " + String(Sleep));
    if (Release_mode) Serial.println("Release: " + String(t_Release + 1) + " out of " + String(Release));
  }
}

//  FUNCTIONS  //
//
//  Interrrupt function, gets triggered when I2C new data available
//
void receiveEvent()
{
  New_msg = true;   // sets a flag for the main program
}

//
//  function that receives I2C data and parses it
//
void parseMessage()
{
  byte hour = 0, min = 0, OP = 0;

  // Reading Operation Code
  if (Wire.available()) OP = Wire.read();
  else return;
  // Reading Hours
  if (Wire.available()) hour = Wire.read();
  else return;
  // Reading Minutes
  if (Wire.available()) min = Wire.read();
  else return;

  // Power timer command
  if (OP == SLEEP_CODE)
  {
    // Starting Sleep mode
    Sleep = (((uint32_t)hour) * 60) + (uint32_t)min;
    if (Sleep > 1500) // Error checking
    {
      Sleep = 0;
      return;
    }
    // Setting up mode parameters
    Sec = 0;
    Sleep_mode = true;
    Serial.println("sleeping for: " + String(Sleep) + " min");
  }
  // Valve command
  if (OP == VALVE_CODE)
  {
    // Starting Sleep mode (CRC succsess)
    Release = (((uint32_t)hour) * 60) + (uint32_t)min;
    if (Release > 9000) // Error checking
    {
      Release = 0;
      return;
    }
    // Setting up mode parameters
    Sec = 0;
    Release_mode = true;
    Serial.println("Releasing in: " + String(Release) + " min");
  }
}

//
//  Grounds pin 5 (SCL) on Raspberry pi to wake it up
//
void triggerPi()
{
  digitalWrite(WAKEPIN, LOW);   // setting pin LOW
  pinMode(WAKEPIN, OUTPUT);     // switching port from High-Z to OUTPUT
  delay(1);
  pinMode(WAKEPIN, INPUT);      // enabling Tri-state
}

//
//  Interrrupt function, gets triggered when I2C master requests data
//  Sends pack the mode status: [Sleep0/1][Release 0/1][VoltageLSB][VoltageMSB]
//
void sendEvent()
{
  byte resp[] = {0, 0, 0, 0};

  resp[0] = (Sleep_mode == true) ? 0x01 : 0x00;
  resp[1] = (Release_mode == true) ? 0x01 : 0x00;
  resp[2] = (byte) (Voltage & 0x00FF);
  resp[3] = (byte) ((Voltage & 0xFF00) >> 8);
  Wire.write(resp, 4);

  //Serial.println("Sent " + String(resp[0]) + " , " + String(resp[1]) + " , " + String(resp[2]) + " , " + String(resp[3]));
  //Serial.println("Voltage: " + String(Voltage));
}

