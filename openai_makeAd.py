import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

import pandas as pd
data = pd.read_csv("C:/Users/yehun_chang/OneDrive/비디오/바탕 화면/대학원 공부 자료/24-2/텐서플로우 활용기초/숙제 실습/기말고사/data/유닉스매직기.csv")
#%%
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
#%%
rewrite_system_prompt = '''
You are a advertiser.
Your goal is to rewrite reviews to create a advertising review with Korean, Hangul.
And you must write reviews naturally, as if they are written by a real human.
you will be provided with a original reviews, and you will output a json object containing the following information:

{
advertising_review : string // A natural review that contains about 2~5 sentences, and must contain below features:
    1. Lack of specific usage experience
    2. Deliberately disparaging competitor's products
    3. A tone strongly encouraging purchase
}
'''
#%%
tasks = []
for idx, review in enumerate(data['리뷰내용']):
    task = {
        "custom_id": f"task_review_{idx}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.1,
            "response_format": { 
                "type": "json_object"
            },
            "messages": [
                {
                    "role": "system",
                    "content": rewrite_system_prompt
                },
                {
                    "role": "user",
                    "content": f'original review: {review}'
                }
            ],
        }
    }
    tasks.append(task)
#%%
import json
file_name = "review_rewrite_task.jsonl"
with open(file_name, "w") as file:
    for task in tasks:
        json.dump(task, file)
        file.write("\n")
#%%
create_data_task = client.files.create(
    file=open(file_name, 'rb'),
    purpose='batch'
    )

batch_job = client.batches.create(
    input_file_id=create_data_task.id,
    endpoint="/v1/chat/completions",
    completion_window='24h'
    )

batchjob_id = batch_job.id
#%%
batch_job = client.batches.retrieve(batchjob_id)
result_file_id = batch_job.output_file_id

result = client.files.content(result_file_id).content
result_file_name = "batch_job_results.jsonl"
with open(result_file_name, 'wb') as file:
    file.write(result)
    
all_results = []
with open(result_file_name, 'r', encoding='utf-8') as file:
    for line in file:
        json_object = json.loads(line.strip())
        all_results.append(json_object)
#%%
ai_df = pd.DataFrame(columns=['리뷰내용', '광고성리뷰'])
for item in all_results:
    ex = item['response']['body']['choices'][0]['message']['content']
    ex_json = json.loads(ex)
    review_ai = ex_json.get('advertising_review')
    isAd = 1
    new_row = pd.DataFrame([{
        '리뷰내용':review_ai,
        "광고성리뷰":isAd
        }])
    
    ai_df = pd.concat([new_row, ai_df], ignore_index=True)
#%%
data_for_concat = data['리뷰내용'].to_frame()
data_for_concat['광고성리뷰'] = 0
data_final = pd.concat([data_for_concat, ai_df], ignore_index=True)
#%%
data_final.to_csv('C:/Users/yehun_chang/OneDrive/비디오/바탕 화면/대학원 공부 자료/24-2/텐서플로우 활용기초/숙제 실습/기말고사/data/유닉스매직기_광고성리뷰_포함.csv', index=False)