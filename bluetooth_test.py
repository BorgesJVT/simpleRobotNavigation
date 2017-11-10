import bluetooth

bd_addr = "00:15:83:00:75:AD"
port = 1
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

while 1:
    tosend = raw_input()
    if tosend != 'q':
        sock.send(tosend)
    else:
        break

sock.close()
