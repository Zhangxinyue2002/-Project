# 数据分析与可视化网页

这是一个基于 **Streamlit + Pandas** 的网页应用，用于上传 CSV / Excel 数据并进行统计分析与可视化。

## 功能

- 上传 CSV / XLSX / XLS
- 数据预览与描述性统计
- 缺失值统计
- 数值分布图、类别频数图
- 分组汇总与可视化
- 数值相关性热力图

## 环境要求

- Windows / macOS / Linux
- Python 3.10+（推荐 3.11/3.12）

## 安装依赖

在项目根目录执行：

```bash
python -m pip install -r requirements.txt
```

## 启动应用

在项目根目录执行：

```bash
python -m streamlit run app.py
```

启动后打开浏览器访问：

```
http://localhost:8501
```

## 让局域网内其他人访问

应用已配置为允许局域网访问（.streamlit/config.toml）。你只需：

1. 在同一局域网内，把你的电脑防火墙放行 8501 端口
2. 获取你的本机 IP（如 192.168.x.x）
3. 其他人用浏览器访问：

```
http://<你的IP>:8501
```

如果需要改端口，修改 .streamlit/config.toml 中的 port。

## 实验说明（Sample.xlsx）

如果项目根目录存在 Sample.xlsx，应用会自动读取并展示实验描述与样本前缀含义，用于增强自动分析摘要。

## 使用说明

1. 点击左侧上传按钮，选择 CSV/Excel 文件
2. 页面会自动显示统计结果与可视化图表
3. 可用分组汇总功能做简单分析

## 示例数据

侧边栏提供“使用示例数据”按钮，可快速体验功能。