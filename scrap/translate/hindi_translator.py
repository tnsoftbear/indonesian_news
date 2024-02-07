from openai import OpenAI

class HindiTranslator:
    RETURN_TRANSLATION = "Return translation to Hindi"
    KEEP_MARKDOWN = "Keep Markdown format"
    def __init__(self, api_key):
        self.api_key = api_key

    def get_hindi_translation(self, original):
        prompt = f"{self.RETURN_TRANSLATION}\n Input:\n```\n'{original}'\n```"
        return self.fetch_hindi(prompt)

    def get_hindi_translation_limited(self, original, limit):
        prompt = f"{self.RETURN_TRANSLATION}. Do not exceed {limit} characters.\n Input:\n```\n'{original}'\n```"
        return self.fetch_hindi(prompt)

    def get_hindi_translation_limited_keep_link(self, original, limit):
        prompt = f"{self.RETURN_TRANSLATION}. Do not exceed {limit} characters. Keep link in the beginning.\n Input:\n```\n'{original}'\n```"
        return self.fetch_hindi(prompt)

    def get_hindi_translation_keep_markdown(self, original, limit):
        prompt = f"Formulate text to be an article. It may contain multiple numbers scrapped from tabular html data, exclude it from answer. Return translation to Hindi. Do not exceed {limit} characters. {self.KEEP_MARKDOWN}.\n Input:\n```\n'{original}'\n```"
        return self.fetch_hindi(prompt)

    def fetch_hindi(self, prompt):
        try:
            client = OpenAI(api_key=self.api_key)
            chat_completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            hindi_translation = chat_completion.choices[0].message.content
            return hindi_translation
        except Exception as e:
            print("An error occurred:", e)
            return None