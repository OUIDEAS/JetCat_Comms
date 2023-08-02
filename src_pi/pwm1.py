# Script for testing the PWM pinout on a RPi 4 model B

import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BOARD)

pwm_pin = 12

GPIO.setup(pwm_pin, GPIO.OUT)
GPIO.setwarnings(False)
pi_pwm = GPIO.PWM(pwm_pin, 1000)
pi_pwm.start(0)

while True:
    for duty in range(0,101,1):
        pi_pwm.ChangeDutyCycle(duty) #provide duty cycle in the range 0-100
        time.sleep(0.01)
    time.sleep(0.5)
    for duty in range(100,-1,-1):
        pi_pwm.ChangeDutyCycle(duty)
        time.sleep(0.01)
    time.sleep(0.5)


