from flask import Flask, Response

app = Flask(__name__)


@app.route("/health")
def healthcheck():
    return Response('OK', status=200)


@app.route("/")
def sample():
    return Response('{"sample":"data"}', status=200)


def main():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
