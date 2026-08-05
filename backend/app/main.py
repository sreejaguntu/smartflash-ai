from fastapi import FastAPI, UploadFile, File
from app.services.upload_service import UploadService

app=FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to SmartFlash AI!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    result = await UploadService.save_file(file)
    return {
        "message": "File uploaded successfully!", 
        "result": result
        }

# @app.post("/flashcards")
# def generate_flashcard(request: FlashcardRequest):
#     return {
#         "message": "Flashcard created successfully!",
#         "goal": request.goal,
#         "difficulty": request.difficulty,
#         "style": request.style}