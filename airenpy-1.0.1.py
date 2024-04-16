import tkinter as tk
from tkinter import scrolledtext, simpledialog, Label
from PIL import Image, ImageTk
import requests
import json
import os
from urllib.request import urlretrieve
import configparser

class App:

    def __init__(self, root):
        self.load_config()
        self.output_folder = os.path.join(os.getcwd(), "output")
        self.script_path = os.path.join(self.output_folder, "script.txt")
        self.ensure_output_folder_exists()
        self.setup_ui(root)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.api_key = config.get('API', 'key')
        self.api_url = config.get('API', 'url')

    def ensure_output_folder_exists(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def setup_ui(self, root):
        root.title("API操作界面")
        self.btn_generate_text = tk.Button(root, text="生成文本", command=self.on_generate_text)
        self.btn_generate_text.pack(pady=5)
        self.btn_generate_image = tk.Button(root, text="生成图片", command=self.on_generate_image)
        self.btn_generate_image.pack(pady=5)
        self.btn_text_to_image = tk.Button(root, text="文本到图片", command=self.on_text_to_image)
        self.btn_text_to_image.pack(pady=5)
        self.output_area = scrolledtext.ScrolledText(root, width=60, height=10, state='disabled')
        self.output_area.pack(pady=10)
        self.image_label = Label(root)
        self.image_label.pack(pady=5)

    def on_generate_text(self):
        prompt = simpledialog.askstring("生成文本", "请输入文本生成的Prompt:")
        if prompt:
            self.generate_text(prompt)

    def on_generate_image(self):
        prompt = simpledialog.askstring("生成图片", "请输入图片生成的Prompt:")
        if prompt:
            self.generate_image(prompt)

    def on_text_to_image(self):
        if hasattr(self, 'last_text_output'):
            self.generate_image(self.last_text_output)
        else:
            self.display_output("没有可用的文本来生成图片。\n")

    def generate_text(self, prompt):
        try:
            url = f"{self.api_url}/v1/chat/completions"
            payload = self.create_payload(prompt, "text")
            response = self.send_request(url, payload)
            if response:
                text_output = response["choices"][0]["message"]["content"]
                self.last_text_output = text_output
                self.display_output(text_output)
                self.save_text(text_output)
            else:
                self.display_output("Error: API request failed.")
        except Exception as e:
            self.display_output(f"Error: {str(e)}")

    def generate_image(self, prompt):
        try:
            url = f"{self.api_url}/v1/images/generations"
            payload = self.create_payload(prompt, "image")
            response = self.send_request(url, payload)
            if response:
                image_url = response['data'][0]['url']
                self.display_output(f"Image URL: {image_url}")
                if image_url:
                    self.save_image(image_url, prompt)
                else:
                    self.display_output("Error: No image URL found in response.")
            else:
                self.display_output("Error: API request failed.")
        except Exception as e:
            self.display_output(f"Error: {str(e)}")

    def display_output(self, message):
        self.output_area.configure(state='normal')
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.configure(state='disabled')

    def create_payload(self, prompt, type):
        if type == "text":
            return json.dumps({
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "system", "content": "You are an assistant that directly output story sentences in RenPy code format."}
                ],
                "safe_mode": False
            })
        elif type == "image":
            return json.dumps({
                "model": "dall-e-3",
                "prompt": prompt,
                "response_format": "url",
                "size": "1024x1024",
            })

    def send_request(self, url, payload):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            self.display_output(f"Error: Received status code {response.status_code}")
            return None

    def save_text(self, text):
        with open(self.script_path, 'a', encoding='utf-8') as file:
            file.write(text + "\n")

    def save_image(self, image_url, prompt):
        try:
            image_name = f"{prompt.replace(' ', '_')[:15]}.png"
            image_path = os.path.join(self.output_folder, image_name)
            urlretrieve(image_url, image_path)
            self.display_output(f"Image saved: {image_path}")
            self.show_image(image_path)  # 显示图片
        except Exception as e:
            self.display_output(f"Error saving image: {str(e)}")

    def show_image(self, image_path):
        """加载并在界面上显示图片"""
        image = Image.open(image_path)
        image = image.resize((1024, 1024), Image.ANTIALIAS)  # 调整图片大小以适应界面
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo  # 保留对PhotoImage对象的引用

root = tk.Tk()
app = App(root)
root.mainloop()