# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: sandbox312
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Description
# - This ipynb file is a test notebook to verify that your custom strategy has been implemented correctly on our system.
#
# - This notebook is preconfigured with default values to work easily on Google Colab. If you are using a local Python notebook environment instead of Colab, please pay close attention to all path configurations.
#
# #### 1. Register Api key
#  - Input your `USER_KEY` and run the shell to check if the env file is created
#
# #### 2. Get Data
#  - Download `sample data` and `strategy/config` files
#
# #### 3. Verify strategy
#  - Test the strategy and config files using `sample data` and verify that the results are returned as a list.
#  - To use a different custom strategy, modify the import path accordingly and then run the notebook.
#
# #### - Original GitHub Link : https://github.com/NeoMatrixAI/nb-runner/tree/main/notebooks

# %% [markdown]
# # Mount Google Drive

# %%
# from google.colab import drive
# drive.mount('/content/drive')

# import warnings
# warnings.filterwarnings('ignore')

# %%
import os
from dotenv import load_dotenv

load_dotenv()

user_key = os.getenv('USER_KEY')
data_apikey = os.getenv('DATA_API_KEY')



# %% [markdown]
# # Register Api key

# %%
# !pip install dotenv

# %%
from dotenv import load_dotenv
import os

env_dir = os.path.join(os.getcwd(), "/content/drive/MyDrive/NeoMatrixAI/module")
env_path = os.path.join(env_dir, ".env")

os.makedirs(env_dir, exist_ok=True)

USER_KEY = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"  # <------------------ Input your User key
DATA_KEY = "a71eaf04-802f-40be-93c2-5bee2548f4db"  # <------------------ Fixed Data Api key

with open(env_path, "w") as f:
    f.write(f"USER_KEY={USER_KEY}\n")
    f.write(f"DATA_KEY={DATA_KEY}\n")
print(".env file is created.")

load_dotenv(dotenv_path=env_path, override=True)

USER_KEY = os.getenv("USER_KEY")
DATA_KEY = os.getenv("DATA_KEY")

print("USER_KEY:", USER_KEY)
print("DATA_KEY:", DATA_KEY)

# %% [markdown]
# # Get Sample Data

# %%
os.makedirs("/content/drive/MyDrive/NeoMatrixAI", exist_ok=True)

# !wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1ZZw4u3uImeuooj-v10VDX_utgEjsfVv4' -O /content/drive/MyDrive/NeoMatrixAI/df_sample.csv # sample data
# !wget https://raw.githubusercontent.com/NeoMatrixAI/strategy/main/future/multi_period_momentum/multi_period_momentum.py -O /content/drive/MyDrive/NeoMatrixAI/multi_period_momentum.py # sample strategy
# !wget https://raw.githubusercontent.com/NeoMatrixAI/strategy/main/future/multi_period_momentum/multi_period_momentum_config.py -O /content/drive/MyDrive/NeoMatrixAI/multi_period_momentum_config.py # sample config

# %%
import pandas as pd
df = pd.read_csv('/content/drive/MyDrive/NeoMatrixAI/df_sample.csv').set_index('datetime')
df

# %% [markdown]
# # Verify strategy

# %%
# example strategy, config
import drive.MyDrive.NeoMatrixAI.multi_period_momentum as strategy       # Replace with your own strategy file
import drive.MyDrive.NeoMatrixAI.multi_period_momentum_config as config  # Replace with your own config file

# run to verify strategy
config_dict = {'strategy_config': config.strategy_config}
long_candidate, short_candidate = strategy.strategy(df, config_dict)
print(f'long_candidate symbol : {long_candidate}')
print(f'short_candidate symbol : {short_candidate}')
