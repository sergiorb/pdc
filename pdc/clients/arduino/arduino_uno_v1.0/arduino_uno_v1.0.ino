#include <EEPROM.h>

// CONSTANTS -----------------------------------------------------------------
const String shortDeviceName = "AED";
const String longDeviceName = "Arduino Echo Device";
const String deviceVersion = "1.0";

// Defines eeprom address where it is stored the device ID.
const int deviceIdEepromAddress = 0;

// Initial ID for unconfigured devices. This helps us to indentify new devices.
const int defaultDeviceID = 0;


// VARIABLES -----------------------------------------------------------------

// Stores device id, initiated to 0.
int deviceId = 0;

// Stores device availability.
boolean deviceReady = true;

// Store incoming orders from serial
String orderString = "";

// Inital char for detecting incoming order's String.
char initialChar = '$';

// Separates order identifier from device id.
char orderIdChar = ':';

// Separates device id and function.
char defuSeparator = '/';

// Variable separator
char varSeparator = '&';

// Final char for detecting the final order's string.
char stopChar = ';';

// Variable to store incoming seral data.
char inBuffer[100];

// Stores orderString data in an array
String orderArray[4];


// FUNCTIONS -----------------------------------------------------------------

// Return orderId from order's string.
String getOrderIdFromOrder(String orderStr) {

  return orderStr.substring(0, orderStr.indexOf(orderIdChar));
}

// Return number's device from order's string.
String getDeviceFromOrder(String orderStr) {

  return orderStr.substring(orderStr.indexOf(orderIdChar) + 1, orderStr.indexOf(defuSeparator));
}

// Return function called from order's string.
String getFunctionFromOrder(String orderStr) {

  // Looks for defuSeparator position in order's string.
  int defuSeparatorPos = orderStr.indexOf(defuSeparator);

  // Returns function number
  return orderStr.substring(defuSeparatorPos + 1, orderStr.indexOf(defuSeparator, defuSeparatorPos + 1));
}

// clean order's string and retrieve params string.
String getParamsFromOrder(String orderStr) {

  int first = orderStr.indexOf(defuSeparator) + 1;
  orderStr =  orderStr.substring(first);
  
  int second = orderStr.indexOf(defuSeparator) + 1;
  orderStr =  orderStr.substring(second);
  
  return orderStr;
}

// Fill orderArray with the data recolected by serialEvent.
void fillOrderArray(String orderString) {

  orderArray[0] = getOrderIdFromOrder(orderString);
  orderArray[1] = getDeviceFromOrder(orderString);
  orderArray[2] = getFunctionFromOrder(orderString);
  orderArray[3] = getParamsFromOrder(orderString);
}

// Resets to void orderArray.
void clearOrderArray() {

  orderArray[0] = "";
  orderArray[1] = "";
  orderArray[2] = "";
  orderArray[3] = "";
}

// Return '$ready;' if deviceReady variable is true.
String getDeviceReady() {
  
  if (deviceReady == true) {
    
    return "$ready;";
    
  } else {

    return "";
  }
}

// Send to serial order response.
void sendResponse(String orderId, String respone) {

  String outputString = initialChar + orderId + orderIdChar + respone + stopChar;
  Serial.print(outputString);
}

// Sets device ID.
void setDeviceId(int id) {

  EEPROM.write(deviceIdEepromAddress, id);
  deviceId = id;
}

// Gets device ID.
int getDeviceId() {

  return deviceId;
}

// Returns device short name.
String getShortDeviceName() {

  return shortDeviceName;
}

// Returns device long name.
String getLongDeviceName() {

  return longDeviceName;
}

// Returns device version.
String getDeviceVersion() {

  return deviceVersion;
}

String echo(String data) {

  return "Hi " + data;
}

// Preprocesses data before calling echo
String echoWrapper(String data) {

  // If data is a multiparametter string, you can
  // extract values here an then pass them to echo function.

  return echo(data);
}


// SETUP ---------------------------------------------------------------------

void setup() {

  // Establishes baud rate
  Serial.begin(9600);

  // EEPROM.write(deviceIdEepromAddress,defaultDeviceID);

  // Stores in devideId the device Id saved in the EEPROM. This allows the program
  // to work with it, reading it just once from EEPROM.
  deviceId = EEPROM.read(deviceIdEepromAddress);

  // Sends to serial that the device is ready.
  Serial.println("$ready;");

  // Sets deviceReady variable to true.
  deviceReady = true;

}


// EVENTS --------------------------------------------------------------------

void serialEvent() {

  String incomingString = "";

  while (Serial.available() > 0) {

    // We wait for intialChar to ensure we dont get any unwanted data.
    if (Serial.read() == initialChar) {

      // Reads until stopChar arrive.
      Serial.readBytesUntil(stopChar, inBuffer, 99);

      // Store readed data.
      incomingString = inBuffer;

      // Reset inBuffer to avoid unespected data in next orders.
      memset( &inBuffer, 0, 100 );

      // Checks that incoming order string is bound to the device
      if (getDeviceFromOrder(incomingString).toInt() == getDeviceId()) {

        fillOrderArray(incomingString);
        orderString = incomingString;
      }
    }
  }
}


// LOOP ----------------------------------------------------------------------

void loop() {

  // Analyces order string just when it exist.
  if (orderString != "") {

    // Runs function called in order's String.
    switch(orderArray[2].toInt()){

      case 0:
        Serial.print(getDeviceReady());
        break;
      case 1:
        sendResponse(orderArray[0], String(getDeviceId()));
        break;
      case 2:
        sendResponse(orderArray[0], getShortDeviceName());
        break;
      case 3:
        sendResponse(orderArray[0], getLongDeviceName());
        break;
      case 4:
        sendResponse(orderArray[0], getDeviceVersion());
        break;
      case 5:
        sendResponse(orderArray[0], echoWrapper(orderArray[3]));
        break;
    }

    // Cleans order string.
    orderString = "";
    clearOrderArray();
  }
}
