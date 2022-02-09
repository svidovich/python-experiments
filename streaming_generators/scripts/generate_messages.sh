#!/usr/bin/env bash

rm messages
for i in {1..1000}; do echo '{"message_body": "'$(uuidgen)-${i}'"}' >> messages; done
