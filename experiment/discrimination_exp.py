
import os, sys
import pygame
from random import randint, choice, sample, shuffle, random
from time import time, sleep
import itertools
import math
import csv

from kelpy.CommandableImageSprite import *
from kelpy.TextSprite import *
from kelpy.DotStimulus import *

from kelpy.Miscellaneous import *
from kelpy.DisplayQueue import *
from kelpy.OrderedUpdates import *
from kelpy.EventHandler import *
from kelpy.Dragable import *
from kelpy.DragDrop import *


from kelpy.tobii.TobiiSimController import *
from kelpy.tobii.TobiiSprite import *

##############################################
## Experiment Parameters

use_tobii_sim = True #toggles between using the tobii simulator or the actual tobii controller
min_dots = 10
max_dots = 90
trials_per_time = 16
times = [x for x in itertools.product([0.1, 1.0], repeat=2)]

random.shuffle(times)
iti = 1.5 #number of seconds to wait between each trial
dot_radius = 10

file_header = ['Subject', 'Session', 'Trial','Time1', 'Time2','Trial_Start', 'Trial_End', 
		'Dots_Shown1','Dots_Shown2', 'Dots_Counted','Score', 'Dot_Width',
			 'Dot_Height', "which_array", 'dl_x', 'dl_y']
data_folder = './data/'

subject = raw_input('Subject ID: ')
session = raw_input('Session #: ')
session_time = str(time())

#also append time to filename
data_file = "%s/discrimination_%s_%s_%s.csv" % (data_folder, 
								subject, session, session_time)

IMAGE_SCALE = 0.1


##############################################
## Set up kelpy

#screen, spot= initialize_kelpy( dimensions=(800,600) )
screen, spot = initialize_kelpy( fullscreen=True )
middle = (screen.get_width()/2, screen.get_height()/2)


##############################################
## Set up eye tracker

if use_tobii_sim:
	#create a tobii simulator
	tobii_controller = TobiiSimController(screen)
	#store tobii data in this file
	tobii_controller.set_data_file(data_folder + subject + '_' + session + '_' + session_time + '.tsv')


else:
	#create an actual tobii controller
	tobii_controller = TobiiController(screen)

	# code for when it's actually hooked up to the eye tracker
	tobii_controller.wait_for_find_eyetracker(3)

	#store tobii data in this file
	tobii_controller.set_data_file(data_folder + subject + '_' + session + '_' + session_time + '.tsv')

	#activate the first tobii eyetracker that was found
	tobii_controller.activate(tobii_controller.eyetrackers.keys()[0])

use_tobii_sim = False



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Run a single trial
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	

#static_im = DotStimulus(screen, middle, N=500, pad=0, 
			#radius=4., circled=False, height=screen.get_height(), 
				#width=screen.get_width(), dot_color=(0,0,0))

static_image = kstimulus('misc/static.png')
dot_image = kstimulus('shapes/circle_red.png')
blank_image = kstimulus('misc/blankbox.png')

blank1 = CommandableImageSprite(screen, 
(screen.get_width()*0.38, screen.get_height() * 0.5),
			 blank_image)
blank2 = CommandableImageSprite(screen, 
(screen.get_width()*0.5, screen.get_height() * 0.5),
			 blank_image)
blank3 = CommandableImageSprite(screen, 
(screen.get_width()*0.62, screen.get_height() * 0.5),
			 blank_image)
static = CommandableImageSprite(screen, middle, static_image, scale=2.5)
request1 = TextSprite("Did the first or second screen have more dots?", screen, middle)
request2 = TextSprite("Press 1 or 2.", screen, 
				(screen.get_width()*0.5, screen.get_height() * 0.55))

def add_fixation(t):
	fixation = kstimulus('fixation/blue_cross.png')

	fix = CommandableImageSprite(screen, middle, fixation)
	Q = DisplayQueue()
	dos = OrderedUpdates(fix) 

	t1 = time()
	for event in kelpy_standard_event_loop(screen, Q, dos,
							 throw_null_events=True):

		if event.type == KEYDOWN:
			#need to do a check for exiting here
			if event.key == K_ESCAPE:
				#make sure to close the data file when exiting, otherwise it'll hang
				if not use_tobii_sim:
					tobii_controller.stop_tracking()
					tobii_controller.close_data_file()
					tobii_controller.destroy()


		time_elapsed = time() - t1
		if time_elapsed > t:
			break


def add_dots(num_dots, max_time):

	dots = DotStimulus(screen, middle, N=num_dots, circled=False,radius=dot_radius,
				 dot_color=(255,0,0), height=screen.get_height()*0.9, 
					width=screen.get_width()*0.9)
	
	dot_locations = dots.dot_positions

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# Set up the updates, etc. 
	
	# A queue of animation operations

	dos = OrderedUpdates(dots) # Draw and update in this order
	Q = DisplayQueue()
	## Note the start time...
	trial_start = time()

	if not use_tobii_sim:
		# start recording the "eye gaze" data
		tobii_controller.start_tracking()		

	for event in kelpy_standard_event_loop(screen, Q, dos,
								 throw_null_events=True):

		time_elapsed = time() - trial_start
		if time_elapsed - max_time > 0:
			trial_end = time()

			if not use_tobii_sim:				
				#stop collecting "eye gaze" data
				tobii_controller.stop_tracking()

			break
		if event.type == KEYDOWN:

			#need to do a check for exiting here
			if event.key == K_ESCAPE:
				#make sure to close the data file when exiting, otherwise it'll hang
				if not use_tobii_sim:
					tobii_controller.stop_tracking()
					tobii_controller.close_data_file()
					tobii_controller.destroy()

	return dot_locations


def make_guess():

	clear_screen(screen)

	
	#l = [static_im, request]
	l = [static, blank1,blank2, blank3, request1, request2]


	dos = OrderedUpdates(l)
	Q = DisplayQueue()


	for event in kelpy_standard_event_loop(screen, Q, dos,
							 throw_null_events=False):
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				#make sure to close the data file when exiting, otherwise it'll hang
				if not use_tobii_sim:
					tobii_controller.stop_tracking()
					tobii_controller.close_data_file()
					tobii_controller.destroy()

			elif event.key == K_1 or event.key == K_KP1:
				return '1';
			elif event.key == K_2 or event.key == K_KP2:
				return '2'

def present_trial(num_dots, max_time):
	"""
	This presents an array of dots, and tracks the participant's eye gaze

	The trial ends after the participant inputs a number + enter
	"""

	#image for dots

	add_fixation(iti)
	clear_screen(screen)

	t1 = time()

	dot_locations1 = add_dots(num_dots[0], max_time[0])
	clear_screen(screen)

	add_fixation(iti/2)
	clear_screen(screen)
	t2 = time()

	dot_locations2 = add_dots(num_dots[1], max_time[1])
	clear_screen(screen)

	guess = make_guess()
	clear_screen(screen)

	return (t1, t2, guess,dot_radius,dot_radius,
		dot_locations1, dot_locations2)

def present_score(score=0, t=20, mult=2):
	score_texts = []
	bonus = score * mult 

	score_texts.append("Your average accuracy this round was: %0.2f." % score)
	score_texts.append("Press enter to continue.")

	text_sprites = []
	for i in xrange(len(score_texts)):
		score_text = score_texts[i]
		plc = (middle[0], middle[1] +
				 (i - len(score_texts)/2) * 0.075*screen.get_height()/2)
		text_sprites.append(TextSprite(score_text, screen, plc))
	dos = OrderedUpdates(text_sprites)
	
	Q = DisplayQueue()
	start_t = time()
	for event in kelpy_standard_event_loop(screen, Q, dos,
				throw_null_events=True):
		time_elapsed = time() - start_t
		if time_elapsed > t:
			clear_screen(screen)
			return None


		if event.type == KEYDOWN:
			#need to do a check for exiting here
			if event.key == K_ESCAPE:
				#make sure to close the data file when exiting, otherwise it'll hang
				if not use_tobii_sim:
					tobii_controller.close_data_file()
					tobii_controller.destroy()

			elif (event.key == K_RETURN or
			 	(event.key == K_KP_ENTER)):
				return

def present_instructions(n):
	texts = []
	texts.append("This experiment will consist of %d rounds with %d trials in each. " % (len(times), n))
	texts.append("Before each trial you will see a blue cross. Please fixate your eyes on it.")
	
	texts.append("During each trial, two arrays of dots will flash on the screen,")
	texts.append("one after the other, separated by a blue fixation cross.")
	texts.append("Your job will be to determine whether the first or second array had more dots.")
	texts.append("The amount of time you have to look at each dot array will vary. ")
	texts.append("Press enter to continue. ")


	text_sprites = []
	for i in xrange(len(texts)):
		text = texts[i]
		text_sprites.append(TextSprite(text, screen, (middle[0], middle[1] +
				 (i - len(texts)/2) * 0.075*screen.get_height()/2)))


	dos = OrderedUpdates(text_sprites)

	Q = DisplayQueue()
	for event in kelpy_standard_event_loop(screen, Q, dos,
				throw_null_events=True):


		if event.type == KEYDOWN:
			#need to do a check for exiting here
			if event.key == K_ESCAPE:
				#make sure to close the data file when exiting, otherwise it'll hang
				if not use_tobii_sim:
					tobii_controller.close_data_file()
					tobii_controller.destroy()

			elif (event.key == K_RETURN or
					 	event.key == K_KP_ENTER):
				#clear_screen(screen)
				return




def round_update(t, n, which_round):

	texts = []

	texts.append("Round %d" % (which_round + 1))
	texts.append("You will have %0.1f seconds to look at array 1" %t[0])
	texts.append("and then %0.1f seconds to look at array 2." % t[1])
	texts.append("There are %d trials in the round." % (n))
	texts.append("Press enter to start.")


	text_sprites = []
	for i in xrange(len(texts)):
		text = texts[i]
		text_sprites.append(TextSprite(text, screen, (middle[0], middle[1] +
				 (i - len(texts)/2) * 0.075*screen.get_height()/2)))


	dos = OrderedUpdates(text_sprites)

	Q = DisplayQueue()
	for event in kelpy_standard_event_loop(screen, Q, dos,
				throw_null_events=True):


		if event.type == KEYDOWN:
			#need to do a check for exiting here
			if event.key == K_ESCAPE:
				#make sure to close the data file when exiting, otherwise it'll hang
				if not use_tobii_sim:
					tobii_controller.close_data_file()
					tobii_controller.destroy()

			elif (event.key == K_RETURN or
					 	event.key == K_KP_ENTER):
				clear_screen(screen)
				return
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main experiment
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	

#will either use a txt/csv file for the number of dots to present, or a RNG; we'll use RNG for now
#trial_dots = [100,50,25]

#choose a number from each number pair between 1 and 20 (e.g. 1 or 2, 3 or 4, 5 or 6, etc.)
trials_dots=[]
trial_dots = []

while len(trial_dots) < trials_per_time:
	r1 = random.randint(min_dots,max_dots-1)

	frac = r1 * (1/3.)

	new_low = max([int(r1 - frac), min_dots])
	new_high = min([int(r1 + frac), max_dots])
	r2 = random.randint(new_low,new_high)
	if r2 == r1:
		r2 += 1

	trial_dots.append((r1, r2))
	trial_dots.append((r2, r1))

for _ in xrange(len(times)):
	random.shuffle(trial_dots)
	trials_dots.append(copy(trial_dots))

#then shuffle

#hide mouse pointer
pygame.mouse.set_visible(False)

#open and start writing to data file
with open(data_file, 'wb') as df:

	#create csv writer (using tabs as the delimiter; the "tsv" extension is being used for the tobii output)
	writer = csv.writer(df, delimiter= ',')

	#write the header for the file
	writer.writerow(file_header)

	#present the 10 trials
	trial = 0
	score = 0.
	present_instructions(trials_per_time)

	for t in xrange(len(times)):
		time_ind = times[t]
		print time_ind
		round_update(time_ind, len(trials_dots[t]), t)
		round_score = 0
		for trial in range(len(trials_dots[t])):
			sleep(iti/2) #wait before presenting next trial

			trial_start, trial_end, guess, dot_width, dot_height, dot_locations1, dot_locations2 = present_trial(trials_dots[t][trial], time_ind)


			gt_21 = (len(dot_locations2) > len(dot_locations1))
			trial_score = ((int(guess) - 1) == (gt_21))
			print len(dot_locations1), len(dot_locations2), guess, trial_score

			score +=  trial_score
			round_score += trial_score
			#output trial info to csv
			for dl in dot_locations1:
				dl1 = dl[0]
				dl2 = dl[1]
				which = "1"
				writer.writerow([subject, session, trial,time_ind[0],time_ind[1], trial_start, trial_end, 
					trials_dots[t][trial][0],trials_dots[t][trial][1],
					 guess, trial_score, dot_width, dot_height, which, dl1, dl2])
			for dl in dot_locations2:
				dl1 = dl[0]
				dl2 = dl[1]
				which = "2"
				writer.writerow([subject, session, trial,time_ind[0],time_ind[1], trial_start, trial_end, 
					trials_dots[t][trial][0],trials_dots[t][trial][1],
					 guess, trial_score, dot_width, dot_height, which, dl1, dl2])



		present_score(round_score / float(trial + 1))

		#print out the number of dots shown and the number counted (for debugging)
		#print 'dots shown: ' + str(trial_dots[trial]) + ', dots counted: ' + str(num_counted)


if not use_tobii_sim:
	#when using the real tobii, make sure to close the eye tracking file and close connection
	tobii_controller.close_data_file()
	tobii_controller.destroy()


