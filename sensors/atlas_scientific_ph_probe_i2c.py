#!/usr/bin/python

import io
import fcntl

import time
import string
import argparse

import ds18b20_sensor


class AtlasI2C:
    long_timeout = 1.5
    short_timeout = .5
    default_bus = 1
    default_address = 100

    def __init__(self, address=default_address, bus=default_bus):
        # open two file streams, one for reading and one for writing
        # the specific I2C channel is selected with bus
        # it is usually 1, except for older revisions where its 0
        self.file_read = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
        self.file_write = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

        # initializes I2C to either a user specified or default address
        self.set_i2c_address(address)

    def set_i2c_address(self, addr):
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)

    def write(self, cmd):
        # appends the null character and sends the string over I2C
        cmd += "\00"
        try:
            self.file_write.write(cmd)
        except Exception as e:
            print(str(e))


    def read(self, num_of_bytes=31):
        # reads a specified number of bytes from I2C, then parses and displays the result
        res = self.file_read.read(num_of_bytes)         # read from the board
        response = filter(lambda x: x != '\x00', res)     # remove the null characters to get the response
        if ord(response[0]) == 1:             # if the response isn't an error
            # change MSB to 0 for all received characters except the first and get a list of characters
            char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
            # NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
            return ''.join(char_list)     # convert the char list to a string and returns it
        else:
            return "Error " + str(ord(response[0]))

    def query(self, string):
        # write a command to the board, wait the correct timeout, and read the response
        self.write(string)

        # the read and calibration commands require a longer timeout
        if((string.upper().startswith("R")) or
           (string.upper().startswith("CAL"))):
            time.sleep(self.long_timeout)
        elif string.upper().startswith("SLEEP"):
            return "sleep mode"
        else:
            time.sleep(self.short_timeout)

        return self.read()

    def close(self):
        self.file_read.close()
        self.file_write.close()


def parse_args():
    parser = argparse.ArgumentParser(description='An adapted script to output PH reading of an Atlas Scientific sensor')
    parser.add_argument('-a','--ph_address', type=int, help='Address of the i2c device', required=True)
    parser.add_argument('-t','--temperature_sensor_id', help='Address of the ds18b20 device. e.g. 28-021503ca1aff')
    return parser.parse_args()


def get_readout(device):
    return device.query("R")


def main():
    args = parse_args()
    device = AtlasI2C(address=args.ph_address) # creates the I2C port object, specify the address or bus if necessary
    try:
        # get temp from module
        if args.temperature_address:
            temperature = ds18b20_sensor.get_temperature(sensor_id=args.temperature_sensor_id)
            print(device.query("T," + temperature))
        # set temp
        print(get_readout(device))
    except:
        time.sleep(3)
        print(get_readout(device))


if __name__ == '__main__':
    main()
