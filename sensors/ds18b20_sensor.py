#!/usr/bin/python
import argparse


def get_temperature(sensor_id, bus_path='/sys/bus/w1/devices'):
    device_location = '%s/%s/w1_slave' % (bus_path, sensor_id)
    if not os.access(device_location, os.R_OK):
        raise Exception('The location %s is not readable.' % device_location)
    with open(device_location) as f:
        lines = f.readlines()
        temperature = int(lines[1].split('t=')[1].strip()) / 1000
        return temperature


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--sensor_id', help='The id of the sensor to query e.g. 28-021503ca1aff')
    parser.add_argument('-p', '--bus_path', help='The bus path for the device.', default='/sys/bus/w1/devices')
    return parser.parse_args()


def main():
    args = parse_args()
    print(get_temperature(bus_path=args.bus_path, sensor_id=args.sensor_id))


if __name__ == '__main__':
    main()
