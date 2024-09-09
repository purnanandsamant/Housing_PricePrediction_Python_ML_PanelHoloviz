import panel as pn
import pickle
import json
import numpy as np
import pandas as pd
import param
import base64
import warnings

warnings.filterwarnings('ignore')

pn.extension('tabulator')
pn.extension(loading_spinner='petal', loading_color='#00aa41')

def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

class ImgBackground(pn.reactive.ReactiveHTML):
    object = param.Parameter()
    img_base64 = param.String()
    
    _template = """
    <div id="pn-component" style="height:100%; width:100%; position:relative;">
        <div id="background" style="background-image: url(data:image/jpeg;base64,${img_base64});
                                    background-repeat: no-repeat;
                                    background-attachment: scroll;
                                    background-position: center center;
                                    background-size: cover;
                                    filter: blur(2px);
                                    opacity: 0.8;
                                    height:100%;
                                    width:100%;
                                    position:absolute;
                                    top:0;
                                    left:0;
                                    z-index:-1;">
        </div>
        <div id="content" style="position:relative; z-index:1;">
            ${object}
        </div>
    </div>
    """
    
# Path to the local background image
background_image_path = "./background.jpg"

# Convert image to base64
img_base64 = image_to_base64(background_image_path)

# Load data and model
X = pd.read_excel("./data.xlsx")
X['total_sqft'] = X['total_sqft'].astype(int)

sqft_list = X['total_sqft'].unique().tolist()
bhk_list = X['bhk'].unique().tolist()
bath_list = X['bath'].unique().tolist()

# Define the threshold
threshold_sqft = 400

# Create a new list with values above the threshold
sqft_list = [x for x in sqft_list if x >= threshold_sqft]

minsqft = min(sqft_list)
maxsqft = max(sqft_list)

def load_saved_artifacts():
    global datacolumns, locations, model
    
    with open('columns.json', 'r') as f:
        datacolumns = json.load(f)['data_columns']
        locations = datacolumns[4:]
    
    with open('./banglore_home_prices_model.pickle', 'rb') as file:
        model = pickle.load(file)

load_saved_artifacts()

# Building widgets
location_select = pn.widgets.Select(name='Location', options=locations, width=300, value=locations[0], align='center')
bedroom_select = pn.widgets.Select(name='Bedrooms', options=[2,3,4], width=300, value=2, align='center')
bathroom_select = pn.widgets.Select(name='Bathrooms', options=[2,3], width=300, value=3, align='center')
sqft_slider = pn.widgets.Select(name='Square Feet', options=[2000,3000,4000], width=300, value=2000, align='center')
# sqft_slider = pn.widgets.IntSlider(name='Square Feet', start=minsqft, end=maxsqft, step=100, value=3000, width=300, align='center')

@pn.depends(location_select, bedroom_select, bathroom_select, sqft_slider)
def get_estimated_price(location, bhk, bath, sqft):
    try:
        loc_index = datacolumns.index(location.lower())
    except:
        loc_index = -1

    x = np.zeros(len(datacolumns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index >= 0:
        x[loc_index] = 1
    
    output = round(model.predict([x])[0], 2)
    
    return pn.indicators.Number(
        name="Estimated House Price",
        value=round(output/100,2),
        format='{value} Crore Rupees',
        title_size='24pt',
        font_size='36pt',
        styles={
            'background-color': 'rgba(95, 158, 160, 0.7)',
            'border': '',
            'color': 'white',
            'padding': '10px 20px',
            'text-align': 'center',
            'text-decoration': 'none',
            'font-family': 'tahoma',
            'margin': '20px auto',
            'cursor': 'default',
            'border-radius': '10px',
            'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'width': '300px'
        }
    )

component1 = pn.Column(
    pn.Row(pn.Spacer(width=300),pn.pane.Markdown("# Housing Price Prediction Model", styles={
                'background-color': '#F0FFFF',
                'border': '',
                'color': 'black',
                'padding': '5px 5px',
                'text-align': 'center',
                'text-decoration': 'none',
                'font-family': 'tahoma',
                'margin': '10px auto',
                'cursor': 'default',
                'font-size': '20px',
                'font-weight': 'bold',
            })),
    pn.Row(
        pn.Column(
            pn.pane.Markdown("## Select a location", styles={
                'background-color': '#F0FFFF',
                'border': '',
                'color': 'black',
                'padding': '5px 5px',
                'text-align': 'center',
                'text-decoration': 'none',
                'font-family': 'tahoma',
                'margin': '10px auto',
                'cursor': 'default',
                'font-size': '10px',
                'font-weight': 'bold',
            }),
            pn.Row(location_select, width=300, align='center'),
            pn.Spacer(height=30),
            pn.pane.Markdown("## Select number of bedrooms", styles={
                'background-color': '#F0FFFF',
                'border': '',
                'color': 'black',
                'padding': '5px 5px',
                'text-align': 'center',
                'text-decoration': 'none',
                'font-family': 'tahoma',
                'margin': '10px auto',
                'cursor': 'default',
                'font-size': '10px',
                'font-weight': 'bold',
            }),
            pn.Row(bedroom_select, width=300, align='center'),
            pn.Spacer(height=30),
            pn.pane.Markdown("## Select number of bathrooms", styles={
                'background-color': '#F0FFFF',
                'border': '',
                'color': 'black',
                'padding': '5px 5px',
                'text-align': 'center',
                'text-decoration': 'none',
                'font-family': 'tahoma',
                'margin': '10px auto',
                'cursor': 'default',
                'font-size': '10px',
                'font-weight': 'bold',
            }),
            pn.Row(bathroom_select, width=300, align='center'),
            pn.Spacer(height=30),
            pn.pane.Markdown("## Select square feet using the slider", styles={
                'background-color': '#F0FFFF',
                'border': '',
                'color': 'black',
                'padding': '5px 5px',
                'text-align': 'center',
                'text-decoration': 'none',
                'font-family': 'tahoma',
                'margin': '10px auto',
                'cursor': 'default',
                'font-size': '10px',
                'font-weight': 'bold',
            }),
            pn.Row(sqft_slider, width=300, align='center'),
            align='center',
            width=600
        ),
        pn.Column(
            pn.pane.Markdown("## Predicted Price", styles={
                'background-color': '#F0FFFF',
                'border': '',
                'color': 'black',
                'padding': '5px 5px',
                'text-align': 'center',
                'text-decoration': 'none',
                'font-family': 'tahoma',
                'margin': '10px auto',
                'cursor': 'default',
                'font-size': '10px',
                'font-weight': 'bold',
            }),
            pn.Row(get_estimated_price, width=300, align='center'),
            align='center',
            width=600
        )
    ), 
    name="Housing Price Prediction"
)

svg_background = ImgBackground(object=component1, height=800, img_base64=img_base64)

svg_background.servable()

