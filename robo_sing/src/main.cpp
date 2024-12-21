#include <Arduino.h>
#include <Servo.h> 

#include "pin_mapping.h"
#include "servo_parallel_control.h"
#include "song_reader.h"

byte serialBuffer[4];

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  Servo baseServo;
  Servo nodServo;
  Servo tiltServo;
  baseServo.attach(baseServoPin);
  nodServo.attach(nodServoPin);
  tiltServo.attach(tiltServoPin);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);

  // noTone(buzzerPin);
  // delay(200);
  // droidSpeak(buzzerPin, 5);
  // struct HeadPos faceMotion;
  // faceMotion.desiredDelay = 3;
  // faceMotion.baseServoAngle = 100;
  // faceMotion.nodServoAngle = 140;
  // faceMotion.tiltServoAngle = 90;
  // for (int i = 0; i < 2; i++) {

  //   faceMotion.tiltServoAngle = 90 + 50;
  //   moveTo(faceMotion, baseServo, nodServo, tiltServo);
  //   faceMotion.tiltServoAngle = 90 - 50;
  //   moveTo(faceMotion, baseServo, nodServo, tiltServo);
  // }

  // faceMotion.tiltServoAngle = 90;
  // moveTo(faceMotion, baseServo, nodServo, tiltServo);

  // tone(buzzerPin, 440, 1000);

}

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0) {
    Serial.readBytes(serialBuffer, 4);
    unsigned int freq = unpackInt(serialBuffer);
    Serial.write(serialBuffer, 4);
    Serial.readBytes(serialBuffer, 4);
    unsigned int delta_t = unpackInt(serialBuffer);
    Serial.write(delta_t);
    tone(buzzerPin,  freq, delta_t);
  }
}
