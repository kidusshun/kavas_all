from fastapi import APIRouter,File,UploadFile, Response
import uuid
from .service import identify_voice, answer_user_query, generate_tts, identify_face, add_voice_user, add_face_user
from .types import GenerateRequest
user_router = APIRouter(prefix="/user", tags=["User"])

@user_router.post("/process_request")
async def process_user(
    audio: UploadFile = File(...),
    image: UploadFile = File(...),
):
    try:
        # audio = await extract_audio(audio)
        # identify voice
        print("CALLING VOICE IDENTIFICATION")  
        voice_user = await identify_voice(voice_file=audio)
        print("IDENTIFIED VOICE")  

        # call face recognition service
        face_user = await identify_face(image)
        # compare the two results

        print("COMPARING VOICE AND FACE IDENTIFICATION")
        print("VOICE USER: ", voice_user)
        print("FACE USER: ", face_user)
        if face_user.userid == 'Unknown' and not voice_user.userid:
            print("USER VOICE AND FACE NOT IDENTIFIED")
            uu = uuid.uuid4()
            await add_voice_user(uu, audio)
            await add_face_user(uu, image)
            request = GenerateRequest(user_id=str(uu), question=voice_user.transcription)
        elif face_user.userid == 'Unknown':
            print("FACE NOT IDENTIFIED")
            await add_face_user(voice_user.userid, image)
            request = GenerateRequest(user_id=voice_user.userid, question=voice_user.transcription)
        elif not voice_user.userid:
            print("VOICE NOT IDENTIFIED")
            await add_voice_user(uuid.UUID(face_user.userid), audio)
            request = GenerateRequest(user_id=face_user.userid, question=voice_user.transcription)
        elif face_user.userid == str(voice_user.userid):
            print("USER IDENTIFIED")
            request = GenerateRequest(user_id=face_user.userid, question=voice_user.transcription)
        else:
            if face_user.score < voice_user.score:
                print("FACE USER IDENTIFIED")
                await add_voice_user(uuid.UUID(face_user.userid), audio)
                request = GenerateRequest(user_id=face_user.userid, question=voice_user.transcription)
            else:
                print("VOICE USER IDENTIFIED")
                await add_face_user(voice_user.userid, image) #type: ignore
                request = GenerateRequest(user_id=str(voice_user.userid), question=voice_user.transcription)
        

        # call rag service
        print("ANSWERING USER QUESTION")  
        response = await answer_user_query(request=request)
        print("USER QUESTION ANSWERED")  

        # generate tts
        speech = await generate_tts(response.generation)
        return Response(
            content=speech.content,
            media_type="audio/wav",
        )
    except Exception as e:
        raise e
    
