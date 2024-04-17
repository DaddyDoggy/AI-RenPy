import requests
import json
import os
from urllib.request import urlretrieve
import configparser

class MainApp:
    def __init__(self):
        self.load_config()
        self.output_folder = os.path.join(os.getcwd(), "output")
        self.script_path = os.path.join(self.output_folder, "script.txt")
        self.ensure_output_folder_exists()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.api_key = config.get('API', 'key')
        self.api_url = config.get('API', 'url')

    def ensure_output_folder_exists(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def generate_text(self, prompt):
        try:
            url = f"{self.api_url}/v1/chat/completions"
            payload = self.create_payload(prompt, "text")
            response = self.send_request(url, payload)
            if response:
                text_output = response["choices"][0]["message"]["content"]
                self.save_text(text_output)
                return text_output
            else:
                return "Error: API request failed."
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_image(self, prompt):
        try:
            url = f"{self.api_url}/v1/images/generations"
            payload = self.create_payload(prompt, "image")
            response = self.send_request(url, payload)
            if response:
                image_url = response['data'][0]['url']
                if image_url:
                    self.save_image(image_url, prompt)
                    return image_url
                else:
                    return "Error: No image URL found in response."
            else:
                return "Error: API request failed."
        except Exception as e:
            return f"Error: {str(e)}"

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
            return None

    def save_text(self, text):
        with open(self.script_path, 'a', encoding='utf-8') as file:
            file.write(text + "\n")

    def save_image(self, image_url, prompt):
        try:
            image_name = f"{prompt.replace(' ', '_')[:15]}.png"
            image_path = os.path.join(self.output_folder, image_name)
            urlretrieve(image_url, image_path)
        except Exception as e:
            print(f"Error saving image: {str(e)}")