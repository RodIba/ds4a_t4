import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import snowflake as sf 
from sqlalchemy import create_engine
from dash.dependencies import Input, Output

#### Step 1. Launch the application
app = dash.Dash()

#### Step 2. Establish connection to snowflake


# 2.1 Establishing connection
engine = create_engine(
  'snowflake://{user}:{password}@{account}/'.format(
    user = ,
    password = ,
    account = ,
  )
)

# 2.2 Try connection
try:
    connection = engine.connect()
    print('Succesfuly connected to Snowflake')
except:
    print('Connection failed, check credentials')
    
# 2.3 Set a cursor
con = sf.connector.connect(user = ,
                           password = ,
                           account = ,
                           warehouse=,
                           database=,
                           schema=
                           )
sfq = con.cursor()
print('Establish connection to snowflake is succesful')



#### Step 3. Retrieve data 


# 3.1 Function to fetch results as pandas dataframe 
def fetch_results(connection, query:str):
    connection.execute(query)
    return connection.fetch_pandas_all()

# 3.2 Fetch results according to query
query1 = '''The desired query'''
q_1 = fetch_results(sfq, query1)
print('Retrieved data is succesful')



#### Step 4. Set dropdown options

# 4.1 Dropdown options
features = list(q_1.columns[3:])
opts = [{'label' : i, 'value' : i} for i in features]


#### Step 5. Create a plotly figure
fig_1 = go.Scatter(x = q_1['Date'],
                   y = q_1['REVENUE'],
                   name = 'REVENUE',
                   line = dict(width = 5,
                               color = 'red'))
layout = go.Layout(title = 'Time Series Plot',
                   hovermode = 'closest')
fig = go.Figure(data = [fig_1], layout = layout)


#### Step 6. Create the Dash visualization

app.layout = html.Div([
                
                # Add the prior plot
                dcc.Graph(id = 'plot', figure = fig),
                
                # Add a dropdown for different columns
                html.P([
                    html.Label("Choose a column"),
                    dcc.Dropdown(id = 'opt', 
                                 options = opts,
                                 value = opts[0]['value'])
                        ], style = {'width': '400px',
                                    'fontSize' : '20px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'})
                ])
  

#### Step 7. Callback function to update figure
@app.callback(Output('plot', 'figure'), [Input('opt', 'value')])


def update_figure(X):
    fig_updated = go.Scatter(x = q_1['Date'], 
                             y = q_1[X],
                             name = X,
                             line = dict(width = 5,
                                         color = 'red'))
    fig = go.Figure(data = fig_updated, layout = layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug = True)
