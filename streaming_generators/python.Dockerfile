from python:3.10-slim-buster

add src /src

cmd ["python", "-m", "http.server"]