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
import re 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
total_entries = 200

# Create a global DataFrame to store all data
df = pd.DataFrame()
scraping_complete = False
scraping_in_progress = False
about_scraping_in_progress = False
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

# Create a single driver to be reused
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # Add additional options for stability
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_about_data_with_driver(driver, profile_name, debug_output=False):
    """Scrape a single profile using an existing driver instance"""
    try:
        # Construct the about page URL
        about_url = f"https://www.twitch.tv/{profile_name}/about"
        
        print(f"Fetching about page for {profile_name}...")
        
        # Dictionary to store contact information
        contact_info = {
            'email': None,
            'discord': None,
            'twitter': None,
            'youtube': None
        }
        
        # Load the page
        driver.get(about_url)
        
        # Wait for the page to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-a-target='channel-about-panel']"))
            )
            # Extra wait for JavaScript to finish
            time.sleep(2)
        except:
            print(f"Timeout waiting for page to load for {profile_name}")
        
        # Save debug output if requested
        if debug_output:
            html_content = driver.page_source
            html_folder = "debug"
            if not os.path.exists(html_folder):
                os.makedirs(html_folder)
            
            file_path = os.path.join(html_folder, f"{profile_name}_about.html")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(html_content)
            print(f"Saved HTML to {file_path}")
        
        # Find all links
        links = driver.find_elements(By.TAG_NAME, 'a')
        
        for link in links:
            try:
                href = link.get_attribute('href')
                if not href:
                    continue
                    
                href_lower = href.lower()
                
                # Extract contact information
                if 'mailto:' in href_lower:
                    contact_info['email'] = href_lower.replace('mailto:', '').strip()
                elif 'discord' in href_lower:
                    contact_info['discord'] = href
                elif 'twitter.com' in href_lower or 'x.com' in href_lower:
                    contact_info['twitter'] = href
                elif 'youtube.com' in href_lower:
                    contact_info['youtube'] = href
            except:
                continue
        
        # Extract additional information from text
        page_text = driver.page_source
        
        # Look for email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, page_text)
        if email_matches and not contact_info['email']:
            contact_info['email'] = email_matches[0]
        
        # Look for Discord handles
        discord_pattern = r'[A-Za-z0-9_]+#\d{4}'
        discord_matches = re.findall(discord_pattern, page_text)
        if discord_matches and not contact_info['discord']:
            contact_info['discord'] = discord_matches[0]
            
        return contact_info
        
    except Exception as e:
        print(f"Error fetching about page for {profile_name}: {e}")
        return contact_info


# Update the multiple profile scraping function to use a single driver
def scrape_multiple_about_data(profile_names):
    global df, about_scraping_in_progress
    
    about_scraping_in_progress = True
    total = len(profile_names)
    processed = 0
    
    # Create a single driver to reuse
    try:
        driver = create_driver()
        
        # Copy the DataFrame to avoid modifying during iteration
        with df_lock:
            temp_df = df.copy()
        
        # Add columns for contact info if they don't exist
        for col in ['email', 'discord', 'twitter', 'youtube']:
            if col not in temp_df.columns:
                temp_df[col] = None
        
        # Process each selected channel
        for profile_name in profile_names:
            # Get the profile name without the full URL
            clean_name = profile_name
            if '/' in profile_name:
                clean_name = profile_name.split('/')[-1]
            
            # Scrape the about data using the shared driver
            contact_info = scrape_about_data_with_driver(driver, clean_name)
            print(contact_info)
            
            # Update the DataFrame with the new contact information
            idx = temp_df.index[temp_df['twitchurl'] == profile_name].tolist()
            if idx:
                for key, value in contact_info.items():
                    temp_df.at[idx[0], key] = value
            
            processed += 1
            print(f"Processed {processed}/{total} channels")
            
            # Add a small delay between requests to avoid getting rate limited
            if processed < total:
                delay = 1 + random.random() * 2  # Random delay between 1-3 seconds
                time.sleep(delay)
        
        # Update the global DataFrame with thread safety
        with df_lock:
            df = temp_df
            # Save the updated DataFrame to CSV
            df.to_csv('twitch_channel_data_with_contacts.csv', index=False)
    
    except Exception as e:
        print(f"Error in scraping process: {e}")
    
    finally:
        # Close the driver when done with all profiles
        try:
            driver.quit()
        except:
            pass
        
        about_scraping_in_progress = False
        print("About page scraping complete!")

# Initialize the Flask server
server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

# App Layout 
app.layout = html.Div([
    html.H1("Twitch Channel Data Scraper", style={'textAlign': 'center'}),
    
    html.Div([
        html.Button('Start Scraping', id='scrape-button', n_clicks=0),
        html.Button('Export CSV', id='export-button', n_clicks=0, style={'marginLeft': '20px'}),
        html.Button('Scrape About Data', id='scrape-about-button', n_clicks=0, style={'marginLeft': '20px'}),
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
            sort_action='native',     # Enable sorting
            sort_mode='multi',        # Allow sorting by multiple columns
            filter_action='native',   # Enable filtering
            row_selectable='multi',   # Allow selecting multiple rows
            selected_rows=[]          # No rows selected by default
        ),
    ]),
    
    # Add status for About page scraping
    html.Div(id='about-scraping-status', style={'margin': '20px', 'textAlign': 'center'})
])


# Add a global variable to track about page scraping requests
about_scrape_request_id = 0

# Callback to handle About page scraping button
@app.callback(
    Output('about-scraping-status', 'children'),
    [Input('scrape-about-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('data-table', 'selected_rows'),
     State('data-table', 'data')]
)
def handle_about_scraping(n_clicks, n_intervals, selected_rows, data):
    global about_scraping_in_progress, about_scrape_request_id
    
    # Use context to determine which input triggered the callback
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Only start scraping if:
    # 1. The button was clicked (not the interval)
    # 2. We haven't already processed this exact click (using request_id)
    # 3. We're not already scraping
    # 4. Rows are selected
    if (trigger_id == 'scrape-about-button' and 
        n_clicks > about_scrape_request_id and 
        not about_scraping_in_progress and 
        selected_rows):
        
        # Update the request ID to match the current click count
        about_scrape_request_id = n_clicks
        
        # Get the twitch URLs from the selected rows
        profile_urls = [data[i]['twitchurl'] for i in selected_rows]
        
        # Start a thread to scrape the about data
        threading.Thread(target=scrape_multiple_about_data, args=(profile_urls,)).start()
    
    # Return status message
    if about_scraping_in_progress:
        return "About page scraping in progress..."
    elif n_clicks > 0 and not selected_rows and trigger_id == 'scrape-about-button':
        return "Please select at least one channel before scraping About pages."
    elif n_clicks > 0 and n_clicks == about_scrape_request_id and not about_scraping_in_progress:
        return "About page scraping complete!"
    else:
        return "Select channels and click 'Scrape About Data' to gather contact information."

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