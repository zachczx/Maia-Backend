from collections import deque
from channels.generic.websocket import AsyncWebsocketConsumer
from core.utils.openai_utils import get_transcription
from .services.openai_service import do_speaker_diarization
from response_generator.services.chat_service import chat
from dotenv import load_dotenv
from pydub import AudioSegment, silence
import numpy as np
from openai import OpenAI
import os
import json
import wave
import logging
import asyncio
import uuid

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

logger = logging.getLogger('django')

# Parameters for audio processing
ENERGY_THRESHOLD = 50
SAMPLE_WIDTH = 2
CHANNELS = 1
RATE = 16000

class Transcript:
    def __init__(self):
        self.transcript_dict = []

    def change_transcript(self, transcript_with_speakers):
        self.transcript_dict = []
        speaker = "caller"
        speaker_list = transcript_with_speakers.split("|")
        
        for speaker_content in speaker_list:
            if speaker == "agent":
                speaker = "caller"
            else:
                speaker = "agent"

            self.transcript_dict.append({"role": speaker, "content": speaker_content})

    def add_suggestion(self, suggestion):
        self.transcript_dict.append({"role": "suggestion", "content": suggestion})

    def get_transcript(self):
        return self.transcript_dict

class AudioConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_chunks = deque()
        self.transcript = Transcript()
        self.processing = False

    async def connect(self):
        await self.accept()
        logger.info("WebSocket connection established.")
        asyncio.create_task(self.process_audio_chunks())

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with close code: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            self.audio_chunks.append(bytes_data)
            
        # if text_data:
        #     try:
        #         data = json.loads(text_data)
        #         logger.info(text_data)
        #         if data.get("type") == "suggestion_request":
        #             suggestion = chat(data["transcript"], True)
        #             self.transcript.add_suggestion(suggestion)
        #             await self.send_transcript(self.transcript.get_transcript())
        #     except json.JSONDecodeError as e:
        #         logger.error(f"JSON decode error: {e}")
        #     except Exception as e:
        #         logger.error(f"Error handling text data: {e}")

    async def process_audio_chunks(self):
        while True:
            await asyncio.sleep(1)  # Wait for 1 second
            if self.audio_chunks and not self.processing:
                self.processing = True
                combined_audio = b''.join(self.audio_chunks)
                
                if len(combined_audio) >= RATE * SAMPLE_WIDTH * CHANNELS * 0.1:
                    if self.is_meaningful_audio(combined_audio):
                        transcript = await self.process_audio_chunk(combined_audio)
                        self.transcript.change_transcript(transcript)
                        logger.info(self.transcript.get_transcript())
                        await self.send_transcript(self.transcript.get_transcript())

                else:
                    logger.warning("Audio chunk too short to process.")

                self.processing = False

    def is_meaningful_audio(self, audio_data):
        audio_segment = AudioSegment(
            data=audio_data,
            sample_width=SAMPLE_WIDTH,
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

    async def process_audio_chunk(self, audio_data):
        wav_filename = f'temp_audio_{uuid.uuid4()}.wav'
        
        with wave.open(wav_filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(SAMPLE_WIDTH)
            wf.setframerate(RATE)
            wf.writeframes(audio_data)

        transcription = get_transcription(wav_filename)
        transcription_with_speakers = do_speaker_diarization(transcription)

        attempts = 0
        while attempts < 3:
            try:
                os.remove(wav_filename)
                break 
            except PermissionError:
                attempts += 1
                logger.error(f"Error removing file, attempt {attempts}: {wav_filename} is in use. Retrying...")
                await asyncio.sleep(1)

        return transcription_with_speakers


    async def send_transcript(self, transcription):
        try:
            await self.send(text_data=json.dumps({
                'type': 'transcript',
                'message': transcription
            }))
        except Exception as e:
            logger.error(f"Error sending transcription: {e}")
            await self.close()
