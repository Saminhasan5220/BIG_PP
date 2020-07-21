import cv2
import sys
import time
import socket
import threading
from UI import *
class Client:
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def __init__(self,ip='192.168.1.5',port=10000):
        self.ip = ip
        self.port = port
        self.running = True
        self.rdata = None
        self.control_command = (0,0)
        #self.sent_data = None
    def scale( x,  in_min,  in_max,  out_min,  out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def run(self):

        print("Client UP and running ...")
        self.recieve_thread = threading.Thread(target=self.recieve)
        self.recieve_thread.daemon = True
        self.recieve_thread.start()
        self.receive_video()

        counter = 0
        while self.recieve_thread.is_alive() or self.sending_thread.is_alive():
            print("Recive thread is alive:",self.recieve_thread.is_alive(), "Sending thread is alive:",self.sending_thread.is_alive(),"Counter:",counter,end="\r")
            counter +=1
        self.quit()
        
    def recieve(self):
        try:
            self.sock.connect((self.ip,self.port))  
        except ConnectionRefusedError:
            print("Server not ready")
            return
            
        self.sending_thread = threading.Thread(target=self.send)
        self.sending_thread.daemon = True
        self.sending_thread.start()
        while self.running:
            try:
                if self.running and self.sock:
                    data = self.sock.recv(1024)

                if not data:
                    print("not data")
                    break
                #print(self.rdata,type(self.rdata))
                self.rdata = tuple(data.decode('utf-8').split(','))
                
                print("From Server to Client =>",self.rdata,type(self.rdata),len(self.rdata))
            except ConnectionResetError or ConnectionAbortedError:
                print("Server Disconnected")
                self.running =False
                break

    def send(self):
            while self.running:
                
                x = self.control_command #time.time()#input("Type to send message:")
                #print(self.control_command)

                time.sleep(0.05)
                if self.sock:
                    try:    
                        msg  = str(x)
                        self.sock.send(msg.encode('utf-8'))
                        #print("From Client to Server->",msg)
                    except OSError:
                        break
                else:
                    break
    def receive_video(self):
        V = Visualizer() 
        while True:
            if self.rdata:
                V.run(self.rdata)
            else: 
                V.run((0,0,0))
            self.control_command = str(V.throttle)+','+str(V.steering)

            
    def quit(self):
        self.running = False
        if self.sock:
            self.sock.close()
        sys.exit()
        
        
        
client = Client()
try:
    client.run()
except KeyboardInterrupt:
    pass
    

