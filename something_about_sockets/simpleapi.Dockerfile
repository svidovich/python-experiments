FROM python:3.10.4

RUN python3 -m pip install Flask==2.1.1
COPY ./simpleapi/main.py /main.py

ENTRYPOINT [ "python3", "/main.py" ]