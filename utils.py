import numpy as np 
from scipy.fftpack import fft
from scipy.fftpack import dct
from pydub import AudioSegment

"""
Static util functions that will be used in the app
"""

"""
Compress user input's audio segment by
	1. reducing the number of channels, if possible
	2. reducing the sample rate, if possible
"""
def compress_audio_segment (segment):

	# limit the number of channels to be one
	if segment.channels > 1:
		segment_out = segment.set_channels (1)

	# limit the segment's frame rate to be 11025
	if segment.frame_rate > 11025:
		segment_out = segment_out.set_frame_rate (11025)

	return segment_out

"""
Generate hamming window function with specific length
for FFT's usage
"""
def gen_hamming_window (length):
	alpha = 0.54
	beta = 1 - alpha
	return -beta * np.cos (np.arange (length) * 2 * np.pi / (length - 1)) + alpha

"""
Convert frequency (in hertz) to Mel scale
"""
def toMel (freq):
	return 1125 * np.log (1 + freq / 700.0)

"""
Convert Mel-scale frequency to Hertz frequency
"""
def toHertz (mel):
	return 700 * (np.exp(mel/1125) - 1)

"""
Generate Mel filterbank that convert the linear frequency
resolution obtained in the result of FFT into nonlinear 
frequency resolution
Filterbank analysis is a process that simulates how human
ears actually perceive sounds 
(http://www.ee.columbia.edu/ln/rosa/doc/HTKBook21/node54.html)
lower and upper are the lower and upper frequencies in hertz
n: number of filter bank we want to generate
"""
def gen_mel_filters (nfft, sample_rate, n = 26, lower = 300, upper = 8000):
	lower_mel = toMel (lower)
	upper_mel = toMel (upper)
	mel_linspace = np.linspace (lower_mel, upper_mel, n + 2)
	hertz_linspace = toHertz (mel_linspace)

	# round the frequencies to nearest FFT bin to match
	# the frequency resolution
	fft_linspace = np.asarray (np.floor (nfft * hertz_linspace / sample_rate), dtype=np.int32)
	filters = []
	for i in range (n):
		filter = np.zeros (nfft)
		filter[fft_linspace[i]:fft_linspace[i+1] + 1] = np.linspace (0.0, 1.0, fft_linspace[i+1] - fft_linspace[i] + 1)
		filter[fft_linspace[i+1] + 1:fft_linspace[i+2] + 1] = np.linspace (1.0, 0.0, fft_linspace[i+2] - fft_linspace[i+1] + 1)[1:]
		filters.append (filter)

	return filters

"""
Extract MFC coefficients from the given signal data x
Implementation steps:
	1. Take DFT of windowed signal
	2. Calculate the Mel-scaled filterbank energy from the power spectrum obtained in step 1
	3. Take the log of each of the filterbank energy
	4. Take the DCT of the log filterbank energy to obtain the cepstrum coefficients
	(http://practicalcryptography.com/miscellaneous/machine-learning/guide-mel-frequency-cepstral-coefficients-mfccs/) 
frame_length and frame_step are in milliseconds
num_coef_kept: number of cepstral coefficients that will be kept in the final step of calculation
nfft: number of fft points
n_filters: number of mel filterbanks that will be used
frame_limit: if greater than zero, only this amount of frames will be processed in x
lower and upper are used as the same lower and upper in gen_mel_filter function declared above
"""
def get_mfccs (x, sample_rate, frame_length = 25, frame_step = 10, num_coef_kept = 13, n_filters = 26, frame_limit = 0, lower = 300, upper = 8000):

	# convert time length of frame length and frame step into
	# array length
	fsize = int (frame_length / 1000.0 * sample_rate)
	fstep = int (frame_step / 1000.0 * sample_rate)

	if frame_limit > 0:
		num_frame = frame_limit
	else:
		# frame limit is not set, process the whole data
		num_frame = (len(x) - fsize) // fstep + 1
	mfccs = np.zeros ((num_frame, num_coef_kept))

	# construct hamming window and mel filterbank beforehand
	hamming_win = gen_hamming_window (fsize)
	mel_filters = gen_mel_filters (fsize, sample_rate, n = n_filters, lower = lower, upper = upper)

	# iterate through each frame and extract its mfcc
	for i in range (num_frame):

		# padding zeros at the end if the last frame goes out of bound
		if i * fstep + fsize > len(x):
			frame = np.zeros (fsize)
			rest_len = len(x) - i * fstep
			frame[:rest_len] = x[i*fstep:]
		else:
			frame = x[i * fstep:i * fstep + fsize]

		# calculate windowed DFT
		f_spectrum = fft (x = hamming_win * frame)

		# convert the complex numbers in the spectrum into their squared magnitudes (power)
		p_spectrum = np.absolute (f_spectrum) ** 2

		# filter the spectrum using mel filterbanks
		mel_energies = np.zeros (len(mel_filters))
		for j in range(len(mel_filters)):
			mel_energies[j] = np.dot (p_spectrum, mel_filters[j])

		# log the energies
		log_mel_energies = np.log (mel_energies + 1e-5)

		# compute DCT of the log energies
		mfcc = dct (log_mel_energies)
		mfccs[i, :] = mfcc[:num_coef_kept]


	return mfccs








