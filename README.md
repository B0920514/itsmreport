# ITSM Ticket Analysis Dashboard

一个用于分析ITSM工单数据的交互式仪表板。

## 功能特点

- 上传并比较两周的工单数据
- 显示总体工单数量对比
- 按站点分布的新工单分析
- 按优先级分布的新工单分析
- 按周分布的工单趋势分析（支持年份选择）

## 技术栈

- Python 3.x
- Flask
- Pandas
- Plotly
- HTML/CSS/JavaScript

## 安装说明

### 本地运行

1. 克隆仓库：
```bash
git clone https://github.com/B0920514/itsmreport.git
cd itsmreport
```

2. 运行启动脚本：
```bash
./start.sh
```

3. 打开浏览器访问：http://127.0.0.1:3038

### 手动安装

1. 确保已安装 Python 3.x
2. 创建虚拟环境：
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行应用：
```bash
python app.py
```

## 使用说明

1. 准备数据文件：
   - 上周的Excel文件
   - 本周的Excel文件
   - 文件格式要求：包含 'ID', 'Created On', 'Site', 'Priority' 等字段

2. 上传文件：
   - 点击"Last Week's File"选择上周数据
   - 点击"This Week's File"选择本周数据
   - 点击"Analyze"按钮开始分析

3. 查看结果：
   - 总体工单数量对比
   - 新工单的站点分布
   - 新工单的优先级分布
   - 按周分布的工单趋势（可选择年份）

## 数据格式要求

Excel文件应包含以下字段：
- ID：工单唯一标识
- Created On：创建日期（格式：DD.MM.YYYY）
- Site：站点信息
- Priority：优先级

## 注意事项

- 确保上传的Excel文件大小不超过16MB
- 日期格式必须为DD.MM.YYYY
- 建议使用Chrome或Firefox浏览器以获得最佳体验

## 许可证

MIT License 