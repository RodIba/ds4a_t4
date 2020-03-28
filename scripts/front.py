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
                           warehouse= ,
                           database= ,
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


# 4.1 Dropdown options for states
features_states = list(q_1.STATE.unique())
features_states = [x for x in features_states if x]
opts_states = [{'label' : i, 'value' : i} for i in features_states]
print(opts_states)

# 4.2 Dropdown options for columns
features_columns = list(q_1.columns[3:])
opts_columns = [{'label' : i, 'value' : i} for i in features_columns]
print(opts_columns)

# 4.3 Time Slider options 
q_1['Date'] = q_1['YEAR'].astype(str) + "-" + q_1['MONTH'].astype(str) 
dates = list(q_1['Date'].unique())
dates = [x for x in dates if x]
q_1['Date'] = pd.to_datetime(q_1['Date'])

# 4.4 Set d_1 for the data of state 1 as default
d_1 = q_1.copy()
d_1 = d_1[d_1.STATE == '01']



#### Step 5. Create the default figure to show
fig_1 = go.Scatter(x = d_1['Date'],
                   y = d_1['REVENUE'],
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
                
                # Add a dropdown for different states
                html.P([
                    html.Label("Choose a State"),
                    dcc.Dropdown(id = 'opt_state', 
                                 options = opts_states,
                                 value = opts_states[0]['value'])
                        ], style = {'width': '400px',
                                    'fontSize' : '20px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'})
                ,

                # Add a dropdown for different columns
                html.P([
                    html.Label("Choose a Column"),
                    dcc.Dropdown(id = 'opt_col', 
                                 options = opts_columns,
                                 value = opts_columns[0]['value'])
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
                                    value = [1,12])
                        ], style = {'width' : '80%',
                                    'fontSize' : '20px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'})

                ])

#### Step 7. Callback function to update figure
@app.callback(Output('plot', 'figure'), 
             [Input('opt_col', 'value'),
              Input('slider', 'value'), 
              Input('opt_state', 'value')])


def update_figure(input1, input2, input3):
    
    # Filter data base on date and state value
    df = q_1[q_1.STATE == input3]
    print(df.head())
    df = df[(df['Date'] > dates[input2[0]]) & (df['Date'] < dates[input2[1]])]
    print(df.head())
    
    # Update figure to display
    fig_updated = go.Scatter(x = df['Date'], 
                             y = df[input1],
                             name = input1,
                             line = dict(width = 5,
                                         color = 'red'))
    fig = go.Figure(data = fig_updated, layout = layout)
    return fig


if __name__ == '__main__':
    app.run_server(debug = True)
