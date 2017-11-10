import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('192.168.1.22', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
#sock.settimeout(0.03)

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()

    try:
        print >>sys.stderr, 'connection from', client_address
        velocity_r = "0"
        velocity_l = "0"

        # Receive the data in small chunks and retransmit it
        while True:
	    velocity_r = connection.recv(3)
	    velocity_l = connection.recv(3)

	    print >>sys.stderr, 'received "%s"' % velocity_r
	    print >>sys.stderr, 'received "%s"' % velocity_l
	    if velocity_r:
	    print >>sys.stderr, 'sending data back to the client'
	    connection.sendall("OK")
	    else:
		print >>sys.stderr, 'no more data from', client_address
		    break
            
    finally:
        # Clean up the connection
        connection.close()
