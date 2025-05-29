# nb-runner 🚀

> 📚 This README is available in multiple languages:  
> - 🇺🇸 English (default) — this file  
> - 🇰🇷 [한국어](./README_KOR.md) 🇰🇷  
> - 🇨🇳 [中文](./README_CHN.md) 🇨🇳  

This repository is a notebook runner composed of `.ipynb` and `.py` files.

It is primarily designed to run in a local environment such as [**Google Colab**](https://colab.research.google.com).  
If you adjust the "Mount Google Drive" cell and specify your **personal path**, it can be easily adapted to other local environments as well.

To use the provided API functions, you must obtain a `data apikey` and `user key` from **NeoMatrix**.

You can run backtests and live trading using either:  
- your own custom strategies and configuration files, or  
- the regularly updated strategies and settings shared via the [strategy](https://github.com/NeoMatrixAI/strategy) repository.

### 📘 Notebook Usage Flow

The typical order of notebook execution is as follows:

1. **`strategy_verify_test.ipynb`**  
   → Validates your strategy by calling the NeoMatrix API server.

2. **`backtest.ipynb`**  
   → Runs a backtest using the verified strategy and your chosen configuration.

3. **`trade.ipynb`**  
   → Executes live auto-trading based on the strategy and final parameters derived from the backtest.

---
### ❓ Support

For questions or support, please reach out via the [**NeoMatrix Discord**](https://discord.gg/n6tMdrse)
