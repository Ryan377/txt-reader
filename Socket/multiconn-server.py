import sys
if(sys.version[:1] == "3"):
    import _thread as thread
import socket


def child_connection(index, sock, connection):
    try:
        print("begin connecion ", index)
        print("begin connecion %d" % index)
        connection.settimeout(50)
        while True:
            buf = connection.recv(1024)
            print("Get value %s from connection %d: " % (buf, index))
            if buf == b'1':
                print("send welcome")

                connection.send('welcome to server!'.encode())
            elif buf != b'0':
                connection.send('please go out!'.encode())
                print("send refuse")

            else:
                print("close")

                break
    except socket.timeout:
        print('time out')

    print("closing connection %d" % index)
    connection.close()
    thread.exit_thread()


if __name__ == "__main__":

    print("Server is starting")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 8998))
    sock.listen(5)
    print( "Server is listenting port 8001, with max connection 5")

    index = 0
    while True:

        connection, address = sock.accept()
        index += 1
        thread.start_new_thread(child_connection, (index, sock, connection))
        if index > 10:
            break
    sock.close()

