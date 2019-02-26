import copy
import csv
import pandas as pd  
import time 
import itertools as it
import scipy.stats as st
import math
import numpy as np

def make_grid(n_grid, grid_size_x, grid_size_y, left_x, down_y):

	grid_x =  [(left_x + i*grid_size_x) for i in xrange(n_grid)]
	grid_y =  [(down_y + i*grid_size_y) for i in xrange(n_grid)]
	grid = list(it.product(grid_x,grid_y))

	return grid



def get_grid_in_gaze(grid, gaze_points, radius):
	in_gaze = set()
	for grd in grid:
		for gp in gaze_points:
			x_diff = float(gp[0]) - float(grd[0])
			y_diff = float(gp[1]) - float(grd[1])
			diff = (x_diff**2 + y_diff**2)**0.5
			if diff < radius:
				in_gaze.add(grd)
				break

	return in_gaze




def get_tracker_data(name):

	f = pd.read_csv(name, sep="\t")
	return f


def get_dot_data(name):

	f = pd.read_csv(name, sep="\t")
	return f


def get_gaze_distance(gaze_point, dot_loc):

	if gaze_point[0] > 0:
		x_diff = float(gaze_point[0]) - float(dot_loc[0])
		y_diff = float(gaze_point[1]) - float(dot_loc[1])
		diff = (x_diff**2 + y_diff**2)**0.5
		return diff
	else:
		return -1

def get_min_gaze(gaze_points, dot,cutoff=100):

	min_dist = -1
	which_gaze = None
	n_below_x = 0

	p_in_gaze = 1.
	n_continuous_below_x = 0
	seen_discrete = []
	n_non_negative = 0

	n_fixate = 0
	fixate_discrete = []
	path_length = 0


	#p_func = lambda x: 2.*(1 - 1/(1+np.exp(-0.01*x)))
	p_func = lambda x: max(2.*(1 - 1/(1+np.exp(-0.01*x))), 1e-3)

	for i in xrange(len(gaze_points)):
		g = gaze_points[i]
		dist = get_gaze_distance(g, dot)
		if dist > 0:
			p_in_gaze *= (1. - p_func(dist))

			if (min_dist == -1 or dist < min_dist):
				min_dist = dist
				which_gaze = g



			if dist < cutoff:

				n_below_x += 1
				n_continuous_below_x += 1

			if ((i == (len(gaze_points) - 1)) or (cutoff <= dist)):

				if ((n_continuous_below_x > 0) or 
					(i == (len(gaze_points) - 1))):
					seen_discrete.append(n_continuous_below_x)
				n_continuous_below_x = 0


		if i == 0:
			g_prev = g
		else:
			if g[0] > 0 and g_prev > 0:
				n_non_negative += 1

				dist_from_prev = get_gaze_distance(g, g_prev)
				path_length  += get_gaze_distance(g, gaze_points[i-1])
				if  (dist_from_prev < 20):
					n_fixate += 1.
				if ((dist_from_prev >= 20) or
					 (i == (len(gaze_points) - 1))):
					fixate_discrete.append(n_fixate)
					n_fixate = 0
					g_prev = g

	if n_non_negative > 0:
		fixate_discrete = np.array(fixate_discrete)
		med_fix = np.mean(fixate_discrete)
	else:
		med_fix = -1


	n_looks =  len(seen_discrete) * (n_below_x > 0)

	p_in_gaze = 1. - p_in_gaze


	return min_dist, which_gaze, n_below_x, n_looks, med_fix, path_length, p_in_gaze



def main(t_d, r_d, o_d, cutoff, dimensions):
	tracker_data = get_tracker_data(t_d)
	response_data = get_dot_data(r_d)

	unique_trial_resp = pd.unique(response_data["trial_id"])
	unique_trial_tracker = pd.unique(tracker_data["trial_id"])
	print len(unique_trial_resp), len(unique_trial_tracker)
	if (len(unique_trial_resp) != len(unique_trial_tracker)):
		#discrimination data
		response_data["trial_id"] = (response_data["trial_id"]-1)* 2 + response_data["which_array"] 

		unique_trial_resp = pd.unique(response_data["trial_id"])
		unique_trial_tracker = pd.unique(tracker_data["trial_id"])

		assert(list(unique_trial_resp)==list(unique_trial_tracker))

	trials = pd.unique(response_data["trial_id"])
	new_resp_data = copy.deepcopy(response_data)
	new_resp_data["gazeX"] = None
	new_resp_data["gazeY"] = None
	new_resp_data["gazeDist"] = None
	new_resp_data["belowX"] = None
	new_resp_data["totArea"] = None
	new_resp_data["pctArea"] = None
	new_resp_data.at['nLooks'] = None
	new_resp_data.at['medFix'] = None
	new_resp_data.at['pathLength'] = None
	new_resp_data.at['pInGaze'] = None

	left_x = dimensions[0][0]
	right_x = dimensions[0][1]
	down_y = dimensions[1][0]
	up_y = dimensions[1][1]
	width = abs(left_x - right_x)
	height =  abs(up_y - down_y)
	grid_size_y = height/float(n_grid)
	grid_size_x = width/float(n_grid)
	grid = make_grid(n_grid, grid_size_x, grid_size_y, left_x, down_y)

	z = 0
	N_row = len(response_data)
	prev_gp = {}
	for z,row in response_data.iterrows():
		t = row["trial_id"]

		td = tracker_data[tracker_data["trial_id"] == t]

		gaze = zip(td["GazePointX"], td["GazePoint"])
		p = row["dl_x"], row["dl_y"]	

		min_gaze = get_min_gaze(gaze, p,  cutoff=cutoff)

		grid_in_gaze = get_grid_in_gaze(grid, gaze, cutoff)

		tot_area = grid_size_x * grid_size_y * len(grid_in_gaze)
		pct_area = tot_area/(float(width*height))

		if min_gaze[1] != None:
			dist = min_gaze[0]		
			gaze_x = min_gaze[1][0]
			gaze_y = min_gaze[1][1]
			n_below_x = min_gaze[2]
			n_looks = min_gaze[3]
			med_fix = min_gaze[4]
			path_length = min_gaze[5]
			p_in_gaze = min_gaze[6]

			new_resp_data.at[z, 'gazeDist'] = dist
			new_resp_data.at[z, 'gazeX'] = gaze_x
			new_resp_data.at[z, 'gazeY'] = gaze_y
			new_resp_data.at[z, 'belowX'] = n_below_x
			new_resp_data.at[z, 'totArea'] = tot_area
			new_resp_data.at[z, 'pctArea'] = pct_area
			new_resp_data.at[z, 'nLooks'] = n_looks
			new_resp_data.at[z, 'medFix'] = med_fix
			new_resp_data.at[z, 'pathLength'] = path_length
			new_resp_data.at[z, 'pInGaze'] = p_in_gaze

		else:
			new_resp_data.at[z, 'gazeDist'] = -1
			new_resp_data.at[z, 'gazeX'] = -1
			new_resp_data.at[z, 'gazeY'] = -1
			new_resp_data.at[z, 'belowX'] = -1
			new_resp_data.at[z, 'totArea'] = -1
			new_resp_data.at[z, 'pctArea'] = -1
			new_resp_data.at[z, 'nLooks'] = -1
			new_resp_data.at[z, 'medFix'] = -1
			new_resp_data.at[z, 'pathLength'] = -1
			new_resp_data.at[z, 'pInGaze'] = -1

		if (z > 0 and z % 1000 == 0):
			time_so_far = time.time() - t0
			pct_so_far = float(z+1.)/(time.time() - t0), z/float(N_row)


			print (z,time_so_far, pct_so_far, 
				time_so_far / pct_so_far[1] - time_so_far)


	new_resp_data.to_csv(o_d, sep="\t")





if __name__ == "__main__":
	t0 = time.time()
	dimensions = ((0,1920),(0,1200))
	n_grid = 10

	cutoff = 400
	t_d = "data/estimation_tracker_data.csv"
	r_d = "data/estimation_response_data.csv"
	o_d = "data/estimation_dot_gaze.csv"
	main(t_d, r_d, o_d, cutoff, dimensions)
	print "Finished Estimation"
	t_d = "data/discrimination_tracker_data.csv"
	r_d = "data/discrimination_response_data.csv"
	o_d = "data/discrimination_dot_gaze.csv"
	main(t_d, r_d, o_d, cutoff, dimensions)
	print "Finished Discrimination"
