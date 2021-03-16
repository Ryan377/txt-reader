import socket
import _thread as thread
import os
import chardet
import json
import struct


def child_connection(no, conn):
    print('begin connection', no)
    fp = None
    buffsize = 1024
    txtpagesz = 1000


    while True:
        try:
            rq = conn.recv(buffsize).decode('utf-8')
            print('request:', rq)

            if rq == '':
                break

            if rq[0] == '0':
                filename = rq[2:]
                print("the client is asking for a file", filename)
                filesize = os.path.getsize(filename)

                head_dic = {'filename': filename, 'filesize': filesize}
                head_raw = json.dumps(head_dic)
                head_len_struct = struct.pack('i', len(head_raw))
                conn.sendall(head_len_struct)
                conn.sendall(head_raw.encode('utf-8'))

                with open(filename, 'rb') as fp:
                    data = fp.read()
                    conn.sendall(data)


            elif rq[0] == '1':
                filename = rq[2:]
                print('opening file..', filename)
                fpagenum = (os.path.getsize(filename) + txtpagesz - 1) // txtpagesz
                fp = open_text(filename)
                conn.sendall(str(fpagenum).encode('utf-8'))

            elif rq[0] == '2':
                pgnum = int(rq[2:])
                if pgnum != 0:
                    fp.seek((pgnum - 1) * txtpagesz)
                content = fp.read(txtpagesz)
                conn.sendall(content.encode('utf-8'))

            elif rq[0] == '3':
                print("closing file")
                fp.close()
                conn.sendall('file closed'.encode('utf-8'))

            else:
                conn.sendall('valid request'.encode('utf-8'))

        except Exception as e:
            conn.sendall(str(e).encode('utf-8'))

    print('end connection', no)
    conn.close()
    if fp:
        fp.close()
    thread.exit_thread()

def detect_code(filename):
    fp = open(filename, 'rb')
    line1 = fp.readline()
    encf = chardet.detect(line1)
    encode = encf['encoding']
    print(encode)

    lines = fp.readlines()
    if encode == 'ascii':
        for line in lines:
            enc = chardet.detect(line)
            if enc['encoding'] != encode:
                if enc['encoding'] == 'ISO-8859-9':
                    encode = 'GBK'
                    break
                else:
                    encode = enc['encoding']
                    print(encode)
                    break

    fp.close()
    return encode


def open_text(filename):
    print(filename)
    encode = detect_code(filename)
    if encode == 'GB2312':
        encode = 'GBK'
    print(encode)

    fp = None
    try:
        fp = open(filename, 'r', encoding=encode)
    except Exception as e:
        print('opentext error', e)
    return fp


if __name__ == '__main__':
    print('Server start')

    ip_port = ('127.0.0.1', 8998)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(ip_port)
    sock.listen()
    print("Server is listening " + str(ip_port[0]) + ':' + str(ip_port[1]))

    no = 0
    while True:
        conn, addr = sock.accept()
        no += 1
        thread.start_new_thread(child_connection, (no, conn))

    sock.close()
