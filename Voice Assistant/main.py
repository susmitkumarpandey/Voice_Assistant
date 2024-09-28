import speech_recognition as sr
import pyttsx3 as p  # for text-to-speech Conversion
from sel import infow
import subprocess
from weather import Weather
from tkinter import *
from dotenv import load_dotenv
import sys
import threading
import google.generativeai as genai
import os
import re


load_dotenv()
API_KEY = os.getenv("API_KEY_GEMINI")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat()


engine = p.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
rate = engine.getProperty('rate')
engine.setProperty('rate', 180)

r = sr.Recognizer()


screen = Tk()
screen.title("Voice Assistant")
screen.config(padx=50, pady=30)

canvas = Canvas(width=400, height=400)
t_image = PhotoImage(file="V_pic.png")
canvas.create_image(200, 150, image=t_image)
action_text = canvas.create_text(
    200, 330, text="Welcome...", font=("Courier", 15, "bold"), width=300)
canvas.grid(row=1, column=1)


# For handling the emojis if they appear in the response.
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F300-\U0001F5FF"  # Miscellaneous Symbols and Pictographs
    "\U0001F680-\U0001F6FF"  # Transport and Map Symbols
    "\U0001F700-\U0001F77F"  # Alchemical Symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"  # Enclosed Characters
    "]+", flags=re.UNICODE
)


listening_thread = None


def speak(text):
    engine.say(text)
    engine.runAndWait()


def listen():
    with sr.Microphone() as source:
        r.energy_threshold = 10000
        r.adjust_for_ambient_noise(source, 1.2)
        print("Listening.....")
        try:
            audio = r.listen(source)
            text = r.recognize_google(audio)
            print(text)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            speak("Sorry, Sir.Please repeat again.")
            return "Try again"
        except sr.RequestError as e:
            print(
                f"Could not request results from Google Speech Recognition service; {e}")
            return "Sorry, there was an issue with the service."


def greeting():
    speak("Hello Sir. I am Cassie. How May I help you.")


def handle_command(tex):
    if "search" and "wikipedia" in tex.lower():
        speak("Please tell me the topic sir")
        query = listen()
        assist = infow()
        assist.get_info(query)

    elif "video" and "youtube" in tex.lower():
        speak("Please tell me the name of the song you want to play")
        query = listen()
        speak("Enjoy the song")
        assist = infow()
        assist.play_video(query)

    elif "open" and "excel" in tex.lower():
        speak("Opening Excel")
        subprocess.Popen(
            "C:/Program Files/Microsoft Office/root/Office16/EXCEL.EXE")

    elif "open" and "word" in tex.lower():
        speak("Opening Word")
        subprocess.Popen(
            "C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE")

    elif "open" and "powerpoint" in tex.lower():
        speak("Opening PowerPoint")
        subprocess.Popen(
            "C:/Program Files/Microsoft Office/root/Office16/POWERPNT.EXE")

    elif "weather" in tex.lower():
        speak("Providing weather details")
        w = Weather()
        data = w.get_weather()
        speak(f"It seems like {data['weather'][0]['description']}")
        speak(
            f"Temperature feels like {data['main']['feels_like']} Fahrenheit")
        speak(f"Wind speed is {data['wind']['speed']} km per hour")

    elif "exit" in tex.lower():
        try:
            speak("Have a good day")
            screen.quit()  # Stop the Tkinter main loop
            screen.destroy()  # Close the window
            sys.exit()
        except RuntimeError:
            pass

    else:
        response = chat.send_message(tex).text[:400].replace('*', '')
        response = emoji_pattern.sub(r'', response)
        speak(response)


def update_text():
    global listening_thread
    # Check if the listening thread is already running to prevent interruption of already running thread and preventing runtime error while exiting the window.
    if listening_thread and listening_thread.is_alive():
        screen.after(1000, update_text)
        return

    def threaded_listen_and_speak():
        canvas.itemconfig(action_text, text="Listening...")
        text = listen()
        canvas.itemconfig(action_text, text=f"{text.capitalize()}")
        handle_command(text)
        listening_thread = None

    listening_thread = threading.Thread(target=threaded_listen_and_speak)
    listening_thread.start()
    screen.after(1000, update_text)


screen.after(1000, greeting)
screen.after(2000, update_text)

screen.mainloop()
