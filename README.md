
# Twitch Channel Data Scraper with Real-time Viewer

This application scrapes Twitch channel data from SullyGnome and displays it in a real-time web interface with sorting and filtering capabilities.

## Features

- Real-time data visualization as scraping progresses
- Interactive data table with sorting and filtering
- Export data to CSV at any time
- Thread-safe data handling

## Detailed Installation Guide (No Programming Experience Required)

### Step 1: Download the Project from GitHub

1. Go to the GitHub repository in your web browser
2. Click on the green "Code" button near the top right
3. Select "Download ZIP" from the dropdown menu
4. Once downloaded, locate the ZIP file in your Downloads folder
5. Right-click the ZIP file and select "Extract All..." or use your preferred extraction tool
6. Choose a location where you want to extract the files (e.g., Desktop)
7. Click "Extract"

### Step 2: Install Python

1. Visit the official Python website: https://www.python.org/downloads/
2. Click on the "Download Python" button (this will download the latest version for your operating system)
3. Once downloaded, run the installer:
   - On Windows: Double-click the downloaded .exe file
   - On Mac: Double-click the downloaded .pkg file
   - On Linux: Follow the instructions for your specific distribution
4. **IMPORTANT**: During installation, check the box that says "Add Python to PATH" before clicking "Install Now"
5. Complete the installation process by following the on-screen instructions

### Step 3: Open Command Line/Terminal

- **On Windows**:
  - Press `Win + R` keys
  - Type `cmd` and press Enter
  - Or search for "Command Prompt" in the Start menu

- **On Mac**:
  - Press `Command + Space` to open Spotlight Search
  - Type "Terminal" and press Enter

- **On Linux**:
  - Press `Ctrl + Alt + T` in most distributions
  - Or find Terminal in your applications menu

### Step 4: Install UV (Python Package Installer)

1. In your Command Prompt/Terminal, type the following command and press Enter:
   ```
   pip install uv
   ```
2. Wait for UV to install (this may take a minute)

### Step 5: Navigate to the Project Directory

1. In your Command Prompt/Terminal, you need to navigate to where you extracted the files
2. Use the `cd` (change directory) command:
   ```
   cd path/to/extracted/folder
   ```
   
   For example, if you extracted to your Desktop:
   - On Windows: `cd C:\Users\YourUsername\Desktop\twitch-channel-scraper-main`
   - On Mac/Linux: `cd ~/Desktop/twitch-channel-scraper-main`

### Step 6: Install Project Dependencies Using UV

1. In your Command Prompt/Terminal (while in the project directory), type:
   ```
   uv sync
   ```
2. This will read the project's requirements and install all necessary dependencies
3. Wait for the installation to complete

### Step 7: Run the Application

1. In the same Command Prompt/Terminal window, type:
   ```
   uv run python scrape_analytics.py
   ```
2. You should see messages indicating that the application has started
3. Open your web browser and navigate to: http://127.0.0.1:8050/

## Using the Application

1. Once the web page loads, click the "Start Scraping" button to begin collecting data
2. You'll see the data table fill with Twitch channel information in real-time
3. To sort the data, click on any column header (click again to reverse sort order)
4. To filter data, type in the filter boxes at the top of each column
5. To save the current data, click the "Export CSV" button

## Notes

- The scraper uses random delays between requests to avoid being blocked
- Data is automatically saved to 'twitch_channel_data.csv' when scraping completes
- Exported CSVs include timestamps in the filename
- If you close the application, you can restart it by following Step 7 again

## Troubleshooting

- **"Python is not recognized as an internal or external command"**: You need to restart your Command Prompt/Terminal after installing Python, or you didn't check "Add Python to PATH" during installation
- **"UV is not recognized as a command"**: Try using `python -m pip install uv` instead
- **"Permission denied"**: Try running the Command Prompt/Terminal as administrator (Windows) or use `sudo` before commands (Mac/Linux)
- **No data appears**: Check your internet connection or the website might be blocking the scraper