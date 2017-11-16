import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 8888)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()

    try:
        print >>sys.stderr, 'connection from', client_address

        # Receive the data in small chunks and retransmit it
        while True:
			velocity_r = connection.recv(3)
			velocity_l = connection.recv(3)
			try:
				print int(velocity_r)
				print int(velocity_l)
			except ValueError:
    			#Handle the exception
			    print 'Please enter an integer'
			print >>sys.stderr, 'received "%s"' % velocity_r
			print >>sys.stderr, 'received "%s"' % velocity_l
			if velocity_r:
				print >>sys.stderr, 'sending data back to the client'
				connection.sendall("OK")
				#connection.sendall(velocity_l)
			else:
				print >>sys.stderr, 'no more data from', client_address
				break
            
    finally:
        # Clean up the connection
        connection.close()
