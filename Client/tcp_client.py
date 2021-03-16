import socket
import struct
import json
import time


class tcp_client:
    ip_port = ('127.0.0.1', 8998)
    buffsize = 1024

    def __init__(self):
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect(self.ip_port)

    def __del__(self):
        self.tcp_sock.close()

    def sendrecv(self, string):
        self.tcp_sock.sendall(string.encode('utf-8'))
        r = self.tcp_sock.recv(self.buffsize).decode('utf-8')
        return r

    def download(self, filename, savename=None):
        if savename is None:
            savename = filename
        self.tcp_sock.sendall(('0 ' + filename).encode('utf-8'))

        head_len_struct = self.tcp_sock.recv(40)
        if not head_len_struct:
            return
        print('[TCP] loading...', filename + (', save as ' + savename if savename != filename else ''))
        head_len = struct.unpack('i', head_len_struct)[0]
        head_raw = self.tcp_sock.recv(head_len)
        head = json.loads(head_raw.decode('utf-8'))
        filesize = head['filesize']

        recv_len = 0
        start_time = time.time()
        fp = open(savename, 'wb')
        while recv_len < filesize:
            recv_cur = self.tcp_sock.recv(min(filesize - recv_len, self.buffsize))
            fp.write(recv_cur)
            recv_len += len(recv_cur)
        fp.close()

        end_time = time.time()
        print('[TCP] length:', recv_len, ', size:', filesize, ', time' + str(end_time - start_time) + 'seconds')
