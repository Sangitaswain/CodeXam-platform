# Technology Stack

## Backend Framework
- **Flask** (Python) - Lightweight web framework for rapid development
- **SQLite** (Phase 1) → **PostgreSQL** (Phase 2) for data persistence
- **Jinja2** templating engine for server-side rendering

## Frontend Stack
- **HTML5** with **Bootstrap CSS** for responsive design
- **JavaScript** for interactive features
- **CodeMirror** or **Monaco Editor** for syntax-highlighted code editing
- **Jinja2 templates** for server-side rendering

## Code Execution Engine
- **Multi-language support**: Python, JavaScript, Java, C++
- **Phase 1**: Restricted execution with subprocess and limited globals
- **Phase 2**: Docker containers or Judge0 API for secure sandboxing
- **Security**: Memory limits, timeout enforcement, restricted file/network access

## Development Tools
- **Python 3.8+** required
- **pip** for dependency management
- **SQLite** for local development database

## System Monitoring & Testing
- **psutil** - System and process monitoring utilities
- **requests** - HTTP client for external API integration
- **selenium** - Browser automation for UI testing (optional)
- **beautifulsoup4** - HTML parsing for accessibility testing (optional)
- **pytest** - Testing framework with coverage reporting

## Common Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run development server
python app.py
# Access at http://localhost:5000
```

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_judge.py

# Run with coverage
python -m pytest --cov=app tests/

# Run UI tests (requires browser drivers)
python -m pytest tests/test_ui.py

# Run accessibility tests
python -m pytest tests/test_accessibility.py
```

### Database Operations
```bash
# Reset database (development)
python reset_db.py

# Add sample problems
python seed_problems.py
```

## Deployment Options

### Phase 1 (Free)
- **Local development**: `python app.py`
- **Heroku free tier**: Git-based deployment
- **Vercel/Netlify**: Static frontend with serverless backend

### Phase 2 (Production)
- **DigitalOcean Droplet**: $5/month VPS
- **AWS/GCP**: Auto-scaling with managed services
- **Docker containers**: For consistent deployment environments