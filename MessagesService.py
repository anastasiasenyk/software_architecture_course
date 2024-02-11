from flask import Flask

app = Flask(__name__)


@app.route('/get_static_message', methods=['GET'])
def get_static_message():
    # Return a static text
    return 'not implemented yet'


if __name__ == '__main__':
    app.run(port=5002)
