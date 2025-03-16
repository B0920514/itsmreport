from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
import logging
from werkzeug.utils import secure_filename
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 优先级翻译字典
PRIORITY_TRANSLATION = {
    '1 : très élevée': 'Priority 1: Critical',
    '2 : élevées': 'Priority 2: High',
    '3 : moyennes': 'Priority 3: Medium',
    '4 : basses': 'Priority 4: Low',
    # 添加可能的变体
    '2 : élevé': 'Priority 2: High',
    '3 : moyen': 'Priority 3: Medium',
    '4 : faible': 'Priority 4: Low'
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
    logger.debug("Starting to process file upload request")
    
    if 'lastWeek' not in request.files or 'thisWeek' not in request.files:
        logger.error("Missing required files")
        return jsonify({'error': 'Both files are required'}), 400
    
    last_week = request.files['lastWeek']
    this_week = request.files['thisWeek']
    
    if last_week.filename == '' or this_week.filename == '':
        logger.error("Empty filenames")
        return jsonify({'error': 'Both files are required'}), 400
    
    try:
        logger.debug(f"Reading last week's file: {last_week.filename}")
        df_last_week = pd.read_excel(last_week, dtype={'ID': str})
        
        logger.debug(f"Reading this week's file: {this_week.filename}")
        df_this_week = pd.read_excel(this_week, dtype={'ID': str})
        
        # Convert Created On to datetime with European date format (DD.MM.YYYY)
        df_last_week['Created On'] = pd.to_datetime(df_last_week['Created On'], format='%d.%m.%Y', dayfirst=True)
        df_this_week['Created On'] = pd.to_datetime(df_this_week['Created On'], format='%d.%m.%Y', dayfirst=True)
        
        # Filter out data before 2022
        df_last_week = df_last_week[df_last_week['Created On'].dt.year >= 2022]
        df_this_week = df_this_week[df_this_week['Created On'].dt.year >= 2022]
        
        logger.debug(f"Filtered data after 2022: Last week records: {len(df_last_week)}, This week records: {len(df_this_week)}")
        
        # Add week number and year columns for both dataframes
        # Use week of US calendar (Sunday start) instead of ISO calendar
        df_last_week['Week'] = df_last_week['Created On'].dt.strftime('%U').astype(int) + 1  # strftime returns 0-based week numbers
        df_last_week['Year'] = df_last_week['Created On'].dt.year
        df_this_week['Week'] = df_this_week['Created On'].dt.strftime('%U').astype(int) + 1  # Adding 1 to match with 1-based week numbers
        df_this_week['Year'] = df_this_week['Created On'].dt.year
        
        # Combine both dataframes for weekly analysis
        combined_df = pd.concat([df_last_week, df_this_week])
        
        # Get weekly ticket counts grouped by year
        weekly_counts = {}
        for year in sorted(combined_df['Year'].unique()):
            year_data = combined_df[combined_df['Year'] == year]
            counts = year_data.groupby('Week').size().reset_index(name='Count')
            counts['Year'] = year
            counts['Week_Label'] = f"{year}-W" + counts['Week'].astype(str).str.zfill(2)
            weekly_counts[year] = counts.sort_values('Week')
            
            # Add missing weeks with zero count
            all_weeks = pd.DataFrame({'Week': range(1, 54)})  # 53 weeks maximum in a year
            weekly_counts[year] = pd.merge(all_weeks, counts, on='Week', how='left').fillna(0)
            weekly_counts[year]['Year'] = year
            weekly_counts[year]['Count'] = weekly_counts[year]['Count'].astype(int)
            weekly_counts[year]['Week_Label'] = f"{year}-W" + weekly_counts[year]['Week'].astype(str).str.zfill(2)
            # Filter out weeks with zero count
            weekly_counts[year] = weekly_counts[year][weekly_counts[year]['Count'] > 0]
            weekly_counts[year] = weekly_counts[year].sort_values('Week')
        
        # Get unique years for filtering (only 2022 and later)
        available_years = sorted([year for year in combined_df['Year'].unique().tolist() if year >= 2022])
        
        # 在读取数据后立即翻译优先级
        df_last_week['Priority'] = df_last_week['Priority'].map(PRIORITY_TRANSLATION)
        df_this_week['Priority'] = df_this_week['Priority'].map(PRIORITY_TRANSLATION)
        
        logger.debug("Processing data comparison")
        # Get unique IDs from both weeks
        last_week_ids = set(df_last_week['ID'].unique())
        this_week_ids = set(df_this_week['ID'].unique())
        
        # Calculate new IDs this week
        new_ids = this_week_ids - last_week_ids
        
        logger.debug(f"Last week tickets: {len(last_week_ids)}, This week tickets: {len(this_week_ids)}, New tickets: {len(new_ids)}")
        
        # Analyze distribution of new tickets by Site and Priority
        new_tickets_df = df_this_week[df_this_week['ID'].isin(new_ids)]
        site_counts = new_tickets_df['Site'].value_counts()
        priority_counts = new_tickets_df['Priority'].value_counts().sort_index()
        
        logger.debug(f"New tickets Site distribution: {site_counts.to_dict()}")
        logger.debug(f"New tickets Priority distribution: {priority_counts.to_dict()}")
        
        # Prepare data for visualization
        data = {
            'last_week_count': len(last_week_ids),
            'this_week_count': len(this_week_ids),
            'new_ids_count': len(new_ids),
            'available_years': available_years,
            'chart_data': create_comparison_charts(
                len(last_week_ids), 
                len(this_week_ids), 
                len(new_ids),
                site_counts.index.tolist(),
                site_counts.values.tolist(),
                priority_counts.index.tolist(),
                priority_counts.values.tolist(),
                weekly_counts
            )
        }
        
        logger.debug("Data processing completed, returning results")
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error occurred during processing: {str(e)}")
        return jsonify({'error': str(e)}), 400

def create_comparison_charts(last_week_count, this_week_count, new_count, 
                           site_labels, site_values, 
                           priority_labels, priority_values,
                           weekly_counts):
    charts = []
    
    # First chart (overall ticket comparison)
    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            x=['Last Week', 'This Week', 'New Tickets'],
            y=[last_week_count, this_week_count, new_count],
            text=[last_week_count, this_week_count, new_count],
            textposition='auto',
            name='Ticket Count',
            marker_color=[COLORS['primary'], COLORS['success'], COLORS['secondary']],
            hovertemplate='%{y:,} tickets<extra></extra>'
        )
    )
    fig1.update_layout(
        title_text="Ticket Count Comparison",
        title_x=0.5,
        height=400,
        showlegend=False,
        margin=dict(t=50, l=50, r=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12)
    )
    fig1.update_xaxes(title_text="Data Type", showgrid=False, showline=True, linewidth=2, linecolor='lightgray')
    fig1.update_yaxes(title_text="Count", showgrid=True, gridwidth=1, gridcolor='lightgray', showline=True, linewidth=2, linecolor='lightgray')
    charts.append(json.loads(fig1.to_json()))
    
    # Second chart (Site distribution)
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=site_labels,
            y=site_values,
            text=site_values,
            textposition='auto',
            name='Site Distribution',
            marker_color=COLORS['info'],
            hovertemplate='%{y:,} tickets<extra></extra>'
        )
    )
    fig2.update_layout(
        title_text="New Tickets by Site",
        title_x=0.5,
        height=400,
        showlegend=False,
        margin=dict(t=50, l=50, r=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12)
    )
    fig2.update_xaxes(title_text="Site", showgrid=False, showline=True, linewidth=2, linecolor='lightgray')
    fig2.update_yaxes(title_text="Ticket Count", showgrid=True, gridwidth=1, gridcolor='lightgray', showline=True, linewidth=2, linecolor='lightgray')
    charts.append(json.loads(fig2.to_json()))
    
    # Third chart (Priority distribution)
    fig3 = go.Figure()
    priority_colors = [COLORS['error'], COLORS['warning'], COLORS['info'], COLORS['success']]
    fig3.add_trace(
        go.Bar(
            x=priority_labels,
            y=priority_values,
            text=priority_values,
            textposition='auto',
            name='Priority Distribution',
            marker_color=priority_colors[:len(priority_labels)],
            hovertemplate='%{y:,} tickets<extra></extra>'
        )
    )
    fig3.update_layout(
        title_text="New Tickets by Priority",
        title_x=0.5,
        height=400,
        showlegend=False,
        margin=dict(t=50, l=50, r=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12)
    )
    fig3.update_xaxes(title_text="Priority", showgrid=False, showline=True, linewidth=2, linecolor='lightgray')
    fig3.update_yaxes(title_text="Ticket Count", showgrid=True, gridwidth=1, gridcolor='lightgray', showline=True, linewidth=2, linecolor='lightgray')
    charts.append(json.loads(fig3.to_json()))
    
    # Fourth chart (Weekly distribution)
    fig4 = go.Figure()
    
    # Add traces for each year
    for year in sorted(weekly_counts.keys()):
        year_data = weekly_counts[year]
        visible = (year == 2025)  # Default to showing 2025
        
        fig4.add_trace(
            go.Bar(
                x=year_data['Week_Label'],
                y=year_data['Count'],
                text=year_data['Count'],
                textposition='auto',
                name=f'Weekly Distribution {year}',
                marker_color=COLORS['primary'],
                hovertemplate='%{x}<br>%{y:,} tickets<extra></extra>',
                visible=visible
            )
        )
    
    # Create year buttons
    year_buttons = []
    for i, year in enumerate(sorted(weekly_counts.keys())):
        visibility = [False] * len(weekly_counts)
        visibility[i] = True
        year_buttons.append(dict(
            args=[{"visible": visibility}],
            label=str(year),
            method="update"
        ))
    
    fig4.update_layout(
        title_text="Weekly Ticket Distribution",
        title_x=0.5,
        height=400,
        showlegend=False,
        margin=dict(t=50, l=50, r=50, b=50),
        paper_bgcolor='white',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        updatemenus=[
            dict(
                buttons=year_buttons,
                direction="down",
                showactive=True,
                x=0.1,
                y=1.15,
                xanchor="left",
                yanchor="top",
                bgcolor='white',
                bordercolor='#2196F3',
                borderwidth=2,
                font=dict(size=14),
                pad=dict(r=10, t=10)
            )
        ],
        annotations=[
            dict(
                text="Select Year:",
                x=0.1,
                y=1.2,
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=14, color='#2196F3'),
                xanchor="right"
            )
        ]
    )
    fig4.update_xaxes(title_text="Week Number", showgrid=False, showline=True, linewidth=2, linecolor='lightgray')
    fig4.update_yaxes(title_text="Ticket Count", showgrid=True, gridwidth=1, gridcolor='lightgray', showline=True, linewidth=2, linecolor='lightgray')
    charts.append(json.loads(fig4.to_json()))
    
    return charts

if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=3000) 