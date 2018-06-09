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

#define PI_SHUTDOWN_S 30

volatile uint32_t t_Sleep = 0, Sleep = 0, t_Release = 0, Release = 0, Sec = 0;
volatile bool Sleep_mode = false;
volatile bool Release_mode = false;
volatile byte OP = 0;

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

  //  DEBUG  //
  Serial.begin(38400);           // start serial for output
  Serial.println("START");
}

//  MAIN LOOP  //
void loop()
{
  // When message received from i2c //
  if (OP == SLEEP_CODE || OP == VALVE_CODE)
  {
    parseMessage(); // Gettting data from I2C register
    OP = 0;         // Reseting Operation Code
  }

  // Checking for end of Sleep mode //
  if (Sleep_mode == true && (t_Sleep >= Sleep))
  {
    Sleep_mode = false;
    t_Sleep = 0;               // Reset sleep timer !
    digitalWrite(LED, LOW);    // Turning indicator OFF
    digitalWrite(POWER, LOW);  // Turning Pi ON
    Serial.println("Sleep mode ENDED");
  }

  // Checking for end of Release mode
  if (Release_mode == true && (t_Release >= Release))
  {
    Release_mode = false;
    t_Release = 0;            // Reset release timer !
    digitalWrite(VALVE, HIGH);  // Turning Pi OFF
    Serial.println("Release valve TRIGGERED!");
  }

  // Keeping track of time with seconds
  Sec ++;
  if (Sec >= 60)
  {
    Sec = 0;
    if (Sleep_mode)
    {
      Serial.println("Sleep: " + String(t_Sleep + 1) + " out of " + String(Sleep));
      t_Sleep ++;
    }
    if (Release_mode)
    {
      Serial.println("Release: " + String(t_Release + 1) + " out of " + String(Release));
      t_Release ++;
    }
  }
  Serial.println("................");
  Delay(1); // Delay for 1 sec
}


//  FUNCTIONS  //
//
//  Interrrupt function, gets triggered when I2C data available
//
void receiveEvent()
{
  byte resp[2] = {0, 0};
  // Check and save operation code
  if (Wire.available()) OP = Wire.read();
  else return;
  // if Pi checks the status, return status
  if (OP == CHECK_CODE)
  {
    resp[0] = (Sleep_mode == true) ? 0x01 : 0x00;
    resp[1] = (Release_mode == true) ? 0x01 : 0x00;
    Wire.write(resp, sizeof(resp));
    Serial.println("Sent " + String(resp[0]) + " , " + String(resp[1]));
  }
}

//
//  function that receives I2C data and parses it
//
void parseMessage()
{
  byte msg[2], received_crc = 0, len = 0;

  // Reading Message Length
  if (Wire.available()) len = Wire.read();
  else return;
  // Reading Hours
  if (Wire.available()) msg[0] = Wire.read();
  else return;
  // Reading Minutes
  if (Wire.available()) msg[1] = Wire.read();
  else return;
  // Reading CRC
  if (Wire.available()) received_crc = Wire.read();
  else return;
  // Error checking
  if (received_crc != CRC(msg, 2))
    return;

  // Power timer command
  if (OP == SLEEP_CODE)
  {
    // Starting Sleep mode (CRC succsess)
    Sleep = (((uint32_t) msg[0]) * 60) + ((uint32_t) msg[1]);
    if (Sleep > 1500) { // Error checking
      Sleep = 0;
      return;
    }
    Serial.println("sleeping for: " + String(Sleep) + " min");
    Sleep_mode = true;
    t_Sleep = 0;
    waitShutdown();
    Serial.println("Shutdown");
    digitalWrite(LED, HIGH);    // Turning indicator ON
    digitalWrite(POWER, HIGH);  // Turning Pi OFF
  }
  // Valve command
  else if (OP == VALVE_CODE)
  {
    // Starting Sleep mode (CRC succsess)
    Release = ((uint32_t)msg[0] * 60) + (uint32_t)msg[1];
    if (Release > 9000) { // Error checking
      Release = 0;
      return;
    }
    Serial.println("Releasing in: " + String(Release) + " min");
    Release_mode = true;
    t_Release = 0;
  }
}

//
//  This function is used to calculate CRC
//
byte CRC(byte* arr, byte len)
{
  byte crc = 0, _byte = 0;
  // Loop throught the lenght of the message
  for (byte i = 0; i < len; i++)
  {
    _byte = arr[i];
    // Loop throught the bits
    for (byte b = 0; b < 8; b++, _byte <<= 1)
    {
      if ((_byte ^ crc) & 0x80)
        crc = (crc << 1) ^ 0x31;
      else
        crc = (crc << 1);
    }
    crc = crc & 0xFF;
  }
  return crc;
}

//
//  Delay function in seconds
//
void Delay(uint64_t sec)
{
  uint64_t start = millis();

  // Waiting for the time interval + checking for overflow
  while (millis() - start < sec * 1000) {
    if (millis() < start) start = millis();
  }
  /*
    for (; sec > 0; sec--)
      LowPower.idle(SLEEP_1S, ADC_OFF, TIMER2_ON, TIMER1_ON,
                   TIMER0_ON, SPI_OFF, USART0_ON, TWI_ON);
  */
}

//
//  Waiting for Pi to shutdown, switching the power off with timeout
//
void waitShutdown ()
{
  // Give Pi time to shutdown + checking alive signal
  // Forcing the Pi to shutdown by cutting the power after a while
  for (int i = 0; i < PI_SHUTDOWN_S && digitalRead(ALIVE) == 1; i++, Delay(1));
}

