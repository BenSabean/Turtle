# function to test CRC
import sys

def CRC(val):
  crc = 0
  for byte in val:
  	for bitnumber in range(0,8):
	    if ( byte ^ crc ) & 0x80 : crc = ( crc << 1 ) ^ 0x31
	    else                  : crc = ( crc << 1 )
	    byte = byte << 1
	    crc = crc & 0xFF
  return crc

num = []
num.append(int(sys.argv[1]))
num.append(int(sys.argv[2]))
num.append(int(sys.argv[3]))
crc = CRC(num)
print("CRC = "+str(hex(crc)))
