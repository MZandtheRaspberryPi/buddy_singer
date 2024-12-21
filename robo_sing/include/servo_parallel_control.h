#include <Servo.h> 

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

  faceMotion.baseServoAngle = constrain(faceMotion.baseServoAngle, 10, 170);
  faceMotion.tiltServoAngle = constrain(faceMotion.tiltServoAngle, 50, 120);
  faceMotion.nodServoAngle = constrain(faceMotion.nodServoAngle, 80, 150);

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
