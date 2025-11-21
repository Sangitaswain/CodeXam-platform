# CodeXam Deployment Guide

This guide provides comprehensive instructions for deploying the CodeXam platform in various environments.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- Node.js 14+ (for JavaScript execution)
- Java 11+ (for Java execution)
- GCC/G++ (for C++ execution)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CodeXam
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-production.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   python scripts/init_db.py
   python scripts/seed_problems.py  # Optional: Add sample problems
   ```

5. **Build assets**
   ```bash
   python scripts/build_assets.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open http://localhost:5000 in your browser
   - Admin panel: http://localhost:5000/admin
   - Performance monitoring: http://localhost:5000/admin/performance

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Basic deployment**
   ```bash
   docker-compose up -d
   ```

2. **With PostgreSQL database**
   ```bash
   docker-compose --profile postgres up -d
   ```

3. **Full production setup with Nginx**
   ```bash
   docker-compose --profile postgres --profile nginx up -d
   ```

### Using Docker directly

1. **Build the image**
   ```bash
   docker build -t codexam:latest .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name codexam \
     -p 5000:5000 \
     -e FLASK_ENV=production \
     -e SECRET_KEY=your-secret-key \
     -v codexam_data:/app/data \
     codexam:latest
   ```

## ☁️ Cloud Deployment

### Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Follow instructions at https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set JUDGE_TIMEOUT=5
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Initialize database**
   ```bash
   heroku run python scripts/init_db.py
   heroku run python scripts/seed_problems.py
   ```

### DigitalOcean Droplet

1. **Create droplet** (Ubuntu 20.04 LTS, minimum 2GB RAM)

2. **Connect and update system**
   ```bash
   ssh root@your-droplet-ip
   apt update && apt upgrade -y
   ```

3. **Install dependencies**
   ```bash
   apt install -y python3 python3-pip python3-venv nodejs npm openjdk-11-jdk gcc g++
   ```

4. **Create application user**
   ```bash
   useradd -m -s /bin/bash codexam
   su - codexam
   ```

5. **Deploy application**
   ```bash
   git clone <repository-url>
   cd CodeXam
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements-production.txt
   ```

6. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with production settings
   ```

7. **Set up systemd service**
   ```bash
   sudo nano /etc/systemd/system/codexam.service
   ```
   
   ```ini
   [Unit]
   Description=CodeXam Application
   After=network.target
   
   [Service]
   Type=simple
   User=codexam
   WorkingDirectory=/home/codexam/CodeXam
   Environment=PATH=/home/codexam/CodeXam/venv/bin
   ExecStart=/home/codexam/CodeXam/venv/bin/python app.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

8. **Start service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable codexam
   sudo systemctl start codexam
   ```

### AWS EC2 Deployment

1. **Launch EC2 instance** (t3.medium or larger, Ubuntu 20.04 LTS)

2. **Configure security group**
   - Allow HTTP (80) and HTTPS (443) from anywhere
   - Allow SSH (22) from your IP

3. **Connect and install dependencies**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3 python3-pip python3-venv nodejs npm openjdk-11-jdk gcc g++ nginx
   ```

4. **Deploy application** (similar to DigitalOcean steps)

5. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/codexam
   ```
   
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       location /static {
           alias /home/ubuntu/CodeXam/static;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

6. **Enable site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/codexam /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Environment mode | `development` | No |
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` | Yes (production) |
| `DATABASE_URL` | Database connection string | `sqlite:///database.db` | No |
| `JUDGE_TIMEOUT` | Code execution timeout (seconds) | `5` | No |
| `JUDGE_MEMORY_LIMIT` | Memory limit (bytes) | `134217728` | No |
| `ENABLE_PERFORMANCE_MONITORING` | Enable performance monitoring | `True` | No |
| `ADMIN_USERNAME` | Admin username | `admin` | No |
| `ADMIN_PASSWORD` | Admin password | `change-this-password` | Yes (production) |

### Database Configuration

#### SQLite (Default)
```bash
DATABASE_URL=sqlite:///database.db
```

#### PostgreSQL
```bash
DATABASE_URL=postgresql://username:password@localhost/codexam
```

#### MySQL
```bash
DATABASE_URL=mysql://username:password@localhost/codexam
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Change default `ADMIN_PASSWORD`
- [ ] Use HTTPS in production
- [ ] Enable `SESSION_COOKIE_SECURE=True`
- [ ] Set up firewall rules
- [ ] Regular security updates
- [ ] Monitor application logs
- [ ] Use strong database passwords
- [ ] Implement rate limiting
- [ ] Regular backups

### SSL/TLS Setup

1. **Using Let's Encrypt (Certbot)**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. **Manual SSL certificate**
   - Place certificate files in `/etc/nginx/ssl/`
   - Update Nginx configuration

## 📊 Monitoring and Maintenance

### Application Monitoring

1. **Performance Dashboard**
   - Access: http://your-domain.com/admin/performance
   - Monitor CPU, memory, request times
   - Track code execution metrics

2. **Log Monitoring**
   ```bash
   # Application logs
   tail -f codexam.log
   
   # System logs
   sudo journalctl -u codexam -f
   ```

3. **Health Checks**
   ```bash
   curl http://your-domain.com/health
   ```

### Database Maintenance

1. **Backup SQLite database**
   ```bash
   cp database.db database_backup_$(date +%Y%m%d).db
   ```

2. **Backup PostgreSQL database**
   ```bash
   pg_dump codexam > codexam_backup_$(date +%Y%m%d).sql
   ```

3. **Database cleanup** (optional)
   ```bash
   python -c "
   from database import get_db
   db = get_db()
   # Clean old submissions (older than 30 days)
   db.execute_update('DELETE FROM submissions WHERE submitted_at < date(\"now\", \"-30 days\")')
   "
   ```

### Performance Optimization

1. **Asset optimization**
   ```bash
   python scripts/build_assets.py
   ```

2. **Cache management**
   ```bash
   python -c "from cache import cache; cache.clear()"
   ```

3. **Database optimization**
   ```bash
   python -c "
   from database import get_db
   db = get_db()
   db.execute_update('VACUUM')  # SQLite only
   db.execute_update('ANALYZE')
   "
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **Permission denied errors**
   ```bash
   sudo chown -R codexam:codexam /path/to/codexam
   chmod +x app.py
   ```

3. **Database connection errors**
   - Check DATABASE_URL format
   - Verify database server is running
   - Check network connectivity

4. **Code execution failures**
   - Verify Node.js installation: `node --version`
   - Verify Java installation: `java --version`
   - Verify GCC installation: `gcc --version`

5. **Memory issues**
   - Increase server memory
   - Adjust `JUDGE_MEMORY_LIMIT`
   - Monitor with performance dashboard

### Log Analysis

1. **Application errors**
   ```bash
   grep ERROR codexam.log
   ```

2. **Performance issues**
   ```bash
   grep "slow" codexam.log
   ```

3. **Security issues**
   ```bash
   grep "security" codexam.log
   ```

## 📞 Support

For deployment issues:

1. Check the troubleshooting section above
2. Review application logs
3. Check system resource usage
4. Verify all dependencies are installed
5. Ensure environment variables are set correctly

## 🔄 Updates and Maintenance

### Updating the Application

1. **Backup current installation**
   ```bash
   cp -r CodeXam CodeXam_backup_$(date +%Y%m%d)
   ```

2. **Pull latest changes**
   ```bash
   cd CodeXam
   git pull origin main
   ```

3. **Update dependencies**
   ```bash
   pip install -r requirements-production.txt --upgrade
   ```

4. **Run database migrations** (if any)
   ```bash
   python migrate_db.py  # If migration script exists
   ```

5. **Rebuild assets**
   ```bash
   python scripts/build_assets.py
   ```

6. **Restart application**
   ```bash
   sudo systemctl restart codexam
   ```

### Scheduled Maintenance

Set up cron jobs for regular maintenance:

```bash
# Daily database backup (2 AM)
0 2 * * * /home/codexam/backup_db.sh

# Weekly log rotation (Sunday 3 AM)
0 3 * * 0 /usr/sbin/logrotate /etc/logrotate.d/codexam

# Monthly asset optimization (1st day, 4 AM)
0 4 1 * * cd /home/codexam/CodeXam && python scripts/build_assets.py
```

## 📚 Additional Resources

- [Implementation Guide](IMPLEMENTATION_GUIDE.md) - Complete development history and technical details
- [Style Guide](STYLE_GUIDE.md) - Design system and UI/UX standards
- [Database Management Guide](DATABASE_MANAGEMENT_GUIDE.md) - Database operations and maintenance
- [Accessibility Testing](ACCESSIBILITY_TESTING.md) - Accessibility compliance and testing procedures
- [Cross-Browser Testing](CROSS_BROWSER_TESTING.md) - Browser compatibility testing guide

---

**Happy Coding! 🚀**

The CodeXam platform is now ready for deployment. Choose the deployment method that best fits your needs and infrastructure requirements.