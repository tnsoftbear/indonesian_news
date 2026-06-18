from openai import OpenAI

class HindiTranslator:
    RETURN_TRANSLATION = "Return translation to Hindi using Devanagari script (हिंदी). Do NOT use Hinglish or Latin transliteration."
    KEEP_MARKDOWN = "Keep Markdown format"
    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        self.base_url = base_url

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
        prompt = f"Formulate text to be an article. It may contain multiple numbers scrapped from tabular html data, exclude it from answer. {self.RETURN_TRANSLATION}. Do not exceed {limit} characters. {self.KEEP_MARKDOWN}.\n Input:\n```\n'{original}'\n```"
        return self.fetch_hindi(prompt)

    def fetch_hindi(self, prompt):
        try:
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            client = OpenAI(**kwargs)
            model = "local" if self.base_url else "gpt-3.5-turbo"
            chat_completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            hindi_translation = chat_completion.choices[0].message.content
            return hindi_translation
        except Exception as e:
            print("An error occurred:", e)
            return None