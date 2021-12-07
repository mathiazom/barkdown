import os
from flask import Flask, render_template
from markdown_generator import generate_markdown

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("output.html", output=generate_markdown().split("\n"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
