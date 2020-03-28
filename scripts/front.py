import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import snowflake as sf 
import pandas as pd
from sqlalchemy import create_engine
from dash.dependencies import Input, Output

# Based on https://towardsdatascience.com/a-gentle-invitation-to-interactive-visualization-with-dash-a200427ccce9

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
query1 = '''SELECT TD.STATE, EXTRACT(YEAR FROM T.CREATED_AT) AS YEAR, EXTRACT(MONTH FROM T.CREATED_AT) AS MONTH, SUM(TD.FEES_CHARGED) AS REVENUE, COUNT(RECEIPT_NO) AS TRANSACTIONS, SUM(IS_CHARGEBACK) AS CHARGEBACKS, SUM(CASE WHEN IS_CHARGEBACK = 1 then TD.FEES_CHARGED ELSE 0 END) AS REVENUE_CHARGEBACKS, COUNT(DISTINCT(T.CLIENT_ID)) AS ACTIVE_CLIENTS, COUNT(DISTINCT(T.READER_ID)) AS ACTIVE_READERS FROM TRANSACTION_DETAIL TD LEFT JOIN TRANSACTIONS T USING (RECEIPT_NO) GROUP BY 1,2,3 ORDER BY STATE, YEAR, MONTH;'''
q_1 = fetch_results(sfq, query1)
print('Retrieved data is succesful')


#### Step 4. Set dropdown options

# 4.1 Dropdown options
features = list(q_1.columns[3:])
opts = [{'label' : i, 'value' : i} for i in features]

# 4.2 Time Slider options 
q_1['Date'] = q_1['YEAR'].astype(str) + "-" + q_1['MONTH'].astype(str) 
dates = q_1['Date'].unique()
q_1 = q_1[q_1.STATE == '01']
q_1['Date'] = pd.to_datetime(q_1['Date'])


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
                ,

                # Add a time slider
                html.P([
                    html.Label("Date"),
                    dcc.RangeSlider(id = 'slider',
                                    marks = {i : dates[i] for i in range(0, len(dates))},
                                    min = 0,
                                    max = len(dates),
                                    value = [1,6])
                        ], style = {'width' : '80%',
                                    'fontSize' : '20px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'})
                ])

#### Step 7. Callback function to update figure
@app.callback(Output('plot', 'figure'), [Input('opt', 'value'),Input('slider', 'value')])


def update_figure(input1, input2):
    print("Values of slider", input2, "\n", "Types of sliders", type(input2))

    q_2 = q_1[(q_1['Date'] > dates[input2[0]]) & (q_1['Date'] < dates[input2[1]])]
    fig_updated = go.Scatter(x = q_2['Date'], 
                             y = q_2[input1],
                             name = input1,
                             line = dict(width = 5,
                                         color = 'red'))
    fig = go.Figure(data = fig_updated, layout = layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug = True)
