# Sample Application
The sample application resides in `my-app` directory.
Applications provides endpoints to digitally sign and verify `PNG` or `JPEG` images files. Signature is done using RSA-4096 key.

Application requires `PostgreSQL` database to write signature log and `Redis` as to cache responses for signing operations.

## Configuration
Application accepts environment variables for configuration:
| Name | Description | Default |
| - | - | - |
| APP_HOST | Host/IP address to listen on | `127.0.0.1` |
| APP_PORT | TCP port to listen on | `8080` |
| APP_PRIVATE_KEY_PATH | Path to private signing key in PEM format | `./signing.private.pem` |
| APP_PUBLIC_KEY_PATH | Path to public signing key in PEM format | `./signing.public.pem` |
| APP_GENERATE_KEYPAIR | Whether application should generate key-pair if not present on startup | `false` |
| DB_HOST | PostgreSQL database server host | `localhost` |
| DB_PORT | PostgreSQL database server port | `5432` |
| DB_USER | PostgreSQL user to use for connection | `my-app` |
| DB_PASSWORD | PostgreSQL user password to use for connection | - |
| DB_NAME | Name of PostgreSQL database to use | `my-app` |
| REDIS_HOST | Redis server host | `localhost` |
| REDIS_PORT | Redis server port | `6379` |

## Endpoints
Application provides HTTP endpoints documented here.

### POST /sign
Any binary data posted to this endpoint is parsed as an images (must be either `.png` or `.jpeg`) image. Data is processed using `Pillow` library and digitally signed using RSA-4096 private key using `pycryptodome` library.

Depending on the value of optional query parameter `get` the following is returned:
* For `image` binary image in `PNG` or `JPEG` format is returned with signature attached in `UserComment` EXIF metadata section,
* For `signature` a JSON response containing digital signature is returned.

### POST /verify
Verifies image file signature either using `UserComment` EXIF metadata value or using URL-safe Base64-encoded value from `signature` query parameter value. Returns `HTTP 200` with JSON body if verification is successful otherwise `HTTP 409` is returned.

## Development
Project contains a `Dockerfile` which builds the required environment based on **Alpine-based Python Image**.

Docker compose file `docker-compose.yaml` provides a quick-start for local development. Ensure signing key-pair is generated before:
```bash
$ ./scripts/generate_keypair.sh
```

Then the environment can be started as follows:
```bash
$ docker-compose up
```
