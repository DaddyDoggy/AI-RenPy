import requests
import json

# 您的API / Your API
api_key = "your api key"
api_url = "https://oa.api2d.net"


# 函数：生成文本 / Function of Generating texts
def generate_text(prompt):
    url = api_url + "/v1/chat/completions"
    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            },
            {
            "role": "system",
            "content": "You are an assistant that directly output RenPy code."
            }
        ],
        "safe_mode": False
    })
    headers = {
        'Authorization': f'Bearer {api_key}',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

# 函数：生成图片 / Function of Generating images
def generate_image(prompt):
    url = api_url + "/v1/images/generations"
    payload = json.dumps({
    "prompt": prompt,
    "response_format": "url",
    "size": "1024x1024",
    "model": "dall-e-3"
    })
    headers = {
    'Authorization': f'Bearer {api_key}',
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

# 主程序 / Main Function
last_text_output = ""  # 用于存储最近生成的文本
while True:
    model_choice = input("请选择要使用的模型（输入 'text'、'img' 或 't2p'）: ")
    if model_choice.lower() == 'text':
        prompt = input("请输入Prompt: ")
        try:
            last_text_output = generate_text(prompt)
            print(last_text_output)
        except Exception as e:
            print(e)
    elif model_choice.lower() == 'img':
        prompt = input("请输入图片的描述Prompt: ")
        try:
            image_path = generate_image(prompt)
            print("生成的图片已保存至:", image_path)
        except Exception as e:
            print(e)
    elif model_choice.lower() == 't2p':
        if last_text_output:
            try:
                image_path = generate_image(last_text_output)
                print("生成的图片已保存至:", image_path)
            except Exception as e:
                print(e)
        else:
            print("请先生成文本作为Prompt。")
    else:
        print("无效的模型选择，请重新输入。")
        continue
    choice = input("是否继续？(输入'y'继续，其他键退出): ")
    if choice.lower() != 'y':
        break