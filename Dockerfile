FROM python:2.7.13-onbuild

COPY . .
RUN pip install -r requirements.txt
CMD ['python proxy.py']