import os
import PIL.Image
import flask
import io
import waitress
import logging
import PIL
import base64
import exiv2
import uuid
import datetime
import redis
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA512
import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID

logging.basicConfig()
logger = logging.getLogger("app")
logging.getLogger("waitress").setLevel(logging.DEBUG)
logging.getLogger("app").setLevel(logging.DEBUG)

# parse configuration
config = {
  "host": os.environ.get("APP_HOST", "127.0.0.1"),
  "port": os.environ.get("APP_PORT", "8080"),
  "private_key_path": os.environ.get("APP_PRIVATE_KEY_PATH", "./signing.private.pem"),
  "public_key_path": os.environ.get("APP_PUBLIC_KEY_PATH", "./signing.public.pem"),
  "allow_key_pair_generation": os.environ.get("APP_GENERATE_KEYPAIR", "false"),
  "db_host": os.environ.get("DB_HOST", "localhost"),
  "db_port": int(os.environ.get("DB_PORT", "5432")),
  "db_user": os.environ.get("DB_USER", "my-app"),
  "db_name": os.environ.get("DB_NAME", "my-app"),
  "db_password": os.environ.get("DB_PASSWORD", ""),
  "redis_host": os.environ.get("REDIS_HOST", "localhost"),
  "redis_port": int(os.environ.get("REDIS_PORT", "6379")),
}

# load or generate RSA keypair
if not os.path.exists(config["private_key_path"]) and config["allow_key_pair_generation"] == "true":
  logger.warning(f'private key not found - generating new RSA-4096 key at {config["private_key_path"]}')
  rsa_private_key = RSA.generate(4096)
  rsa_public_key = rsa_private_key.public_key()
  with open(config["private_key_path"], "wb") as file:
    data = rsa_private_key.export_key(format="PEM", pkcs=1)
    file.write(data)
    logger.info(f'stored new private key at {config["private_key_path"]}')
  with open(config["public_key_path"], "wb") as file:
    data = rsa_public_key.export_key(format="PEM", pkcs=1)
    file.write(data)
    logger.info(f'stored new public key at {config["private_key_path"]}')
else:
  with open(config["private_key_path"], "rb") as file:
    data = file.read()
    rsa_private_key = RSA.import_key(data)
  with open(config["public_key_path"], "rb") as file:
    data = file.read()
    rsa_public_key = RSA.import_key(data)
if not rsa_private_key or not rsa_public_key:
  raise Exception("failed to load RSA key-pair")

# setup database
db_engine = sqlalchemy.create_engine(f'postgresql+psycopg2://{config["db_user"]}:{config["db_password"]}@{config["db_host"]}:{config["db_port"]}/{config["db_name"]}')
db_factory = sessionmaker(bind=db_engine)
db_session = db_factory()
db_base = declarative_base()
class SignatureLogEntry(db_base):
    __tablename__ = "signature_log_entry"
    id = sqlalchemy.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    file_sha512 = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image_sha512 = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    signature = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    create_timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
db_base.metadata.create_all(bind=db_engine)

# setup redis
redis = redis.Redis(host=config["redis_host"], port=config["redis_port"], db=0)

# create Flask application
app = flask.Flask(__name__)

# info endpoint
@app.route("/")
def app_handle_info():
  return flask.jsonify({"status": "ok"})

# signature endpoint
@app.route("/sign", methods=["POST"])
def app_handle_sign():
  requested_output = flask.request.args.get("get", "signature")
  uploaded_file = flask.request.get_data()
  uploaded_file_hash = SHA512.new(uploaded_file)
  try:
    # return cached data if present
    cached_signature = redis.get(f'signature:{uploaded_file_hash.hexdigest()}')
    cached_exif_image = redis.get(f'exif-image:{uploaded_file_hash.hexdigest()}')
    if requested_output == "signature" and cached_signature:
      logger.debug(f'{uploaded_file_hash.hexdigest()} ({requested_output}) -> CACHE_HIT')
      return flask.jsonify({"signature": cached_signature.decode()})
    elif requested_output == "image" and cached_exif_image:
      logger.debug(f'{uploaded_file_hash.hexdigest()} ({requested_output}) -> CACHE_HIT')
      return app.response_class(response=cached_exif_image, status=200, mimetype="image/jpeg")
    logger.debug(f'{uploaded_file_hash.hexdigest()} ({requested_output}) -> CACHE_MISS')

    with PIL.Image.open(io.BytesIO(uploaded_file)) as image:
      if image.format not in ["PNG", "JPEG"]:
        return flask.jsonify({ "error": "only jpeg and png files are supported" }), 400
      # generate hash and signature
      image = image.convert("RGB")
      image_bytes = image.tobytes()
      image_hash = SHA512.new(image_bytes)
      signature = pkcs1_15.new(rsa_private_key).sign(image_hash)
      signature_b64 = base64.urlsafe_b64encode(signature).decode()
      
      # write db log entry
      uploaded_file_hash = SHA512.new(uploaded_file)
      log_entry = SignatureLogEntry(file_sha512=uploaded_file_hash.hexdigest(), file_size=len(uploaded_file), image_sha512=image_hash.hexdigest(), signature=signature_b64)
      db_session.add(log_entry)
      db_session.commit()

      # generate and cache output
      exif_image = exiv2.ImageFactory.open(uploaded_file)
      exif_image.readMetadata()
      exif_data = exif_image.exifData()
      exif_data["Exif.Photo.UserComment"] = signature_b64
      exif_image.writeMetadata()
      exit_image_bytes = bytes(exif_image.io())
      redis.set(f'signature:{uploaded_file_hash.hexdigest()}', signature_b64, 3600)
      redis.set(f'exif-image:{uploaded_file_hash.hexdigest()}', exit_image_bytes, 3600)
      logger.debug(f'{uploaded_file_hash.hexdigest()} ({requested_output}) -> CACHE_SET')

      # generate and return output
      if requested_output == "image":
        logger.debug(f'{uploaded_file_hash.hexdigest()} ({requested_output}) -> DIRECT_RESPOND')
        return app.response_class(response=exit_image_bytes, status=200, mimetype="image/jpeg")
      else:
        logger.debug(f'{uploaded_file_hash.hexdigest()} ({requested_output}) -> DIRECT_RESPOND')
        return flask.jsonify({"signature": signature_b64})
  except Exception as e:
    logger.error(e)
    return flask.jsonify({"error": str(e)}), 500

# verify endpoint
@app.route("/verify", methods=["POST"])
def app_handle_verify():
  uploaded_file = flask.request.get_data()
  uploaded_file_hash = SHA512.new(uploaded_file)
  try:
    with PIL.Image.open(io.BytesIO(uploaded_file)) as image:
      if image.format not in ["PNG", "JPEG"]:
        return flask.jsonify({ "error": "only jpeg and png files are supported" }), 400
      image = image.convert("RGB")
      raw_bytes = image.tobytes()
      hash = SHA512.new(raw_bytes)
      exif_image = exiv2.ImageFactory.open(uploaded_file)
      exif_image.readMetadata()
      exif_data = exif_image.exifData()
      exif_signature = exif_data["Exif.Photo.UserComment"].getValue().toString()
      signature = flask.request.args.get("signature", None) or exif_signature
      if not signature:
        return flask.jsonify({"error": "no signature found in file nor provided via query parameters"}), 400
      signature_bytes = base64.urlsafe_b64decode(signature)
      pkcs1_15.new(rsa_public_key).verify(hash, signature_bytes)
      logger.debug(f'{uploaded_file_hash.hexdigest()} -> VERIFY_RESPOND')
      return flask.jsonify({
        "status": "ok",
        "digest": hash.digest().hex(),
        "signature": signature,
      })
  except Exception as e:
    if isinstance(e, ValueError) and str(e) == "Invalid signature":
      logger.debug(f'{uploaded_file_hash.hexdigest()} -> VERIFY_FAIL')
      return flask.jsonify({"error": "verification failed"}), 409
    logger.error(e)
    return flask.jsonify({"error": str(e)}), 500

waitress.serve(app, host=config["host"], port=config["port"])
