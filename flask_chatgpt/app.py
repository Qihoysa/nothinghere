from flask import Flask, render_template
import requests
from flask import Flask, render_template, request, jsonify
from vits_pack import Vits
from recording import recording
from aiui import XFServerAudio

vits = Vits()
app = Flask(__name__, template_folder="templates")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    message = request.form['message']
    response = chat_gpt(message)
    return jsonify(response=response)


@app.route('/microphone', methods=['POST'])
def microphone():
    recording()
    text = XFServerAudio()[-2:]
    print(text)
    return jsonify(response=text)


@app.route('/speaking', methods=['POST'])
def speaking():
    print("开始生成语音")
    text = request.form['message']
    vits.speaking(text)
    return None


def chat_gpt(message):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your own key"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    print(response_json)
    response_message = response_json['choices'][0]['message']['content']
    # print(response_message)
    return response_message.strip()


if __name__ == '__main__':
    app.run(debug=True)
