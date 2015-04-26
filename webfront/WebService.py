from Toretti import Abmessungen
from Toretti import draw
from Toretti import get_time
from Stepper import PiStepper
from Servo import PiServo
import os, os.path
import cherrypy
import cv2

class MotorControl(object):	
	@cherrypy.expose
	def index(self):
		return file('index.html')

class Indication(object):
	exposed = True
	
	def POST(self, information, Alpha1, Alpha2, Beta, P, B , A, R, S, L1_alt, L2_alt):
		M = Abmessungen(float(Alpha1), float(Alpha2), float(Beta), float(P), float(B) ,float(A), float(R),float(S), float(L1_alt), float(L2_alt))
		img = cv2.imread("public/pics/img.jpg",0)
		can = cv2.Canny(img, 100,200)
		
		if information == 'time':
			t = get_time(can,M)
			if t < 60:
				return '%d Sekunden'%t
			else:
				if t < 3600:
					return '%d Minuten'%(int(t/60))
				else:
					return '%d Stunde/n %d Minute/n'%(t/3600, t/60-(int(t/3600)*60))
		
		if information == 'error':
			y,x = can.shape
			if M.x_max < x:
				return 'Bild ist zu breit. Maximale breite: %d Pixel'%M.x_max
			else:
				return 'none'

class MotorControlWebService(object):
	exposed = True
	#max speed = 0.002
	stepper_l = PiStepper([14,15,18,23],0.00001)
	stepper_r = PiStepper([17,27,22,10],0.00001)
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
		
		#img = cv2.imread("public/pics/img.jpg",1)
		im_gray = cv2.imread('public/pics/img.jpg', cv2.CV_LOAD_IMAGE_GRAYSCALE)
		#(thresh, im_bw) = cv2.threshold(im_gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
		
		# edges
		can = cv2.Canny(im_gray, 100,200)
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
		'/indicator': {
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
	webapp.indicator = Indication()
	webapp.picupload = PictureUpload()
	cherrypy.quickstart(webapp,'/', conf)
