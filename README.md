# ITSM Report Generator

一个基于Flask的Web应用，用于比较和分析ITSM工单数据。

## 功能特点 / Features

- 支持上传并比较两个Excel文件中的工单数据
- 可视化展示工单数量变化
- 分析新增工单的Site分布
- 分析新增工单的优先级分布
- 支持法语到中文的优先级翻译
- 现代化的图表样式和配色方案

## 技术栈 / Tech Stack

- Python 3.x
- Flask
- Pandas
- Plotly
- JavaScript
- HTML/CSS

## 安装步骤 / Installation

1. 克隆仓库 / Clone the repository
```bash
git clone [repository-url]
cd itsmreport
```

2. 安装依赖 / Install dependencies
```bash
pip install -r requirements.txt
```

3. 运行应用 / Run the application
```bash
python app.py
```

应用将在 http://localhost:3000 启动

## 使用说明 / Usage

1. 准备两个Excel文件，分别包含上周和本周的工单数据
2. 在网页界面上传这两个文件
3. 系统将自动生成对比分析图表，包括：
   - 工单总量对比
   - 新增工单的Site分布
   - 新增工单的优先级分布

## 注意事项 / Notes

- Excel文件必须包含以下字段：
  - ID（工单号）
  - Site（站点）
  - Priority（优先级）
- 支持的优先级值：
  - 1 : très élevée（1级：非常高）
  - 2 : élevé（2级：高）
  - 3 : moyen（3级：中）
  - 4 : faible（4级：低） 