#include <EEPROM.h>

const String shortDeviceName = "AED";
const String longDeviceName = "Arduino Echo Device";
const String deviceVersion = "0.1";
// Store the eeprom address where we store device ID
const int deviceIdEepromAddress = 0;
// Initial ID for unconfigured devices. This helps us to indentify new devices.
const int defaultDeviceID = 0;
// Default device id
int deviceId = 0;
// Monitor device availability.
boolean deviceReady = false;
// Store incoming orders from serial
String orderString = "";
// Inital char for detecting incoming order's String.
char initialChar = '$';
//
char identifierChar = ':';
// device Id and function separator in order's String.
char defuSeparator = '/';
// Variable separator
char varSeparator = '&';
// Final char for detecting the final order's string.
char stopChar = ';';
// Variable to store incoming seral data.
char inBuffer[100];
// Stores orderString data in array
String orderArray[4];

// ---- Functions Variables ----
String paramStr = "";
// -----------------------------

// --------------------------------------------------------
const int led = 9;
const int tDelayShort = 10;
const int tDelayLong = 1000;
// --------------------------------------------------------


void setup(){
  Serial.begin(9600);
  deviceId = EEPROM.read(deviceIdEepromAddress);
  Serial.println("$ready;");
  deviceReady = true;
}

void loop(){
  
  if(orderString != ""){
    // Runs function called in order's String.
    switch(orderArray[2].toInt()){
      case 0:
        if(deviceReady==true){
          Serial.println("$ready;");
        }
        break;
      case 1:
        setDeviceId(orderString);
        break;
      case 2:
        Serial.print(getDeviceId());
        break;
      case 3:
        Serial.print(getShortDeviceName());
        break;
      case 4:
        Serial.print(getLongDeviceName());
        break;
      case 5:
        Serial.print(getDeviceVersion());
        break; 
      case 6:
        helloAnswerFunction(orderString);
        break;

    }
    // Cleans order string.
    orderString = "";
    clearOrderArray();
  }
}

void serialEvent() {
  
  String incomingString = "";
  
  while(Serial.available() > 0){
    
    // We wait for intialChar to ensure we dont get any unwanted data.
    if(Serial.read() == initialChar) {

      // Reads until stopChar arrive.
      Serial.readBytesUntil(stopChar,inBuffer,99);
      // Store readed data.
      incomingString = inBuffer;
      // Reset inBuffer to avoid unespected data in next orders.
      memset( &inBuffer, 0, 100 );
      // Checks that incoming order string is bound to the device
      if(getDeviceFromOrder(incomingString).toInt() == getDeviceId()){
        fillOrderArray(incomingString);
        orderString = incomingString;
      }
    }
  }
}

// Sets device ID
void setDeviceId(String orderString){
  paramStr = getParamsFromOrder(orderString);
  int id = paramStr.toInt();
  EEPROM.write(deviceIdEepromAddress, id);
  deviceId = id;
}

//gets device ID
int getDeviceId(){
 return deviceId; 
}

String getShortDeviceName(){
 return shortDeviceName;
}

String getLongDeviceName(){
 return longDeviceName;
}

String getDeviceVersion(){
 return deviceVersion;
}

// Return orderId from order's string.
String getOrderIdFromOrder(String orderStr) {
 return orderStr.substring(0, orderStr.indexOf(identifierChar));
}

// Return number's device from order's string.
String getDeviceFromOrder(String orderStr){
  return orderStr.substring(orderStr.indexOf(identifierChar)+1,orderStr.indexOf(defuSeparator));
}

// Return function called from order's string.
String getFunctionFromOrder(String orderStr){
  // Looks for defuSeparator position in order's string.
  int defuSeparatorPos = orderStr.indexOf(defuSeparator);
  // Returns function number
  return orderStr.substring(defuSeparatorPos+1,orderStr.indexOf(defuSeparator,defuSeparatorPos+1));
}

// clean order's string and retrieve params string.
String getParamsFromOrder(String orderStr){
 return orderStr.substring(orderString.indexOf(defuSeparator,orderStr.indexOf(defuSeparator)+1)+1); 
}

// Fill orderArray with the data recolected by serialEvent
void fillOrderArray(String orderString){

    orderArray[0] = getOrderIdFromOrder(orderString);
    orderArray[1] = getDeviceFromOrder(orderString);
    orderArray[2] = getFunctionFromOrder(orderString);
    orderArray[3] = getParamsFromOrder(orderString);
}

// 
void clearOrderArray() {
  
  orderArray[0] = "";
  orderArray[1] = "";
  orderArray[2] = "";
  orderArray[3] = "";
} 

void helloAnswerFunction(String orderString) {
  paramStr = getParamsFromOrder(orderString);
  Serial.print(initialChar);
  Serial.print(orderArray[0]);
  Serial.print(identifierChar);
  Serial.print("Hi "+paramStr+" this is "+longDeviceName+" saying hello to you too!");
  Serial.print(stopChar);
}
