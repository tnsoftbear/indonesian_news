from openai import OpenAI

# https://platform.openai.com/docs/guides/images
class DalleImageGenerator:
  def __init__(self, api_key, base_url=None):
    self.api_key = api_key
    self.base_url = base_url

  def generate(self, content):
    try:
      kwargs = {"api_key": self.api_key}
      if self.base_url:
        kwargs["base_url"] = self.base_url
      client = OpenAI(**kwargs)
      prompt = f"Avoid text on image. Generate image for visualizing the next article: {content}"
      model = "dall-e-2"
      response = client.images.generate(
        model=model,
        prompt=prompt[:1000],
        size="512x512",
        quality="standard",
        n=1,
      )
      image_url = response.data[0].url
      return image_url
    
    except Exception as e:
      print("An error occurred:", e)
      return None
    