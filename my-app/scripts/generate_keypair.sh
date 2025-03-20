#!/bin/bash

if [ -f "./signing.private.pem" ] || [ -f "./signing.public.pem" ]; then
  echo "Keypair or one of its files already exist!"
  exit 1
fi

openssl genrsa -out ./signing.private.pem 4096
openssl rsa -in ./signing.private.pem -pubout -out ./signing.public.pem
