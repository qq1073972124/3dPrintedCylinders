from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots

voxelD=0.03228 #voxel diameter in mm
base = 2.45 #base height in mm
thickness=51/284 #layer thickness in mm

def importData(fileName):
    df = pd.read_csv(fileName)
    cylinder = pd.DataFrame()
    cylinder['Diameter [mm]'] = df.iloc[:,2]
    #convert voxel coordinates to mm
    cylinder['Center x [mm]'] = voxelD * df.iloc[:,3]
    cylinder['Center y [mm]'] = voxelD * df.iloc[:,4]
    cylinder['Center z [mm]'] = voxelD * df.iloc[:,5] - base
    #calculate layer number
    cylinder['Layer#'] = np.ceil(cylinder['Center z [mm]'] / thickness).astype(int)
    #porosities higher than layer 284 belong to layer 284
    cylinder['Layer#'] = np.where(cylinder['Layer#'] > 284, 284, cylinder['Layer#'])
    return cylinder

def sortData(cylinder):
    #count number of porosities in each layer
    a = cylinder[['Layer#','Diameter [mm]']].groupby('Layer#').count()
    b = [0] * 284
    for i in range(284):
        if i+1 in a.index:
            b[i] = a.loc[i+1].values[0]
    layerInfo = pd.DataFrame(np.arange(1,285), columns=['Layer#'])
    layerInfo['Porosity#'] = b
    #find maximum porosity diameter in each layer
    c = cylinder[['Layer#','Diameter [mm]']].groupby('Layer#').max()
    d = [0] * 284
    for i in range(284):
        if i+1 in c.index:
            d[i] = c.loc[i+1].values[0]
    layerInfo['maxD'] = d
    #classify layers as pass or fail
    layerInfo['#Fail'] = np.where(layerInfo['Porosity#'] > 5, 'Fail', 'Pass')
    layerInfo['DFail'] = np.where(layerInfo['maxD'] > 0.2, 'Fail', 'Pass')
    layerInfo['Fail'] = np.where((layerInfo['#Fail'] == 'Fail')|(layerInfo['DFail'] == 'Fail') , 'Fail', 'Pass')
    return layerInfo

# Import data
cylinder1 = importData('cylinder1.csv')
cylinder2 = importData('cylinder2.csv')

# Sort data
layerInfo1 = sortData(cylinder1)
layerInfo2 = sortData(cylinder2)

# Create histograms
his1 = make_subplots(rows=1, cols=2,
                     subplot_titles=('Cylinder 1', 'Cylinder 2'),
                     y_title='Frequency', shared_yaxes=True)
his1.add_trace(px.histogram(cylinder1, x='Diameter [mm]', nbins=40, range_x=(0.08,0.43)).data[0], row=1, col=1)
his1.add_trace(px.histogram(cylinder2, x='Diameter [mm]', nbins=40, range_x=(0.08,0.43)).data[0], row=1, col=2)
his1['layout']['xaxis']['title']='Porosity Diameter [mm]'
his1['layout']['xaxis2']['title']='Porosity Diameter [mm]'

# Create bar charts
barn1 = px.bar(layerInfo1, x='Layer#', y='Porosity#',
               color='#Fail', color_discrete_map={'Pass':'green', 'Fail':'red'},
               title='Cylinder 1', range_y=(0, 16)
               )
barn1.update_layout(yaxis_title='Number of Porosities', xaxis_title='Layer Number',
                    legend_title_text='', height=500, width=648,title_x=0.5
                    )

barn2 = px.bar(layerInfo2, x='Layer#', y='Porosity#',
               color='#Fail', color_discrete_map={'Pass':'green', 'Fail':'red'},
               title='Cylinder 2', range_y=(0, 16)
               )
barn2.update_layout(yaxis_title='Number of Porosities', xaxis_title='Layer Number',
                    legend_title_text='', height=500, width=648,title_x=0.5
                    )

bard1 = px.bar(layerInfo1, x='Layer#', y='maxD', 
               color='DFail', color_discrete_map={'Pass':'green', 'Fail':'red'},
               title='Cylinder 1', range_y=(0.08, 0.43)
               )
bard1.update_layout(yaxis_title='Maximum Diameter [mm]', xaxis_title='Layer Number',
                    legend_title_text='', height=500, width=648,title_x=0.5
                    )

bard2 = px.bar(layerInfo2, x='Layer#', y='maxD', 
               color='DFail', color_discrete_map={'Pass':'green', 'Fail':'red'},
               title='Cylinder 2', range_y=(0.08, 0.43)
               )
bard2.update_layout(yaxis_title='Maximum Diameter [mm]', xaxis_title='Layer Number',
                    legend_title_text='', height=500, width=648,title_x=0.5
                    )

e =[1] * 284
dl1 = px.bar(layerInfo1, x=e, y='Layer#', orientation='h',
             color='Fail', color_discrete_map={'Pass':'green', 'Fail':'red'},
             range_y=(1,284), range_x=(0,0.5)
             )
dl1.update_layout(title_text='Cylinder 1', 
                  title_x=0.5, xaxis_visible=False, yaxis_title='Layer Number',
                  bargap=0, height=1600, width=648, legend_title_text=''
                  )
dl1.update_yaxes(tick0=5, dtick=5)

dl2 = px.bar(layerInfo2, x=e, y='Layer#', orientation='h',
             color='Fail', color_discrete_map={'Pass':'green', 'Fail':'red'},
             range_y=(1,284), range_x=(0,0.5)
             )
dl2.update_layout(title_text='Cylinder 2', 
                  title_x=0.5, xaxis_visible=False, yaxis_title='Layer Number',
                  bargap=0, height=1600, width=648, legend_title_text=''
                  )
dl2.update_yaxes(tick0=5, dtick=5)

# Create 3d scatter plots
sca1 = px.scatter_3d(cylinder1, x='Center x [mm]', y='Center y [mm]', z='Center z [mm]',
                    color='Diameter [mm]', color_continuous_midpoint=0.175,
                    range_color=[0.08, 0.43], size='Diameter [mm]',
                    size_max=20, opacity=1, title='Cylinder 1'
                    )
sca1.update_layout(scene = dict(xaxis_title='x [mm]', yaxis_title='y [mm]', zaxis_title='z [mm]'),
                   width=648, height=820, title_x=0.5
)

sca2 = px.scatter_3d(cylinder2, x='Center x [mm]', y='Center y [mm]', z='Center z [mm]',
                    color='Diameter [mm]', color_continuous_midpoint=0.175,
                    range_color=[0.08, 0.43], size='Diameter [mm]',
                    size_max=20, opacity=1, title='Cylinder 2'
                    )
sca2.update_layout(scene = dict(xaxis_title='x [mm]', yaxis_title='y [mm]', zaxis_title='z [mm]'),
                   width=648, height=820, title_x=0.5
)

# Initialize the app
app = Dash(
    name = '3D Printed Cylinders',
    external_stylesheets=[dbc.themes.FLATLY]
)

# App layout
app.layout = dbc.Container([
    html.Br(),
    html.Div(children='3D Printed Cylinders', style={'fontSize': 24, 'textAlign': 'center'}),
    html.Br(),
    dcc.Tabs([
        dcc.Tab(label='Data Table', children=[
            html.Br(),
            dcc.RadioItems(options=['Cylinder 1', 'Cylinder 2'], value='Cylinder 1', id='selectTable'),
            html.Br(),
            dash_table.DataTable(data= [], id = 'table1', page_size=15)
        ]),
        dcc.Tab(label='Histograms', children=[
            dcc.Graph(figure = his1, id='his1')
        ]),
        dcc.Tab(label = 'Bar Charts', children = [
            html.Br(),
            dcc.RadioItems(options=['Porosity Number', 'Maximum Diameter'], value='Porosity Number', id='selectBar'),
            dcc.Graph(figure={}, id='bar1', style={'display': 'inline-block'}),
            dcc.Graph(figure={}, id='bar2', style={'display': 'inline-block'})
        ]),
        dcc.Tab(label='Defective Layers', children=[
            html.Br(),
            dcc.Graph(figure = dl1, style={'display': 'inline-block'}),
            dcc.Graph(figure = dl2, style={'display': 'inline-block'})
        ]),
        dcc.Tab(label = 'Scatter Plots', children = [
            dcc.Graph(figure=sca1, id='sca1', style={'display': 'inline-block'}),
            dcc.Graph(figure=sca2, id='sca2', style={'display': 'inline-block'})
        ])   
    ])
])

# Callbacks
@callback(
    Output(component_id='table1', component_property='data'),
    Input(component_id='selectTable', component_property='value'),
)
def updateTable(selectTable):
    if selectTable == 'Cylinder 1':
        return cylinder1.round(3).to_dict('records')
    else:
        return cylinder2.round(3).to_dict('records')

@callback(
    Output(component_id='bar1', component_property='figure'),
    Output(component_id='bar2', component_property='figure'),
    Input(component_id='selectBar', component_property='value')
)
def updateBar(selectBar):
    if selectBar == 'Porosity Number':
        return barn1, barn2
    else:
        return bard1, bard2

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
