# Streaming Generators

I wanted a data pipeline based on generators. When you have a data pipeline, you'll generally
wind up with a message bus and a data sink, so I had to build a message bus and a data sink.

## Development

TODO as I finish up the minimal PoC

## Testing

At _very_ minimum, you'll need docker, docker-compose, and python 3 something. Probably 3.7+.

Let's build the cluster:

```
docker-compose build
docker-compose up
```

Good work!

### Message Queue: RabbitMQ

We use RabbitMQ as the message bus because it's easy and I didn't want to think hard. Feel free to implement your own message adapter using the message adapter base class.
To interact with the message queue, you can use the included script in the `scripts` directory. First, install some prerequisites:

```
cd scripts
python3 -m venv venv
source !$/bin/activate
python3 -m pip install -r requirements_scripts.txt
```

Then, send the message. _As written, the plugin that will process the message, the sample plugin, expects a JSON object with a `message_body` key._

```
python send_message.py -q messages -m '{"message_body": "hello-world"}'
```

### Database: PostgreSQL 12

We pick postgres because again, easy to set up. I _don't_ use a management framework. You _absolutely could_. Intead, I use a very basic `init.sql` ( found in `database` ) to set up the database. You get a user for free, `pipeline_user`, whose password is ( very elegantly ) `pipeline`. Once the database is up and initialized, interact with it via psql thus:

```
psql -h localhost -p 5432 -d postgres -U pipeline_user
```

Then, select from the built in messages table with:

```
select * from message_table;
```

You should see your message in the table, supposing you sent one.
