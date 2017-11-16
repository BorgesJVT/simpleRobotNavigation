import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('192.168.1.22', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    for i in range(35, 55, 2):
		# Send data
		velocity_r = str(i)
		velocity_l = str(i)
		print >>sys.stderr, 'sending "%s"' % velocity_r
		print >>sys.stderr, 'sending "%s"' % velocity_l
		sock.sendall(velocity_r)
		sock.sendall(velocity_l)

		# Look for the response
		amount_received = 0
		amount_expected = len(velocity_r) + len(velocity_l)
		
		#while amount_received < amount_expected:
		#	data = sock.recv(amount_expected)
		#	amount_received += len(data)
		#	print >>sys.stderr, 'received "%s"' % data

		time.sleep(1)

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
