FROM python:3.13-alpine

WORKDIR /scrap

COPY ./scrap /scrap

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "run.py" ]