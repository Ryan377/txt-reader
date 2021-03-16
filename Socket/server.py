from socketserver import BaseRequestHandler,ThreadingTCPServer
import threading

BUF_SIZE=1024

class Handler(BaseRequestHandler):
    def handle(self):
        address,pid = self.client_address
        print('%s connected!'%address)
        while True:
            data = self.request.recv(BUF_SIZE)
            if len(data)>0:
                print('receive=',data.decode('utf-8'))
                cur_thread = threading.current_thread()
                self.request.sendall('response'.encode('utf-8'))
                print('send:','response')
            else:
                print('close')
                break

if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8998
    ADDR = (HOST,PORT)
    server = ThreadingTCPServer(ADDR,Handler)
    print('listening')
    server.serve_forever()
    print(server)
