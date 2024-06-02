#include <Wire.h>
#include <VL6180X.h>

VL6180X sensor;

int ena = 11;
int in1 = 12;
int in2 = 10;

int enb = 5;
int in3 = 6;
int in4 = 7;
String input = "EMPTY";

int leftPower;
int leftReverse;
int rightPower;
int rightReverse;
int noUpdateCounter = 0;

char payload[64];

void setup() {
  Serial.begin(9600); 
  Wire.begin();

  sensor.init();
  sensor.configureDefault();
  sensor.setTimeout(500);

  pinMode(ena, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);

  pinMode(enb, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  
  }

int getIntFromString(String text) {
  return text.toInt();
}

void updateMotorPower(int leftPower, int rightPower) {

  if(leftPower > 255) {
    leftPower = 255;
  } 

  if(leftPower < 0) {
    leftPower = 0;
  }

  if(rightPower > 255) {
    rightPower = 255;
  }

  if(rightPower < 0) {
    rightPower = 0;
  }
  
  analogWrite(ena, leftPower);
  analogWrite(enb, rightPower);
}

void updateMotorDirection(int leftReverse, int rightReverse) {

  if(leftReverse == 0) {
    //Left
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
  }

  if(leftReverse == 1) {
    //Left
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
  }
  
  if(rightReverse == 0) {
    //Right
    digitalWrite(in3, LOW);
    digitalWrite(in4, HIGH);
  }

  if(rightReverse == 1) {
    //Right
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);
  }
}

void loop() {

  //Input -> 255,0,255,0 -> turned to 255 | 0 | 255 | 0
  if (Serial.available() > 0) {
    Serial.readStringUntil( '\n' ).toCharArray(payload, 64);
    leftPower = getIntFromString(strtok(payload, ","));
    leftReverse = getIntFromString(strtok(NULL, ","));
    rightPower = getIntFromString(strtok(NULL, ","));
    rightReverse = getIntFromString(strtok(NULL, ","));

    updateMotorPower(leftPower, rightPower);
    updateMotorDirection(leftReverse, rightReverse);
    noUpdateCounter = 0;
  } else {
    noUpdateCounter = noUpdateCounter + 1;
  }

  Serial.print(sensor.readRangeSingleMillimeters());
  //if (sensor.timeoutOccurred()) { Serial.print(" TIMEOUT"); }
  Serial.println();

  if(noUpdateCounter > 15) {
    updateMotorPower(0, 0);
  }

  delay(50);
}
