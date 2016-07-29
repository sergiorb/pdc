# PDC v1.0

PDC or Python Device Connection is a library to facilitate data exchange between physical devices like Arduino
with programs written in Python. I use it with my own IOT-alike projects (aquarium automatization for example) and I share it just with the purpose of learning and sharing with the community. 

## Getting Started

At the moment, there is only a serial device and a Arduino client in the library. In the future I would like to write other kind of devices such Wireless or ethernet ones.

### Prerequisities

You need:
* [Arduino](https://www.arduino.cc/) Board (I use the Arduino UNO model), loaded with the code that you can find on ```clients/arduino/arduino_uno_v*.*.ino```. To do so, just follow this guide [https://www.arduino.cc/en/Guide/Linux](https://www.arduino.cc/en/Guide/Linux).

* USB cable (A plug to B plug).

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

Now, install dependencies wit make. Make calls virtualenv to create an isolated enviroment for python and install the project dependencies with pip3

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

To run automatic test, use make:

```
$ make test
```

## Built With

* Python3
* [Pyserial](https://github.com/pyserial/pyserial)

## Authors

* **Sergio Romero Barra**

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
