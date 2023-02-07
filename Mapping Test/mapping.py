from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def map_page():
    return render_template("map.html")

if __name__ == "__main__":
    app.run(debug=True)
