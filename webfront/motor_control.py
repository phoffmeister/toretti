import os, os.path
import string

import cherrypy

from RPIO import PWM
import RPi.GPIO as GPIO

import cv2
import numpy as nu
from matplotlib import pyplot as plt
import sys
from time import sleep

import math



class PiStepper(object):
	def __init__(self, pin_assoc, speed):
		GPIO.setmode(GPIO.BCM)
		self.Speed = speed
		self.A = pin_assoc[0]
		self.B = pin_assoc[1]
		self.C = pin_assoc[2]
		self.D = pin_assoc[3]
		
		GPIO.setup(self.A, GPIO.OUT)
		GPIO.setup(self.B, GPIO.OUT)
		GPIO.setup(self.C, GPIO.OUT)
		GPIO.setup(self.D, GPIO.OUT)
		GPIO.output(self.A, False)
		GPIO.output(self.B, False)
		GPIO.output(self.C, False)
		GPIO.output(self.D, True)
	
	def off(self):
		GPIO.output(self.D, False)
		
	def on(self):
		GPIO.output(self.D, True)
		
	def step(self, clockwise):
		if not  clockwise:
			GPIO.output(self.C, True)
			sleep(self.Speed)			## D, C
			GPIO.output(self.D, False)
			sleep(self.Speed)			## C
			GPIO.output(self.B, True)
			sleep(self.Speed)			## C, B
			GPIO.output(self.C, False)
			sleep(self.Speed)			## B
			GPIO.output(self.A, True)
			sleep(self.Speed)			## B, A
			GPIO.output(self.B, False)
			sleep(self.Speed)			## A
			GPIO.output(self.D, True)
			sleep(self.Speed)			## A, D
			GPIO.output(self.A, False)
			sleep(self.Speed)			## D
		else:
			GPIO.output(self.A, True)
			sleep(self.Speed)			## A, D
			GPIO.output(self.D, False)
			sleep(self.Speed)			## A
			GPIO.output(self.B, True)
			sleep(self.Speed)			## B, A
			GPIO.output(self.A, False)
			sleep(self.Speed)			## B
			GPIO.output(self.C, True)
			sleep(self.Speed)			## C, B
			GPIO.output(self.B, False)
			sleep(self.Speed)			## C
			GPIO.output(self.D, True)
			sleep(self.Speed)			## D, C
			GPIO.output(self.C, False)
			sleep(self.Speed)			## D

class Abmessungen(object):
	def __init__(self, Alpha1, Alpha2, Beta, P, B , A, R, S, L1_alt, L2_alt):
		self.alpha1 = Alpha1
		self.alpha2 = Alpha2
		self.beta = Beta
		self.p = P
		self.b = B
		self.a = A
		self.s = S
		self.r = R
		self.l1_alt = L1_alt
		self.l2_alt = L2_alt
		self.delta_l_min = R * math.pi / 256
		self.x_max = ( (S - Alpha1 - Alpha2) / P) + 1
	
	def print_m(self):
		print self.alpha1, self.alpha2, self.beta, self.p, self.b, self.a, self.s, self.r, self.l1_alt, self.l2_alt, self.delta_l_min, self.x_max
		

class PiServo(object):
	def __init__(self, Chan, Upper, Lower):
		self.chan = Chan
		self.upper = Upper
		self.lower = Lower
		self.servo = PWM.Servo()
		PWM.set_loglevel(1)
		self.servo.set_servo(self.chan, self.upper)
	
	def down(self):
		self.servo.set_servo(self.chan, self.lower)
	
	def up(self):
		self.servo.set_servo(self.chan, self.upper)
	
	def draw_dot(self):
		sleep(0.6)
		self.down()
		sleep(0.7)
		self.up()
		sleep(0.3)


def goto_x_y(x,y,l1_alt,l2_alt,masze,step_l, step_r):
	l1_tmp, l2_tmp = pix2len(x,y,masze)
	s1 = int((l1_tmp - l1_alt) / masze.delta_l_min)
	s2 = int((l2_tmp - l2_alt) / masze.delta_l_min)
	
	print "going to %d,%d l1_alt=%f, l2_alt=%f, l1_neu=%f, l2_neu=%f, s1=%d s2=%d"%(x,y,l1_alt,l2_alt,l1_tmp,l2_tmp,s1,s2)
	
	if s1 < 0:
		ccw_l = True
		steps_l = s1*(-1)
	else:
		ccw_l = False
		steps_l = s1
		
	if s2 < 0:
		ccw_r = False
		steps_r = s2*(-1)
	else:
		ccw_r = True
		steps_r = s2
		
	move = True
	
	while move:
		move = False
		if steps_l > 0:
			move = True
			step_l.step(ccw_l)
			steps_l = steps_l - 1
		if steps_r > 0:
			move = True
			step_r.step(ccw_r)
			steps_r = steps_r - 1

	return l1_alt+(s1*masze.delta_l_min), l2_alt+(s2*masze.delta_l_min)
	#return l1_tmp, l2_tmp

def go_home(l1_alt,l2_alt,masze,step_l, step_r):

	s1 = int((masze.l1_alt -l1_alt) / masze.delta_l_min)
	s2 = int((masze.l2_alt - l2_alt) / masze.delta_l_min)
	
	print "going HOME"
	
	if s1 < 0:
		ccw_l = True
		steps_l = s1*(-1)
	else:
		ccw_l = False
		steps_l = s1
		
	if s2 < 0:
		ccw_r = False
		steps_r = s2*(-1)
	else:
		ccw_r = True
		steps_r = s2
		
	move = True
	
	while move:
		move = False
		if steps_l > 0:
			move = True
			step_l.step(ccw_l)
			steps_l = steps_l - 1
		if steps_r > 0:
			move = True
			step_r.step(ccw_r)
			steps_r = steps_r - 1

		
	return l1_tmp, l2_tmp
	
def pix2len( pix_x, pix_y , masze):
	
	x1 = masze.alpha1 + ( masze.p * pix_x ) - ( masze.b / 2 )
	y1 = masze.beta + ( masze.p * pix_y * 1.17 ) + masze.a
	#print "alpha1=%f p=%f pix_x=%d b=%f"%(masze.alpha1, masze.p,pix_x,masze.b)
	len_1 = math.sqrt( (x1*x1) + (y1*y1) )
	
	x2 = ( ( masze.x_max - pix_x ) * masze.p ) - (masze.b/2) + masze.alpha2
	y2 = ( pix_y * masze.p * 1.17 ) + masze.a + masze.beta
	
	len_2 = math.sqrt( (x2*x2) + (y2*y2) )
	
	return len_1, len_2


class MotorControl(object):
	@cherrypy.expose
	def index(self):
		return file('index.html')

def draw(m, pen, st_l, st_r):
		m.print_m()
		img = cv2.imread("public/pics/img.jpg",0)

		## <-------------- scale img here

		# edges
		can = cv2.Canny(img, 200,200)
		
		##<---------------  ausgangsposition messen
		l1_alt = m.l1_alt
		l2_alt = m.l2_alt
		
				
		s_y , s_x = can.shape
		
		
		offset = int( (m.x_max - s_x ) / 2)
		
		print "bildgroesze: %d, %d"%(s_x,s_y)
		print "xmax=%d"%(m.x_max)
		for j in range(s_y-1,0,-2):
			for i in range(s_x):
				if can[j][i]:
					# goto i,j and print a dot
					l1_alt, l2_alt = goto_x_y(i+offset,j,l1_alt,l2_alt,m,st_l,st_r)
					#print 'going to %d, %d'%(i,j)
					pen.draw_dot()
			if j-1 >= 0:
				for i in range(s_x-1,0,-1):
					if can[j-1][i]:
						# goto i,j and print a dot
						l1_alt, l2_alt = goto_x_y(i+offset,j-1,l1_alt,l2_alt,m,st_l,st_r)
						#print 'going to %d, %d'%(i,j)
						pen.draw_dot()
		go_home(l1_alt,l2_alt,m,st_l,st_r)

class MotorControlWebService(object):
	exposed = True
	
	stepper_l = PiStepper([14,15,18,23],0.002)
	stepper_r = PiStepper([17,27,22,10],0.002)
	stift = PiServo(7, 1700, 1800)
	
	def PUT(self,motor,steps,direction):
		if motor == 'servo':
			if direction == 'up':
				self.stift.up()
			else:
				self.stift.down()
		elif motor == 'left':
			for st in range(int(steps)):
				self.stepper_l.step(direction == 'ccw')
		elif motor == 'right':
			for st in range(int(steps)):
				self.stepper_r.step(direction == 'ccw')
	
	def POST(self, Alpha1, Alpha2, Beta, P, B , A, R, S, L1_alt, L2_alt):
		self.M = Abmessungen(float(Alpha1), float(Alpha2), float(Beta), float(P), float(B) ,float(A), float(R),float(S), float(L1_alt), float(L2_alt))
		print self.M.l2_alt
		draw(self.M, self.stift, self.stepper_l, self.stepper_r)
		return 'done'

class PictureUpload(object):
	
	@cherrypy.expose
	def index(self):
		return """<html><body><form action="upload" method="post" enctype="multipart/form-data"><input type="file" name="myFile" /> <br /><input type="submit" /></form></body></html>"""

	@cherrypy.expose
	def upload(self, myFile):
		out = open("public/pics/img.jpg", "w")
		while True:
			data = myFile.file.read(8192)
			if not data:
				break
			out.write(data)
		out.close()
		
		img = cv2.imread("public/pics/img.jpg",0)

		## <-------------- scale img here

		# edges
		can = cv2.Canny(img, 200,200)
		
		cv2.imwrite("public/pics/canny.jpg",can)
		return """<html><body>done<a href="/">back<a/>"""
		

if __name__ == '__main__':
	conf = {
		'global': { 
			'server.socket_host': '0.0.0.0',
			'server.socket_port': 8080,
			},
		'/' : {
			'tools.sessions.on': True,
			'tools.staticdir.root': os.path.abspath(os.getcwd())
		},
		'/picupload' : {
			'tools.sessions.on': True
		},
		'/control': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.response_headers.on': True,
			'tools.response_headers.headers': [('Content-Type', 'text/plain')],
		},
		'/static': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': './public'
		}
	}
	
	webapp = MotorControl();
	webapp.control = MotorControlWebService()
	webapp.picupload = PictureUpload()
	cherrypy.quickstart(webapp,'/', conf)
