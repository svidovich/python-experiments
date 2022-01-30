# Pika constants

# Returned by the server if there was no message in the queue to retrieve;
# see documentation: https://pika.readthedocs.io/en/stable/examples/blocking_basic_get.html
PIKA_NULL_MESSAGE = (None, None, None)

# Message adapter constants

# How frequently to poll.
POLL_INTERVAL = 1.0