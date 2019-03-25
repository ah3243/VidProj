import serial

SERIALLOC = 1410

ser = serial.Serial('/dev/tty.usbserial-'+ str(SERIALLOC), 19200)
while True:
	print(ser.readline())


