FROM python:2.7.13-onbuild

COPY . .
CMD ['python proxy.py']