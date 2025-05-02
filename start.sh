#!/bin/bash

# Start the scraper in the background
python run_scraper.py &

# Start the web application
python app.py
