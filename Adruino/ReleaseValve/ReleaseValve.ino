/*
   Feb 16, 2018
   Timer program to trigger a valve
*/

// GPIO
#define VALVE   4
#define LED     13

//////////////////////////////////////////////////////////
//                                                      //
//   Time interval for the timer days+hours+minutes     //
//                                                      //
#define DAYS    0                                       //
#define HOURS   0                                       //
#define MINUTES 1                                       //
//                                                      //
//////////////////////////////////////////////////////////

// Variables to hold current counter status
int seconds = 0, minutes = 0, hours = 0, days = 0, now = 0;
// Calculating recording interval in minutes
int recording_interval = DAYS * 1440 + HOURS * 60 + MINUTES;

/* Programs Starts */
void setup ()
{
  Serial.begin(230400);       // DEBUG
  Serial.println("START");  // DEBUG
  // Configure the Valve pin
  pinMode(VALVE, OUTPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(VALVE, LOW);
  digitalWrite(LED, LOW);
}

/* Program Loop */
void loop ()
{
  char time[8];
  // Calculating current mission time in minutes
  now = days * 1440 + hours * 60 + minutes;
  // Checking for end of mission
  if ( now >= recording_interval)
  {
    // DEBUG
    Serial.println("RELEASE");
    // DEBUG
    digitalWrite(VALVE, HIGH);  // Trigger Release Valve
    digitalWrite(LED, HIGH);
    while (1);                  // Mission accomplished
  }
  // DEBUG
  sprintf(time, "%d days %02d:%02d:%02d", days, hours, minutes, seconds);
  Serial.println(time);
  // DEBUG
  update_time();
  delay(1 * 1000);
}

/* Updates time in 8s intervals */
void update_time()
{
  seconds += 1;
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
  // Hours overflow
  if (hours >= 24) {
    hours -= 24;
    days += 1;
  }
}

