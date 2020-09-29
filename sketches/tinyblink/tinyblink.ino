#include <EEPROM.h>


int ledPin = PB3;
void setup() {
  pinMode(ledPin, OUTPUT);
  for (int i = 0; i < 255; i++)
    EEPROM.write(i, i);
}

void loop() {
  static bool b = true;
  digitalWrite(ledPin, b);
  delay(1000);
  b = !b;
}
