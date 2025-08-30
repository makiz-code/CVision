from config.envs import LLM_MODEL, HF_API_TOKEN
from huggingface_hub import InferenceClient

def query_llm(prompt: str, model_name=LLM_MODEL, token=HF_API_TOKEN) -> str:
    client = InferenceClient(api_key=token)
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content
    