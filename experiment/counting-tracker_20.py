
import os, sys
import pygame
from random import randint, choice, sample, shuffle, random
from time import time, sleep
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
max_dots = 150
trials_per_time = 3
times = [0.1, 0.5, 2.5]
iti = 1.5 #number of seconds to wait between each trial
dot_radius = 14

file_header = ['Subject', 'Session', 'Trial','Time', 'Trial_Start', 'Trial_End', 
		'Dots_Shown', 'Dots_Counted','Score', 'Dot_Width',
			 'Dot_Height', 'dl_x', 'dl_y']
data_folder = './data/'

subject = raw_input('Subject ID: ')
session = raw_input('Session #: ')
session_time = str(time())

#also append time to filename
data_file = data_folder + subject + '_' + session + '_' + session_time + '.csv'

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

static_im = DotStimulus(screen, middle, N=500, pad=0, 
			radius=1., circled=False, height=screen.get_height(), 
				width=screen.get_width(), dot_color=(0,0,0))



def present_trial(num_dots, max_time = 1):
	"""
	This presents an array of dots, and tracks the participant's eye gaze

	The trial ends after the participant inputs a number + enter
	"""

	#image for dots
	dot_image = kstimulus('shapes/circle_red.png')
	blank_image = kstimulus('misc/blankbox.png')
	static_image = kstimulus('misc/static.png')
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
		if time_elapsed > iti:
			break

	clear_screen(screen)




	dots = DotStimulus(screen, middle, N=num_dots, circled=False,radius=dot_radius,
				 dot_color=(255,0,0), height=screen.get_height()*0.9, 
					width=screen.get_width()*0.9)
	
	dot_locations = dots.dot_positions

	# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
	# Set up the updates, etc. 
	
	# A queue of animation operations

	dos = OrderedUpdates(dots) # Draw and update in this order
	
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




	clear_screen(screen)
	request = TextSprite("Guess the number of red dots you saw:",screen, middle)
	dos = OrderedUpdates([static_im, request])

	reported_number = '';
	prev_num = '';

	for event in kelpy_standard_event_loop(screen, Q, dos,
							 throw_null_events=False):
		time_elapsed = time() - trial_start
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				#make sure to close the data file when exiting, otherwise it'll hang
				if not use_tobii_sim:
					tobii_controller.stop_tracking()
					tobii_controller.close_data_file()
					tobii_controller.destroy()

			elif event.key == K_0 or event.key == K_KP0:
				reported_number += '0';
			elif event.key == K_1 or event.key == K_KP1:
				reported_number += '1';
			elif event.key == K_2 or event.key == K_KP2:
				reported_number += '2';
			elif event.key == K_3 or event.key == K_KP3:
				reported_number += '3';
			elif event.key == K_4 or event.key == K_KP4:
				reported_number += '4';
			elif event.key == K_5 or event.key == K_KP5:
				reported_number += '5';
			elif event.key == K_6 or event.key == K_KP6:
				reported_number += '6';
			elif event.key == K_7 or event.key == K_KP7:
				reported_number += '7';
			elif event.key == K_8 or event.key == K_KP8:
				reported_number += '8';
			elif event.key == K_9 or event.key == K_KP9:
				reported_number += '9';
			elif event.key == K_BACKSPACE:
				reported_number = reported_number[:-1]
			elif (event.key == K_RETURN or
			 	(event.key == K_KP_ENTER)):
				if reported_number:
					#get the end time

					clear_screen(screen) #function defined in Miscellaneous

					return (trial_start, trial_end, int(reported_number),
							 dot_radius, dot_radius, dot_locations)
			
			if len(reported_number) > 3:
				reported_number = reported_number[:-1]
			if reported_number != prev_num:

				#dos.append(TextSprite(reported_number,screen, placement))

				if len(reported_number) < len(prev_num):
					placement = ((1 + 0.025 * (len(prev_num)-2)) * screen.get_width()/2, 
								screen.get_height()*0.55)
					dos.append(TobiiSprite(screen,placement,blank_image, tobii_controller,
							scale=0.1))
				else:
					placement = ((1 + 0.025 * (len(reported_number)-2)) * screen.get_width()/2, 
								screen.get_height()*0.55)
					dos.append(TextSprite(reported_number[-1],screen, placement))

				prev_num = reported_number


def present_score(score=0, t=2):
	score_text = "Your average accuracy this round so far: %0.2f" % score
	dos = OrderedUpdates([TextSprite(score_text, screen, middle)])
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



def present_instructions(n):
	texts = []
	texts.append("This experiment will consist of %d rounds with %d trials in each. " % (len(times), n))
	texts.append("Before each trial you will see a blue cross. Please fixate your eyes on it.")
	
	texts.append("During each trial, a number of dots will appear on the screen, ")
	texts.append("and your job will be to estimate how many you saw. ")
	texts.append("You will get a bonus payment proportional to your overall accuracy. ")
	texts.append("The amount of time you have to estimate will vary between rounds. ")

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
				clear_screen(screen)
				return




def round_update(t, n, which_round):

	texts = []

	texts.append("In this round, you will have %0.2f seconds to estimate on each trial." % t)
	texts.append("There are %d trials in the round. " % n)

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
	r = random.randint(min_dots,max_dots)
	if r not in trials_dots or random.random() > 0.5:
		trial_dots.append(r)

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
		round_update(time_ind, len(trials_dots[t]), t)
		round_score = 0
		for trial in range(len(trials_dots[t])):
			sleep(iti/2) #wait before presenting next trial

			trial_start, trial_end, num_counted, dot_width, dot_height, dot_locations = present_trial(trials_dots[t][trial], time_ind)


			trial_score = (1 - min(1,abs(num_counted - len(dot_locations))/float(len(dot_locations))))
			print len(dot_locations), num_counted, trial_score

			score +=  trial_score
			round_score += trial_score
			#output trial info to csv
			for dl in dot_locations:
				dl1 = dl[0]
				dl2 = dl[1]
				writer.writerow([subject, session, trial,time_ind, trial_start, trial_end, 
					trials_dots[t][trial], num_counted, trial_score, dot_width, dot_height, dl1, dl2])

			present_score(round_score / float(trial + 1))

			#print out the number of dots shown and the number counted (for debugging)
			#print 'dots shown: ' + str(trial_dots[trial]) + ', dots counted: ' + str(num_counted)


if not use_tobii_sim:
	#when using the real tobii, make sure to close the eye tracking file and close connection
	tobii_controller.close_data_file()
	tobii_controller.destroy()


