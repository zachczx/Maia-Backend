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
CHANNELS = 1  # Number of channels
RATE = 44100  # Sample rate (samples per second)
CHUNKS_PER_SECOND = RATE // CHUNK  # Number of chunks per second
SECONDS = 2  # Duration in seconds
CHUNKS_FOR_DURATION = int(CHUNKS_PER_SECOND * SECONDS)  # Number of chunks for the desired duration
ENERGY_THRESHOLD = 50  # Energy threshold for detecting silence

# Initialize PyAudio
p = pyaudio.PyAudio()

# List available audio devices
def list_devices():
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    devices = []
    for i in range(num_devices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            devices.append((i, p.get_device_info_by_host_api_device_index(0, i).get('name')))
    return devices

devices = list_devices()
print("Available audio devices:")
for i, device in devices:
    print(f"{i}: {device}")

caller_device_index = int(input("Enter the device index for the caller (AirPods): "))
staff_device_index = int(input("Enter the device index for the staff (USB-C earphone): "))

caller_stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       input_device_index=caller_device_index,
                       frames_per_buffer=CHUNK)

staff_stream = p.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      input=True,
                      input_device_index=staff_device_index,
                      frames_per_buffer=CHUNK)

print("Recording...")

caller_buffer = deque()
staff_buffer = deque()

current_speaker = None

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

def process_audio_chunk(role, audio_buffer):
    with threading.Lock():
        combined_audio = b''.join(audio_buffer)
    
    if not is_meaningful_audio(combined_audio):
        print(f"Detected silence or low-energy frames in {role} audio, skipping transcription.")
        return
    
    timestamp = int(time.time())
    wav_filename = f'{role}_audio_{timestamp}.wav'
    
    with wave.open(wav_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(combined_audio)
    
    transcript_text = send_to_whisper(wav_filename)
    print(f"{role.capitalize()} Whisper response: {transcript_text}")

    transcript_queue.append((role, transcript_text))

try:
    while True:
        caller_frames = []
        staff_frames = []

        for _ in range(CHUNKS_FOR_DURATION):
            caller_data = caller_stream.read(CHUNK)
            staff_data = staff_stream.read(CHUNK)
            if current_speaker == "caller":
                caller_buffer.clear()
            elif current_speaker == "staff":
                staff_buffer.clear()
            caller_frames.append(caller_data)
            staff_frames.append(staff_data)
        
        with threading.Lock():
            caller_buffer.extend(caller_frames)
            staff_buffer.extend(staff_frames)
        
        threading.Thread(target=process_audio_chunk, args=("caller", caller_buffer.copy())).start()
        threading.Thread(target=process_audio_chunk, args=("staff", staff_buffer.copy())).start()

except KeyboardInterrupt:
    print("Recording stopped")

# Close the streams
caller_stream.stop_stream()
caller_stream.close()
staff_stream.stop_stream()
staff_stream.close()
p.terminate()

# Print the transcripts after the call has ended
print("Transcripts:")
for role, transcript in transcript_queue:
    print(f"{role.capitalize()} transcript: {transcript}")
