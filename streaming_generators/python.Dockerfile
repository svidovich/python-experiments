FROM python:3.10-slim-buster

ADD src /src
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install wheel setuptools
RUN python3 -m pip install -r /src/requirements.txt

CMD ["python3", "-u", "/src/sample.py"]