#coding:utf-8

from SocketServer import ThreadingTCPServer,StreamRequestHandler
import traceback
from array import array
import chat
class MyStreamRequestHandler(StreamRequestHandler):
    def handle(self):
        r=array('h')
        try:
            data=self.rfile.read(10)
            if(len(data)!=4):
                self.wfile.write("frame header length error\r\n")
            else:
                i=0
                if(ord(data[i+0])==0xAA and ord(data[i+1])==0xAB and ord(data[i+2])==0xAC and ord(data[i+3])==0xAD):
                    self.wfile.write("you can send!\r\n")
                    rece=self.rfile.read(1024)
                    while(len(rece)>0):
                        print "len:",len(rece)
                        j=0
                        while((j+1)<len(rece)):
                            d=(ord(rece[j+1])+256*ord(rece[j]))
                            if(d>32767):
                                d=d-65535
                            print d
                            r.append(d)
                            j=j+2
                        rece=self.rfile.read(1024)
                    print "receive success"
                    TR=chat.cRobot()
                    res_MP3=TR.chat(r)
                    print "get MP3 res!"

                else:
                    self.wfile.write("frame header error\r\n")

        except:
            traceback.print_exc()

if __name__ == "__main__":
    host = "192.168.4.128"       #主机名，可以是ip,像localhost的主机名,或""
    port = 8080     #端口
    addr = (host, port)

    #ThreadingTCPServer从ThreadingMixIn和TCPServer继承
    #class ThreadingTCPServer(ThreadingMixIn, TCPServer): pass
    server = ThreadingTCPServer(addr, MyStreamRequestHandler)
    server.serve_forever()