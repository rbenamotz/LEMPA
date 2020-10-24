int pinLed = 2;
int blinkDuration = 500;
byte intensity = 100;

void setup() {
  Serial.begin(9600);
  Serial.println("Hello from blink");
  pinMode(pinLed, OUTPUT);
}

void handleSerial() {
  if (!Serial.available()) {
    return;
  }
  byte buf[2];
  int c = Serial.readBytes(buf, 2);
  blinkDuration = buf[0] * 100;
  Serial.print("Blink rate set to ");
  Serial.println(blinkDuration);
  if (c == 0) {
    return;
  }
  intensity = buf[1];
  Serial.print("Intensity set to ");
  Serial.println(intensity);

}

void loop() {
  static unsigned long lastChange = 0;
  static bool b = true;
  handleSerial();
  unsigned long l = millis() - lastChange;
  if (l >= blinkDuration) {
    if (b) {
      analogWrite(pinLed, intensity);
    } else {
      digitalWrite(pinLed, 0);
    }
    b = !b;
    lastChange = millis();
  }
}
