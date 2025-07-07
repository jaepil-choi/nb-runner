# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: aifinance
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Description
# - This ipynb file is used to run live trading.
# - Users proceed with live trading based on strategies that have been verified and successfully backtested.
#
# 1. Load API Key
# 2. Upload to Main Server
#    - Just like in backtesting, upload both the strategy and config files to the server.  
# 2-1. Upload strategy  
# 2-2. Upload config  
#
# 3. DELETE – Optional
# 4. Run Auto-Trade
#    - Download the log_viewer.py file
#    - Run the #run-system cell
#    - Then, execute the terminal command to run log_viewer.py
# 5. Terminate
# 6. Confirm Position Holding After Terminating
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
# # health check

# %%
import requests

root_url = f'https://aifapbt.fin.cloud.ainode.ai/{USER_KEY}/'
requests.get(root_url).json()

# %% [markdown]
# # upload to main server

# %% [markdown]
# ## strategy

# %%
strategy_name = "multi_period_momentum"

# %%
# Upload strategy file
endpoint = 'upload/strategy/'
url = root_url + endpoint

base_path = "/content/drive/MyDrive/NeoMatrixAI"
file_path = os.path.join(base_path, strategy_name + ".py")

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print("📂 Upload Response:", response.json())

# %%
# Check strategy file upload
endpoint = 'upload/check/strategy/'
url = root_url + endpoint

params = {"strategy_name": strategy_name}

response = requests.get(url, params=params)
print(response.json()['content'])

# %%
# Check all uploaded strategy files
endpoint = 'upload/check/all-files/strategy/'
url = root_url + endpoint

response = requests.get(url)
print(response.json())

# %% [markdown]
# ## DELETE

# %%
# # Delete uploaded strategy settings file
# endpoint = 'upload/delete/strategy/'
# url = root_url + endpoint

# params = {"strategy_name": strategy_name}

# # Sending a DELETE request
# response = requests.delete(url, params=params)
# print(response.json())

# %% [markdown]
# ## config

# %%
# Upload strategy file
endpoint = 'upload/config/'
url = root_url + endpoint

config_name = strategy_name + "_config"
base_path = "/content/drive/MyDrive/NeoMatrixAI/"
file_path = os.path.join(base_path, config_name + ".py")

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print("📂 Upload Response:", response.json())

# %%
# Check strategy file upload
endpoint = 'upload/check/config/'
url = root_url + endpoint

config_name = strategy_name + "_config"
params = {"config_name": config_name}

response = requests.get(url, params=params)
print(response.json()['content'])

# %%
# Check all uploaded config files
endpoint = 'upload/check/all-files/config/'
url = root_url + endpoint

response = requests.get(url)
print(response.json())

# %% [markdown]
# ## DELETE

# %%
# # Delete uploaded strategy settings file
# endpoint = 'upload/delete/config/'
# url = root_url + endpoint

# config_name = strategy_name + "_config"
# params = {"config_name": config_name}

# # Sending a DELETE request
# response = requests.delete(url, params=params)
# print(response.json())

# %% [markdown]
# # Run Auto-Trade

# %%
# download oncetime
# !wget https://raw.githubusercontent.com/NeoMatrixAI/nb-runner/main/modules/log_viewer.py -O /content/drive/MyDrive/NeoMatrixAI/module/log_viewer.py  # trade log module

# %%
# run-system
endpoint = 'command/run-system'
url = root_url + endpoint

data = {
    "strategy_name": strategy_name,
    "method": "rebalancing"
}

response = requests.post(url, json=data)

try:
  session_id = response.json()['session_id']
  print('session id :',response.json()['session_id'])
  print('dashboard :',response.json()['dashboard_url'])
except:
  print('Error :',response.json()['message']['message'])

  session_id = response.json()['message']['session_id']
  print('session id :',session_id)

  print('dashboard :',response.json()['message']['dashboard_url'])

# %%
# # !python {your path for 'log_viewer.py'} --USER_KEY {USER_KEY} --session_id {session_id} --save_log true/false
# !python /content/drive/MyDrive/NeoMatrixAI/module/log_viewer.py --USER_KEY {USER_KEY} --session_id {session_id} --save_log true

# %% [markdown]
# # terminate

# %%
# terminate process
# You must execute terminate to force liquidation of the current process.
endpoint = 'command/terminate/'
url = root_url + endpoint

params = {"session_id": f"{session_id}"}

response = requests.get(url, params=params)
print(response.json())

# %% [markdown]
# # Confirm position holding after Terminating

# %%
import pandas as pd

def all_positions(user_key, productType, marginCoin):
    url = f"https://bitgettrader.fin.cloud.ainode.ai/{USER_KEY}/future/position/all-positions"

    payload = {
        "user_key": USER_KEY,
        "all_positions": {
            "productType": productType,
            'marginCoin': marginCoin.upper()
        }
    }

    response = requests.post(url, json=payload)
    data = response.json()['data']
    df = pd.DataFrame(data)
    if df.empty:
        print('Everything has been liquidated')
        pass
    return df


productType = 'susdt-futures'
marginCoin = 'susdt'
df = all_positions(USER_KEY, productType, marginCoin)
df
