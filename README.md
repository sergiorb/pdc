# PDC v1.1.5

PDC or Python Device Connection is a library to facilitate data exchange between physical devices like Arduino
with programs written in Python. I use it with my own IOT-alike projects (aquarium automatization for example) and I share it just with the purpose of learning and sharing with the community. 

## Getting Started

At the moment, there is only a serial device and a Arduino client in the library. In the future I would like to write other kind of devices such as Wireless or Ethernet ones.

### Prerequisities

You need:
* [Arduino](https://www.arduino.cc/) Board (I use the Arduino UNO model), loaded with the code that you can find on ```clients/arduino/arduino_uno_v*.*.ino```. To do so, just follow this guide [https://www.arduino.cc/en/Guide/Linux](https://www.arduino.cc/en/Guide/Linux).

* USB cable (A plug to B plug).

* Python 3 installed on your system.

* virtualenv installed on your system.

### Installing

Clone or download the code:

```
$ git clone https://github.com/sergiorb/PDC.git
```
```
$ wget https://github.com/sergiorb/PDC/archive/master.zip
$ unzip master.zip
```

Using pip:

```
pip install pdc
```

Now, install dependencies with Make. It calls virtualenv to create an isolated enviroment for python and install the project dependencies with pip3.

```
$ make
```

Now you can execute activate the environment and run the example file:

```
$ source pdc_env/bin/activate

$ python3 example.py
``` 

If everything is correct, the program should say ```Device response: Hi [name that you entered]```

## Running the tests

To run automatic test, use Make:

```
$ make test
```

## Using and adding functions

The arduino client has only defined functions to:

```arduino
case 0: // Retrieves if client is ready.
	Serial.print(getDeviceReady());
	break;
case 1: // Returns client id.
	sendResponse(orderArray[0], String(getDeviceId()));
	break;
case 2: // Returns the client acronym.
	sendResponse(orderArray[0], getShortDeviceName());
	break;
case 3: // Returns the full client name.
	sendResponse(orderArray[0], getLongDeviceName());
	break;
case 4: // Returns client version.
	sendResponse(orderArray[0], getDeviceVersion());
	break;
case 5: // Returns 'Hi: ' plus given data (by orderArray[3]).
	sendResponse(orderArray[0], echoWrapper(orderArray[3]));
	break;
```

For example, if you want to retrieve the device version, write a script as follows:

```python
serial_device = SerialDevice(route_str='/dev/ttyACM0')
serial_device.connect()

order_id = serial_device.send_order(device=0, function=4)) # This function doesn't need any extra data.
time.sleep(0.5)
response = serial_device.get_order_response(order_id)

serial_device.disconnect()
```

If you want to add new functions, modify the arduino client

```arduino
case 6:
	sendResponse(orderArray[0], foo(orderArray[3]));
	break;

// orderArray[0] => order_id
// orderArray[3] => data 
```

and call it from from Python with:

```python
order_id = serial_device.send_order(device=0, function=6, data='data for foo function'))
```

## Caveats

If you try to retrieves an ```order_id``` result just after the function call, probably ```get_order_response``` will return ```None```. This happens because Python script runs faster than the communication with the client. 

In the future, this should be handle by the library itself. Meanwhile, call ```time.sleep(0.5)``` between function call and get_order_response.

## Built With

* Python3
* [Pyserial](https://github.com/pyserial/pyserial)

## Authors

* **Sergio Romero Barra**

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
