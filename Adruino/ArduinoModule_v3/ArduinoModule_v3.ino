/*
   June 7, 2018

   Timing controller program
   Using I2C protocol to interface with Raspberry Pi
   Excepts various commands from the Pi:
   0x01 - Starts sleep timer for the Pi
   0x02 - Triggers release system after a cirtain period of time
   ...

   I2C message format:
   [Operation code][msg lenght][Hour][Minute][CRC]

*/

#include <Wire.h>         // I2C protocol library
//#include <LowPower.h>     // Decreases Power consumption

#define VALVE       2     // Release MOSFET control (HIGH-ON, LOW-OFF)
#define BATTERY     A1    // Battery Monitor pin
#define POWER       12    // Pi Power MOSFET control (LOW-ON, HIGH-OFF)
#define ALIVE       11    // Checking Pi Status
#define LED         10    // Sleep mode indicator

#define I2C_ADDRESS 0x05
#define SLEEP_CODE  0x01
#define VALVE_CODE  0x02
#define CHECK_CODE  0xAA

#define PI_SHUTDOWN_S 300

volatile uint32_t t_Sleep = 0, Sleep = 0, t_Release = 0, Release = 0, Sec = 0, t_Shutdown = 0;
volatile bool Sleep_mode = false;
volatile bool Release_mode = false;
volatile bool New_msg = false;
volatile bool Once = false;
volatile byte OP = 0;
volatile uint64_t Start = 0;

//  INIT //
void setup()
{
  //  GPIO setup  //
  pinMode(VALVE, OUTPUT);
  pinMode(POWER, OUTPUT);
  pinMode(LED, OUTPUT);
  pinMode(BATTERY, INPUT);
  pinMode(ALIVE, INPUT);
  pinMode(A4, INPUT);           // I2C pins setup
  pinMode(A5, INPUT);           // I2C pins setup
  digitalWrite(VALVE, LOW);     // Valve OFF
  digitalWrite(POWER, LOW);     // Starting the Pi on boot
  digitalWrite(LED, LOW);

  //  I2C setup  //
  Wire.begin(I2C_ADDRESS);      // join i2c bus with address
  Wire.onReceive(receiveEvent); // register event
  Wire.onRequest(sendEvent);

  // Initializing timer var //
  Start = millis();

  /*
    //  DEBUG  //
    Serial.begin(38400);           // start serial for output
    Serial.println("START");
  */
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
  if (Sleep_mode == true && Once == false && (t_Shutdown > PI_SHUTDOWN_S || digitalRead(ALIVE) == 0))
  {
    Once = true;
    t_Shutdown = 0;
    digitalWrite(LED, HIGH);    // Turning indicator ON
    digitalWrite(POWER, HIGH);  // Turning Pi OFF
    //Serial.println("Shutdown");
  }

  // Checking for end of Sleep mode //
  if (Sleep_mode == true && (t_Sleep >= Sleep))
  {
    Sleep_mode = false;
    t_Sleep = 0;               // Reset sleep timer !
    digitalWrite(LED, LOW);    // Turning indicator OFF
    digitalWrite(POWER, LOW);  // Turning Pi ON
    //Serial.println("Sleep mode ENDED");
  }

  // Checking for end of Release mode
  if (Release_mode == true && (t_Release >= Release))
  {
    Release_mode = false;
    t_Release = 0;            // Reset release timer !
    digitalWrite(VALVE, HIGH);  // Turning Pi OFF
    //Serial.println("Release valve TRIGGERED!");
  }

  // Check if 1 sec past
  if (millis() - Start > 1000)
  {
    Start = millis();
    Sec++;
    if (Once == false && Sleep_mode) t_Shutdown++;
    //Serial.println(t_Shutdown);
  }
  // In case of overflow
  if (Start > millis()) Start = millis();
  // Keeping track of time with seconds
  if (Sec >= 60)
  {
    Sec = 0;
    // Sleep mode active
    if (Sleep_mode)
    {
      //Serial.println("Sleep: " + String(t_Sleep + 1) + " out of " + String(Sleep));
      t_Sleep ++;
    }
    else t_Sleep = 0;
    // Rlease mode active
    if (Release_mode)
    {
      t_Release ++;
      //Serial.println("Release: " + String(t_Release + 1) + " out of " + String(Release));
    }
    else t_Release = 0;
  }
}


//  FUNCTIONS  //
//
//  Interrrupt function, gets triggered when I2C new data available
//
void receiveEvent()
{
  New_msg = true;
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
    // Starting Sleep mode (CRC succsess)
    Sleep = (((uint32_t)hour) * 60) + (uint32_t)min;
    if (Sleep > 1500) // Error checking
    {
      Sleep = 0;
      t_Sleep = 0;
      return;
    }
    // Setting up mode parameters
    Sec = 0;
    Sleep_mode = true;
    t_Sleep = 0;
    t_Shutdown = 0;
    Once = false;
    //Serial.println("sleeping for: " + String(Sleep) + " min");
  }
  // Valve command
  if (OP == VALVE_CODE)
  {
    // Starting Sleep mode (CRC succsess)
    Release = (((uint32_t)hour) * 60) + (uint32_t)min;
    if (Release > 9000) // Error checking
    {
      Release = 0;
      t_Release = 0;
      return;
    }
    // Setting up mode parameters
    Sec = 0;
    Release_mode = true;
    t_Release = 0;
    //Serial.println("Releasing in: " + String(Release) + " min");
  }
}

//
//  Delay function in seconds
//
/*
  void Delay(uint64_t sec)
  {
    for (; sec > 0; sec--)
      LowPower.idle(SLEEP_1S, ADC_OFF, TIMER2_ON, TIMER1_ON,
                   TIMER0_ON, SPI_OFF, USART0_ON, TWI_ON);
  }
*/

//
//  Interrrupt function, gets triggered when I2C master requests data
//  Sends pack the mode status - Sleep 0/1 Release 0/1
//
void sendEvent()
{
  byte resp[2] = {0, 0};

  resp[0] = (Sleep_mode == true) ? 0x01 : 0x00;
  resp[1] = (Release_mode == true) ? 0x01 : 0x00;
  Wire.write(resp, 2);
  //Serial.println("Sent " + String(resp[0]) + " , " + String(resp[1]));
}

