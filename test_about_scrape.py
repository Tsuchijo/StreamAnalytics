# test_about_scrape.py
import requests
import time
import random
import re
from bs4 import BeautifulSoup
import pandas as pd
import sys
from scrape_analytics import scrape_about_data_with_driver, create_driver

# Browser-like headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://twitch.tv/',
    'Connection': 'keep-alive',
}



def test_scrape_about_data(profile_list):
    """
    Test the scrape_about_data function on a list of profiles
    """
    results = []
    try:
        driver = create_driver()    

        print(f"Starting to scrape {len(profile_list)} profiles...")
        
        for profile in profile_list:
            # Extract username from URL if needed
            if '/' in profile:
                profile = profile.split('/')[-1]
            
            # Clean up the profile name 
            # Remove 'about' if it's at the end
            if profile.endswith('/about'):
                profile = profile[:-6]
            
            # Remove trailing slash if present
            if profile.endswith('/'):
                profile = profile[:-1]
            
            # Scrape the about data

            contact_info = scrape_about_data_with_driver(driver, profile, debug_output=True)
            results.append(contact_info)
            
            # Print the results
            print("\nContact Information:")
            for key, value in contact_info.items():
                print(f"  {key}: {value}")
            
            print("\n" + "-"*50 + "\n")
            
            # Add a delay between requests
            time.sleep(2)
        
        # Convert results to DataFrame and save to CSV
        df = pd.DataFrame(results)
        df.to_csv('twitch_contact_info.csv', index=False)
        print(f"Results saved to 'twitch_contact_info.csv'")
        
        return df
    
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


if __name__ == "__main__":
    # Check if profile list is provided as command-line arguments
    if len(sys.argv) > 1:
        profiles = sys.argv[1:]
    else:
        # Default test profiles
        profiles = [
            "ninja",
            "shroud",
            "pokimane",
            "moistcr1tikal",
            "xqc"
        ]
    
    print(f"Testing with profiles: {profiles}")
    results_df = test_scrape_about_data(profiles)
    print("\nFinal Results:")
    print(results_df)