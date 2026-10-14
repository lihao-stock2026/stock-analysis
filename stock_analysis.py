# 股票数据分析示例代码
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf

# ========== 解决matplotlib中文乱码（给收益曲线图使用） ==========
plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams['axes.unicode_minus'] = False

# 定义字体字典
font_dict = {"family":"SimHei"}

# ========== 模拟行情数据 ==========
def generate_sim_data():
    dates = pd.date_range(start="2024-01-01", end="2025-01-01", freq="B")
    np.random.seed(42)
    price = 10
    data_list = []
    for _ in dates:
        change = np.random.normal(0, 0.02)
        price = price * (1 + change)
        open_p = price * np.random.uniform(0.98, 1.02)
        high_p = open_p * np.random.uniform(1, 1.03)
        low_p = open_p * np.random.uniform(0.97, 1)
        close_p = price
        vol = np.random.randint(50000, 200000)
        data_list.append([open_p, high_p, low_p, close_p, vol])

    df = pd.DataFrame(data_list,
                      index=dates,
                      columns=["open", "high", "low", "close", "volume"])
    return df

# 计算均线、收益率、买卖信号
def calc_indicators_and_signal(df):
    # 复制一份，不改动传入的原始df
    df_new = df.copy()
    # ========== 计算技术指标 ==========
    df_new["ma5"] = df_new["close"].rolling(window=5).mean()
    df_new["ma20"] = df_new["close"].rolling(window=20).mean()

    # 日收益率
    df_new["daily_return"] = df_new["close"].pct_change()

    # 均线策略：5日均线大于20日均线买入
    df_new["signal"] = np.where(df_new["ma5"] > df_new["ma20"], 1, 0)
    df_new["strategy_return"] = df_new["daily_return"] * df_new["signal"].shift(1)

    # ======================【新增：识别买入卖出信号】======================
    # 买入信号：signal由0→1
    df_new["buy_signal"] = np.where((df_new["signal"] == 1) & (df_new["signal"].shift(1) == 0), df_new["low"] * 0.98, np.nan)
    # 卖出信号：signal由1→0
    df_new["sell_signal"] = np.where((df_new["signal"] == 0) & (df_new["signal"].shift(1) == 1), df_new["high"] * 1.02, np.nan)
    return df_new

# 回测，输出各项指标
def backtest(df):
    # 新增计算最大回撤、夏普比率
    cum_return = (1 + df["strategy_return"]).cumprod()
    running_max = cum_return.cummax()
    drawdown = (cum_return / running_max) - 1
    max_drawdown = drawdown.min()

    # 夏普比率(无风险利率取0),增加分母防除零
    std_ret = df["strategy_return"].std()
    if std_ret == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = df["strategy_return"].mean() / std_ret * np.sqrt(252)

    # 统计交易次数
    buy_count = df["buy_signal"].notna().sum()
    sell_count = df["sell_signal"].notna().sum()

    # ========== 输出统计结果 ==========
    print("===== 均线策略回测报告 =====")
    print(f"总收益率: {df['strategy_return'].sum():.2%}")
    print(f"年化波动率: {df['daily_return'].std() * np.sqrt(252):.2%}")
    print(f"最大回撤: {max_drawdown:.2%}")
    print(f"夏普比率: {sharpe_ratio:.2f}")
    print(f"买入次数: {buy_count}")
    print(f"卖出次数: {sell_count}")
    print("\n代码运行完成！")
    return cum_return, drawdown

#  绘制K线、收益曲线，保存图片
def plot_charts(df, cum_return, drawdown):
    # 构造addplot，用于mpf绘图
    apd = [
        mpf.make_addplot(df["buy_signal"], type="scatter", marker="^", color="green", markersize=8),
        mpf.make_addplot(df["sell_signal"], type="scatter", marker="v", color="red", markersize=8)
    ]

    # 绘制K线图
    mpf.plot(df,
        type="candle",
        mav=(5, 20),
        volume=True,
        title="Simulated Stock K-line & MA",
        figratio=(12, 6),
        addplot=apd,
        savefig="kline.png"
    )

    # 收益曲线
    plt.figure(figsize=(10,4))
    cum_return.plot(title="Strategy Cumulative Return Curve")
    plt.savefig("return_curve.png", dpi=150)

    # 回撤曲线
    plt.figure(figsize=(10,4))
    drawdown.plot(title="Drawdown Curve", color="red")
    plt.savefig("drawdown_curve.png", dpi=150)
    plt.show()

if __name__ == "__main__":
    df_raw = generate_sim_data()
    print("原始数据列：", df_raw.columns.tolist())

    df = calc_indicators_and_signal(df_raw)
    print("处理后数据列：", df.columns.tolist())
    print("校验：原始数据未被修改：", df_raw.columns.tolist())

    cum_return, drawdown = backtest(df)
    plot_charts(df, cum_return, drawdown)
