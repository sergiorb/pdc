import unittest, time

from pdc.pdc.serial.serial import SerialDevice

class TestPDC(unittest.TestCase):

    def test_echo(self, route_str='/dev/ttyACM0'):

        data = "Jhon de las nieves"

        serial_device = SerialDevice(route_str=route_str)

        serial_device.connect()

        order_id = serial_device.send_order(device=0, function=5, data=data)

        time.sleep(0.5)

        response = serial_device.get_order_response(order_id)

        serial_device.disconnect()

        self.assertEqual(response, 'Hi {data}'.format(data=data))

if __name__ == '__main__':

    unittest.main()