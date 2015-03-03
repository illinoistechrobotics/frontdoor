char data[35];
boolean valid = false;
//Leonardo pin 3
const int ZERO_PIN = 0;
//Leonardo pin 2
const int ONE_PIN = 1;
unsigned long timestamp = 0;
int curr_bit = 0;
void setup(){
  attachInterrupt(ZERO_PIN,zero_bit,FALLING);
  attachInterrupt(ONE_PIN,one_bit,FALLING);
  Serial.begin(115200);
}
void loop(){
  if(valid == true){
    noInterrupts();
    int i;
    //Serial.print("Card Number: ");
    for(i=0;i<35;i++){
      Serial.print(data[i]);
    }
    Serial.println();
    curr_bit = 0;
    valid = false;
    interrupts();
  }
}
void zero_bit(){
  if((valid == true) || (millis() - timestamp > 100)){
    valid = false;
    curr_bit = 0;
  }
  data[curr_bit++] = '0';
  if(curr_bit>34){
    valid = true;
  }
  timestamp = millis();
}
void one_bit(){
if((valid == true) || (millis() - timestamp > 100)){
    valid = false;
    curr_bit = 0;
  }
  data[curr_bit++] = '1';
  if(curr_bit>34){
    valid = true;
  }
  timestamp = millis();
}
