#include <Servo.h>

Servo ESC;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  ESC.attach(7, 1000, 2000);
  ESC.writeMicroseconds(200); // Send stop signal to esc so it will arm
  digitalWrite(2, LOW);
  delay(10000);
}

void loop() {
  
  ESC.write(180);
  digitalWrite(2, HIGH);
  delay(10000);
  ESC.write(0);
  digitalWrite(2, LOW);
  exit(0);
}
