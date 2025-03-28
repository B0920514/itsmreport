#!/bin/bash

# 安装必要的系统包
echo "Installing system packages..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nginx

# 创建应用目录
echo "Creating application directory..."
sudo mkdir -p /var/www/itsmreport
sudo chown -R $USER:$USER /var/www/itsmreport

# 克隆代码
echo "Cloning repository..."
cd /var/www/itsmreport
git clone https://github.com/B0920514/itsmreport.git .

# 创建虚拟环境
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt
pip install gunicorn

# 创建系统服务文件
echo "Creating systemd service file..."
sudo tee /etc/systemd/system/itsmreport.service << EOF
[Unit]
Description=ITSM Report Gunicorn Service
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=/var/www/itsmreport
Environment="PATH=/var/www/itsmreport/.venv/bin"
ExecStart=/var/www/itsmreport/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:3038 app:app

[Install]
WantedBy=multi-user.target
EOF

# 创建Nginx配置文件
echo "Creating Nginx configuration..."
sudo tee /etc/nginx/sites-available/itsmreport << EOF
server {
    listen 80;
    server_name _;  # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:3038;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /var/www/itsmreport/static;
    }

    location /uploads {
        alias /var/www/itsmreport/uploads;
    }
}
EOF

# 启用Nginx配置
echo "Enabling Nginx configuration..."
sudo ln -sf /etc/nginx/sites-available/itsmreport /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 创建上传目录
echo "Creating uploads directory..."
mkdir -p uploads
chmod 755 uploads

# 重启服务
echo "Restarting services..."
sudo systemctl daemon-reload
sudo systemctl start itsmreport
sudo systemctl enable itsmreport
sudo systemctl restart nginx

echo "Deployment completed!"
echo "Please configure your domain name in /etc/nginx/sites-available/itsmreport"
echo "You can check the service status with: sudo systemctl status itsmreport" 