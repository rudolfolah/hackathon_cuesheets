# Based on https://towardsdatascience.com/machine-learning-on-sound-and-audio-data-3ae03bcf5095
# Based on https://towardsdatascience.com/how-to-apply-machine-learning-and-deep-learning-methods-to-audio-analysis-615e286fcbbc
import librosa
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import layers, models
from tensorflow.keras.utils import to_categorical


def cut_song(audio_time_series):
    start = 0
    end = len(audio_time_series)
    song_pieces = []
    slice_size = 100000
    while start + slice_size < end:
        song_pieces.append(audio_time_series[start:start + slice_size])
        start += slice_size
    return song_pieces


def prepare_song(song_path):
    list_matrices = []
    audio_time_series, sampling_rate = librosa.load(song_path)
    song_pieces = cut_song(audio_time_series)
    for song_piece in song_pieces:
        melspectrogram = librosa.feature.melspectrogram(song_piece)
        list_matrices.append(melspectrogram)
    return list_matrices

# Construct the data set
songs = (
    ("Song 00001", "dataset/drake.ogg"),
    ("Song 00002", "dataset/planets.ogg"),
    ("Song 00003", "dataset/teeth.ogg"),
)
melspectrograms = []
name_labels = []
for (name_label, path) in songs:
    song_pieces = prepare_song(path)
    melspectrograms += song_pieces
    name_labels += ([name_label] * len(song_pieces))

X = np.array(melspectrograms)
y = np.array(name_labels)
label_encoder = LabelEncoder()
yy = to_categorical(label_encoder.fit_transform(y))

# Construct the training and test data sets
X_train, X_test, y_train, y_test = train_test_split(X, yy, test_size=0.33, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_test, y_test, test_size=0.5, random_state=42)

# Construct the machine learning model
model = models.Sequential()
model.add(layers.Conv2D(32, (3, 3), activation="relu", input_shape=(128, 196, 1)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(128, (3, 3), activation="relu"))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation="relu"))

model.add(layers.Flatten())
model.add(layers.Dense(64, activation="relu"))
model.add(layers.Dense(1))

model.summary()

# Fit the model for song recognition
model.compile(loss="binary_crossentropy", optimizer='adam', metrics="accuracy")
history = model.fit(X_train, y_train, epochs=15, validation_data=(X_val, y_val))

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test,  y_test, verbose=2)
plt.plot(history.history["accuracy"], label="accuracy")
plt.plot(history.history["val_accuracy"], label="val_accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.ylim([0.5, 1])
plt.legend(loc="lower right")
plt.show()
