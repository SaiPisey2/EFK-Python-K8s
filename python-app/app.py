import logging
import re
import json
import random
import os
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
import resource_user as eater

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key in production

# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Disable Flask's default request logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Define a custom JSON formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.msg,
            "time": self.formatTime(record, self.datefmt),
            "logger": record.name,
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcname": record.funcName,
            "request": {
                "method": request.method,
                "url": request.url,
                "remote_addr": request.remote_addr,
                "user_agent": str(request.user_agent)
            }
        }
        if record.args:
            log_record['message'] = log_record['message'] % record.args
        return json.dumps(log_record)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler with JSON formatting
console_handler = logging.StreamHandler()
console_handler.setFormatter(JSONFormatter())
logger.addHandler(console_handler)

# File handler to write logs to logfile.log
file_handler = logging.FileHandler('logs/logfile.log')
file_handler.setFormatter(JSONFormatter())
logger.addHandler(file_handler)


@app.before_request
def log_request_info():
    logger.info(f"Request received")

@app.after_request
def log_response_info(response):
    logger.info(f"Response sent with status: {response.status_code}")
    return response

# First block routes

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # Generate a random username like USER1, USER2, etc.
    username = f'USER{random.randint(1, 100)}'
    # password = request.form['password']

    # Randomly decide success or failure
    if random.choice([True,True, False]):
        logger.info('Login successful for user: %s', username)
        # if is_weak_password(password):
        #     logger.warning('Weak password used by user: %s', username)
        return {"status": "login_success", "user": username}, 200
    else:
        logger.warning('Login failed for user: %s', username)
        return {"status": "login_failed", "user": username}, 401

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/second_level_auth')
def second_level_auth():
    return render_template('second_level_auth.html')

# Second block routes

res_bp = Blueprint("resource_user", __name__, url_prefix="/resource_user")

@app.route("/random_client_side_error")
def rcse():
    return {"status": "client_failure"}, random.randrange(400, 418)

@app.route("/random_server_side_error")
def rsse():
    return {"status": "server_failure"}, random.randrange(500, 508)

@app.route("/unhandled_exception")
def ue():
    raise Exception("Unhandled exception!")

@res_bp.route("/high_cpu_low_mem")
def hclm():
    n = request.args.get("n", type=int, default=1)
    result = eater.high_cpu_low_mem(n)
    return {"n": n, "result": result}

@res_bp.route("/high_cpu_high_mem")
def hchm():
    n = request.args.get("n", type=int, default=1)
    result = eater.high_cpu_high_mem(n)
    return {"n": n, "result": result}

@res_bp.route("/low_cpu_low_mem")
def lclm():
    n = request.args.get("n", type=int, default=1)
    result = eater.low_cpu_low_mem(n)
    return {"n": n, "result": result}

@res_bp.route("/med_cpu_high_mem")
def mchm():
    n = request.args.get("n", type=int, default=1)
    result = eater.med_cpu_high_mem(n)
    return {"n": n, "result": result}

app.register_blueprint(res_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
