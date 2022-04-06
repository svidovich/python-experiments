import random
import uuid
from flask import Flask, Response, request

app = Flask(__name__)


@app.route("/health")
def healthcheck():
    return Response('OK', status=200)


@app.route("/")
def sample():
    return Response('{"sample":"data"}', status=200)

ephemeral_store = list()

@app.route("/generator", methods=["GET", "POST", "PUT"])
def id_endpoint():
    id = request.args.get('id', None)
    if request.method == "GET":
        if not id and len(ephemeral_store) > 0:
            return Response(random.choice(ephemeral_store), status=200)
        elif not id and not len(ephemeral_store):
            return Response("No ID supplied.", status=400)
        elif id in ephemeral_store:
            return Response(f"ID {id} found!\n", status=200)
        else:
            return Response(f"ID {id} not found!\n", status=404)
    elif request.method == "POST":
        return Response(f'{uuid.uuid4()}', status=200)
    elif request.method == "PUT":
        try:
            uuid.UUID(id)
            ephemeral_store.append(id)
            return Response("OK", status=200)
        except ValueError as e:
            return Response(f"Couldn't add ID {id}: {e}\n", status=422)
    else:
        return Response("Not Implemented", status=501)

def main():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
