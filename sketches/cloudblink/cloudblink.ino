int pinLed = PD3;
int blinkDuration = 500;

void setup() {
  Serial.begin(38400);
  pinMode(pinLed, OUTPUT);
}


void loop() {
  static unsigned long lastChange = 0;
  static bool b = true;
  int p = Serial.read();
  if (p>0) {
    blinkDuration = p * 100;
  }
  unsigned long l = millis() - lastChange;
  if (l >= blinkDuration) {
    digitalWrite(pinLed, b);
    b = !b;
    lastChange = millis();
  }
}
