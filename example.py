import openai
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


openai.api_key = "sk-XXXXXXXXXXXXXXXX" # ваш ключ в VseGPT после регистрации

openai.api_base = "https://api.vsegpt.ru/v1"

base64_image = encode_image("Einstein.jpg")
messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What you think the person in the image is doing?"},
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        }
    ]

response_big = openai.ChatCompletion.create(
    model="vis-google/gemini-pro-vision",
    messages=messages,
    temperature=0.8,
    n=1,
    max_tokens=300,
)

#print("Response BIG:",response_big)
response = response_big["choices"][0]["message"]
print("Response:",response)