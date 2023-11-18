import speech_recognition as sr
from openai import OpenAI
import pygame

api_key = "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"
client = OpenAI(api_key=api_key)

recognizer = sr.Recognizer()

def capture_voice_input():
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            return audio
        except sr.WaitTimeoutError:
            print("Timeout. No speech detected.")
            return None

def convert_voice_to_text(audio):
    try:
        text = recognizer.recognize_google(audio)
        print("You said: " + text)
        return text
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def wakeword(text):
    if "eliza" in text.lower():
        print("Hello! How can I help you?")
        return True
    return False

def call_gpt_api(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
                {
                    "role": "assistant",
                    "content": "Come posso aiutarti?",
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling GPT-4 API: {e}")
        return "Sorry, an error occurred."
    
def TTS(plaintext):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=plaintext,
    )

    response.stream_to_file("temp\output.mp3")
    
def play_audio_file(file_path):
       pygame.mixer.init()
       pygame.mixer.music.load(file_path)
       pygame.mixer.music.play()
       while pygame.mixer.music.get_busy():  # Wait for audio to finish playing
           pygame.time.Clock().tick(10)

def main():
    end_program = False
    while not end_program:
        audio = capture_voice_input()

        if audio:
            text = convert_voice_to_text(audio)

            if text:
                end_program = wakeword(text)
                if end_program:
                    gpt_response = call_gpt_api(text[len("eliza"):].strip())  # Use the prompt after the wakeword
                    TTS(gpt_response)
                    play_audio_file("temp\output.mp3")
                    print("GPT Response:", gpt_response)

if __name__ == "__main__":
    main()
