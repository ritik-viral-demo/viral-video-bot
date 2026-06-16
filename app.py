import os
import json
import requests

from flask import Flask, request, jsonify

import google.generativeai as genai
from gtts import gTTS

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip
)


app = Flask(__name__)


# =====================
# GEMINI
# =====================

GEMINI_KEY = os.environ.get("GEMINI_KEY")

genai.configure(
    api_key=GEMINI_KEY
)


model = genai.GenerativeModel(
    "gemini-2.0-flash"
)



def generate_script(news):

    prompt = f"""

Create a YouTube Shorts script.

Length:
20-60 seconds

Return ONLY JSON.

Format:

{{
"voice":"",
"caption":"",
"image_prompt":""
}}

News:

{news}

"""


    result = model.generate_content(prompt)

    return json.loads(result.text)



# =====================
# VOICE
# =====================


def create_voice(text):

    file="voice.mp3"

    audio=gTTS(
        text=text,
        lang="en"
    )

    audio.save(file)

    return file



# =====================
# PLACEHOLDER IMAGE
# =====================


def create_image():

    url="https://picsum.photos/1080/1920"


    data=requests.get(url).content


    with open("image.jpg","wb") as f:
        f.write(data)


    return "image.jpg"



# =====================
# VIDEO BUILDER
# =====================


def build_video(image, audio, caption):


    img=ImageClip(image)


    sound=AudioFileClip(audio)


    img=img.set_duration(
        sound.duration
    )


    img=img.resize(
        height=1920
    )


    img=img.crop(
        x_center=img.w/2,
        width=1080
    )


    txt=TextClip(
        caption,
        fontsize=60,
        color="white",
        size=(900,None),
        method="caption"
    )


    txt=txt.set_position(
        ("center","bottom")
    )


    final=CompositeVideoClip(
        [
            img,
            txt
        ]
    )


    final=final.set_audio(sound)


    final.write_videofile(
        "output.mp4",
        fps=30
    )


# =====================
# API
# =====================


@app.route("/")
def home():

    return "AI Video Bot Running"



@app.route("/generate",methods=["POST"])
def generate():


    news=request.json["news"]


    script=generate_script(news)


    voice=create_voice(
        script["voice"]
    )


    image=create_image()


    build_video(
        image,
        voice,
        script["caption"]
    )


    return jsonify({

        "status":"done",

        "script":script,

        "video":"output.mp4"

    })




if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
