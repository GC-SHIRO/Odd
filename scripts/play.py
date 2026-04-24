from anthropic import Anthropic


model_id = "MiniMax-M2.7"
api_key = ""
base_url = "https://api.minimaxi.com/anthropic"

client = Anthropic(api_key=api_key, base_url=base_url)

messages = []

while(10):
    typecontent = input("请输入：")

    messages.append({
        "role": "user",
        "content": typecontent
    })

    resp = client.messages.create(
        model=model_id,
        max_tokens=4096,
        system="你是我的人工智能助手",
        messages=messages
    )
    messages.append({
        "role": "assistant",
        "content": resp.content[1].text
    })

    print(resp)
