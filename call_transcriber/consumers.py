from channels.generic.websocket import AsyncWebsocketConsumer
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from dotenv import load_dotenv
from response_generator.services.chat_service import chat
import os
import wave
import asyncio
import json
import logging

logger = logging.getLogger('django')
load_dotenv()

class Transcript:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transcript_dict = []
        self.current_speaker = '0' #assume first to speak is call center agent

    def toggle_speaker(self):
        self.current_speaker = '1' if self.current_speaker == '0' else '0'

    def add_transcript(self, content, type):
        speaker = 'agent' if self.current_speaker == '0' else 'caller'

        if len(self.transcript_dict) != 0:
            last_entry = self.transcript_dict[-1]
            if last_entry["role"] == speaker:
                if type == "pronunciation":
                    last_entry["content"] += " " + content
                elif type == "punctuation":
                    last_entry["content"] += content
                return

        entry = {
            "role": speaker,
            "content": content
        }
        self.transcript_dict.append(entry)
        return 

    def add_suggestion(self, suggestion):
        logger.info("in here")
        entry = {
            "role": "suggestion",
            "content": suggestion
        }
        self.transcript_dict.append(entry)
        logger.info(self.transcript_dict)

    def get_transcript(self):
        return self.transcript_dict

class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, output_stream, send_func, transcript):
        super().__init__(output_stream)
        self.send_func = send_func
        self.transcript = transcript

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        results = transcript_event.transcript.results
        for result in results:
            if result.is_partial:
                break
            for alt in result.alternatives:
                for item in alt.items:
                    type = item.item_type
                    
                    if item.item_type == "speaker-change":
                        self.transcript.toggle_speaker()
                        continue
                    
                    if item.speaker != self.transcript.current_speaker and item.speaker != None:
                        self.transcript.toggle_speaker()
                    
                    content = item.content
                    self.transcript.add_transcript(content, type)

                await self.send_func(self.transcript.get_transcript())

class AudioConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_chunks = []
        self.transcript = Transcript()
        self.connected = True
        
    async def send_transcript(self, transcript):
        if self.connected:
            try:
                await self.send(text_data=json.dumps({
                    'type': 'transcript',
                    'message': transcript
                }))
            except Exception as e:
                self.connected = False
                await self.close()
        else:
            logger.error("Unable to send information as web socket is closed")

    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'You are now connected!'
        }))
        logger.info("WebSocket connection established")
        
        self.client = TranscribeStreamingClient(region="ap-southeast-1")
        self.stream = await self.client.start_stream_transcription(
            language_code="en-US",
            media_sample_rate_hz=16000,
            media_encoding="pcm",
            show_speaker_label=True,
        )
        
        

        self.handler = MyEventHandler(self.stream.output_stream, self.send_transcript, self.transcript)
        self.handler_task = asyncio.create_task(self.handler.handle_events())

        logger.info("Transcription stream started")

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with close code: {close_code}")
        
        if self.audio_chunks:
            audio_filename = 'recorded_audio.wav' 
            audio_path = os.path.join('./', audio_filename)
            with wave.open(audio_path, 'wb') as audio_file:
                audio_file.setnchannels(1)
                audio_file.setsampwidth(2)
                audio_file.setframerate(16000)
                for chunk in self.audio_chunks:
                    audio_file.writeframes(chunk)

            logger.info(f"Audio file saved at: {audio_path} ----------------")

        if self.stream:
            await self.stream.input_stream.end_stream()
            logger.info("Transcription stream ended")

        if self.handler_task:
            await self.handler_task
            logger.info("Event handler task finished")

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            try:
                logger.info("111111")
                data = json.loads(text_data)
                logger.info(text_data)
                if data.get("type") == "suggestion_request":
                    logger.info("3333333")
                    suggestion = chat(data["transcript"], True)
                    logger.info(suggestion)
                    self.transcript.add_suggestion(suggestion)
                    logger.info(self.transcript.get_transcript())
                    logger.info("-------------")
                    await self.send_transcript(self.transcript.get_transcript())
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
            except Exception as e:
                logger.error(f"Error handling text data: {e}")

        if bytes_data is not None:
            try:
                if self.stream:
                    await self.stream.input_stream.send_audio_event(audio_chunk=bytes_data)
                    self.audio_chunks.append(bytes_data)
                else:
                    logger.warning("Transcription stream not initialized")
            except Exception as e:
                logger.error(f"Error sending audio chunk: {e}")
