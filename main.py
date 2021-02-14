from io import BytesIO
from flask import Flask, render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from PIL import Image
import numpy as np
from itertools import islice
import base64

SENSITIVITY = 30

app = Flask(__name__)
app.secret_key = b'mytopsecretkey'


class UploadForm(FlaskForm):
    image = FileField(validators=[FileRequired()])


@app.route('/', methods=['GET', 'POST'])
def index():

    form = UploadForm()

    if form.validate_on_submit():

        # save the uploaded image in memory
        image_buffer = BytesIO()
        f = form.image.data
        f.save(image_buffer)

        # use Pillow and numpy to analyse
        img = Image.open(image_buffer)

        img_data = np.asarray(img)
        img_data_agg = img_data // SENSITIVITY * SENSITIVITY  # aggregate near colors

        # reshape the array to flatten it to pixel and count the unique occurrence
        unique_pixels, counts = np.unique(img_data_agg.reshape(-1, img_data_agg.shape[2]), axis=0, return_counts=True)

        colors = []
        for pixel in unique_pixels:
            colors.append(html_color(pixel))

        color_dict = dict(zip(colors, counts))
        colors_sorted = dict(sorted(color_dict.items(), key=lambda item: item[1], reverse=True))

        main_colors = dict(islice(colors_sorted.items(), 10))

        # base64 encode image and decode to string and pass it to the html template
        image_str = base64.b64encode(image_buffer.getvalue()).decode()
        return render_template('index.html', form=form, colors=main_colors, image_str=image_str)

    return render_template('index.html', form=form)


def html_color(list_r_g_b):
    """Turns a list with RGB value in to html color code """
    html_color_code = f'#{list_r_g_b[0]:02x}{list_r_g_b[1]:02x}{list_r_g_b[2]:02x}'
    return html_color_code


if __name__ == '__main__':
    app.run(debug=True)
