from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/druga')
def druga_stran():
    return render_template('druga_stran.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)