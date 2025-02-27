import time
import dash
from dash import dcc, html
import plotly.graph_objects as go
from ping3 import ping
from collections import deque
import pandas as pd
import threading

# Create the Dash app
app = dash.Dash(__name__)

# Global variables to store trace data
traces = {}
addresses = []
ping_thread = None
ping_interval = 1000  # Default ping interval is 1000ms (1 second)

# Layout of the web app
app.layout = html.Div([
    html.H1("Live Ping Response Times"),
    
    # User input for addresses
    html.Div([
        html.Label("Enter Addresses to Ping (comma-separated):"),
        dcc.Input(id="address-input", type="text", placeholder="e.g., google.com, 8.8.8.8"),
        html.Button("Start Ping", id="start-ping", n_clicks=0),
        html.Button("Stop Ping", id="stop-ping", n_clicks=0),
    ]),
    
    # Ping interval input
    html.Div([
        html.Label("Ping Interval (ms):"),
        dcc.Input(id="ping-interval-input", type="number", value=ping_interval),
    ]),
    
    # CSV actions
    html.Div([
        html.Button("Save Ping Data", id="save-ping", n_clicks=0),
        html.Button("Load Ping Data", id="load-ping", n_clicks=0),
    ]),
    
    # Graph for live plot
    dcc.Graph(id="live-graph"),
    
    # Interval component for periodic updates
    dcc.Interval(
        id="graph-update",
        interval=ping_interval,  # This will be dynamically updated
        n_intervals=0
    )
])

# Function to ping addresses and get response time
def ping_address(address):
    response = ping(address)
    return response * 1000 if response is not None else None  # Convert to ms, None if unreachable

# Function to save ping data as a CSV file
def save_ping_data():
    global traces
    # Convert trace data into a pandas DataFrame
    data = {}
    for address, trace_data in traces.items():
        data[address] = [t[1] for t in trace_data]
    
    df = pd.DataFrame(data)
    df.to_csv("ping_data.csv", index_label="Timestamp")

# Function to load ping data from a CSV file
def load_ping_data():
    global traces
    try:
        df = pd.read_csv("ping_data.csv", index_col="Timestamp")
        traces = {col: deque(zip(df.index, df[col]), maxlen=100) for col in df.columns}
    except FileNotFoundError:
        print("No saved ping data found.")

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

# Function to ping addresses in a separate thread
def ping_addresses():
    global traces, addresses, ping_interval
    start_time = time.time()
    
    while True:
        current_time = time.time() - start_time
        for address in addresses:
            response_time = ping_address(address)
            if address not in traces:
                traces[address] = deque(maxlen=100)
            traces[address].append((current_time, response_time))
        
        time.sleep(ping_interval / 1000)  # Sleep for the specified ping interval

# Callback for updating the graph
@app.callback(
    dash.dependencies.Output('live-graph', 'figure'),
    dash.dependencies.Input('graph-update', 'n_intervals')
)
def update_graph(n_intervals):
    return {
        'data': get_traces(),
        'layout': go.Layout(
            title="Live Ping Response Times",
            xaxis={'title': 'Time'},
            yaxis={'title': 'Response Time (ms)'},
            showlegend=True
        )
    }

# Start ping callback
@app.callback(
    dash.dependencies.Output('start-ping', 'n_clicks'),
    dash.dependencies.Output('stop-ping', 'n_clicks'),
    dash.dependencies.Output('graph-update', 'interval'),
    dash.dependencies.Input('start-ping', 'n_clicks'),
    dash.dependencies.Input('stop-ping', 'n_clicks'),
    dash.dependencies.Input('ping-interval-input', 'value'),
    dash.dependencies.Input('address-input', 'value')
)
def control_ping(start_clicks, stop_clicks, interval, addresses_input):
    global ping_thread, addresses, ping_interval
    
    if start_clicks > 0 and stop_clicks == 0:  # Start Ping
        addresses = [addr.strip() for addr in addresses_input.split(',')]
        ping_interval = interval
        if ping_thread is None or not ping_thread.is_alive():
            ping_thread = threading.Thread(target=ping_addresses, daemon=True)
            ping_thread.start()
        return 0, 1, ping_interval  # Reset button states
    elif stop_clicks > 0:  # Stop Ping
        ping_thread = None
        return 0, 0, 0  # Stop the updates

    return start_clicks, stop_clicks, ping_interval

# Callback for saving ping data
@app.callback(
    dash.dependencies.Output('save-ping', 'n_clicks'),
    dash.dependencies.Input('save-ping', 'n_clicks')
)
def save_data(n_clicks):
    if n_clicks > 0:
        save_ping_data()
    return n_clicks

# Callback for loading ping data
@app.callback(
    dash.dependencies.Output('load-ping', 'n_clicks'),
    dash.dependencies.Input('load-ping', 'n_clicks')
)
def load_data(n_clicks):
    if n_clicks > 0:
        load_ping_data()
    return n_clicks

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)