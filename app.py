from flask import Flask, render_template, request, redirect, url_for
import speech_recognition as sr
from gtts import gTTS
from datetime import datetime
import pyttsx3, pygame, json, re, shutil, os, random
from videogen import combine_video_and_audio
from chatbot import chatbot1
import videocap

app = Flask(__name__)

if not os.path.exists('./static/tempvoice'):
    os.makedirs('./static/tempvoice')

# Load OUTPUTS
def load_json(file):
    with open(file) as bot_responses:
        print(f"Loaded '{file}' successfully!")
        return json.load(bot_responses)
response_data = load_json("bot.json")

# Initialize the voice Recognition
r = sr.Recognizer()
engine = pyttsx3.init()
pygame.mixer.init()

# Create an MP3 for the Text
def speak(text):
    date_string = datetime.utcnow().strftime("%d%m%Y%H%M%S")
    filename = "./static/tempvoice/voice"+date_string+".mp3"
    tts = gTTS(text=text, lang='en', tld='com.au')
    tts.save(filename)
    filename="voice"+date_string+".mp3"
    file="voice"+date_string
    return filename,file

#Print Interaction
def listen():
    with sr.Microphone() as source:
        print("Speak something!")
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print("You said: ", text)
            return text
        except:
            print("Sorry, I did not understand that.")
            return ""

#Response Definition

def respond(command):
    split_message = re.split(r'\s+|[,;?!.-]\s*', command.lower())
    score_list = []

    for response in response_data:
        response_score = 0
        required_score = 0
        required_words = response["required_words"]

        if required_words:
            for word in split_message:
                if word in required_words:
                    required_score += 1

        if required_score == len(required_words):
            for word in split_message:
                if word in response["user_input"]:
                    response_score += 1

        score_list.append(response_score)

    best_response = max(score_list)
    response_index = score_list.index(best_response)

    if command == "":
        return "Please tell me something so we can talk to each other"

    # Return if blank voice
    if best_response != 0:
        response = response_data[response_index]["bot_response"]

        #Specific Responses
        #TIME
        if "time" in command: 
            current_time_now = datetime.now()
            current_time = current_time_now.strftime("%H:%M")
            bot_response = response.replace("LATIME", current_time)

        #DATE
        if "date" in command:
            current_date_now = datetime.now()
            current_date = current_date_now.strftime("%m-%d-%Y")
            bot_response = response.replace("LADATE", current_date)
        
        #JOKES
        if "tell" and "joke" in command:
            randjoke = random.randint(1,3)
            if randjoke == 1: 
                bot_response = "Why did the chatbot go to therapy? Because it had too many unresolved dialogues!"
            elif randjoke == 2: 
                bot_response = "Why did the chatbot go on a diet? It wanted to reduce its word count!"
            elif randjoke == 3: 
                bot_response = "What did the chatbot say when it got confused? I need to reboot my artificial stupidity!"
            return bot_response

    return random.choice(["I didn't catch that.", "Can you please repeat that?", "I'm not sure I understand."])


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/greeting')
def greeting():
    face = videocap.meth()
    txt=''
    st=''
    #face = 'sad'
    if face == 'happy':
        st= 'Do you want to share with me the reason that makes you %s ?' % (face)
    elif face == 'neutral':
       st= "Today is the same like yesterday, I see that on your face. Nothing is happend, isn't it?"
    elif face == 'sad':
        st ='I understand that, you are not in a good mood. What happened?'
    elif face == 'angry':
        st= 'I believe that you need to calm down, you look a bit %s. What makes you feel that way?' % (face)
    elif face == 'surprise':
        st ='What is the reason that you look %s.' % (face)
    au_path,au=speak(st)
    video_path=r"F:\empathyai\Video.mp4"
    audio_path="F:/empathyai/static/tempvoice/"+au_path
    output_path="F:/empathyai/static/"+au+".mp4"
    f=au+".mp4"
    
    combine_video_and_audio(video_path, audio_path, output_path)

   
    return render_template('greeting.html',filename=f)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    command = request.form['command'].lower()
    if "exit" in command:
        shutil.rmtree('tempvoice', ignore_errors=True)
        return redirect(url_for('index'))
    print(command)
    response = chatbot1(str(command))
    print(response)
    filename,file = speak(response)
    video_path=r"F:\empathyai\Video.mp4"
    audio_path="F:/empathyai/static/tempvoice/"+filename
    output_path="F:/empathyai/static/"+file+".mp4"
    f=file+".mp4"
    
    combine_video_and_audio(video_path, audio_path, output_path)

    return render_template('index.html', response=response, filename=f)

if __name__ == '__main__':
    app.run(debug=True)
