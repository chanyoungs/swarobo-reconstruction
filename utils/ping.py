import time
import dash
from dash import dcc, html
import plotly.graph_objects as go
from ping3 import ping
from collections import deque
import threading

# Function to ping addresses and get response time
def ping_address(address):
    response = ping(address)
    return response * 1000 if response is not None else None  # Convert to ms, None if unreachable

# Create the dash app
app = dash.Dash(__name__)

# Global variables to store trace data
traces = {}
addresses = []

# Layout of the web app
app.layout = html.Div([
    html.H1("Live Ping Response Times"),
    dcc.Graph(id="live-graph"),
    dcc.Interval(
        id="graph-update",
        interval=1000,  # Update every second
        n_intervals=0
    )
])

# Function to get traces for each address
def get_traces():
    global traces
    data = []
    for address in addresses:
        trace_data = traces.get(address, deque(maxlen=100))
        data.append(go.Scatter(x=[t[0] for t in trace_data],
                               y=[t[1] for t in trace_data],
                               mode='lines+markers',
                               name=address))
    return data

# Callback function to update the graph live
@app.callback(
    dash.dependencies.Output('live-graph', 'figure'),
    dash.dependencies.Input('graph-update', 'n_intervals')
)
def update_graph(n_intervals):
    global traces
    current_time = time.time()
    
    # Ping each address and update the trace data
    for address in addresses:
        response_time = ping_address(address)
        if address not in traces:
            traces[address] = deque(maxlen=100)
        traces[address].append((current_time, response_time))
    
    # Update the graph with new data
    return {
        'data': get_traces(),
        'layout': go.Layout(
            title="Live Ping Response Times",
            xaxis={'title': 'Time'},
            yaxis={'title': 'Response Time (ms)'},
            showlegend=True
        )
    }

# Function to start the app with addresses
def start_app(input_addresses):
    global addresses
    addresses = [addr.strip() for addr in input_addresses.split(',')]
    
    # Start the Dash app
    app.run_server(debug=True, use_reloader=False)

# User input: List of addresses to ping
# input_addresses = input("Enter addresses to ping (separated by commas): ")
input_addresses = "google.com, 172.16.1.58, 172.16.1.0"
start_app(input_addresses)


