
#define LED 2 //Define blinking LED pin

void setup() {
  pinMode(LED, OUTPUT); // Initialize the LED pin as an output
}
// the loop function runs over and over again forever
void loop() {
  digitalWrite(LED, LOW); // Turn the LED on (Note that LOW is the voltage level)
  delay(1000); // Wait for a second
  digitalWrite(LED, HIGH); // Turn the LED off by making the voltage HIGH
  delay(1000); // Wait for two seconds
}
