import requests
import pandas as pd
import time
import json
import random
import threading
import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import flask
import os
from datetime import datetime

# Browser-like headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://sullygnome.com/',  # Important! This makes it look like you're coming from the main site
    'Origin': 'https://sullygnome.com',
    'Connection': 'keep-alive',
}

# Base URL and parameters
base_url = "https://sullygnome.com/api/tables/channeltables/getchannels/7/0/1/3/desc/"
entries_per_page = 100
total_entries = 5000

# Create a global DataFrame to store all data
df = pd.DataFrame()
scraping_complete = False
scraping_in_progress = False

# Create a lock for thread-safe DataFrame updates
df_lock = threading.Lock()

# Function to scrape data
def scrape_data():
    global df, scraping_complete, scraping_in_progress
    
    scraping_in_progress = True
    all_data = []
    
    # Create a session object to maintain cookies across requests
    session = requests.Session()
    
    # Make an initial request to the main site to get cookies
    try:
        print("Visiting main page to get cookies...")
        session.get('https://sullygnome.com/', headers=headers)
    except Exception as e:
        print(f"Error accessing main page: {e}")
    
    # Loop through all the pages
    for offset in range(0, total_entries, entries_per_page):
        # Construct the URL
        url = f"{base_url}{offset}/{entries_per_page}"
        
        print(f"Fetching data from offset {offset}...")
        
        try:
            # Add a random delay between requests (0.5 to 3 seconds)
            delay = 0.5 + random.random() * 0.5
            time.sleep(delay)
            
            # Send the request with our browser-like headers
            response = session.get(url, headers=headers)
            
            # Check if request was successful
            if response.status_code == 200:
                # Parse the JSON
                data = response.json()
                
                # Extract the data array
                channel_data = data.get('data', [])
                
                # Add the data to our list
                all_data.extend(channel_data)
                
                # Update the global DataFrame with thread safety
                with df_lock:
                    df = pd.DataFrame(all_data)
                    # Remove logo column and reorder columns to put display name and twitch URL first
                    if not df.empty and 'logo' in df.columns:
                        # Drop the logo column
                        df = df.drop('logo', axis=1)
                        # Get all column names
                        cols = df.columns.tolist()
                        # Remove the columns we want to move to front
                        cols.remove('displayname')
                        cols.remove('twitchurl')
                        # Add them back at the beginning
                        cols = ['displayname', 'twitchurl'] + cols
                        # Reorder the DataFrame
                        df = df[cols]
                
                # Print progress
                print(f"Retrieved {len(channel_data)} entries. Total so far: {len(all_data)}")
                
            else:
                print(f"Error: Received status code {response.status_code} for offset {offset}")
                print(f"Response: {response.text[:200]}...")  # Print first 200 chars of response
                
        except Exception as e:
            print(f"Error fetching data for offset {offset}: {e}")
    
    # Save the DataFrame to CSV
    with df_lock:
        df.to_csv('twitch_channel_data.csv', index=False)
    
    print(f"\nTotal entries collected: {len(all_data)}")
    scraping_complete = True
    scraping_in_progress = False

# Initialize the Flask server
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

# Define the layout
app.layout = html.Div([
    html.H1("Twitch Channel Data Scraper", style={'textAlign': 'center'}),
    
    html.Div([
        html.Button('Start Scraping', id='scrape-button', n_clicks=0),
        html.Button('Export CSV', id='export-button', n_clicks=0, style={'marginLeft': '20px'}),
        dcc.Download(id="download-dataframe-csv"),
        html.Div(id='scraping-status', style={'marginLeft': '20px', 'display': 'inline-block'})
    ], style={'textAlign': 'center', 'margin': '20px'}),
    
    html.Div([
        dcc.Interval(
            id='interval-component',
            interval=2*1000,  # in milliseconds (2 seconds)
            n_intervals=0
        ),
        
        dash_table.DataTable(
            id='data-table',
            columns=[],
            data=[],
            page_size=20,
            style_table={'overflowX': 'auto'},
            sort_action='native',  # Enable sorting
            sort_mode='multi',     # Allow sorting by multiple columns
            filter_action='native' # Enable filtering
        ),
    ]),
])

# Callback to update the table
@app.callback(
    [Output('data-table', 'data'),
     Output('data-table', 'columns')],
    [Input('interval-component', 'n_intervals')]
)
def update_table(n):
    with df_lock:
        if df.empty:
            return [], []
        
        # Convert DataFrame to dict for the table
        data = df.to_dict('records')
        
        # Create columns configuration
        columns = [{'name': col, 'id': col, 'selectable': True} for col in df.columns]
        
        return data, columns

# Callback to handle scraping button
@app.callback(
    Output('scraping-status', 'children'),
    [Input('scrape-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def handle_scraping(n_clicks, n_intervals):
    global scraping_in_progress
    
    # Start scraping if button is clicked and not already scraping
    if n_clicks > 0 and not scraping_in_progress and not scraping_complete:
        threading.Thread(target=scrape_data).start()
    
    # Return status message
    if scraping_complete:
        return "Scraping complete!"
    elif scraping_in_progress:
        with df_lock:
            return f"Scraping in progress... {len(df)} entries collected so far."
    else:
        return "Click 'Start Scraping' to begin data collection."

# Callback for CSV export
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-button", "n_clicks"),
    prevent_initial_call=True,
)
def export_csv(n_clicks):
    if n_clicks > 0:
        with df_lock:
            if not df.empty:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                return dcc.send_data_frame(df.to_csv, f"twitch_data_{timestamp}.csv", index=False)

# Run the app
if __name__ == '__main__':
    print("Starting web server. Navigate to http://127.0.0.1:8050/ in your browser")
    app.run_server(debug=True, use_reloader=False)