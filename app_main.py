import os
from os.path import join
import json
from werkzeug.utils import secure_filename
from flask import Flask, url_for, redirect, render_template, send_file, request, flash
import StringIO

from sklearn.neural_network import MLPRegressor, MLPClassifier
from pydub import AudioSegment
from utils import get_mfccs
from utils import compress_audio_segment
import numpy as np
import matplotlib.pyplot as plt

app = Flask (__name__)
app.secret_key = "this is a secret oooh"

# Preload NN models using pickle
import pickle

curr_dir = os.path.dirname (__file__)
version_code = "v1"
with open (join (curr_dir, "nnet_models/pace_regressor_" + version_code + ".pickle"), "r") as file:
	pace_regressor = pickle.load (file)
with open (join (curr_dir, "nnet_models/arousal_regressor_" + version_code + ".pickle"), "r") as file:
	arousal_regressor = pickle.load (file)
with open (join (curr_dir, "nnet_models/valence_regressor_" + version_code + ".pickle"), "r") as file:
	valence_regressor = pickle.load (file)
with open (join (curr_dir, "nnet_models/genre_classifier_" + version_code + ".pickle"), "r") as file:
	genre_classifier = pickle.load (file)

allowed_extensions = ["wav", "mp3", "ogg", "flac", "wma", "aac"]
global imgIO
imgIO = None
nn_code_to_genre_map = {
	0: "Western Classical",
	1: "East Asia Classical",
	2: "Country",
	3: "Electronic",
	4: "Hip-hop",
	5: "Jazz",
	6: "New Age",
	7: "Rock",
	8: "Soundtracks"
}

@app.route ("/", methods=["POST", "GET"])
def main_page ():
	if request.method == "POST":

		if "sound_file_upload" not in request.files:
			flash ("Error in uploading music file")
			return redirect (request.url)

		file = request.files["sound_file_upload"]
		if file.filename == "":
			flash ("No file has been selected")
			return redirect (request.url)

		fn_parts = file.filename.split (".")
		extension = fn_parts[-1]
		if extension not in allowed_extensions:
			flash ("This file format is not supported")
			return redirect (request.url)

		aud = AudioSegment.from_file (file)
		aud = compress_audio_segment (aud)
		wave_data = np.asarray (aud.get_array_of_samples ())

		# Convert the middle 50% part of the music into MFCC arrays
		# which will be fed into the regressors and the genre classifier
		frame_length = 5000
		frame_step = 500
		mfcc_frame_length = 25
		num_mfcc_coef_kept = 12
		frame_length_i = int (frame_length / 1000. * 11025) # compressed format always have sample rate of 11025
		frame_step_i = int (frame_step / 1000. * 11025)

		first_quarter = int (len (wave_data) * 0.25)
		last_quarter = int (len (wave_data) * 0.75)

		if (last_quarter - first_quarter) / 11025. < 5.0:
			# Middle section is less than 5 seconds
			# Music is too short for analysis
			flash ("The music you uploaded is too short. A length of at least 10 seconds is required")
			return redirect (request.url)

		mid_segment = wave_data[first_quarter:last_quarter]
		num_frame = (len(mid_segment) - frame_length_i) // frame_step_i


		mfccs_mat = np.zeros ((num_frame, int (frame_length / mfcc_frame_length * num_mfcc_coef_kept)))
		for i in range (num_frame):
			start_pos = i * frame_step_i
			end_pos = start_pos + frame_length_i
			mfccs = get_mfccs (mid_segment[start_pos:end_pos], sample_rate=11025, frame_length=mfcc_frame_length,
				frame_step=mfcc_frame_length, num_coef_kept=num_mfcc_coef_kept)
			mfccs_mat[i] = mfccs.flatten()

		# feed the data into regressors
		pace_regressor_result = pace_regressor.predict (mfccs_mat)
		arousal_regressor_result = arousal_regressor.predict (mfccs_mat) + 1.5
		valence_regressor_result = valence_regressor.predict (mfccs_mat) + 1.5

		# shrink overrated scores
		pace_regressor_result[np.where (pace_regressor_result>2.0)[0]] = 2.0
		pace_regressor_result[np.where (pace_regressor_result<0.0)[0]] = 0.0
		arousal_regressor_result[np.where(arousal_regressor_result>3.0)[0]] = 3.0
		arousal_regressor_result[np.where(arousal_regressor_result<0.0)[0]] = 0.0
		valence_regressor_result[np.where(valence_regressor_result>3.0)[0]] = 3.0
		valence_regressor_result[np.where(valence_regressor_result<0.0)[0]] = 0.0

		# calculate mean results
		pace_score = np.mean (pace_regressor_result)
		arousal_score = np.mean (arousal_regressor_result)
		valence_score = np.mean (valence_regressor_result)

		# calculate result ratios
		pace_fast_ratio = len (np.where (pace_regressor_result>1.33)[0]) / float (len (pace_regressor_result))
		pace_slow_ratio = len (np.where (pace_regressor_result<0.66)[0]) / float (len (pace_regressor_result))
		pace_mid_ratio = 1. - pace_fast_ratio - pace_slow_ratio

		arousal_intense_ratio = len (np.where (arousal_regressor_result>2.0)[0]) / float (len (arousal_regressor_result))
		arousal_relaxing_ratio = len (np.where (arousal_regressor_result<1.0)[0]) / float (len (arousal_regressor_result))
		arousal_mid_ratio = 1. - arousal_intense_ratio - arousal_relaxing_ratio

		valence_happy_ratio = len (np.where (valence_regressor_result>2.0)[0]) / float (len (valence_regressor_result))
		valence_sad_ratio = len (np.where (valence_regressor_result<1.0)[0]) / float (len (valence_regressor_result))
		valence_neutral_ratio = 1. - valence_happy_ratio - valence_sad_ratio

		# now classify the music genre
		mfccs_mid_segment = get_mfccs (mid_segment, sample_rate=11025, frame_length=20, frame_step=20, n_filters=20, num_coef_kept=15)
		mfccs_mean = np.mean (mfccs_mid_segment, axis=0)
		triu_indices = np.triu_indices (len (mfccs_mean))
		cov_mat = np.cov (mfccs_mid_segment.T)
		mfccs_cov_mat_upper_flatten = cov_mat[triu_indices]
		data_mid_segment = np.concatenate ((mfccs_mean, mfccs_cov_mat_upper_flatten))

		genre_probs = genre_classifier.predict_proba ([data_mid_segment])[0]
		sorted_indices = np.argsort (genre_probs)[::-1]
		best_cand = nn_code_to_genre_map[sorted_indices[0]]
		sec_best_cand = nn_code_to_genre_map[sorted_indices[1]]

		# generate wave form plot
		num_indices = 5000
		plot_indices = np.asarray (np.linspace (0, len(wave_data) - 1, num_indices), dtype=np.int32)
		plt.figure (figsize=(8,2), dpi=80)
		plt.title ("Waveform of " + file.filename)
		plt.axis ("off")
		plt.plot (wave_data[plot_indices])
		global imgIO
		if imgIO is not None:
			imgIO.close ()
		imgIO = StringIO.StringIO()
		plt.savefig (imgIO)
		imgIO.seek (0)

		return render_template ("index.html",
			file_uploaded = True,
			upload_filename = file.filename,
			tempo_value = pace_score / 2.0 * 100.0,
			arousal_value = arousal_score / 3.0 * 100.0,
			valence_value = valence_score / 3.0 * 100.0,
			pace_fast_ratio = 100. * pace_fast_ratio,
			pace_mid_ratio = 100. * pace_mid_ratio,
			pace_slow_ratio = 100. * pace_slow_ratio,
			arousal_intense_ratio = 100. * arousal_intense_ratio,
			arousal_mid_ratio = 100. * arousal_mid_ratio,
			arousal_relaxing_ratio = 100. * arousal_relaxing_ratio,
			valence_happy_ratio = 100. * valence_happy_ratio,
			valence_neutral_ratio = 100. * valence_neutral_ratio,
			valence_sad_ratio = 100. * valence_sad_ratio,
			best_cand = best_cand,
			sec_best_cand = sec_best_cand)



	return render_template ("index.html", 
		file_uploaded = False,
		upload_filename = "Filename",
		tempo_value = 0,
		arousal_value = 0,
		valence_value = 0,
		pace_fast_ratio = 0,
		pace_mid_ratio = 0,
		pace_slow_ratio = 0,
		arousal_intense_ratio = 0,
		arousal_mid_ratio = 0,
		arousal_relaxing_ratio = 0,
		valence_happy_ratio = 0,
		valence_neutral_ratio = 0,
		valence_sad_ratio = 0,
		best_cand = "Not Determined",
		sec_best_cand = "Not Determined")

@app.route ("/waveform_image")
def get_waveform_img ():
	global imgIO
	if imgIO is None:
		return None
	else:
		return send_file (imgIO,
			mimetype="Image/png",
			attachment_filename="waveform.png",
			as_attachment=True)


if __name__ == "__main__":
	app.run (debug=True)