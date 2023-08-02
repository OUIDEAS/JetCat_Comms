void setup() {
  // put your setup code here, to run once:
  pinMode(8, OUTPUT);
  Serial.begin(115200);
  while(!Serial);
  analogWrite(8, 0);
}

void loop() {
  // put your main code here, to run repeatedly:
  static int flag = 0;
  if (flag==0) {
    Serial.println("Enter PWM value: ");
    flag = 1;
  }
  if (Serial.available()) {
//    Serial.println("Ser available");
    int pwm_val = Serial.parseInt();
    Serial.print("Wrote value ");
    Serial.print(pwm_val);
    Serial.println(" to PWM pin");
    int waste = Serial.parseInt();
    flag = 0;
    analogWrite(8, pwm_val);
    
  }
//  delay(1000);




//  while(!Serial.available()){
//    int value = Serial.parseInt();
//    Serial.println(value);
//  }
}
