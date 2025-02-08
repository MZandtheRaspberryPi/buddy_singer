#include <Servo.h> 

const uint8_t NOD_MIN = 80;
const uint8_t NOD_MAX = 150;
const uint8_t NOD_MIDDLE = NOD_MIN + (NOD_MAX - NOD_MIN) / 2;
const uint8_t BASE_MIN = 10;
const uint8_t BASE_MAX = 170;
const uint8_t BASE_MIDDLE = BASE_MIN + (BASE_MAX - BASE_MIN) / 2;
const uint8_t TILT_MIN = 50;
const uint8_t TILT_MAX = 120;
const uint8_t TILT_MIDDLE = TILT_MIN + (TILT_MAX - TILT_MIN) / 2;

// Robot Joint Motion Stuctures
struct HeadPos {
  int baseServoAngle;
  int nodServoAngle ;
  int tiltServoAngle ;
  int desiredDelay ;
};

int servoParallelControl (int pos, Servo& servo, int speed ) {

  int startPos = servo.read();        //read the current pos
  int newPos = startPos;

  // define where the pos is with respect to the command
  // if the current position is less that the actual move up
  if (startPos < (pos - 5)) {
    newPos = newPos + 1;
    servo.write(newPos);
    delay(speed);
    return 0;
  }

  else if (newPos > (pos + 5)) {
    newPos = newPos - 1;
    servo.write(newPos);
    delay(speed);
    return 0;
  }

  else {
    return 1;
  }

}

void moveTo(struct HeadPos& faceMotion, Servo& baseServo, Servo& nodServo, Servo& tiltServo) {

  faceMotion.baseServoAngle = constrain(faceMotion.baseServoAngle, BASE_MIN, BASE_MAX);
  faceMotion.tiltServoAngle = constrain(faceMotion.tiltServoAngle, TILT_MIN, TILT_MAX);
  faceMotion.nodServoAngle = constrain(faceMotion.nodServoAngle, NOD_MIN, NOD_MAX);

  int status1 = 0;
  int status2 = 0;
  int status3 = 0;
  int done = 0 ;

  while ( done == 0) {
    //move all servos to the desired position
    //this loop will cycle through the servos sending each the desired position.
    //Each call will cause the servo to iterate about 1-5 degrees
    //the rapid cycle of the loop makes the servos appear to move simultaneously
    status1 = servoParallelControl(faceMotion.baseServoAngle, baseServo, faceMotion.desiredDelay);
    status2 = servoParallelControl(faceMotion.nodServoAngle, nodServo, faceMotion.desiredDelay);
    status3 = servoParallelControl(faceMotion.tiltServoAngle, tiltServo, faceMotion.desiredDelay);

    //continue until all have reached the desired position
    if (status1 == 1 && status2 == 1 && status3 == 1 ) {
      done = 1;
    }
  }// end of while
} //function end
