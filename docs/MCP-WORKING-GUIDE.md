# CodeXam Bootstrap MCP Working Guide

This guide explains how to use the Bootstrap MCP (Model Context Protocol) system in CodeXam, which automates the initialization and configuration of your coding platform.

## Overview

The Bootstrap MCP system is inspired by DataHub's bootstrap approach but tailored for CodeXam. It allows you to:

- **Automate setup**: Initialize database with sample problems and configuration
- **Template-driven**: Use customizable templates with environment variable overrides
- **Version control**: Track execution history to prevent duplicate runs
- **Flexible execution**: Support blocking/non-blocking and sync/async operations
- **Error handling**: Graceful failure handling with optional components

## Quick Start

### 1. Basic Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run bootstrap MCPs
python run_bootstrap.py
```

### 2. Advanced Usage

```bash
# Run only blocking MCPs
python bootstrap/bootstrap_runner.py --blocking-only

# Use custom configuration
python bootstrap/bootstrap_runner.py --config my_bootstrap.yaml

# Enable verbose logging
python bootstrap/bootstrap_runner.py --verbose
```

## Configuration Structure

### bootstrap_mcps.yaml

The main configuration file defines templates to execute:

```yaml
templates:
  - name: "sample_problems"           # Unique template name
    version: "1.0.0"                 # Version for tracking
    force: false                     # Skip if already executed
    blocking: true                   # Run before app starts
    async: false                     # Synchronous execution
    optional: false                  # Required for success
    mcps_location: "bootstrap/templates/sample_problems.yaml"
    values_env: "CODEXAM_SAMPLE_PROBLEMS_CONFIG"
    description: "Initialize database with sample coding problems"
```

### Template Files

Templates use Mustache syntax for variable substitution:

```yaml
# bootstrap/templates/sample_problems.yaml
- type: problem
  data:
    title: "{{#title}}{{title}}{{/title}}{{^title}}Two Sum{{/title}}"
    difficulty: "{{#difficulty}}{{difficulty}}{{/difficulty}}{{^difficulty}}Easy{{/difficulty}}"
    description: |
      {{#description}}{{description}}{{/description}}{{^description}}
      Default problem description here...
      {{/description}}
```

## Environment Configuration

### Setting Custom Values

Use environment variables to customize templates:

```bash
# Custom problem configuration
export CODEXAM_SAMPLE_PROBLEMS_CONFIG='{"title":"Custom Problem","difficulty":"Hard"}'

# Custom admin user
export CODEXAM_ADMIN_CONFIG='{"admin_username":"myAdmin","admin_email":"admin@example.com"}'

# Custom system settings
export CODEXAM_SYSTEM_CONFIG='{"app_name":"My CodeXam","execution_timeout":"10"}'
```

### JSON Structure Examples

#### Sample Problems Configuration
```json
{
  "title": "Custom Algorithm Problem",
  "difficulty": "Medium",
  "description": "Solve this custom algorithmic challenge..."
}
```

#### Admin User Configuration
```json
{
  "admin_username": "platform_admin",
  "admin_email": "admin@mycompany.com",
  "admin_role": "admin",
  "demo_username": "demo_user",
  "demo_email": "demo@mycompany.com"
}
```

#### System Configuration
```json
{
  "app_name": "My Coding Platform",
  "app_version": "2.0.0",
  "max_code_length": "15000",
  "execution_timeout": "8",
  "memory_limit": "256",
  "theme": "dark",
  "items_per_page": "25"
}
```

## Template Types

### 1. Problem Templates

Create coding problems with test cases:

```yaml
- type: problem
  data:
    title: "Problem Title"
    difficulty: "Easy|Medium|Hard"
    description: "Problem description with examples"
    test_cases:
      - input: { "nums": [1,2,3], "target": 5 }
        expected_output: [1,2]
        description: "Test case description"
```

### 2. User Templates

Create user accounts:

```yaml
- type: user
  data:
    username: "user123"
    email: "user@example.com"
    role: "user|admin"
```

### 3. Configuration Templates

Set system configuration:

```yaml
- type: config
  data:
    setting_key: "setting_value"
    complex_setting:
      nested_key: "nested_value"
```

### 4. Test Case Templates

Add comprehensive test cases to existing problems:

```yaml
- type: test_case
  data:
    problem_title: "Two Sum"
    test_cases:
      - input: { "nums": [2,7,11,15], "target": 9 }
        expected_output: [0,1]
        description: "Basic test case"
```

## Execution Modes

### Blocking vs Non-Blocking

```yaml
# Blocking: Must complete before app starts
blocking: true

# Non-blocking: Can run in background
blocking: false
```

### Synchronous vs Asynchronous

```yaml
# Synchronous: Wait for completion
async: false

# Asynchronous: Run in background
async: true
```

### Optional vs Required

```yaml
# Required: Failure stops bootstrap
optional: false

# Optional: Failure is logged but doesn't stop bootstrap
optional: true
```

## Execution Tracking

The system tracks execution history in the database:

```sql
-- View execution history
SELECT name, version, executed_at, success, error_message 
FROM bootstrap_execution_history 
ORDER BY executed_at DESC;

-- Check if template was executed
SELECT success FROM bootstrap_execution_history 
WHERE name = 'sample_problems' AND version = '1.0.0';
```

### Force Re-execution

To re-run a template that was already executed:

```yaml
# In bootstrap_mcps.yaml
- name: "sample_problems"
  version: "1.0.0"
  force: true  # This will re-run even if previously executed
```

## Advanced Features

### Custom Configuration Files

```bash
# Use custom bootstrap configuration
export SYSTEM_UPDATE_BOOTSTRAP_MCP_CONFIG="/path/to/my_bootstrap.yaml"
python bootstrap/bootstrap_runner.py
```

### Template Inheritance

Templates can reference shared values:

```yaml
# In template file
common_settings: &common
  created_by: "bootstrap"
  version: "1.0.0"

- type: problem
  data:
    <<: *common
    title: "Problem 1"
    
- type: problem
  data:
    <<: *common
    title: "Problem 2"
```

### Conditional Templates

Use Mustache conditionals for flexible templates:

```yaml
# Only create admin user if configured
{{#admin_username}}
- type: user
  data:
    username: "{{admin_username}}"
    role: "admin"
{{/admin_username}}

# Default user if no admin configured
{{^admin_username}}
- type: user
  data:
    username: "default_admin"
    role: "admin"
{{/admin_username}}
```

## Error Handling

### Common Issues

1. **Template Not Found**
   ```
   ERROR: Template file not found: bootstrap/templates/missing.yaml
   ```
   Solution: Verify file path and ensure template exists

2. **Invalid JSON in Environment Variable**
   ```
   ERROR: Failed to render template: Expecting ',' delimiter
   ```
   Solution: Validate JSON syntax in environment variables

3. **Database Connection Error**
   ```
   ERROR: Failed to create tracking table: database is locked
   ```
   Solution: Ensure database is not in use by another process

4. **Template Syntax Error**
   ```
   ERROR: Failed to execute MCPs: mapping values are not allowed here
   ```
   Solution: Check YAML syntax in template files

### Debugging

Enable verbose logging:

```bash
python bootstrap/bootstrap_runner.py --verbose
```

Check execution history:

```python
from bootstrap.bootstrap_runner import BootstrapMCPRunner
runner = BootstrapMCPRunner()
# Check if template was executed
success = runner._is_already_executed("sample_problems", "1.0.0")
print(f"Template executed: {success}")
```

## Integration with CodeXam

### Database Schema

The bootstrap system creates these tables:

- `problems`: Coding problems with test cases
- `users`: User accounts and roles
- `system_config`: Application configuration
- `bootstrap_execution_history`: Execution tracking

### Application Integration

```python
# In your Flask app
from bootstrap.bootstrap_runner import BootstrapMCPRunner

def initialize_app():
    # Run bootstrap on app startup
    runner = BootstrapMCPRunner()
    runner.run_bootstrap(blocking_only=True)
```

### Configuration Access

```python
# Access bootstrap configuration in your app
import sqlite3
import json

def get_system_config(key):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute(
            "SELECT value FROM system_config WHERE key = ?", 
            (key,)
        )
        result = cursor.fetchone()
        if result:
            try:
                return json.loads(result[0])
            except:
                return result[0]
    return None

# Usage
app_name = get_system_config('app_name')
max_code_length = int(get_system_config('max_code_length'))
```

## Best Practices

### 1. Version Management

- Increment version numbers when changing templates
- Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
- Document changes in template descriptions

### 2. Environment Variables

- Use descriptive environment variable names
- Validate JSON syntax before deployment
- Provide sensible defaults in templates

### 3. Error Handling

- Mark non-critical templates as `optional: true`
- Test templates in development environment
- Monitor execution logs in production

### 4. Security

- Validate all input data in templates
- Use parameterized database queries
- Avoid exposing sensitive data in templates

### 5. Performance

- Use `async: true` for non-critical templates
- Limit the number of database operations per template
- Consider batch operations for large datasets

## Examples

### Complete Setup Example

```bash
# 1. Set up environment
export CODEXAM_ADMIN_CONFIG='{"admin_username":"admin","admin_email":"admin@codexam.local"}'
export CODEXAM_SYSTEM_CONFIG='{"app_name":"CodeXam Pro","execution_timeout":"10"}'

# 2. Run bootstrap
python run_bootstrap.py

# 3. Verify setup
python -c "
import sqlite3
conn = sqlite3.connect('database.db')
problems = conn.execute('SELECT COUNT(*) FROM problems').fetchone()[0]
users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
print(f'Created {problems} problems and {users} users')
"

# 4. Start application
python app.py
```

### Custom Template Example

Create `my_problems.yaml`:

```yaml
- type: problem
  data:
    title: "{{#custom_title}}{{custom_title}}{{/custom_title}}{{^custom_title}}Default Problem{{/custom_title}}"
    difficulty: "{{difficulty}}"
    description: |
      {{description}}
      
      This problem was created via Bootstrap MCP system.
    test_cases:
      - input: {{test_input}}
        expected_output: {{test_output}}
```

Use it:

```bash
export MY_PROBLEM_CONFIG='{"custom_title":"My Algorithm","difficulty":"Hard","description":"Solve this challenge","test_input":{"n":5},"test_output":120}'
python bootstrap/bootstrap_runner.py --config my_bootstrap.yaml
```

This Bootstrap MCP system provides a powerful, flexible way to initialize and configure your CodeXam platform with minimal manual setup while maintaining full customization capabilities.