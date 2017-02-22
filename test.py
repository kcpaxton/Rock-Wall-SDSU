from flask import Flask, render_template
import os


app = Flask(__name__)

@app.route('/')

def home():
	return render_template('login.html')

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)