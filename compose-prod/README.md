# Docker Compose Production Sample
This folder provides a sample of possible production-grade deployment of the application on a VPS/VM using Docker Compose.

It is necessary to generate keypair before launching the application, these keys will get mounted to the application container:
```bash
$ openssl genrsa -out ./signing.private.pem 4096
$ openssl rsa -in ./signing.private.pem -pubout -out ./signing.public.pem
```
or using the script provided in `my-app` sources:
```bash
$ ../my-app/scripts/generate_keypair.sh
```

Then the deployment can be launched as follows:
```bash
$ docker-compose up -d
```

> The `-d` flag launches the stack in detached mode - does not keep the log open.
