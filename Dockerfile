FROM pytorch/pytorch:latest
COPY ./cai.py cai.py
COPY ./voicebot.py voicebot.py
RUN pip3 install torchaudio python-telegram-bot transformers oauthlib requests-oauthlib
CMD [ "python3", "voicebot.py"]
