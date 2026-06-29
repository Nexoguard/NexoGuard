import os
from kivy.app import App
from kivy.utils import platform
from flask import Flask, render_template
import threading

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

def iniciar_servidor():
    app.run(host='127.0.0.1', port=5000, debug=False)

class NexoguardApp(App):
    def build(self):
        threading.Thread(target=iniciar_servidor, daemon=True).start()
        if platform == 'android':
            from android.webview import WebView
            self.webview = WebView("http://127.0.0.1:5000")
            return self.webview
        else:
            from kivy.uix.label import Label
            return Label(text="Abra http://127.0.0.1:5000 no navegador")

if __name__ == '__main__':
    NexoguardApp().run()
