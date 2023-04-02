import json
import os
from flask import Flask, request
from src.logger import setup_logger
from src.util.parse_config import parse_config
from src.util.secrets.secrets import SecretsManager
from src.util.reports.reports import UndertideReport

L = setup_logger()

# Basic workflow -- for cloud run and docker call:

L.info("Starting up...")
#   Get the config_secret from mounted file secrets/config.json and determine the service to use:
#       Add config items as env variables
#       Use them to initiate the secret manager client and secrets cache
config = parse_config()
secrets_manager = SecretsManager()

app = Flask(__name__)
@app.route("/", methods=["POST"])
def build_and_send_report():
    """Builds and sends a report to the delivery method."""

    L.info("Received request!")

    # Log the request body, and then parse it
    body = request.get_json()
    L.info(f"Request body: {body}")

    # Initialize the report object
    report = UndertideReport(
        report_name=body.get("report_name"),
        report_config_jinja=body.get("report_config_jinja"),
        delivery_method=body.get("delivery_method"),
        delivery_secret_name=body.get("delivery_secret_name"),
        file_format=body.get("file_format"),
        compression=body.get("compression"),
        delivery_directory=body.get("delivery_directory"),
    )






    



# 4. Get the delivery secret from the delivery secret
# 5. Get the report config from the report config
# 6. Build the report
#    a. Find and execute the sql query (or other data pull method)
#    b. Write the report to a file
# 7. Compress the file if needed
# 8. Upload the file to the reports_archive_bucket 
# 9. Deliver the file to the delivery method

    # L.info("Checking for token...")
    # token = None
    # if 'Authorization' in request.headers:
    #     bearer_token = request.headers.get('Authorization')
    #     token = bearer_token.split(" ")[1]
    # else: 
    #     L.error("Authorization header is missing!")
    #     return "Authorization header is missing!", 401

    # if not token:
    #     L.error("Token is missing!")
    #     return "Token is missing!", 401

    # if secrets_manager.check_token(token) is False:
    #     L.error("Invalid token!")
    #     return "Invalid token!", 401
    

    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 8080)))
