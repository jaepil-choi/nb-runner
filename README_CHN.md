# nb-runner 🚀

本仓库是由 `.ipynb` 和 `.py` 文件组成的笔记本运行工具。

主要设计用于在本地环境中运行，例如 [**Google Colab**](https://colab.research.google.com)。  
如果您调整“挂载 Google 云端硬盘”单元格并指定您的**个人路径**，也可以轻松适配其他本地环境。

要使用提供的 API 功能，您必须从 **NeoMatrix** 获取 `data apikey` 和 `user key`。

您可以通过以下两种方式运行回测和实时交易：
- 使用您自定义的策略和配置文件  
- 使用通过 [strategy](https://github.com/NeoMatrixAI/strategy) 仓库定期更新的策略和设置

### 📘 笔记本使用流程

典型的笔记本执行顺序如下：

1. **`strategy_verify_test.ipynb`**  
   → 通过调用 NeoMatrix API 服务器验证您的策略。

2. **`backtest.ipynb`**  
   → 使用验证后的策略和您选择的配置进行回测。

3. **`trade.ipynb`**  
   → 基于回测得出的最终参数执行实时自动交易。

---
### ❓ 支持

如有问题或需要支持，请通过 [**NeoMatrix Discord**](https://discord.gg/n6tMdrse) 联系我们。
