import pyaudio
import struct

audio = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

data = list()
bytecount = 1024
for i in range(bytecount):
	data.append(440)
frames = struct.pack(f'{bytecount}h', *data)

stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True)
stream.write(data)
stream.stop_stream()
stream.close()

