import cv2
import sys
import math
import pygame
from serial import*
import numpy as np

#p[(i-U) % len(p)]
#p=[0, 1, 0, 0, 0]

#color = (57,100,20,10)

  
        
class HUD:
    #fix color
    def __init__(self,screen,width=640,height=480):
        self.screen = screen
        self.width, self.height = width, height
        self.linewidth = 2
        self.fontsize = 20
        self.fov = 90
        self.increments = 5
        self.vlen = 18
        self.tickY = 0
        self.font = pygame.font.SysFont(None, self.fontsize)



    def transfrom(self,x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        
        
        
    def nearest_multiple(self,a_number):
        return self.increments * round(a_number/self.increments)
        
    def constrain_angle(self,angle):
        if angle >= 180.0:
            angle-=360.0
        if angle <- 180.0:
            angle += 360.0
        return angle
    def rotate(self,x,y, angle):
        """Use numpy to build a rotation matrix and take the dot product."""
        #x, y = xy
        cx = self.width/2
        cy = self.height/2
        c, s = np.cos(np.radians(angle)), np.sin(np.radians(angle))
        j = np.matrix([[c, s], [-s, c]])
        m = np.dot(j, [x-cx, y-cy])
        return float(m.T[0]) + cx, float(m.T[1]) + cy 
    
    def render(self,yaw  = 0,pitch = 0,roll = 0):
        start = self.nearest_multiple(yaw - (self.fov/2))
        ended = self.nearest_multiple(yaw + (self.fov/2))
        #pygame.draw.line(self.screen, (255,255,255), (self.width/2,self.tickY + self.vlen/2), (self.width/2,self.tickY + self.vlen), self.linewidth)
        for i in range(start,ended + 1,self.increments):
            tickX = self.transfrom(i,yaw - (self.fov/2),yaw + (self.fov/2),0,self.width)
            pygame.draw.line(self.screen, (127,127,127), (tickX,self.tickY), (tickX,self.vlen + self.tickY), self.linewidth)
            text = str(int(round(self.constrain_angle(i))))
            img = self.font.render(text , True, (127,127,127))
            textSize = self.font.size(text)
            self.screen.blit(img, (tickX - textSize[0]/2  , textSize[1]//2 + self.tickY + self.vlen))
        #pygame.draw.line(self.screen, (255,255,255), (0,self.height/2),(self.width,self.height/2), self.linewidth)
        self.line_segments(pitch,roll)
    
    def line_segments(self,pitch = 0,roll = 0):
        lim = 50

        start = self.nearest_multiple(pitch - (15))
        ended = self.nearest_multiple(pitch + (15))
        #pygame.draw.line(self.screen, (255,255,255), (self.width/2,self.tickY + self.vlen/2), (self.width/2,self.tickY + self.vlen), self.linewidth)
        for j in range(start,ended + 1,self.increments):
            text = str(int(round(-self.constrain_angle(j))))
            textSize = self.font.size(text)
            h = self.transfrom(j,pitch - (15),pitch + (15),lim,self.height-lim)
            half_width = self.width / 2
            quarter_width = self.width / 4
            half_quarter_width = quarter_width/8
            x0, y0 = quarter_width,h
            x1, y1 = x0 + half_quarter_width*4 ,h
            x2, y2 = x1, h - half_quarter_width * 0.5 * np.sign(j)#
            x3, y3 = half_width + half_quarter_width*4 ,h 
            x4, y4 = x3 + half_quarter_width*4  ,h
            x5, y5 = x3, h - half_quarter_width *0.5 * np.sign(j)#
            x6, y6  = x0 - textSize[0] -half_quarter_width ,h - textSize[1]//2 
            x7, y7 = x4 + textSize[0] + 0.5 *half_quarter_width ,h - textSize[1]//2 
            x0, y0 = self.rotate(x0,y0,roll)#,-half_width,h)
            x1, y1 = self.rotate(x1,y1,roll)#,-half_width,h)
            x2, y2 = self.rotate(x2,y2,roll)#,-half_width,h)
            x3, y3 = self.rotate(x3,y3,roll)#,-half_width,h)
            x4, y4 = self.rotate(x4,y4,roll)#,-half_width,h)
            x5, y5 = self.rotate(x5,y5,roll)#,-half_width,h)
            x6, y6 = self.rotate(x6,y6,roll)#,-half_width,h)
            x7, y7 = self.rotate(x7,y7,roll)#, - half_width,h)
            if (y1 and y2 and y3 and y4 and y5 and y6 and y7 > lim) and (y1 and y2 and y3 and y4 and y5 and y6 and y7 < self.height - lim):
                pygame.draw.line(self.screen, (255,255,255),(x0,y0),(x1,y1) , self.linewidth)
                pygame.draw.line(self.screen, (255,255,255),(x1,y1),(x2,y2) , self.linewidth)
                pygame.draw.line(self.screen, (255,255,255),(x3,y3),(x4,y4) , self.linewidth)
                pygame.draw.line(self.screen, (255,255,255),(x3,y3),(x5,y5) , self.linewidth)       
                img = self.font.render(text , True, (127,127,127))
                self.screen.blit(img, (x6,y6))                
                self.screen.blit(img, (x7,y7))                
class Visualizer:
    def __init__(self,width=640,height=480):
        self.mouseX, self.mouseY, self.throttle, self.steering = 0, 0, 0, 0
        pygame.init()
        pygame.joystick.init()
        self.clock = clock = pygame.time.Clock()
        self.fps = 11
        self.width, self.height = width, height
        self.display = pygame.display
        self.screen = self.display.set_mode((self.width, self.height))
        self.display.set_caption('pants')
        #self.icon = pygame.image.load('SPCX.ico')
        #self.display.set_icon(self.icon)
        self.running = True
        self.background_colour = (0, 0, 0)
        self.debug = False
        self.joystick = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        self.joystick_init = [self.joystick[x].init() for x in range(pygame.joystick.get_count())]
        self.joystick_name = [self.joystick[x].get_name() for x in range(pygame.joystick.get_count())]
        #self.joystick = pygame.joystick.Joystick(1)
        #self.joystick_name = self.joystick.get_name()
        self.joystick_ids = [self.joystick[x].get_id() for x in range(pygame.joystick.get_count())]
        self.axes = [self.joystick[x].get_numaxes() for x in range(pygame.joystick.get_count())]
        self.buttons = [self.joystick[x].get_numbuttons() for x in range(pygame.joystick.get_count())]
        self.hats = [self.joystick[x].get_numhats() for x in range(pygame.joystick.get_count())]
        self.hud = HUD(self.screen)
        #self.cap_receive = cv2.VideoCapture('udpsrc port=5000 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER)
        self.cap_receive = cv2.VideoCapture(0)
        if not self.cap_receive.isOpened():
            print('VideoCapture not opened')


        
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.cap_receive.release()
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.debug:
                    print(pygame.key.name(event.key),"DOWN")
                else:
                    pass
            elif event.type == pygame.KEYUP:
                if self.debug:
                    print(pygame.key.name(event.key),"UP")
                else:
                    pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.debug:
                    print(event.pos,event.button)
                else:
                    pass
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.debug:
                    print(event.pos,event.button)
                else:
                    pass
            elif event.type == pygame.MOUSEMOTION:    
                self.mouseX = event.pos[0]
                self.mouseY = event.pos[1]

                
                if self.debug:
                    print(event.pos,event.rel,event.buttons)
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    self.steering = event.value
                if event.axis == 2:
                    self.throttle = event.value
                if self.debug:
                    print(event.joy, "---", event.axis, "---", event.value)

            elif event.type == pygame.JOYBUTTONDOWN:
                if self.debug:
                    print(event.joy, "---", event.button)
                    print(pygame.key.name(event.button),"DOWN")

            elif event.type == pygame.JOYBUTTONUP:
                if self.debug:
                    print(event.joy,"---",event.button)
                    print(pygame.key.name(event.button),"UP")

            elif event.type == pygame.JOYHATMOTION:
                if self.debug:
                    print(event.joy, "---", event.hat, "---", event.value)
                else:
                    pass

    def run(self,angle=(0,0,0)):
        self.handle_events()
        if self.running:
            try:
                if  self.cap_receive.isOpened():
                    ret,frame = self.cap_receive.read()
                if not ret:
                    frame = np.zeros(shape=((480, 640, 3)))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = np.rot90(frame)
                frame = pygame.surfarray.make_surface(frame)
                self.screen.blit(frame, (0,0))
                #self.screen.fill(self.background_colour)
                self.hud.render(float(angle[2]),-float(angle[0]),float(angle[1]))
                self.display.flip()# UPDATE ENTIRE SCREEN
                self.clock.tick(self.fps)
                #print("Attitude:",angle,"FPS:",int(round(self.clock.get_fps())),end="\r")
            except Exception as e:
                print(e)
        else:
            return
         
#V = Visualizer()
#while V.running:
#    V.run()
     
