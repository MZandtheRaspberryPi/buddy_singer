#include <Arduino.h>
#include <Servo.h> 

#include "pin_mapping.h"
#include "servo_parallel_control.h"
#include "song_reader.h"

byte serialBuffer[4];
HeadPos faceMotion;
Servo baseServo;
Servo nodServo;
Servo tiltServo;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  // if analog input pin 0 is unconnected, random analog
  // noise will cause the call to randomSeed() to generate
  // different seed numbers each time the sketch runs.
  // randomSeed() will then shuffle the random function.
  randomSeed(analogRead(0));

  baseServo.attach(baseServoPin);
  nodServo.attach(nodServoPin);
  tiltServo.attach(tiltServoPin);

  faceMotion.desiredDelay = 0;
  faceMotion.baseServoAngle = BASE_MIDDLE;
  faceMotion.nodServoAngle = NOD_MIDDLE;
  faceMotion.tiltServoAngle = TILT_MIDDLE;

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);

  noTone(buzzerPin);
  droidSpeak(buzzerPin, 5);
  faceMotion.desiredDelay = 3;
  faceMotion.baseServoAngle = 100;
  faceMotion.nodServoAngle = 140;
  faceMotion.tiltServoAngle = 90;
  for (int i = 0; i < 2; i++) {

    faceMotion.tiltServoAngle = 90 + 50;
    moveTo(faceMotion, baseServo, nodServo, tiltServo);
    faceMotion.tiltServoAngle = 90 - 50;
    moveTo(faceMotion, baseServo, nodServo, tiltServo);
  }

  faceMotion.tiltServoAngle = 90;
  moveTo(faceMotion, baseServo, nodServo, tiltServo);
  delay(200);

}

void loop() {
  // put your main code here, to run repeatedly:

  if (Serial.available() > 0) {
    Serial.readBytes(serialBuffer, 4);
    unsigned int freq = unpackInt(serialBuffer);
    Serial.readBytes(serialBuffer, 4);
    unsigned int delta_t = unpackInt(serialBuffer);
    
    if (freq == 0)
    {
      noTone(buzzerPin);
      return;
    }
    tone(buzzerPin,  freq);


    unsigned int n =  ( 12 * (log((float)freq / 440.0) / log(2)) ) + 69.01 ;
    unsigned int zoomed_n = max(62, min(n, 74));
    uint8_t nod_target_angle = map(zoomed_n, 62, 74, NOD_MAX, NOD_MIN);

    uint8_t base_target_angle = 0;
    if (faceMotion.baseServoAngle <= BASE_MIDDLE)
    {
      base_target_angle = map(random(30), 0, 30, BASE_MIDDLE, BASE_MAX-40);
    }
    else
    {
      base_target_angle = map(random(30), 0, 30, BASE_MIN + 40, BASE_MIDDLE);
    }

    uint8_t tilt_target_angle = 0;
    if (faceMotion.tiltServoAngle <= TILT_MIDDLE)
    {
      tilt_target_angle = map(random(30), 0, 30, TILT_MIDDLE, TILT_MAX);
    }
    else
    {
      tilt_target_angle = map(random(30), 0, 30, TILT_MIN, TILT_MIDDLE);
    }

    int8_t nod_diff = nodServo.read() - nod_target_angle;
    int8_t base_diff = baseServo.read() - base_target_angle;
    int8_t tilt_diff = tiltServo.read() - tilt_target_angle;
    uint8_t biggest_diff = max(abs(nod_diff), max(abs(base_diff), abs(tilt_diff)));
    uint8_t delay_ms = 1;
    faceMotion.desiredDelay = delay_ms;
    // faceMotion.baseServoAngle = base_target_angle;
    faceMotion.nodServoAngle = nod_target_angle;
    faceMotion.tiltServoAngle = tilt_target_angle;
    moveTo(faceMotion, baseServo, nodServo, tiltServo);

  }
}
