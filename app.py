from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import logging
from werkzeug.utils import secure_filename

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 优先级翻译字典
PRIORITY_TRANSLATION = {
    '1 : très élevée': '1级：非常高',
    '2 : élevé': '2级：高',
    '3 : moyen': '3级：中',
    '4 : faible': '4级：低'
}

# 现代配色方案
COLORS = {
    'primary': '#2196F3',    # 主要
    'secondary': '#FF4081',  # 次要
    'success': '#4CAF50',    # 成功
    'info': '#00BCD4',       # 信息
    'warning': '#FFC107',    # 警告
    'error': '#F44336',      # 错误
    'light': '#90CAF9',      # 浅色
    'dark': '#1976D2'        # 深色
}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    logger.debug("开始处理文件上传请求")
    
    if 'lastWeek' not in request.files or 'thisWeek' not in request.files:
        logger.error("缺少必要的文件")
        return jsonify({'error': 'Both files are required'}), 400
    
    last_week = request.files['lastWeek']
    this_week = request.files['thisWeek']
    
    if last_week.filename == '' or this_week.filename == '':
        logger.error("文件名为空")
        return jsonify({'error': 'Both files are required'}), 400
    
    try:
        logger.debug(f"正在读取上周文件: {last_week.filename}")
        df_last_week = pd.read_excel(last_week, dtype={'ID': str})
        
        logger.debug(f"正在读取本周文件: {this_week.filename}")
        df_this_week = pd.read_excel(this_week, dtype={'ID': str})
        
        logger.debug("处理数据比较")
        # Get unique IDs from both weeks
        last_week_ids = set(df_last_week['ID'].unique())
        this_week_ids = set(df_this_week['ID'].unique())
        
        # Calculate new IDs this week
        new_ids = this_week_ids - last_week_ids
        
        logger.debug(f"上周工单数: {len(last_week_ids)}, 本周工单数: {len(this_week_ids)}, 新增工单数: {len(new_ids)}")
        
        # 分析新增工单的Site分布和Priority分布
        new_tickets_df = df_this_week[df_this_week['ID'].isin(new_ids)]
        site_counts = new_tickets_df['Site'].value_counts()
        priority_counts = new_tickets_df['Priority'].value_counts().sort_index()  # 按优先级排序
        
        # 翻译优先级标签
        priority_counts.index = [PRIORITY_TRANSLATION.get(x, x) for x in priority_counts.index]
        
        logger.debug(f"新增工单Site分布: {site_counts.to_dict()}")
        logger.debug(f"新增工单Priority分布: {priority_counts.to_dict()}")
        
        # Prepare data for visualization
        data = {
            'last_week_count': len(last_week_ids),
            'this_week_count': len(this_week_ids),
            'new_ids_count': len(new_ids),
            'chart_data': create_comparison_charts(
                len(last_week_ids), 
                len(this_week_ids), 
                len(new_ids),
                site_counts.index.tolist(),
                site_counts.values.tolist(),
                priority_counts.index.tolist(),
                priority_counts.values.tolist()
            )
        }
        
        logger.debug("数据处理完成，返回结果")
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"处理过程中出现错误: {str(e)}")
        return jsonify({'error': str(e)}), 400

def create_comparison_charts(last_week_count, this_week_count, new_count, 
                           site_labels, site_values, 
                           priority_labels, priority_values):
    # 创建三个子图
    fig = make_subplots(
        rows=3, 
        cols=1,
        subplot_titles=('工单数据对比', '新增工单Site分布', '新增工单优先级分布'),
        vertical_spacing=0.15
    )
    
    # 添加第一个图表（工单总体对比）
    fig.add_trace(
        go.Bar(
            x=['上周工单数', '本周工单数', '新增工单数'],
            y=[last_week_count, this_week_count, new_count],
            text=[last_week_count, this_week_count, new_count],
            textposition='auto',
            name='工单数量',
            marker_color=[COLORS['primary'], COLORS['success'], COLORS['secondary']],
            hovertemplate='%{y:,}个工单<extra></extra>'
        ),
        row=1, 
        col=1
    )
    
    # 添加第二个图表（Site分布）
    fig.add_trace(
        go.Bar(
            x=site_labels,
            y=site_values,
            text=site_values,
            textposition='auto',
            name='Site分布',
            marker_color=COLORS['info'],
            hovertemplate='%{y:,}个工单<extra></extra>'
        ),
        row=2, 
        col=1
    )
    
    # 添加第三个图表（Priority分布）
    priority_colors = [COLORS['error'], COLORS['warning'], COLORS['info'], COLORS['success']]
    fig.add_trace(
        go.Bar(
            x=priority_labels,
            y=priority_values,
            text=priority_values,
            textposition='auto',
            name='优先级分布',
            marker_color=priority_colors[:len(priority_labels)],
            hovertemplate='%{y:,}个工单<extra></extra>'
        ),
        row=3, 
        col=1
    )
    
    # 更新布局
    fig.update_layout(
        height=1200,  # 设置图表总高度
        showlegend=False,
        title_text="工单分析报告",
        title_x=0.5,  # 标题居中
        title_font_size=24,
        margin=dict(t=100, l=50, r=50, b=50),  # 调整边距
        paper_bgcolor='white',  # 背景色
        plot_bgcolor='rgba(0,0,0,0)',  # 透明背景
        font=dict(family="Arial", size=12)  # 设置字体
    )
    
    # 更新所有子图的样式
    for i in range(1, 4):
        # 更新x轴样式
        fig.update_xaxes(
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor='lightgray',
            row=i,
            col=1
        )
        # 更新y轴样式
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            showline=True,
            linewidth=2,
            linecolor='lightgray',
            row=i,
            col=1
        )
    
    # 更新x轴和y轴标签
    fig.update_xaxes(title_text="数据类型", row=1, col=1)
    fig.update_yaxes(title_text="数量", row=1, col=1)
    
    fig.update_xaxes(title_text="Site", row=2, col=1)
    fig.update_yaxes(title_text="工单数量", row=2, col=1)
    
    fig.update_xaxes(title_text="优先级", row=3, col=1)
    fig.update_yaxes(title_text="工单数量", row=3, col=1)
    
    return json.loads(fig.to_json())

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=3000) 