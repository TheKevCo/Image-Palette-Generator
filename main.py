from base64 import b64encode
from flask import Flask, render_template, request, redirect, url_for, Response
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)


# https://flask-wtf.readthedocs.io/en/latest/form/#module-flask_wtf.file

class UploadForm(FlaskForm):
    file = FileField(validators=[FileRequired()])


@app.route("/", methods=['GET', 'POST'])
def home():
    form = UploadForm()
    images = Img.query.all()
    image_data = images[0]
    image = b64encode(image_data.img).decode("utf-8")
    if form.validate_on_submit():
        new_img = form.file.data
        filename = secure_filename(new_img.filename)
        mimetype = new_img.mimetype
        input_img = Img(img=new_img.read(), name=filename, mimetype=mimetype)
        db.session.add(input_img)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('index.html', form=form, image_data=image_data, image=image)


@app.route("/true")
def test():
    images = Img.query.all()
    image_data = images[0]

    return Response(image_data.img, mimetype=image_data.mimetype)


if __name__ == "__main__":
    app.run(debug=True)
