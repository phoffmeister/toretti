import math
import cv2
import numpy as nu

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


def goto_x_y(x,y,l1_alt,l2_alt,masze,step_l, step_r):
	l1_tmp, l2_tmp = pix2len(x,y,masze)
	s1 = int((l1_tmp - l1_alt) / masze.delta_l_min)
	s2 = int((l2_tmp - l2_alt) / masze.delta_l_min)
	
	#print "going to %d,%d l1_alt=%f, l2_alt=%f, l1_neu=%f, l2_neu=%f, s1=%d s2=%d"%(x,y,l1_alt,l2_alt,l1_tmp,l2_tmp,s1,s2)
	print "moving to %d/%d"%(x,y)
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

def time_goto_x_y(x,y,l1_alt,l2_alt,masze,step_l, step_r):
	l1_tmp, l2_tmp = pix2len(x,y,masze)
	s1 = int((l1_tmp - l1_alt) / masze.delta_l_min)
	s2 = int((l2_tmp - l2_alt) / masze.delta_l_min)

	return s1+s1, l1_alt+(s1*masze.delta_l_min), l2_alt+(s2*masze.delta_l_min)

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
	
def draw(m, pen, st_l, st_r):
	m.print_m()
	img = cv2.imread("public/pics/img.jpg",0)

	## <-------------- scale img here

	# edges
	can = cv2.Canny(img, 200,200)
	
	l1_alt = m.l1_alt
	l2_alt = m.l2_alt
	
	
	s_y , s_x = can.shape
	
	
	offset = int( (m.x_max - s_x ) / 2)
	
	all_steps = 0
	all_dots = 0
	##measure time
	for j in range(s_y-1,0,-2):
		for i in range(s_x):
			if can[j][i]:
				# goto i,j and print a dot
				steps, l1_alt, l2_alt = time_goto_x_y(i+offset,j,l1_alt,l2_alt,m,st_l,st_r)
				all_steps += steps
				all_dots += 1
		if j-1 >= 0:
			for i in range(s_x-1,0,-1):
				if can[j-1][i]:
					steps, l1_alt, l2_alt = time_goto_x_y(i+offset,j-1,l1_alt,l2_alt,m,st_l,st_r)
					all_steps += steps
					all_dots += 1
	
	all_seconds = all_steps * 0.002 * 8
	all_seconds += all_dots * 1.6
	
	print 'printing will take %f seconds'%all_seconds
	
	
	print "bildgroesze: %d, %d"%(s_x,s_y)
	print "xmax=%d"%(m.x_max)
	##start bottom and go up
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
	
