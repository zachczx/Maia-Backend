import pyaudio
import numpy as np
import wave
import time
import os
import threading
from collections import deque
from pydub import AudioSegment, silence
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Parameters
CHUNK = 1024  # Number of samples per frame
FORMAT = pyaudio.paInt16  # Format of audio stream
CHANNELS = 1  # Number of channels (mono)
RATE = 44100  # Sample rate (samples per second)
CHUNKS_PER_SECOND = RATE // CHUNK  # Number of chunks per second
SECONDS = 1  # Duration in seconds
CHUNKS_FOR_DURATION = int(CHUNKS_PER_SECOND * SECONDS)  # Number of chunks for the desired duration
ENERGY_THRESHOLD = 50  # Energy threshold for detecting silence

# Initialize PyAudio
p = pyaudio.PyAudio()

# Get default input device info
default_device_info = p.get_default_input_device_info()
print(f"Using default input device: {default_device_info['name']}")

stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       input_device_index=default_device_info['index'],
                       frames_per_buffer=CHUNK)

print("Recording...")

buffer = deque()

transcript_queue = deque()

def send_to_whisper(wav_filename):
    with open(wav_filename, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            temperature=0,
            prompt="This audio chunk is part of a conversation between a call center staff and a customer. Do not attempt to complete any cut-off words; transcribe only what is clearly audible.",
            language="en",
            response_format="text"
        )
        return transcript

def is_meaningful_audio(audio_data):
    audio_segment = AudioSegment(
        data=audio_data,
        sample_width=p.get_sample_size(FORMAT),
        frame_rate=RATE,
        channels=CHANNELS
    )
    
    # Detect silence
    silent_ranges = silence.detect_silence(audio_segment, min_silence_len=1000, silence_thresh=-40)
    if len(silent_ranges) == 1 and silent_ranges[0][0] == 0 and silent_ranges[0][1] == len(audio_segment):
        return False

    # Calculate energy of the audio
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    energy = np.sum(audio_array**2) / len(audio_array)
    if energy < ENERGY_THRESHOLD:
        return False

    return True

def process_audio_chunk(audio_buffer):
    with threading.Lock():
        combined_audio = b''.join(audio_buffer)
    
    if not is_meaningful_audio(combined_audio):
        print("Detected silence or low-energy frames, skipping transcription.")
        return
    
    timestamp = int(time.time())
    wav_filename = f'audio_{timestamp}.wav'
    
    with wave.open(wav_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(combined_audio)
    
    transcript_text = send_to_whisper(wav_filename)
    print(f"Whisper response: {transcript_text}")

    # Append transcript to queue
    transcript_queue.append(transcript_text)
    
    # Delete the WAV file after getting the response
    os.remove(wav_filename)
    print(f"Deleted {wav_filename}")

try:
    while True:
        frames = []

        for _ in range(CHUNKS_FOR_DURATION):
            data = stream.read(CHUNK)
            frames.append(data)
        
        with threading.Lock():
            buffer.extend(frames)
        
        threading.Thread(target=process_audio_chunk, args=(buffer.copy(),)).start()

except KeyboardInterrupt:
    print("Recording stopped")

# Close the stream
stream.stop_stream()
stream.close()
p.terminate()

# Print the transcripts after the call has ended
print("Transcripts:")
for transcript in transcript_queue:
    print(f"Transcript: {transcript}")


# from pyannote.audio import Pipeline
# from dotenv import load_dotenv
# import os

# load_dotenv()
# PYANNOTE_TOKEN = os.getenv("PYANNOTE_TOKEN")
# print(PYANNOTE_TOKEN)

# print("11111")

# pipeline = Pipeline.from_pretrained(
#     "pyannote/speaker-diarization-3.0",
#     use_auth_token="PYANNOTE_TOKEN")

# print(pipeline)
# # apply pretrained pipeline
# audio_file = "c:\\Users\\ASUS\\Documents\\School\\Internship\\MINDEF\\_1_6914518371596867979_1_62.wav"
# diarization = pipeline(audio_file)
# print(diarization)
# # print the result
# for turn, _, speaker in diarization.itertracks(yield_label=True):
#     print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")

# 1. visit hf.co/pyannote/segmentation and accept user conditions
# 2. visit hf.co/settings/tokens to create an access token
# 3. instantiate pretrained speaker segmentation pipeline
