# Twitch Channel Data Scraper with Real-time Viewer

This application scrapes Twitch channel data from SullyGnome and displays it in a real-time web interface with sorting and filtering capabilities.

## Features

- Real-time data visualization as scraping progresses
- Interactive data table with sorting and filtering
- Export data to CSV at any time
- Thread-safe data handling

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:

```bash
python scrape_analytics.py
```

2. Open your web browser and navigate to: http://127.0.0.1:8050/

3. Click the "Start Scraping" button to begin collecting data

4. Use the table's sorting functionality by clicking on column headers

5. Filter data by typing in the filter boxes at the top of each column

6. Export the current data to CSV at any time by clicking the "Export CSV" button

## Notes

- The scraper uses random delays between requests to avoid being blocked
- Data is automatically saved to 'twitch_channel_data.csv' when scraping completes
- Exported CSVs include timestamps in the filename
