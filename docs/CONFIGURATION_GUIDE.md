# CodeXam Configuration Guide

This guide explains the standardized configuration system for the CodeXam platform, including dependency management, environment configuration, and testing setup.

## 📦 Dependencies Management

### Single Requirements File
The project now uses a single, comprehensive `requirements.txt` file that consolidates all dependencies with clear organization:

- **Core Flask Application**: Essential web framework components (Flask, Jinja2, Werkzeug)
- **Environment and Configuration**: Environment variable loading and YAML support
- **System Monitoring**: Performance and resource monitoring tools (psutil)
- **HTTP and Networking**: External service communication (requests, urllib3)
- **Template Processing**: Mustache template support for dynamic content
- **Testing Framework**: Development and CI testing tools (pytest, coverage)
- **Optional Components**: Browser automation (Selenium) and HTML parsing (BeautifulSoup)
- **Production Notes**: Comprehensive deployment guidance and recommendations

### Installation
```bash
# Install all dependencies
pip install -r requirements.txt

# For development with additional tools
pip install ipython ipdb black flake8 mypy

# For accessibility testing
pip install webdriver-manager lxml pillow pandas numpy

# For production deployment
pip install gunicorn psycopg2-binary redis
```

### Requirements File Structure
The new `requirements.txt` includes:
- **Detailed Comments**: Each section clearly documented with purpose
- **Version Pinning**: All packages pinned to specific versions for reproducibility
- **Production Guidance**: Inline notes for production deployment considerations
- **Optional Dependencies**: Clear separation of core vs. optional packages
- **Windows Support**: Commented Windows-specific dependencies
- **Development Tools**: Suggestions for enhanced development experience

### Removed Files
- `requirements-production.txt` - Consolidated into main file with production notes
- `requirements-accessibility.txt` - Moved to optional installation section

## 🔧 Environment Configuration

### Environment Variables (.env.example)
The `.env.example` file provides a comprehensive template with:

#### Flask Application Settings
- `FLASK_ENV`: Environment mode (development/testing/production)
- `SECRET_KEY`: Cryptographic key for sessions and security
- `DEBUG`: Debug mode toggle

#### Server Configuration
- `PORT`: Application port (default: 5000)
- `HOST`: Host interface (default: 0.0.0.0)

#### Database Settings
- `DATABASE_URL`: Database connection string
- Support for SQLite (development) and PostgreSQL (production)

#### Code Execution Engine
- `JUDGE_TIMEOUT`: Code execution timeout (seconds)
- `JUDGE_MEMORY_LIMIT`: Memory limit for code execution

#### Performance and Caching
- `ENABLE_PERFORMANCE_MONITORING`: System monitoring toggle
- Cache TTL settings for different data types
- Performance logging configuration

#### Security Settings
- CSRF protection configuration
- Session cookie security settings
- Admin credentials

#### Asset Optimization
- Asset minification and compression settings
- Static file serving configuration

#### Rate Limiting
- Request rate limiting configuration
- Burst allowance settings

### Setup Instructions
1. Copy `.env.example` to `.env`
2. Update values for your environment
3. **CRITICAL**: Change `SECRET_KEY` and `ADMIN_PASSWORD` in production
4. Set `FLASK_ENV=production` and `DEBUG=False` for production

## 🧪 Testing Configuration

### Device Testing Configuration (device_testing_config.json)
Standardized configuration for cross-browser and device testing:

- **Browser Support**: Chrome, Firefox, Edge, Safari
- **Device Categories**: Desktop, tablet, mobile with specific configurations
- **Test Scenarios**: Page load, responsive layout, navigation, forms
- **Responsive Breakpoints**: Bootstrap 5 breakpoint definitions
- **Reporting**: Multiple output formats with comprehensive metrics

### Accessibility Testing Configuration (accessibility_config.json)
WCAG 2.1 AA compliance testing configuration:

- **WCAG Criteria**: Color contrast, keyboard navigation, ARIA labels
- **Test Categories**: Critical, major, and minor issue classification
- **Browser Configuration**: Chrome and Firefox support
- **Reporting**: HTML, JSON, and text output formats
- **Thresholds**: Configurable pass/fail criteria

### Lighthouse Configuration (.lighthouserc.json)
Automated accessibility and performance auditing:

- **URL Testing**: All major application pages
- **Categories**: Accessibility, best practices, SEO
- **Assertions**: Specific WCAG compliance checks
- **Reporting**: Temporary public storage for CI/CD

## 📁 File Organization

### Configuration Files Structure
```
CodeXam/
├── requirements.txt              # Single consolidated dependencies file
├── .env.example                 # Environment configuration template
├── .gitignore                   # Enhanced to prevent clutter
├── device_testing_config.json   # Cross-browser testing configuration
├── accessibility_config.json    # Accessibility testing configuration
├── .lighthouserc.json          # Lighthouse CI configuration
└── CONFIGURATION_GUIDE.md       # This guide
```

### Enhanced Requirements Management
- **Single Source of Truth**: All dependencies in one well-organized file
- **Clear Documentation**: Each package purpose explained with inline comments
- **Production Ready**: Deployment guidance and optional component separation
- **Version Control**: All packages pinned for reproducible deployments

## 🔒 Security Considerations

### Environment Variables
- Never commit `.env` files to version control
- Use strong, unique `SECRET_KEY` in production
- Change default `ADMIN_PASSWORD`
- Enable `SESSION_COOKIE_SECURE` with HTTPS

### Configuration Security
- Sensitive data in environment variables only
- No hardcoded credentials in configuration files
- Proper file permissions on configuration files

## 🚀 Production Deployment

### Environment Setup
1. Set production environment variables:
   ```bash
   FLASK_ENV=production
   DEBUG=False
   SECRET_KEY=<strong-random-key>
   SESSION_COOKIE_SECURE=True
   ```

2. Database configuration:
   ```bash
   DATABASE_URL=postgresql://username:password@localhost/codexam
   ```

3. Security settings:
   ```bash
   CSRF_ENABLED=True
   RATE_LIMIT_ENABLED=True
   ```

### Additional Production Dependencies
```bash
pip install gunicorn psycopg2-binary redis
```

### Production Checklist
- [ ] Environment variables configured
- [ ] Strong SECRET_KEY generated
- [ ] Admin password changed
- [ ] Database migrated to PostgreSQL
- [ ] SSL/TLS certificates configured
- [ ] Reverse proxy (Nginx/Apache) set up
- [ ] Firewall and security groups configured
- [ ] Logging and monitoring enabled
- [ ] Backup procedures implemented

## 🔄 Configuration Updates

### Adding New Configuration
1. Add to `.env.example` with documentation
2. Update this guide with new settings
3. Add to appropriate JSON config if needed
4. Update deployment documentation

### Modifying Existing Configuration
1. Update `.env.example` template
2. Document changes in this guide
3. Test in development environment
4. Update production deployment notes

## 🧹 Maintenance

### Regular Tasks
- Review and update dependency versions
- Audit security settings
- Clean up temporary configuration files
- Update documentation with changes

### Monitoring
- Check for deprecated configuration options
- Monitor for security vulnerabilities
- Review performance impact of configuration changes
- Validate configuration in different environments

## 📚 Related Documentation

- [Implementation Guide](IMPLEMENTATION_GUIDE.md) - Complete development details
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [Style Guide](STYLE_GUIDE.md) - Development standards and conventions
- [Database Management Guide](DATABASE_MANAGEMENT_GUIDE.md) - Database operations

## 🆘 Troubleshooting

### Common Issues

#### Environment Variables Not Loading
- Verify `.env` file exists and is readable
- Check file permissions
- Ensure `python-dotenv` is installed

#### Configuration Validation Errors
- Check JSON syntax in configuration files
- Verify all required fields are present
- Validate data types match expected values

#### Testing Configuration Issues
- Ensure browser drivers are installed
- Check network connectivity for external services
- Verify file paths and permissions

### Getting Help
1. Check this configuration guide
2. Review error logs for specific issues
3. Validate configuration against examples
4. Test in isolated environment

---

**Configuration Status**: ✅ **STANDARDIZED**  
**Last Updated**: January 28, 2025  
**Version**: 1.1 - Enhanced Requirements Management  
**Compatibility**: CodeXam v1.0+