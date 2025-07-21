# MCP Integration Guide

This document explains the Model Context Protocol (MCP) integration in the CodeXam project and how to effectively use the configured MCP servers for development.

## Overview

MCP servers provide enhanced capabilities for AI assistants working with the CodeXam codebase. The configuration enables direct database access, development tool integration, and external service connectivity.

## Configuration Files

The MCP configuration is available in two files:

- **Main configuration**: `.kiro/settings/mcp.json` - Comprehensive server configuration with all available services
- **Working configuration**: `.kiro/settings/mcp-working.json` - Simplified configuration with only essential servers enabled

The working configuration provides a streamlined setup with core functionality while reducing resource usage and potential connection issues.

### Current Configuration

The MCP configuration includes essential servers for CodeXam development plus frontend development tools:

| Server | Status | Purpose |
|--------|--------|---------|
| **SQLite Server** | ✅ Enabled | Direct database access with full CRUD operations |
| **Time Server** | ✅ Enabled | Time and timezone operations |
| **HTTP Server** | ✅ Enabled | Web content fetching for external resources |
| **Web Search** | ❌ Disabled | Brave Search integration (requires API key) |

The streamlined MCP configuration provides:
- **Focused functionality**: Only essential servers for core development tasks
- **Reduced resource usage**: Fewer active connections and processes
- **Simplified setup**: Minimal configuration complexity
- **Enhanced stability**: Fewer potential connection issues
- **Security-focused**: Only necessary services enabled

## Available MCP Servers

### Database Servers

#### SQLite Server
- **Purpose**: Direct access to the CodeXam database
- **Database**: `./database.db`
- **Auto-approved operations**:
  - `read_query`: Execute SELECT statements
  - `list_tables`: View database tables
  - `describe_table`: Get table schema information
  - `write_query`: Execute INSERT, UPDATE, DELETE statements
  - `create_table`: Create new database tables
  - `append_insight`: Add business insights to memo

**Common Usage Examples:**
```sql
-- List all problems
SELECT id, title, difficulty FROM problems ORDER BY difficulty, title;

-- Get submission statistics
SELECT 
    language,
    result,
    COUNT(*) as count
FROM submissions 
GROUP BY language, result;

-- Find problems by difficulty
SELECT title, description FROM problems WHERE difficulty = 'Easy';
```

### Development Tools

Development tool servers have been removed from the current configuration to focus on core functionality. Use Kiro's built-in tools for:
- **File Operations**: Use Kiro's native file tools instead of filesystem server
- **Command Execution**: Use Kiro's terminal integration for shell commands
- **Python Execution**: Use Kiro's code execution capabilities
- **Version Control**: Use Kiro's Git integration features

### External Services

#### Web Search Server (Disabled)
- **Status**: Currently disabled
- **Service**: Brave Search integration
- **Auto-approved operations**: `brave_web_search`
- **Usage**: Research programming concepts, find documentation, troubleshoot issues
- **Note**: Enable when web search capabilities are needed for development

#### HTTP Server
- **Purpose**: Web content fetching
- **Auto-approved operations**: `fetch`
- **Usage**: Access documentation, APIs, external resources

### Frontend Development

Frontend development tools have been removed from the current MCP configuration to focus on core functionality. For Bootstrap and CSS framework needs:
- **Use Kiro's built-in tools**: Leverage native file editing capabilities
- **Manual Bootstrap implementation**: Reference Bootstrap documentation directly
- **HTTP server**: Fetch Bootstrap documentation and examples as needed
- **Custom CSS development**: Use Kiro's CSS editing and preview features

### Utility Servers

#### Time Server
- **Purpose**: Time and timezone operations
- **Auto-approved operations**: `get_current_time`, `convert_time`
- **Usage**: Timestamp operations, scheduling, time-based features

## Development Workflows

### Database Development
1. **Schema Inspection**: Use SQLite server to examine table structures
2. **Data Analysis**: Query submission patterns, user statistics
3. **Data Modification**: Execute INSERT, UPDATE, DELETE operations
4. **Testing**: Validate database operations before implementing in code

### Code Development
1. **File Management**: Use Kiro's native file tools for code organization
2. **Testing**: Use Kiro's code execution capabilities for Python snippets
3. **Version Control**: Use Kiro's Git integration features

### Research and Documentation
1. **HTTP Fetching**: Access external documentation and APIs
2. **Time Operations**: Handle timestamps and timezone conversions
3. **Business Insights**: Store development insights using append_insight

## Security Considerations

### Auto-Approved Operations
- Operations listed in `autoApprove` arrays execute without manual confirmation
- Review auto-approved operations periodically for security
- Remove operations from auto-approve if they become security risks

### Disabled Servers
- Some servers are disabled by default (PostgreSQL, AWS Docs, Sequential Thinking, Everything)
- Sequential Thinking and Everything servers are disabled due to package availability issues
- Enable only when needed to reduce attack surface
- Monitor enabled servers for unusual activity

### Environment Variables
- `FASTMCP_LOG_LEVEL` set to `ERROR` to reduce log noise
- Adjust log levels for debugging when needed
- Ensure sensitive environment variables are not exposed

## Troubleshooting

### Server Connection Issues
1. Verify `uvx` and `uv` are installed
2. Check server-specific dependencies
3. Review log output for error messages
4. Restart MCP servers from Kiro interface

### Database Access Problems
1. Verify `database.db` exists and is readable
2. Check file permissions
3. Ensure SQLite is properly installed
4. Test database connection manually

### Performance Issues
1. Monitor server resource usage
2. Disable unused servers
3. Adjust auto-approve settings to reduce overhead
4. Review query complexity for database operations

## Best Practices

### Database Queries
- Use parameterized queries to prevent SQL injection
- Limit result sets with `LIMIT` clauses
- Index frequently queried columns
- Test queries before implementing in application code

### File Operations
- Use relative paths when possible
- Validate file paths and names
- Handle file operation errors gracefully
- Backup important files before modifications

### External Service Usage
- Cache results when appropriate
- Handle API rate limits
- Validate external data before use
- Monitor service availability and costs

## Configuration Management

### Adding New Servers
1. Add server configuration to `mcp.json`
2. Install required dependencies with `uvx`
3. Test server functionality
4. Update documentation

### Modifying Existing Servers
1. Update configuration in `mcp.json`
2. Restart affected servers
3. Test modified functionality
4. Update auto-approve lists as needed

### Server Maintenance
1. Regularly update server packages
2. Monitor server logs for issues
3. Review and update auto-approve operations
4. Remove unused servers to improve performance

## Bootstrap MCP System

The project includes an advanced bootstrap configuration system that automates initial setup and data population tasks through MCP integration.

### Bootstrap Configuration File

The `bootstrap_mcps.yaml` file defines initialization templates that run during system setup:

```yaml
templates:
  - name: "sample_problems"
    version: "1.0.0"
    force: false
    blocking: true
    async: false
    optional: false
    mcps_location: "bootstrap/templates/sample_problems.yaml"
    values_env: "CODEXAM_SAMPLE_PROBLEMS_CONFIG"
    description: "Initialize database with sample coding problems"

  - name: "admin_user"
    version: "1.0.0"
    force: false
    blocking: true
    async: false
    optional: true
    mcps_location: "bootstrap/templates/admin_user.yaml"
    values_env: "CODEXAM_ADMIN_CONFIG"
    description: "Create default admin user and permissions"

  - name: "system_config"
    version: "1.0.0"
    force: false
    blocking: true
    async: false
    optional: false
    mcps_location: "bootstrap/templates/system_config.yaml"
    values_env: "CODEXAM_SYSTEM_CONFIG"
    description: "Initialize system configuration and settings"

  - name: "test_cases"
    version: "1.0.0"
    force: false
    blocking: false
    async: true
    optional: true
    mcps_location: "bootstrap/templates/test_cases.yaml"
    values_env: "CODEXAM_TEST_CASES_CONFIG"
    description: "Load comprehensive test cases for problems"
```

### Bootstrap Template Configuration

Each bootstrap template supports the following configuration options:

#### Core Settings
- **name**: Unique identifier for the template
- **version**: Template version for update tracking
- **description**: Human-readable description of template purpose

#### Execution Control
- **force**: Override existing data during bootstrap (default: false)
- **blocking**: Wait for template completion before continuing (default: true)
- **async**: Run template in background without blocking (default: false)
- **optional**: Skip template if environment not properly configured (default: false)

#### File References
- **mcps_location**: Path to the template definition file
- **values_env**: Environment variable containing template configuration

### Bootstrap Templates

#### Sample Problems Template
- **Purpose**: Populate database with initial coding problems
- **Execution**: Blocking, synchronous
- **Environment**: `CODEXAM_SAMPLE_PROBLEMS_CONFIG`
- **Use Case**: Essential for development and testing environments
- **Template Location**: `bootstrap/templates/sample_problems.yaml`
- **Problems Included**:
  - **Two Sum** (Easy): Classic array problem with multiple test cases
  - **Reverse Integer** (Medium): Integer manipulation with overflow handling
  - **Palindrome Number** (Easy): Number validation problem
- **Template Features**:
  - Mustache templating for customizable problem data
  - Comprehensive test cases for each problem
  - Detailed problem descriptions with examples
  - Support for multiple input/output formats

#### Admin User Template
- **Purpose**: Create default administrative user account
- **Execution**: Blocking, synchronous, optional
- **Environment**: `CODEXAM_ADMIN_CONFIG`
- **Use Case**: Optional setup for administrative access
- **Template Location**: `bootstrap/templates/admin_user.yaml`
- **Users Created**:
  - **Admin User**: Full administrative privileges (default: admin@codexam.local)
  - **Demo User**: Standard user for testing (default: demo@codexam.local)
- **Template Features**:
  - Configurable usernames and email addresses
  - Role-based access control setup
  - Environment variable customization

#### System Configuration Template
- **Purpose**: Initialize core system settings and preferences
- **Execution**: Blocking, synchronous
- **Environment**: `CODEXAM_SYSTEM_CONFIG`
- **Use Case**: Required for proper system operation

#### Test Cases Template
- **Purpose**: Load comprehensive test case data for problems
- **Execution**: Non-blocking, asynchronous, optional
- **Environment**: `CODEXAM_TEST_CASES_CONFIG`
- **Use Case**: Enhanced testing capabilities for problem validation

### Bootstrap Workflow Integration

The bootstrap system integrates with the MCP infrastructure to provide:

1. **Automated Setup**: Streamlined initialization of development environments
2. **Version Control**: Track template versions for consistent deployments
3. **Environment Flexibility**: Configure templates through environment variables
4. **Execution Control**: Fine-grained control over template execution order and behavior
5. **Error Handling**: Graceful handling of optional components and failures

### Environment Configuration

Configure bootstrap templates through environment variables:

```bash
# Sample problems configuration
export CODEXAM_SAMPLE_PROBLEMS_CONFIG='{"difficulty_distribution": {"Easy": 10, "Medium": 8, "Hard": 5}}'

# Admin user configuration (optional)
export CODEXAM_ADMIN_CONFIG='{"username": "admin", "email": "admin@codexam.dev"}'

# System configuration
export CODEXAM_SYSTEM_CONFIG='{"max_submissions_per_hour": 100, "default_timeout": 5}'

# Test cases configuration (optional)
export CODEXAM_TEST_CASES_CONFIG='{"comprehensive_mode": true, "edge_cases": true}'
```

### Bootstrap Usage Examples

#### Development Environment Setup
```bash
# Set up development environment with sample data
python bootstrap/bootstrap_runner.py --template sample_problems --template system_config

# Full setup including optional components
python bootstrap/bootstrap_runner.py --all --include-optional
```

#### Production Environment Setup
```bash
# Production setup without sample data
python bootstrap/bootstrap_runner.py --template system_config --template admin_user

# Async test case loading for production
python bootstrap/bootstrap_runner.py --template test_cases --async
```

## Integration with CodeXam Features

### Problem Management
- Query problems database for analysis
- Validate problem data integrity
- Generate problem statistics and reports
- Bootstrap sample problems for development

### Submission Processing
- Analyze submission patterns
- Debug code execution issues
- Monitor system performance
- Load comprehensive test cases through bootstrap

### User Analytics
- Track user engagement metrics
- Identify popular problems and languages
- Generate leaderboard statistics
- Initialize admin users through bootstrap

### Development Automation
- Automate testing workflows
- Generate documentation
- Deploy application updates
- Streamline environment setup through bootstrap templates

### Bootstrap-Enhanced Development
- **Rapid Environment Setup**: Quickly initialize development environments
- **Consistent Data**: Ensure consistent sample data across environments
- **Flexible Configuration**: Adapt setup to different deployment scenarios
- **Version Management**: Track and update bootstrap templates over time

This MCP integration enhances the development experience by providing direct access to project resources and external services while maintaining security through controlled access and auto-approval mechanisms. The bootstrap system further streamlines development by automating initial setup and data population tasks.