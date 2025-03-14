import PyInstaller.__main__
import os
import site
import platform
import sys

# Find site-packages directory
site_packages = site.getsitepackages()[0]

# Common options for both platforms
common_options = [
    'scrape_analytics.py',
    '--onefile',
    '--clean',
    '--console',  # Show terminal window for debugging (replaces --windowed)
    f'--add-data={os.path.join(site_packages, "dash")}{os.pathsep}dash',
    f'--add-data={os.path.join(site_packages, "dash_core_components")}{os.pathsep}dash_core_components',
    f'--add-data={os.path.join(site_packages, "dash_html_components")}{os.pathsep}dash_html_components',
    f'--add-data={os.path.join(site_packages, "dash_table")}{os.pathsep}dash_table',
    f'--add-data={os.path.join(site_packages, "plotly")}{os.pathsep}plotly',
    '--hidden-import=dash',
    '--hidden-import=dash_core_components',
    '--hidden-import=dash_html_components',
    '--hidden-import=dash_table',
    '--hidden-import=plotly',
    '--hidden-import=flask',
    '--hidden-import=pandas',
    '--hidden-import=requests',
    '--hidden-import=threading',
    '--hidden-import=json',
    '--hidden-import=time',
    '--hidden-import=random',
    '--hidden-import=datetime',
]

# Detect current platform
current_platform = platform.system()

# Build for Windows
if current_platform == 'Windows' or (len(sys.argv) > 1 and sys.argv[1] == '--windows'):
    print("Building for Windows...")
    PyInstaller.__main__.run([
        '--name=TwitchScraper-Windows',
        '--icon=icon.ico',  # Add an icon file if you have one
        *common_options
    ])

# Build for macOS
if current_platform == 'Darwin' or (len(sys.argv) > 1 and sys.argv[1] == '--mac'):
    print("Building for macOS...")
    PyInstaller.__main__.run([
        '--name=TwitchScraper-Mac',
        '--icon=icon.icns',  # Add an icon file if you have one
        *common_options
    ])

print("Build process completed!")