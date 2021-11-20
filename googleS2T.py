from http import client
from google.cloud.speech_v1.types.cloud_speech import SpeechContext
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1.services import adaptation
from google.cloud.speech_v1p1beta1.services.adaptation.transports.base import AdaptationTransport
from google.cloud.speech_v1p1beta1.types.cloud_speech_adaptation import GetPhraseSetRequest
from google.cloud.speech_v1p1beta1.types.resource import CustomClass, PhraseSet
# import requests
# import base64
# import json
from google.oauth2 import service_account
# from google.cloud import speech
import io
import sys
import os
import subprocess

# with open ("records/2.wav", "rb") as audio_file:
#     content = audio_file.read
# f= open("temp.txt", "w")
# f.write(encoded)
# f.close


file_name = str(sys.argv[1:][0])
device = str(sys.argv[1:][1])
# file_name = 'records/1.wav'

if device == "esp":
    sampleRate = 16000

elif device == "pi":
    sampleRate = 44100

SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
SERVICE_ACCOUNT_FILE = 'braided.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'braided.json'


credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

client = speech.SpeechClient(credentials=credentials)

with io.open(file_name, "rb") as audio_file:
    content = audio_file.read()

speech_context = speech.SpeechContext(phrases=["$00V_CLASS_TEMPERATURE", "$OOV_CLASS_TV_CHANNEL", "$OPERAND", "on", "off", "ac", "air conditioner",
                                      "light", "mode", "fan", "cool", "dry", "swing", "toggle", "tv", "television", "volume", "increase", "decrease", "up", "down", "channel", "speed"],boost=15)


audio = speech.RecognitionAudio(content=content)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=sampleRate,
    language_code="en-US",
    model="command_and_search",
    speech_contexts=[speech_context],

)


response = client.recognize(config=config, audio=audio)
text = ""
for result in response.results:
    # print(u"Transcript: {}".format(result.alternatives[0].transcript))
    text += result.alternatives[0].transcript

# print(text)

subprocess.Popen(["python3", "filter.py", str(text), device], cwd=os.getcwd())

# import broadlink
# devices = broadlink.discover(timeout=2, discover_ip_address='192.168.1.163')
# devices[0].auth()


# if text.find("on")>=0:
#     f=open("switch.on","rb")
#     lines=f.readline()
#     f.close()
#     print("turning lights on")
#     devices[0].send_data(lines)

# elif text.find("off")>=0:
#     f=open("switch.off","rb")
#     lines=f.readline()
#     f.close()
#     print("turning lights off")
#     devices[0].send_data(lines)

# else:
#     print("command not recognized")


# url = "https://speech.googleapis.com/v1/speech:recognize"

# payload = {
#     "config": {
#         "encoding": "LINEAR16",
#         "sampleRateHertz": 44100,
#         "languageCode": "en-US",
#         "enableWordTimeOffsets": False
#     },
#     "audio": {"content": encoded}
# }
# headers = {
#     "Content-Type": "application/json",
#     "Authorization": "Bearer REDACTED"
# }

# response = requests.request("POST", url, json=payload, headers=headers)
# print(response.text)
# data = json.loads(response.text)

# transcript = data['results'][0]['alternatives'][0]['transcript']
# confidence = data['results'][0]['alternatives'][0]['confidence']
# print("Transcript: "+transcript)
# print("Confidence: "+str(confidence))
