import os
from openai import OpenAI

class HindiTranslator:
    
    def get_hindi_translation(self, original):
        prompt = f"Return translation to Hindi '{original}'"
        return self.fetch_hindi(prompt)

    def get_hindi_translation_limited(self, original, limit):
        prompt = f"Return translation to Hindi. Do not exceed {limit} characters. Keep link in the beginning: '{original}'"
        return self.fetch_hindi(prompt)

    def get_hindi_translation_keep_markdown(self, original, limit):
        prompt = f"Formulate text to be an article. Return translation to Hindi. Do not exceed {limit} characters. Keep Markdown format: '{original}'"
        return self.fetch_hindi(prompt)

    def fetch_hindi(self, prompt):
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        hindi_translation = chat_completion.choices[0].message.content
        return hindi_translation