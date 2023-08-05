#include "SoftwareSerial.h"

#include <avr/sleep.h>

#define dir_1 4
#define pwm_left 3

#define dir_2 7
#define pwm_right 6

#define buzzer 8


const int pingPin = 9; // Trigger Pin of Ultrasonic Sensor
const int echoPin = 10; // Echo Pin of Ultrasonic Sensor

String DEVICE_ID="BNMITAGV1";
String device_id; // Variable to store the device ID
String duration_received; 
String speed_received; 

String direction_command;
int duration  = 0;       // Variable to store the duration

int  speed  = 35 ;// MAX 255

long int start_time = 0;


void setup() {
  // Configure pins as outputs
  pinMode(pwm_left, OUTPUT);
  pinMode(dir_1, OUTPUT);
  pinMode(pwm_right, OUTPUT);
  pinMode(dir_2, OUTPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(pingPin, OUTPUT);
  pinMode(echoPin, INPUT);




  // Start serial communication
  Serial.begin(57600);
}

void loop() {
  
   long us_duration, inches, cm;
   digitalWrite(pingPin, LOW);
   delayMicroseconds(2);
   digitalWrite(pingPin, HIGH);
   delayMicroseconds(10);
   digitalWrite(pingPin, LOW);
   us_duration = pulseIn(echoPin, HIGH);
   cm = microsecondsToCentimeters(us_duration);
   

  if(cm < 10){
     Serial.write("OBSTACLE");

     STOP();
     for(int b=0;b<3;b++){
        digitalWrite(buzzer, HIGH);
        delay(500);
        digitalWrite(buzzer, LOW);
        delay(500);
     }        
  }

  if(duration != 0 && (millis()-start_time) >= duration){
    start_time =0;
    duration = 0;
    STOP();
  }
   
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove leading/trailing whitespaces

    Serial.println(command);

    // Split the message into parts
    int delimiterIndex1 = command.indexOf('_');
    int delimiterIndex2 = command.indexOf('_', delimiterIndex1 + 1);
    int delimiterIndex3 = command.indexOf('_', delimiterIndex2 + 1);

    if (delimiterIndex1 != -1 && delimiterIndex2 != -1) {
      device_id = command.substring(0, delimiterIndex1);                  // Extract Device_id
      direction_command = command.substring(delimiterIndex1 + 1, delimiterIndex2); // Extract Direction
      duration_received = command.substring(delimiterIndex2 + 1, delimiterIndex3);                  // Extract duration
      speed_received = command.substring(delimiterIndex3 + 1);
      duration=duration_received.toInt();
      speed=speed_received.toInt();
    }
    

    if (device_id == DEVICE_ID) {
    
      if (direction_command == "FORWARD") {
        moveForward();
      } else if (direction_command == "BACKWARD") {
        moveBackward();
      } else if (direction_command == "RIGHT") {
         moveRight();
      } else if (direction_command == "LEFT") {
         moveLeft();
      } else if (direction_command == "STOP") {
         STOP();
      }
    }
  }
}

long microsecondsToInches(long microseconds) {
   return microseconds / 74 / 2;
}

long microsecondsToCentimeters(long microseconds) {
   return microseconds / 29 / 2;
}

void moveForward() {
  digitalWrite(dir_1, HIGH);
  digitalWrite(dir_2, LOW);
  analogWrite(pwm_left, speed);
  analogWrite(pwm_right, speed);
  if(duration!=0){
    start_time = millis();
  }
}

void moveBackward() {
  digitalWrite(dir_1, LOW);
  digitalWrite(dir_2, HIGH);
  analogWrite(pwm_left, speed);
  analogWrite(pwm_right, speed);
  if(duration!=0){
    start_time = millis();
  }
}

void moveLeft() {
  digitalWrite(dir_1, LOW);
  digitalWrite(dir_2, LOW);
  analogWrite(pwm_left, speed);
  analogWrite(pwm_right, speed);
  if(duration!=0){
    start_time = millis();
  }
}

void moveRight() {
  digitalWrite(dir_1, HIGH);
  digitalWrite(dir_2, HIGH);
  analogWrite(pwm_left, speed);
  analogWrite(pwm_right, speed);
  if(duration!=0){
   start_time = millis();
  }
}
void STOP() {
  digitalWrite(dir_1, HIGH);
  digitalWrite(dir_2, HIGH);
  analogWrite(pwm_left, 0);
  analogWrite(pwm_right, 0);
}
