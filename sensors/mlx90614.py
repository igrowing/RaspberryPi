#!/usr/bin/env python
# Run without arguments to read all 3 temperatures of MLX90614.
# Run with one integer argument to read the register.
# Import as module.

import sys
import Adafruit_GPIO.I2C as I2C

class Melexis:
    ''' Data registers can be read only (access RAM).
    Config registers can be read/write (access EEPROM).
    Consult with datasheet for reserved bits and registers before writing into them.
    '''

    def __init__(self, addr=0x5A, bus=1, c=True):
        self._i2c = I2C.Device(addr, bus)
        self._c = c  # Celsius by default

    def readAmbient(self):
        return self._readTemp(0x06)

    def readObject1(self):
        return self._readTemp(0x07)

    def readObject2(self):
        return self._readTemp(0x08)

    def readData(self, reg):
        return self._i2c.readS16(reg)

    def _readTemp(self, reg):
        temp = self.readData(reg)
        temp = temp * .02 - 273.15
        return temp if self._c else ((temp * 9 / 5) + 32)

    def readConfig(self, reg):
        return self.readData(reg | 0x20)

    def writeConfig(self, reg, data):
        self._i2c.write16(reg | 0x20, data)
        

if  __name__ == "__main__":
    sensor = Melexis()
    try:
        print 'Data: 0x%04x' % sensor.readData(int(sys.argv[1]))
        try:
            d = int(sys.argv[2], 16)
            print 'Config: 0x%04x' % sensor.readConfig(int(sys.argv[1]))
            sensor.writeConfig(int(sys.argv[1]), d)
            print 'Written 0x%04x in %s' % (d, sys.argv[1])
        except:
            pass
    except:
        print 'Ambient |  Obj1  |  Obj2'
        print '%7s | %06s | %s' % (sensor.readAmbient(), sensor.readObject1(), sensor.readObject2())
