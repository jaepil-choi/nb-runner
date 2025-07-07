# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Description
# - This ipynb file is a notebook for running backtests on verified strategies only.
#
# - The user must first choose whether the strategy will be used for futures or spot by selecting the appropriate `tradeType` value.
#
# - This notebook is preconfigured with default values to work easily on Google Colab. If you are using a local Python notebook environment instead of Colab, please pay close attention to all path configurations.
#
# #### 1. Import library
#  - Import the required libraries.
#
# #### 2. Load Api key
#  - Load the registered `USER_KEY` and `DATA_KEY` from the .env file.
#
# #### 3. Upload strategy to backtest server
#  - You need to specify the location of your strategy file in the `file_path` variable.
#  - At this stage, it is crucial to ensure that the `tradeType` is correctly set to either `future` or `spot`.
#  - Then, upload the verified strategy to the server for backtesting.
#  - If successful, a success message will be displayed.
#  - You can also review the code of the uploaded strategy.
#
# #### 4. Delete – Optional
#  - If there are any modifications to the uploaded strategy, you can delete the existing one and upload it again.
#
# #### 5. Config
#  - This cell is for **configuring the strategy**.
#  - In the backtesting phase, you don’t need to upload a separate configuration file (`config.py`). Instead, strategy parameters can be modified **flexibly** within this notebook.
#  - The user should copy and use the `rebalancing_config` and `strategy_config` sections from their actual `config.py` file here.
#  - System-related additional configuration parameters:
#  - start, end date: Set the start and end dates of the backtest in UTC.
#  - lookback_min: The maximum value among the strategy parameters. This determines how many minutes of past data should be fetched to calculate the current position.
#  - initial capital: The initial amount of capital for the backtest. If this value is too small, decimal-based trading may not be possible for some assets.
#  - leverage: The leverage multiplier to be applied in the strategy.
#  - symbols: A list of trading pairs (symbols) to include in the backtest.
#  - calendar: A fixed value
#  - frequency: A fixed value
#  - weight method:
#      - "equal": Assigns equal weight to all symbols.
#      - "split": Automatically splits the weights between long and short positions.
#      - "custom": Allows you to manually define weights using a `custom_weights` dictionary.
#        - Example:
# ```python
# custom_weights = {
#     "BTCUSDT": 0.5,
#     "ETHUSDT": 0.3,
#     ...
# }
# ```
#        - ※ In this case, all values in the dictionary must be exactly 1.0.
#  - generate_report_flag:
#     - True: Displays backtest logs along with a graph in HTML format for visualization.
#     - False: Displays only the logs, which is useful for faster testing.
#     
# #### 6. Run backtest
# - Check the save location for the HTML report file, then start this cell.
# - If the backtest runs successfully, the logs will be printed in the following order:
#  1. Runtime configuration
#  2. Backtest started
#  3. Logs showing the backtest progress
#  4. Backtest completed
#  5. Backtest analysis and HTML file saved successfully message will appear
#
# ---
#
# #### ⚠️ Important
#  - If the `.env` file does not contain `USER_KEY` and `DATA_KEY`, you must register the `USER_KEY` and generate the configuration file using `"1. strategy_verify_test.ipynb"`.
#
# ---
#
# #### - Original GitHub Link : https://github.com/NeoMatrixAI/nb-runner/tree/main/notebooks

# %% [markdown]
# # Mount Google Drive

# %%
# from google.colab import drive
# drive.mount('/content/drive')

# import warnings
# warnings.filterwarnings('ignore')

# %% [markdown]
# # Import library

# %%
import requests
import json
import pandas as pd
from datetime import datetime

# %%
import os
from dotenv import load_dotenv

load_dotenv()

user_key = os.getenv('USER_KEY')
data_apikey = os.getenv('DATA_API_KEY')



# %% [markdown]
# # Load Api Key

# %%
# !pip install dotenv

# %%
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path= "/content/drive/MyDrive/NeoMatrixAI/module/.env")

USER_KEY = os.getenv("USER_KEY")
DATA_KEY = os.getenv("DATA_KEY")

print("USER_KEY:", USER_KEY if USER_KEY else "Not found")
print("DATA_KEY:", DATA_KEY if DATA_KEY else "Not found")

# %% [markdown]
# # Health check

# %%
root_url = f'https://zipline.fin.cloud.ainode.ai/{USER_KEY}/'
requests.get(root_url).json()

# %% [markdown]
# # Upload to backtest server

# %%
tradeType = 'future' # spot / future
strategy_name = 'multi_period_momentum'

# %%
# Upload strategy file
endpoint = 'upload/strategy/'
url = root_url + endpoint

params = {'tradeType':tradeType} # spot / future

file_path = f"/content/drive/MyDrive/NeoMatrixAI/{strategy_name}.py"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, params=params, files=files)

print("📂 Upload Response:", response.json())

# %%
# Check strategy file upload
endpoint = 'upload/strategy/check/'
url = root_url + endpoint

params = {'tradeType':tradeType, "strategy_name":strategy_name}

response = requests.get(url, params=params)
print(response.json()['content'])

# %% [markdown]
# # Delete - Optional

# %%
# # Delete uploaded strategy settings file
# endpoint = 'upload/strategy/delete/'
# url = root_url + endpoint

# params = {"tradeType":tradeType, "strategy_name":strategy_name}

# # Sending a DELETE request
# response = requests.delete(url, params=params)
# print(response.json())

# %% [markdown]
# # config

# %%
hours = [1,3,6]
strategy_config_params = {
  "rebalancing_config": {             # Rebalancing settings
    "rebalancing_interval_hours": 72, ## Rebalancing cycle (choose between 6, 12, 24, and 72 hours)
    "minimum_candidates": 0           ## Minimum number of symbols to select
  },
  "strategy_config": {                # Setting strategy parameters
    "long_maximum_candidates": 5,     ## Parameters for your strategy
    "short_maximum_candidates": 5,    ## Parameters for your strategy
    "minutes": [int(i*60) for i in hours]          ## Parameters for your strategy
  }
}

start_date_str = "2025-03-10"
end_date_str = "2025-03-20"
lookback_min = 360 # Max lookback minutes the script needs for data history
initial_capital = 200000
leverage = 10
symbols = ['BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'BCHUSDT', 'LTCUSDT',
           'ADAUSDT', 'ETCUSDT', 'TRXUSDT', 'DOTUSDT', 'DOGEUSDT']
calendar = "24/7" # fixed variable
frequency = "minute" # fixed variable
weight_method = "custom" # weight method - equal, split(long/short), custom
custom_weights = { # example
  # 'symbol_n': 'value',
    'BTCUSDT': 0.5,
    'ETHUSDT': 0.2,
    'XRPUSDT': 0.1,
    'BCHUSDT': 0.04,
    'LTCUSDT': 0.04,
    'ADAUSDT': 0.03,
    'ETCUSDT': 0.03,
    'TRXUSDT': 0.03,
    'DOTUSDT': 0.02,
    'DOGEUSDT': 0.01
    }

generate_report_flag = True # True : backtest logging + html backtest result
                            # False : backtest logging

# %% [markdown]
# # Run backtest

# %%
path = "/content/drive/MyDrive/NeoMatrixAI/backtest_report" # <---------------- Modify your own route

request_payload = {
    "data_apikey": DATA_KEY,
    "strategy": strategy_name + '.py',
    "strategy_config": strategy_config_params,
    "start_date": start_date_str,
    "end_date": end_date_str,
    "lookback_minutes": lookback_min,
    "capital": initial_capital,
    "leverage": leverage,
    "symbols": symbols,
    "calendar": calendar,
    "frequency": frequency,
    "weight_method": weight_method,
    "generate_pyfolio_report": generate_report_flag
}

# Add custom_weights if weight_method is custom
if weight_method == "custom":
    if not custom_weights:
        raise ValueError("custom_weights is required if weight_method is 'custom'")
    request_payload["custom_weights"] = custom_weights

endpoint = 'run/future/backtest/'
url = root_url + endpoint

try:
    response = requests.post(url, json=request_payload)
    response.raise_for_status()
    print(f"\n--- Backtest execution successful (Status Code: {response.status_code}) ---")

    try:
        result_data = response.json()
        report_type = result_data.get('report_type') # Check report type

        if report_type == 'html':
            print("Report Type: HTML Report included.")
            html_content = result_data.get('html_content')
            logs = result_data.get('logs', 'No stderr logs received.')
            stdout_logs = result_data.get('stdout', 'No stdout received.')

            if html_content:
                if not os.path.exists(path):
                    os.makedirs(path)

                report_filename = os.path.join(path, f"{datetime.now().strftime('%Y-%m-%d %H:%M')}_{strategy_name}_backtest_report.html")
                try:
                    with open(report_filename, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    print(f"HTML report received and saved successfully as '{report_filename}'.")
                except Exception as e:
                    print(f"ERROR: Failed to save received HTML report: {e}")
                    print("\n--- Received HTML Content (Snippet) ---")
                    print(html_content[:1000] + "...") # Output some content when saving fails
            else:
                print("WARN: Report type was 'html' but no HTML content found in response.")

            # print logging
            print("\n--- Execution Logs (stderr) ---")
            print(logs)
            if stdout_logs:
                print("\n--- Execution Output (stdout) ---")
                print(stdout_logs)

        elif report_type == 'logs_only':
            print(f"Report Type: Logs Only (Report generation skipped).")
            print(f"Message: {result_data.get('message')}")
            print("\n--- Execution Logs (stderr) ---")
            print(result_data.get('logs', 'No stderr logs received.'))
            if 'stdout' in result_data:
                 print("\n--- Execution Output (stdout) ---")
                 print(result_data.get('stdout', 'No stdout received.'))
        else:
            print(f"WARN: Received successful response with unknown report_type: '{report_type}'")
            print("\n--- Full JSON Response ---")
            print(json.dumps(result_data, indent=2, ensure_ascii=False))

    except json.JSONDecodeError:
        print("ERROR: Failed to decode JSON response from successful API call.")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print("\n--- Received Raw Content (First 1000 chars) ---")
        print(response.text[:1000] + "...")

except requests.exceptions.Timeout:
    print(f"\n--- API call failed: Timeout) ---")
except requests.exceptions.HTTPError as e:
    print(f"\n--- API call failed: HTTP Error {e.response.status_code} ---")
    try:
        error_details = e.response.json()
        print("Error details:")
        print(json.dumps(error_details, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("Error response content (Non-JSON):")
        print(e.response.text)
except requests.exceptions.RequestException as e:
    print(f"\n--- API call failure: Request Error ---")
    print(f"Error connecting to or requesting the API server ({url}): {e}")
except Exception as e:
    print(f"\n--- Unexpected error occurred ---")
    print(f"Error type: {type(e).__name__}, Content: {e}")
