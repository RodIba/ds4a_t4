import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import snowflake as sf 
import pandas as pd
from sqlalchemy import create_engine
from dash.dependencies import Input, Output
from utils import plugins_options

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
query2 = '''SELECT TD.MUNICIPALITY, EXTRACT(YEAR FROM T.CREATED_AT) AS YEAR, EXTRACT(MONTH FROM T.CREATED_AT) AS MONTH, SUM(TD.FEES_CHARGED) AS REVENUE, COUNT(RECEIPT_NO) AS TRANSACTIONS, SUM(IS_CHARGEBACK) AS CHARGEBACKS, SUM(CASE WHEN IS_CHARGEBACK = 1 then TD.FEES_CHARGED ELSE 0 END) AS REVENUE_CHARGEBACKS, COUNT(DISTINCT(T.CLIENT_ID)) AS ACTIVE_CLIENTS, COUNT(DISTINCT(T.READER_ID)) AS ACTIVE_READERS FROM TRANSACTION_DETAIL TD LEFT JOIN TRANSACTIONS T USING (RECEIPT_NO) GROUP BY 1,2,3 ORDER BY MUNICIPALITY, YEAR, MONTH;'''
q_1, q_2 = fetch_results(sfq, query1), fetch_results(sfq, query2)
print('Retrieved data is succesful')

# 3.3 Add date variable
q_1['Date'] = q_1['YEAR'].astype(str) + "-" + q_1['MONTH'].astype(str) 
q_1['Date'] = pd.to_datetime(q_1['Date'])
q_2['Date'] = q_2['YEAR'].astype(str) + "-" + q_2['MONTH'].astype(str) 
q_2['Date'] = pd.to_datetime(q_2['Date'])


#### Step 4. Set plugins options

opts_states, opts_columns, dates = plugins_options(q_1, 'STATE', 'Date')
opts_municipalities, opts_columns_mp, dates_mp = plugins_options(q_2, 'MUNICIPALITY', 'Date')

# 4.1 Set d_1 for the data of state 1 as default
d_1, d_2 = q_1.copy(), q_2.copy()
d_1 = d_1[d_1.STATE == '01']
d_2 = d_2[d_2.MUNICIPALITY == '001']


#### Step 5. Create defaults figure to show
fig_1 = go.Scatter(x = d_1['Date'],
                   y = d_1['REVENUE'],
                   name = 'REVENUE',
                   line = dict(width = 5,
                               color = 'red'))
layout = go.Layout(title = 'Time Series Plot by State',
                   hovermode = 'closest')
fig_st = go.Figure(data = [fig_1], layout = layout)

fig_2 = go.Scatter(x = d_2['Date'],
                   y = d_2['REVENUE'],
                   name = 'REVENUE',
                   line = dict(width = 5,
                               color = 'red'))

layout_2 = go.Layout(title = 'Time Series Plot by Municipality',
                   hovermode = 'closest')
fig_mp = go.Figure(data = [fig_2], layout = layout_2)


#### Step 6. Create the Dash visualization

app.layout = html.Div([
                
                # Add the prior plot
                dcc.Graph(id = 'plot_st', figure = fig_st),
                
                # Add a dropdown for different states
                html.P([
                    html.Label("Choose a State"),
                    dcc.Dropdown(id = 'opt_state', 
                                 options = opts_states,
                                 value = opts_states[0]['value'])
                        ], 
                    style = {'width': '400px',
                             'fontSize' : '20px',
                             'padding-left' : '100px',
                             'display': 'inline-block'})
                ,

                # Add a dropdown for different columns
                html.P([
                    html.Label("Choose a Column"),
                    dcc.Dropdown(id = 'opt_col_st', 
                                 options = opts_columns,
                                 value = opts_columns[0]['value'])
                        ],
                    style = {'width': '400px',
                             'fontSize' : '20px',
                             'padding-left' : '100px',
                             'display': 'inline-block'})
              ,
              # Add a time slider
                html.P([
                    html.Label("Date"),
                    dcc.RangeSlider(id = 'slider_st',
                                    marks = {i : dates[i] for i in range(0, len(dates))},
                                    min = 0,
                                    max = len(dates),
                                    value = [1,12])
                        ], style = {'width' : '80%',
                                    'fontSize' : '20px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'})
              ,

              # Add the prior plot
              dcc.Graph(id = 'plot_mp', figure = fig_mp)
              ,

              # Add a dropdown for different municipalities
              html.P([
                    html.Label("Choose a Municipality"),
                    dcc.Dropdown(id = 'opt_mp', 
                                 options = opts_municipalities,
                                 value = opts_municipalities[0]['value'])
                     ], 
                     style = {'width': '400px',
                              'fontSize' : '20px',
                              'padding-left' : '100px',
                              'display': 'inline-block'})
                ,

              # Add a dropdown for different columns
              html.P([
                     html.Label("Choose a Column"),
                     dcc.Dropdown(id = 'opt_col_mp', 
                                 options = opts_columns_mp,
                                 value = opts_columns_mp[0]['value'])
                     ], 
                     style = {'width': '400px',
                              'fontSize' : '20px',
                              'padding-left' : '100px',
                              'display': 'inline-block'})
              ,

              # Add a time slider for municipalities
              html.P([
                  html.Label("Date"),
                    dcc.RangeSlider(id = 'slider_mp',
                                    marks = {i : dates_mp[i] for i in range(0, len(dates_mp))},
                                    min = 0,
                                    max = len(dates_mp),
                                    value = [1,12])
                     ], 
                     style = {'width' : '80%',
                              'fontSize' : '20px',
                              'padding-left' : '100px',
                              'display': 'inline-block'})
                ])

#### Step 7. Callback function to update figure
@app.callback([Output('plot_st', 'figure'),
               Output('plot_mp', 'figure')], 
              [Input('opt_col_st', 'value'),
               Input('slider_st', 'value'), 
               Input('opt_state', 'value'),
               Input('opt_col_mp', 'value'),
               Input('slider_mp', 'value'), 
               Input('opt_mp', 'value')])
              

def update_figure(input1, input2, input3, input4, input5, input6):
    
    # Filter data base on date, state and municipality value
    df_st = q_1[q_1.STATE == input3]
    df_st = df_st[(df_st['Date'] > dates[input2[0]]) & (df_st['Date'] < dates[input2[1]])]
    
    df_mp = q_2[q_2.MUNICIPALITY == input6]
    df_mp = df_mp[(df_mp['Date'] > dates_mp[input5[0]]) & (df_mp['Date'] < dates_mp[input5[1]])]   
    
    # Update figures to display
    fig_st_updated = go.Scatter(x = df_st['Date'], 
                                y = df_st[input1],
                                name = input1,
                                line = dict(width = 5,
                                         color = 'red'))
    
    fig_mp_updated = go.Scatter(x = df_mp['Date'], 
                                y = df_mp[input4],
                                name = input4,
                                line = dict(width = 5,
                                            color = 'red'))

    fig_st = go.Figure(data = [fig_st_updated], layout = layout)
    fig_mp = go.Figure(data = [fig_mp_updated], layout = layout_2)
    
    return fig_st, fig_mp 


if __name__ == '__main__':
    app.run_server(debug = True)
