import whisper

# model = whisper.load_model("turbo")
model = whisper.load_model("tiny.en")
result = model.transcribe("test.mp3")
print(result["text"])