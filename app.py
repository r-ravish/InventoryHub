from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/loading')
def loading():
    return render_template("loading.html")

@app.route('/inventory')
def inventory():
    return render_template("inventory.html")

@app.route('/inventory/add-item')
def item_form():
    return render_template("item_form.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
