int pinLed = PD3;
int blinkDuration = 500;

void setup() {
  Serial.begin(9600);
  Serial.println("Hello from blink cloud");
  pinMode(pinLed, OUTPUT);
}


void loop() {
  static unsigned long lastChange = 0;
  static bool b = true;
  int p = Serial.read();
  if (p>0) {
    blinkDuration = p * 100;
    Serial.print("Recieved ");
    Serial.print(p);
    Serial.print(". Setting blink rate to ");
    Serial.println(blinkDuration);
  }
  unsigned long l = millis() - lastChange;
  if (l >= blinkDuration) {
    digitalWrite(pinLed, b);
    b = !b;
    lastChange = millis();
  }
}
