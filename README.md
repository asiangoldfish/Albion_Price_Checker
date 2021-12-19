# Albion Price Checker

Welcome to the Albion Online's standalone price checker!

This project's goal is making price checking easier. As the project develops, more features will be implemented.
The current future plans are listed below:
  - Local save for price searches. This enables you to use previous searches offline.
  - Using local saves as a backup. In case the online data base shows the 0 silver price because of missing data, the local save is used instead.
  - A seperate history category. Shows graphs from past prices. Allows for studying price trends and predict future prices.
  - Crafting calculator and profiles for saving your crafting skills.
 
All credits for the data collection goes to the Albion Online Data Project team and their contributors.

___

## Using the App with Source Code

The repository is currently a little hot mess. However, feel free to explore it.

1. Install Python 3:
  ```
  sudo apt update \
  sudo apt install python3
  ```
2. Install pip:
  ```
  sudo apt install python3-pip
  ```
3. Using a virtual environment is preferred. Use your virtual environment of your choice or do the following:
  ```
  python3 -m venv venv \
  source venv/bin/activate
  ```
4. Install dependencies:
  ```
  pip3 install -r requirements.txt` \
  sudo apt install python3-tk
  ```

___

# Running the program

To run the program from binary, check out the releases and download `albion_price_check.zip`.
