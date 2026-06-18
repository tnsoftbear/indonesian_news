FROM python:3.13-slim

WORKDIR /scrap

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make \
    && rm -rf /var/lib/apt/lists/*

COPY ./scrap /scrap

RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium and system dependencies
RUN playwright install --with-deps chromium

# Remove build tools to reduce image size
RUN apt-get purge -y gcc g++ make \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

CMD [ "python", "run.py" ]
