# DeepSent
## Project Description
This project will analyze the user-uploaded music files based on the arousal-valence emotion model (aka [Circumplex model](https://en.wikipedia.org/wiki/Emotion_classification)). Arousal represents how intense or "stimulating" the music is to the human ears, ranging from a plain and relaxing feeling to a strong and arousing feeling. Valence here describes how delightful or how sad the music sounds like. This definition is narrower than the one presented in [wikipedia](https://en.wikipedia.org/wiki/Valence_(psychology)), but is easier for the machine learning models to classify. Besides, the project also implemented the functionalities of pace detection and music genre detection.<br/>
Web Framework: [Flask](http://flask.pocoo.org/), [jQuery](https://jquery.com/)<br/>
Skills Involved: HTML, CSS, javascript, python<br/>

### Implmentation Details
Pace, arousal and valence detection: the middle 50% of the music's raw data is splitted into 5-second frames, with a step of 0.5 seconds. Each frame is then splitted into smaller 25ms subframes that are then transformed into an array of MFCCs (Mel-frequency cepstral coefficients). Finally, the MFCC array, which is initially in matrix form, is flattened and fed into a 3-layer neural network regressor. The intention here is trying to let the neural nets capture the patterns in the changes of the MFCCs and relates the patterns with the emotions that the music represents. (an instinctive approach, more researches are needed)<br/>

Genre detection: the middle 50% of the music's raw data is splitted into 20ms frames. From each of the frames, an vector of MFCC values is calculated. The mean vector and the upper part of the covariance matrix of the MFCC vectors are then taken and concatenated together into a single array, which is finally fed into a 6-layer neural network that outputs the numerical label for the predicted genre.<br/>

Datasets: GTZAN Music Genre Dataset + music files collected from my own favorite playlists for added genres (East Asia Classical, Electronic, New Age and Soundtracks)   

## Getting Started
The project is hosted on the site: <del>mchen241.pythonanywhere.com</del> (Expired)<br/>
Or you can download the repository and run app_main.py (For requirements that need to be installed, see "Prerequisites" below):
```
python app_main.py
```
The project will be running on localhost:5000/

## Prerequisites
```
python>=2.7.12
scikit-learn>=0.18rc2
scipy>=0.17.0
numpy>=0.11.0
flask>=0.12.2
pydub (with libav or ffmpeg)
```

## Author
Mu Chen [muchen2](https://github.com/muchen2)

## References
1. Music Genre Classification, cs229.stanford.edu/proj2011/HaggbladeHongKao-MusicGenreClassification.pdf
2. http://practicalcryptography.com/miscellaneous/machine-learning/guide-mel-frequency-cepstral-coefficients-mfccs/
3. http://www.ee.columbia.edu/ln/rosa/doc/HTKBook21/node54.html
4. Wikipedia, https://www.wikipedia.org/
