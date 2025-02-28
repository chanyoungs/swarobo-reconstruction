import time
import dash
from dash import dcc, html
import plotly.graph_objects as go
from ping3 import ping
from collections import deque
import pandas as pd
import threading
from datetime import datetime

# Create the Dash app
app = dash.Dash(__name__)

# Global variables
traces = {}
addresses = []
ping_thread = None
ping_running = False
ping_interval = 1000

def clear_traces():
    global traces
    traces = {addr: deque(maxlen=100) for addr in addresses}

# Layout of the web app
app.layout = html.Div([
    html.H1("Live Ping Response Times"),
    
    html.Div([
        html.Label("Enter Addresses to Ping (comma-separated):"),
        dcc.Input(id="address-input", type="text", 
                  placeholder="e.g., google.com, 8.8.8.8", 
                  value="192.168.1.11, 192.168.1.12"),
        html.Button("Start Ping", id="toggle-ping", n_clicks=0),
    ]),
    
    html.Div([
        html.Label("Ping Interval (ms):"),
        dcc.Input(id="ping-interval-input", type="number", value=ping_interval),
    ]),
    
    dcc.Graph(id="live-graph"),
    
    dcc.Interval(id="graph-update", interval=ping_interval, n_intervals=0)
])

# Function to ping addresses
def ping_address(address):
    response = ping(address)
    return response * 1000 if response is not None else None

def ping_addresses():
    global traces, addresses, ping_running
    while ping_running:
        current_time = time.time()
        for address in addresses:
            response_time = ping_address(address)
            if address not in traces:
                traces[address] = deque(maxlen=100)
            traces[address].append((current_time, response_time))
        time.sleep(ping_interval / 1000)

# Function to get traces
def get_traces():
    COLORS = ["red", "orange", "yellow", "green", "blue"]
    data = []
    for i, address in enumerate(addresses):
        trace_data = traces.get(address, deque(maxlen=100))
        color = COLORS[i % len(COLORS)]
        data.append(go.Scatter(
            x=[datetime.fromtimestamp(t[0]).strftime('%H:%M:%S') for t in trace_data],
            y=[t[1] for t in trace_data],
            mode='lines+markers',
            name=address,
            line=dict(color=color)
        ))
    return data

@app.callback(
    [dash.dependencies.Output('live-graph', 'figure'),
     dash.dependencies.Output('toggle-ping', 'children'),
     dash.dependencies.Output('graph-update', 'interval')],
    [dash.dependencies.Input('toggle-ping', 'n_clicks'),
     dash.dependencies.Input('ping-interval-input', 'value'),
     dash.dependencies.Input('address-input', 'value'),
     dash.dependencies.Input('graph-update', 'n_intervals')]
)
def toggle_ping(n_clicks, interval, addresses_input, n_intervals):
    global ping_thread, ping_running, addresses, ping_interval
    if n_clicks % 2 == 1 and not ping_running:  # Start Ping
        addresses = [addr.strip() for addr in addresses_input.split(',')]
        ping_interval = interval
        clear_traces()
        ping_running = True
        if ping_thread is None or not ping_thread.is_alive():
            ping_thread = threading.Thread(target=ping_addresses, daemon=True)
            ping_thread.start()
    elif n_clicks % 2 == 0 and ping_running:  # Stop Ping
        ping_running = False
    
    return {'data': get_traces(), 'layout': go.Layout(title="Live Ping Response Times")}, "Stop Ping" if ping_running else "Start Ping", ping_interval

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)