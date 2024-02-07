from openai import OpenAI

# https://platform.openai.com/docs/guides/images
class DalleImageGenerator:
  def __init__(self, api_key):
    self.api_key = api_key

  def generate(self, content):
    try:
      client = OpenAI(api_key=self.api_key)
      prompt = f"Avoid text on image. Generate image for visualizing the next article: {content}"
      response = client.images.generate(
        model="dall-e-2",
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
    