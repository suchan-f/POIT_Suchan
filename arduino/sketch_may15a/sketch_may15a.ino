int x;
int bright;


void setup() {
  Serial.begin(9600);
  Serial.setTimeout(1);
  pinMode(6, OUTPUT);
   bright = 10;
}

void loop() {
   
  int analogSensor = analogRead(A0);
  analogWrite(6 , bright);
  
  //Serial.println("Sensor:");
  Serial.println(analogSensor);
  
  
  if (Serial.available()>0){
  x = Serial.readString().toInt();
  Serial.println(x);
  bright=x;
  }
delay(1000);

}
