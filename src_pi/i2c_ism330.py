
import smbus

channel = 1

address = 0x6b

reg_write_dac = 0x40

bus = smbus.SMBus(channel)
