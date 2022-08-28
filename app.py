from uuid import uuid4

from flask import Flask, render_template, request

from main import main, Namespace


app = Flask('My app')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def process():
    image_name = 'static/' + str(uuid4()) + '.png'
    ns = Namespace(playlist=request.form['playlist'],
                   shape=(int(request.form['rows']), int(request.form['cols'])),
                   image_size=int(request.form['size']),
                   output=image_name)
    main(ns)
    return render_template('show_image.html', image_url=image_name)


if __name__ == '__main__':
    app.run(port=8888)
