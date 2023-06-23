#include <Servo.h>

Servo ESC;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  ESC.attach(7, 1000, 2000);
  ESC.writeMicroseconds(200); // Send stop signal to esc so it will arm
  delay(10000);
}

void loop() {
  // put your main code here, to run repeatedly:

  // Motor does not spin until 29
  for(int i = 25; i <= 180; i = i + 2) {
    ESC.write(i);
    Serial.print("i: ");
    Serial.print(i);
    Serial.print("\n");
    delay(3000);
  }
