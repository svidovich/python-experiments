from rabbitmq:latest

# TODO Probably don't do this.
RUN rabbitmq-plugins enable rabbitmq_management

ENV RABBITMQ_CONFIG_FILE=/etc/rabbitmq/rabbitmq.conf
COPY queue/rabbit-definitions.json /etc/rabbitmq/definitions.json
COPY queue/rabbitmq.conf ${RABBITMQ_CONFIG_FILE}