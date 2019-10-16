# Reverse Engineering and coding by Aviad Golan @AviadGolan and Shai Rod @NightRang3r

#!/usr/bin/env python

import binascii as ba
import time
import struct
import socket
import sys
import re

########## CHANGE TO YOUR PARAMS ##########
switcherIP = sys.argv[2]
phone_id = sys.argv[3]
device_id = sys.argv[4]
device_pass = sys.argv[5]
########## DO NOT CHANGE BYOND THIS LINE  ##########


UDP_IP = "0.0.0.0"
UDP_PORT = 20002

pSession = "00000000"
pKey = "00000000000000000000000000000000"

if len (sys.argv) != 6:
	print("Arguments incorrect")
elif sys.argv[1] == "0":
	sCommand = "0"
elif sys.argv[1] == "1":
	sCommand = "1"
elif sys.argv[1] == "2":
	sCommand = "2"
elif sys.argv[1].startswith('t'):
	sCommand = "1"
elif sys.argv[1].startswith('m'):
	sCommand = "2"

# CRC
def crcSignFullPacketComKey(pData, pKey):
	#print("pData is: ", pData)
	#print("pKey is: ", pKey)
	crc = ba.hexlify(struct.pack('>I', ba.crc_hqx(ba.unhexlify(pData), 0x1021)))
	pData = pData + crc[6:8] + crc[4:6]
	crc = crc[6:8] + crc[4:6] + ba.hexlify( pKey )
	crc = ba.hexlify(struct.pack('>I', ba.crc_hqx(ba.unhexlify(crc), 0x1021)))
	pData = pData + crc[6:8] + crc[4:6]
	#print("pData is: ", pData)
	return pData
# Generate Time Stamp
def getTS():
	return ba.hexlify(struct.pack('<I', int(round(time.time()))))
# Generate Timer value
def sTimer(sMinutes):
    sSeconds = int(sMinutes) * 60
    sDelay = struct.pack('<I', sSeconds)
    return ba.hexlify(sDelay)
# Get Power consumption and Elctrical current
def getPower(res):
	b = ba.hexlify(res)[154:162]
	i = int(b[2:4]+b[0:2], 16)
	return '"electric_current" : "%.1f"' % (i/float(220)) + ',' + '"power_consumption" : "' + str(i) + '",'
# Auto shutdown countdown
def sTime(res):
	b = ba.hexlify(res)[178:186]
	open_time = int(b[6:8] + b[4:6] + b[2:4] + b[0:2] , 16)
	m, s = divmod(open_time, 60)
	h, m = divmod(m, 60)
	return '"time_left" : "%d:%02d:%02d"' % (h, m, s)
#  Generate auto shutdown time
def setAutoClose(hours):
	h, m = hours.split(':')
	mSeconds = int(h) * 3600 + int(m) * 60
	if mSeconds < 3600:
		print "[!] Value Can't be less than 1 hour!"
		sys.exit()
	elif mSeconds > 86340:
		print "[!] Value can't be more than 23 hours and 59 minutes!"
		sys.exit()
	else:
		print "[+] Auto shutdown was set to " + str(hours) + " Hour(s)"
		return ba.hexlify(struct.pack('<I', mSeconds))

def getAutoClose(res):
	b = ba.hexlify(res)[194:202]
	open_time = int(b[6:8] + b[4:6] + b[2:4] + b[0:2] , 16)
	m, s = divmod(open_time, 60)
	h, m = divmod(m, 60)
#	print "[+] Device is configured to auto shutdown in: %d:%02d" % (h, m)  + " hour(s)"
	return '"shutdown" : "%d:%02d",' % (h, m)

hourRe = re.compile(r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$')

try:

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((switcherIP, 9957))
	data = "fef052000232a100" + pSession + "340001000000000000000000"  + getTS() + "00000000000000000000f0fe1c00" + phone_id + "0000" + device_pass + "00000000000000000000000000000000000000000000000000000000"
	data = crcSignFullPacketComKey(data, pKey)
	s.send(ba.unhexlify(data))
	res = s.recv(1024)
	pSession2 = ba.hexlify(res)[16:24]
	if not pSession2:
		s.close()
		print ("[!] Operation failed, Could not acquire SessionID, Please try again...")
		sys.exit()

	data = "fef0300002320103" + pSession2 + "340001000000000000000000" + getTS() + "00000000000000000000f0fe" + device_id + "00"
	data = crcSignFullPacketComKey(data, pKey)
#	print ("[*] Getting Switcher state...")
	sys.stdout.write("{")
	s.send(ba.unhexlify(data))
	res = s.recv(1024)
	state = ba.hexlify(res)[150:154]
	if sys.argv[1] == "0" and state == "0000":
		s.close()
		sys.stdout.write('"state" : "OFF",')
		sys.stdout.write(getPower(res))
		sys.stdout.write(getAutoClose(res))
		sys.stdout.write(sTime(res))
		sys.exit()
	elif sys.argv[1] == "1" and state == "0100":
		s.close()
		sys.stdout.write('"state" : "ON",')
		sys.stdout.write(getPower(res))
		sys.stdout.write(getAutoClose(res))
		sys.stdout.write(sTime(res))
		sys.exit()
	elif sys.argv[1] == "2" and state == "0100":
		s.close()
		sys.stdout.write('"state" : "ON",')
		sys.stdout.write(getPower(res))
		sys.stdout.write(getAutoClose(res))
		sys.stdout.write(sTime(res))
		sys.exit()
	elif sys.argv[1] == "2" and state == "0000":
		s.close()
		sys.stdout.write('"state" : "OFF",')
		sys.stdout.write(getPower(res))
		sys.stdout.write(getAutoClose(res))
		sys.stdout.write(sTime(res))
		sys.exit()
	elif sys.argv[1].startswith('t'):
		try:
			sMinutes = int(sys.argv[1][1:])
		except:
			print ("[!] " + sys.argv[1][1:] + " Is not a valid number!")
			sys.exit()
		if sMinutes > 0 and sMinutes <=60:
			if sMinutes < 10:
				sys.stdout.write('"state" : "ON", "time_left" : "00:0' + str(sMinutes) + ':00"}')
			else:
				sys.stdout.write('"state" : "ON", "time_left" : "00:' + str(sMinutes) + ':00"}')
			data = "fef05d0002320102" + pSession2 + "340001000000000000000000" + getTS() + "00000000000000000000f0fe" + device_id + "00" + phone_id + "0000" + device_pass + "000000000000000000000000000000000000000000000000000000000106000" + sCommand + "00"  + sTimer(sMinutes)
			data = crcSignFullPacketComKey(data, pKey)
			s.send(ba.unhexlify(data))
			res = s.recv(1024)
			s.close()
		else:
			print "[!] Enter a value between 1-60 minutes"
			sys.exit()
	elif sys.argv[1].startswith('m'):
		if not hourRe.match(sys.argv[1][1:]):
			print "[!] Please enter a value between 01:00 - 23:59"
			sys.exit()

		else:
			auto_close = setAutoClose(sys.argv[1][1:])
			data ="fef05b0002320102" + pSession2 + "340001000000000000000000" + getTS() + "00000000000000000000f0fe" + device_id + "00" + phone_id + "0000" + device_pass + "00000000000000000000000000000000000000000000000000000000040400" + auto_close
			data = crcSignFullPacketComKey(data, pKey)
			s.send(ba.unhexlify(data))
			res = s.recv(1024)
			s.close()
	else:
		data = "fef05d0002320102" + pSession2 + "340001000000000000000000" + getTS() + "00000000000000000000f0fe" + device_id + "00" + phone_id + "0000" + device_pass + "000000000000000000000000000000000000000000000000000000000106000" + sCommand + "0000000000"
		data = crcSignFullPacketComKey(data, pKey)
		if sCommand == "0":
			sys.stdout.write('"state" : "OFF",}')
		elif sCommand == "1":
			sys.stdout.write('"state" : "ON",}')

		s.send(ba.unhexlify(data))
		res = s.recv(1024)
		s.close()

except SystemExit:
    sys.stdout.write('}')
#except Exception as e:
#	print("[!] Something went wrong...")
#	print "[!] " + str(e)
