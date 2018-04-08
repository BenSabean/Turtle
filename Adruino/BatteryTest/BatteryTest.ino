/*
 * Apr 4, 2018
 * Battery auto shutdown test
 */

void setup() 
{
  pinMode(13, OUTPUT);
  pinMode(2, OUTPUT);

  digitalWrite(13, HIGH);
  digitalWrite(2, LOW);
  
  delay(10*1000);
  digitalWrite(13, LOW);

  delay(20*1000);
  digitalWrite(2, HIGH);
  
}

void loop() 
{
  // put your main code here, to run repeatedly:

}
