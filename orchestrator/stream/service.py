import base64
import uuid
import cv2
import numpy as np
from typing import Any, Optional
import time
import httpx
import io
from PIL import Image
import wave
from .utils import answer_user_query, generate_tts, add_voice_user, add_face_user, greet_user, update_face_user
from .types import GenerateRequest, VoiceRecognitionResponse, FaceRecognitionResponse
from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from io import BytesIO

import websockets
import asyncio
import json
import os
from asyncio import Lock
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessRequest:
    def __init__(self):
        # self.transcription = ""
        self.queries: list[VoiceRecognitionResponse] = []
        self.voice_user = []
        self.face_user = []
        # self.user_id = None
        self.image = None
        self.audio = None
        self.face_rec_ws = None
        self.latest_face_rec_state: Optional[FaceRecognitionResponse] = None
        self.face_rec_config = {
            "action": "configure",
            "threshold": 0.5,
            "max_faces": 5
        }
        face_host = os.getenv("FACE_RECOGNITION_HOST")
        face_port = os.getenv("FACE_RECOGNITION_PORT")
        voice_host = os.getenv("VOICE_RECOGNITION_HOST","")
        voice_port = os.getenv("VOICE_RECOGNITION_PORT","")
        self.face_rec_url = f"ws://{face_host}:{face_port}/api/v2/identify"
        self.voice_rec_url = f"http://{voice_host}:{voice_port}/voice/process"
        self.ws_lock = Lock()
        self.isQueryNoise = False
    async def _ensure_face_rec_connection(self):
        """Ensures the WebSocket connection for face recognition is active."""
        if self.face_rec_ws and (await self.face_rec_ws.ping()):
            return True

        print("Face Rec WebSocket connection not active. Attempting to connect...")
        try:
            self.face_rec_ws = await websockets.connect(self.face_rec_url)
            print(f"Connected to Face Rec WebSocket at {self.face_rec_url}")
            await self.face_rec_ws.send(json.dumps(self.face_rec_config))
            await asyncio.sleep(0.1)  # Brief pause after configuration
            print(f"Face Rec WebSocket configured: {self.face_rec_config}")
            return True
        except (websockets.exceptions.WebSocketException, ConnectionRefusedError, OSError) as e:
            print(f"Failed to connect or configure Face Rec WebSocket: {e}")
            self.face_rec_ws = None
            self.latest_face_rec_state = None # Clear state on connection failure
            return False
        except Exception as e:
             print(f"An unexpected error occurred during WebSocket connection/configuration: {e}")
             self.face_rec_ws = None
             self.latest_face_rec_state = None
             return False
    def convert_to_wav(self,audio_data: bytes, channels: int = 1, sampwidth: int = 2, framerate: int = 48000) -> bytes:
        """
        Convert raw PCM audio data to a WAV file in memory.
        Assumes 16-bit PCM.
        """
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sampwidth)
            wav_file.setframerate(framerate)
            wav_file.writeframes(audio_array.tobytes())
        wav_buffer.seek(0)
        return wav_buffer.read()

    
    async def process_audio(self,audio_data):
        print("Processing audio data...")
        try:
            start = time.time()
            if len(audio_data) == 0:
                print("Empty audio data")
                return
            wav_data = self.convert_to_wav(audio_data)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.voice_rec_url,
                    files={"file": ("audio.wav", wav_data, "audio/wav")},
                    timeout=30.0
                )
                if response.status_code == 200:
                    res =  response.json()
                    
                    print("time taken to process voice: ", time.time() - start)
                    return [VoiceRecognitionResponse(**item) for item in res]

        except Exception as e:
            print("Error processing audio:", e)
            return None
        
    async def _process_video_frame_ws(self, img: np.ndarray):
        """Sends a video frame over WebSocket and updates the face rec state."""
        if not await self._ensure_face_rec_connection():
            print("Cannot process video frame, WebSocket connection failed.")
            return

        if self.face_rec_ws is None:
             print("Cannot process video frame, WebSocket is None.")
             return
        try:
            async with self.ws_lock:  # Enforce sequential access
                # Encode and send frame
                _, buffer = cv2.imencode('.jpg', img)
                if buffer is None:
                    print("Error: cv2.imencode failed.")
                    return
                
                # debug_image_path = f"debug_frame_{int(time.time())}.jpg"
                # cv2.imwrite(debug_image_path, img)
                # print(f"Saved debug image to {debug_image_path}")
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                
                message = json.dumps({
                    "image": image_base64,
                    "timestamp": time.time()
                })

                await self.face_rec_ws.send(message)
                
                # Wait for response (now protected by lock)
                response_str = await asyncio.wait_for(self.face_rec_ws.recv(), timeout=5.0)
                response_data = json.loads(response_str)
                if response_data.get("status") == "error":
                    logger.error(f"Face recognition error: {response_data.get('error')}")
                    return

                self.latest_face_rec_state = FaceRecognitionResponse(**response_data) 
                
        except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK) as e:
            print(f"Face Rec WebSocket connection closed during send/recv: {e}")
            self.face_rec_ws = None
            self.latest_face_rec_state = None
        except json.JSONDecodeError as e:
            print(f"Failed to decode Face Rec JSON response: {e} - Response: {response_str}")
        except asyncio.TimeoutError:
            print("Timeout waiting for face recognition response.")
        except Exception as e:
            print(f"Error during Face Rec WebSocket send/recv/process: {type(e).__name__}: {e}")
    
    async def process_input(self, audio_data):
        """
        Processes audio and video input, identifies user using latest face state.
        """
        voice_user_result = None
        if audio_data:
            voice_user_result = await self.process_audio(audio_data)
            if voice_user_result:
                self.queries = voice_user_result
            else:
                self.isQueryNoise = True
        
        if self.latest_face_rec_state is None:
            print("No face recognition state available")
            self.isQueryNoise = True
            return
        
        current_face_state = self.latest_face_rec_state.model_copy()

        if voice_user_result and current_face_state.matches:
            user_id = await self.identify_user(voice_user_result, current_face_state)
            print("User_ID:", user_id)
        else:
            print("process_input: No voice result or face state with matches available for identification.")



    async def identify_user(self, voice_users:list[VoiceRecognitionResponse], face_user:FaceRecognitionResponse) -> str:
        """
        Identify the user based on voice and face recognition results.
        """
        
        if not face_user:
            self.isQueryNoise = True
            return None
        
        voice_ids = set(voice_user.user_id for voice_user in voice_users if voice_user.user_id != None)
        null_voice_ids = len(set(voice_user.user_id for voice_user in voice_users if voice_user.user_id == None))
        is_multiple_speakers = len(voice_ids) > 1
        face_matches = face_user.matches
        processed_faces = len(face_matches)
        face_detected = face_user.face_detected

        known_face_matches = [m for m in face_matches if m.person_id != "Unknown" and m.confidence is not None]
        unknown_face_count = len([m for m in face_matches if m.person_id == "Unknown"])
        
        # Initialize queries
        self.queries = voice_users

        # No face detected: noise
        if not face_detected or processed_faces == 0:
            print("SCENARIO: NO FACE DETECTED")
            self.isQueryNoise = True
            self.queries = []
            return None

        # No voice detected: noise
        if not voice_users:
            print("SCENARIO: NO QUERY DETECTED")
            self.isQueryNoise = True
            self.queries = []
            return None
        
        if not is_multiple_speakers:
            # Get voice_id (None if unrecognized)
            voice_id = voice_ids.pop() if voice_ids else None

             # Scenario 1: One unrecognized voice
            if not voice_id and null_voice_ids == 1:
                print("SCENARIO 1: ONE UNRECOGNIZED VOICE")
                if processed_faces == 1:
                    face = face_matches[0]
                    if face.person_id == "Unknown":
                        print("SUB-SCENARIO 1.1: ONE UNKNOWN FACE DETECTED")
                        new_id = uuid.uuid4()
                        await add_voice_user(new_id, self.audio)
                        await add_face_user(new_id, self.image)
                        corrected_queries = [
                            VoiceRecognitionResponse(user_id=new_id, score=voice_user.score)
                            if voice_user.user_id is None else voice_user
                            for voice_user in voice_users
                        ]
                        self.queries = corrected_queries
                        return str(new_id)
                    else:
                        print("SUB-SCENARIO 1.2: ONE KNOWN FACE DETECTED")
                        user_id = uuid.UUID(face.person_id)
                        await add_voice_user(user_id, self.audio)
                        corrected_queries = [
                            VoiceRecognitionResponse(user_id=user_id, score=voice_user.score)
                            if voice_user.user_id is None else voice_user
                            for voice_user in voice_users
                        ]
                        self.queries = corrected_queries
                        return face.person_id
                else:
                    print("SUB-SCENARIO 1.3: MULTIPLE FACES DETECTED")
                    self.isQueryNoise = True
                    self.queries = []
                    # TODO: possibly infer speaker from face recognition
                    return None


            # Scenario 2: One recognized voice
            elif voice_id:
                print("SCENARIO 2: ONE RECOGNIZED VOICE")
                # Subscenario 2.1: One face match
                if processed_faces == 1:
                    print("SUB-SCENARIO 2.1: ONE FACE MATCH")
                    # Subscenario 2.1.1: Face not recognized
                    if unknown_face_count == 1 and not known_face_matches:
                        print("SUB-SCENARIO 2.1.1: FACE NOT RECOGNIZED")
                        await add_face_user(voice_id, self.image)
                        return str(voice_id)
                    # Subscenario 2.1.2: Face recognized
                    elif len(known_face_matches) == 1:
                        print("SUB-SCENARIO 2.1.2: FACE RECOGNIZED")
                        if known_face_matches[0].person_id == str(voice_id):
                            print("SUB-SCENARIO 2.1.2.1: FACE ID == VOICE ID")
                            self.queries = [v for v in voice_users if v.user_id == voice_id]
                            return str(voice_id)
                        else:
                            print("SUB-SCENARIO 2.1.2.2: FACE ID != VOICE ID")
                            await update_face_user(voice_id, self.image)
                            return str(voice_id)
                # Subscenario 2.2: Multiple face matches
                elif processed_faces > 1:
                    print("SUB-SCENARIO 2.2: MULTIPLE FACE MATCHES")
                    face_ids = [match.person_id for match in known_face_matches]
                    # Subscenario 2.2.1: All faces not recognized
                    if unknown_face_count == processed_faces and not known_face_matches:
                        print("SUB-SCENARIO 2.2.1: ALL FACES NOT RECOGNIZED")
                        await add_face_user(voice_id, self.image)
                        return str(voice_id)
                    # Subscenario 2.2.2: Mixed recognition on face
                    elif known_face_matches and unknown_face_count > 0:
                        print("SUB-SCENARIO 2.2.2: MIXED RECOGNITION ON FACE")
                        if str(voice_id) in face_ids:
                            print("SUB-SCENARIO 2.2.2.1: VOICE ID IN LIST OF FACE IDs")
                            self.queries = [v for v in voice_users if v.user_id == voice_id]
                            return str(voice_id)
                        else:
                            print("SUB-SCENARIO 2.2.2.2: VOICE ID NOT IN LIST OF FACE IDs")
                            await add_face_user(voice_id, self.image)
                            self.queries = [v for v in voice_users if v.user_id == voice_id]
                            return str(voice_id)
                    # Subscenario 2.2.3: All recognized faces
                    elif len(known_face_matches) == processed_faces and unknown_face_count == 0:
                        print("SUB-SCENARIO 2.2.3: ALL RECOGNIZED FACES")
                        if str(voice_id) in face_ids:
                            print("SUB-SCENARIO 2.2.3.1: VOICE ID IN LIST OF FACE IDs")
                            self.queries = [v for v in voice_users if v.user_id == voice_id]
                            return str(voice_id)
                        else:
                            print("SUB-SCENARIO 2.2.3.2: VOICE ID NOT IN LIST OF FACE IDs")
                            await update_face_user(voice_id, self.image)
                            return str(voice_id)
        else:
            print("SCENARIO: MULTIPLE VOICES DETECTED")
            # All faces recognized
            if unknown_face_count == 0 and len(known_face_matches) == processed_faces:
                print("SUB-SCENARIO: ALL FACES RECOGNIZED")
                face_ids = {match.person_id for match in known_face_matches}
                # Filter voice_users to those matching face_ids
                matching_voices = [v for v in voice_users if v.user_id is None or str(v.user_id) in face_ids]
                if len(matching_voices) == 1:
                    print("SUB-SCENARIO: ONE MATCHING VOICE")
                    return str(matching_voices[0].user_id)
                elif matching_voices:
                    print("SUB-SCENARIO: MULTIPLE MATCHING VOICES")
                    # Select highest-scoring voice
                    self.queries = matching_voices
                    return None
                else:
                    print("SUB-SCENARIO: NO MATCHING VOICES")
                    self.isQueryNoise = True
                    return None
            # Some or all faces unrecognized
            else:
                print("SUB-SCENARIO: NOT ALL FACES RECOGNIZED")
                # If exactly one recognized voice, use it
                self.queries = voice_users
                return None
        
        print("UNHANDLED SCENARIO.")
        self.isQueryNoise = True
        self.queries = []

    async def __call__(self, audio_payload):
        if not audio_payload:
            print("Missing audio payload; skipping this message.")
            return None
        
        audio_data = None
        
        if audio_payload:
            try:
                audio_data = base64.b64decode(audio_payload)
            except Exception as e:
                print("Error decoding audio payload:", e)
        


        # Convert audio bytes to UploadFile
        audio_upload_file = None
        if audio_data:
            audio_upload_file = UploadFile(
            filename="audio.wav",
            file=BytesIO(audio_data),
            )

        # Convert image bytes to UploadFile

        if audio_upload_file:
            self.audio = audio_upload_file

        # Pass the converted UploadFile objects to process_input
        await self.process_input(audio_data)
        
        if self.isQueryNoise:
            self.isQueryNoise = False
            return None
        
        if audio_payload and self.queries != []:
            print("send transcription to RAG")
            answer = await answer_user_query([GenerateRequest(user_id = str(x.userid) if x.userid else str(uuid.uuid4()), question = x.transcription) for x in self.queries])
            print("Answer from RAG: ", answer.generation)
            self.queries = []

            start_time_tts = time.time()
            response_tts = await generate_tts(answer.generation)
            end_time_tts = time.time()
            
            print(f'Total TTS TIme: ' , end_time_tts - start_time_tts)
            return response_tts
        else:
            print("No transcription available")
            return None
        
        
    async def process_video(self, img_payload, isProcessingAudio):

        if not img_payload:
            print("Missing video payload; skipping this message.")
            return None

        img = None

        try:
            video_bytes = base64.b64decode(img_payload)
            np_arr = np.frombuffer(video_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        except Exception as e:
            print("Error decoding video payload:", e)

        # Convert image bytes to UploadFile
        img_upload_file = None
        if img is not None:
            _, img_encoded = cv2.imencode('.jpg', img)
            img_bytes = img_encoded.tobytes()
            img_upload_file = UploadFile(
                filename="image.jpg",
                file=BytesIO(img_bytes),
            )

        if img_upload_file:
            self.image = img_upload_file

        # Pass the converted UploadFile objects to process_input
        await self._process_video_frame_ws(img)
        
        if self.latest_face_rec_state.new_faces and not isProcessingAudio:
            user_id = self.latest_face_rec_state.new_faces[0]
            
            # rag greeting
            response = await greet_user(user_id)

            # send to tts
            tts_response = await generate_tts(response.generation)

            return tts_response    
        
    async def close(self):
        """Closes the WebSocket connection."""
        print("Close requested. Shutting down WebSocket connection...")
        if self.face_rec_ws and (await self.face_rec_ws.ping()):
             try:
                  await self.face_rec_ws.send(json.dumps({"action": "close"}))
                  await self.face_rec_ws.close()
                  print("Face Rec WebSocket connection closed.")
             except Exception as e:
                  print(f"Error closing WebSocket: {e}")
             finally:
                  self.face_rec_ws = None
                  self.latest_face_rec_state = {}
        else:
             print("WebSocket connection already closed or never established.")