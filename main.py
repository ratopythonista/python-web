import os
import base64
from io import BytesIO

from PIL import Image

from loguru import logger

from dash import Dash, html, dcc, callback, Output, Input, State, get_asset_url
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd

portraits = [' '.join(filename.replace(".jpg", "").split("_")[1:]).capitalize() for filename in os.listdir("assets")]

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Character 1"),
    dcc.Dropdown(portraits, id='char-1'),
    html.H1("Character 2"),
    dcc.Dropdown(["----", *portraits], id='char-2'),
    html.H1("Character 3"),
    dcc.Dropdown(["----", *portraits], id='char-3'),
    html.Img(id="preview"),
    html.Button("Download", id="btn-download"),
    dcc.Download(id="download-image")
])


class Preview:
    def __init__(self) -> None:
        self.image_name = "time.png"
        self.images = [None, None, None]
        self.posixes: tuple = ((0,0), (48, 15), (96, 30))

    def build_preview(self):
        size = (68, 70)
        image_size = size

        images = [value for value in self.images if value != None]

        if len(images) == 3:
            image_size = (size[0] + self.posixes[-1][0], size[1] + self.posixes[-1][1])
        elif len(images) == 2:
            image_size = (size[0] + self.posixes[-2][0], size[1] + self.posixes[-2][1])            
        new_image = Image.new('RGBA', image_size, (0, 0, 0, 0))

        posixes = self.posixes[:len(images)][::-1]
        for index, image in enumerate(images[::-1]):
            new_image.paste(Image.open(f".{image}"), posixes[index])

        self.image_name = "-".join([image.split("/")[-1].replace(".jpg", "").replace("SG_", "") for image in images]) + ".png"
        return new_image

preview = Preview()


@callback(
    Output("download-image", "data"),
    Input("btn-download", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    buffered = BytesIO()
    image = preview.build_preview()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return dict(base64=True, content=img_str.decode(), filename=preview.image_name, type='image/png')


@callback(
    Output('preview', 'src', allow_duplicate=True),
    Input('char-1', 'value'),
    prevent_initial_call=True
)
def img_char_1(character: str):
    preview.images[0] = (get_asset_url(f'SG_{character.lower().replace(" ", "_")}.jpg'))
    return preview.build_preview() 

@callback(
    Output('preview', 'src', allow_duplicate=True),
    Input('char-2', 'value'),
    prevent_initial_call=True
)
def img_char_2(character: str):
    preview.images[1] = None if character == "----" else get_asset_url(f'SG_{character.lower().replace(" ", "_")}.jpg')
    return preview.build_preview()

@callback(
    Output('preview', 'src', allow_duplicate=True),
    Input('char-3', 'value'),
    prevent_initial_call=True
)
def img_char_3(character: str):
    preview.images[2] = None if character == "----" else get_asset_url(f'SG_{character.lower().replace(" ", "_")}.jpg')
    return preview.build_preview()


if __name__ == '__main__':
    app.run(debug=True)
