#!/usr/bin/env bash

[ -f messages ] && rm messages
for i in {1..10000}; do echo '{"message_body": "'$(uuidgen)-${i}'"}' >> messages; done
