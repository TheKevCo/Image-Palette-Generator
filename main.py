from base64 import b64encode
from flask import Flask, render_template, request, redirect, url_for, Response
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
import os
from io import BytesIO
from PIL import Image
from numpy import asarray
import pandas as pd

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


# https://www.youtube.com/watch?v=Ljo46Hsb-0Q
def rgb_to_hex(rgb_list):
    return '#' + '{:x}{:x}{:x}'.format(rgb_list[0], rgb_list[1], rgb_list[2])


@app.route("/", methods=['GET', 'POST'])
def home():
    form = UploadForm()
    images = Img.query.all()
    if images:
        image_data = images[0]
        image = b64encode(image_data.img).decode("utf-8")

        # above is for displaying the image on the web page

        #  -------------------------------------- code for making hexcode -------------------------------#
        an_image = BytesIO(image_data.img)
        the_img = Image.open(an_image)
        hex_list = []
        data = asarray(the_img)
        for dimension in data:
            for i in range(len(dimension)):
                hex_list.append(rgb_to_hex(dimension[i]))
        hex_dataframe = pd.DataFrame({'HexCodes': hex_list})
        sum_hex = hex_dataframe.count()
        top_10 = hex_dataframe['HexCodes'].value_counts().reset_index().head(10)
        top_10['Percentage'] = (top_10['HexCodes'] / sum_hex.values) * 100
        top_10_dict = top_10.to_dict()
        top_10_hex = []
        top_10_hexper = []
        for i in range(10):
            top_10_hex.append(top_10_dict['index'][i])
            top_10_hexper.append(round(top_10_dict['Percentage'][i], 2))
    #  -------------------------------------- code for making hexcode -------------------------------#
    if form.validate_on_submit():
        new_img = form.file.data
        filename = secure_filename(new_img.filename)
        mimetype = new_img.mimetype
        input_img = Img(img=new_img.read(), name=filename, mimetype=mimetype)
        db.session.add(input_img)
        db.session.commit()
        return redirect(url_for('home'))
    if images:
        return render_template('index.html', form=form, image_data=image_data, image=image, hexname=top_10_hex,
                           hexper=top_10_hexper)
    else:
        return render_template('index.html', form=form)


@app.route("/true")
def test():
    images = Img.query.all()
    image_data = images[0]

    return Response(image_data.img, mimetype=image_data.mimetype)


@app.route("/delete/")
def delete_post():
    post_to_delete = Img.query.get(1)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
