# 股票均线策略数据分析与回测项目
## 项目简介
本项目使用Python实现**5日、20日均线金叉死叉量化策略**，模拟股票行情数据，完成指标计算、买卖信号识别、策略回测与可视化绘图。
采用模块化编程，将功能拆分为数据生成、指标计算、回测、绘图四大函数。
代码中使用`df.copy()`副本方式，避免修改原始数据，消除函数副作用。

## 环境依赖
项目依赖包写在 `requirements.txt`，包含：
- pandas：表格数据处理
- numpy：数值计算
- matplotlib：绘图
- mplfinance：K线图绘制

### 安装依赖
```bash
pip install -r requirements.txt   