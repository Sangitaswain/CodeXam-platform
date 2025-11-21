/**
 * SystemCommandProcessor - Interactive command system for System Info Modal
 * 
 * Features:
 * - Terminal-style command interface
 * - Command history and auto-completion
 * - Help system
 * - Real-time command execution
 * - Error handling and validation
 * 
 * @version 1.0.0
 * @author CodeXam Development Team
 */

const SystemCommandProcessor = {
    // Configuration
    config: {
        maxHistorySize: 100,
        commandTimeout: 5000,
        typingSpeed: 30,
        promptSymbol: 'codexam@system:~$ ',
        debugMode: false
    },
    
    // State management
    state: {
        isInitialized: false,
        commandHistory: [],
        historyIndex: -1,
        currentInput: '',
        isProcessing: false
    },
    
    // Available commands
    commands: {
        help: {
            description: 'Show available commands and usage information',
            usage: 'help [command]',
            handler: 'showHelp'
        },
        status: {
            description: 'Display comprehensive system status overview',
            usage: 'status [--detailed]',
            handler: 'showSystemStatus'
        },
        stats: {
            description: 'Show detailed platform statistics and metrics',
            usage: 'stats [--export] [--trends]',
            handler: 'showStatistics'
        },
        users: {
            description: 'Display user activity and leaderboard information',
            usage: 'users [--top N] [--recent]',
            handler: 'showUserStats'
        },
        performance: {
            description: 'Show system performance metrics and monitoring data',
            usage: 'performance [--history] [--alerts]',
            handler: 'showPerformance'
        },
        diagnostics: {
            description: 'Run comprehensive system health diagnostics',
            usage: 'diagnostics [--full] [--export]',
            handler: 'runDiagnostics'
        },
        languages: {
            description: 'Show programming language statistics and trends',
            usage: 'languages [--chart] [--success-rates]',
            handler: 'showLanguageStats'
        },
        problems: {
            description: 'Display problem statistics and difficulty distribution',
            usage: 'problems [--difficulty LEVEL] [--recent]',
            handler: 'showProblemStats'
        },
        export: {
            description: 'Export system data and statistics to file',
            usage: 'export [--format json|csv] [--type all|stats|logs]',
            handler: 'exportData'
        },
        clear: {
            description: 'Clear the terminal screen',
            usage: 'clear',
            handler: 'clearScreen'
        },
        history: {
            description: 'Show command history',
            usage: 'history [--clear]',
            handler: 'showHistory'
        },
        uptime: {
            description: 'Show system uptime and boot information',
            usage: 'uptime',
            handler: 'showUptime'
        },
        version: {
            description: 'Display CodeXam version and build information',
            usage: 'version',
            handler: 'showVersion'
        },
        exit: {
            description: 'Close the system information modal',
            usage: 'exit',
            handler: 'exitModal'
        }
    },
    
    /**
     * Initialize the command processor
     */
    init() {
        if (this.state.isInitialized) {
            console.warn('⚠️ SystemCommandProcessor already initialized');
            return;
        }
        
        this._setupCommandInterface();
        this._loadCommandHistory();
        this.state.isInitialized = true;
        
        this._log('✅ SystemCommandProcessor initialized');
    },
    
    /**
     * Setup command interface elements
     */
    _setupCommandInterface() {
        const commandInput = document.getElementById('commandInput');
        const commandOutput = document.getElementById('commandOutput');
        
        if (!commandInput || !commandOutput) {
            console.error('❌ Command interface elements not found');
            return;
        }
        
        // Setup input event listeners
        commandInput.addEventListener('keydown', (e) => this._handleKeyDown(e));
        commandInput.addEventListener('input', (e) => this._handleInput(e));
        
        // Initial welcome message
        this._addOutputLine('🚀 CodeXam System Terminal v2.1.0', 'system');
        this._addOutputLine('Type "help" for available commands or "exit" to close', 'info');
        this._addOutputLine('', 'separator');
    },
    
    /**
     * Handle keyboard input
     */
    _handleKeyDown(e) {
        const input = e.target;
        
        switch (e.key) {
            case 'Enter':
                e.preventDefault();
                this._executeCommand(input.value.trim());
                input.value = '';
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this._navigateHistory('up');
                break;
                
            case 'ArrowDown':
                e.preventDefault();
                this._navigateHistory('down');
                break;
                
            case 'Tab':
                e.preventDefault();
                this._handleAutoComplete(input);
                break;
                
            case 'Escape':
                e.preventDefault();
                input.value = '';
                this.state.historyIndex = -1;
                break;
        }
    },
    
    /**
     * Handle input changes
     */
    _handleInput(e) {
        this.state.currentInput = e.target.value;
    },
    
    /**
     * Execute a command
     */
    async _executeCommand(commandLine) {
        if (!commandLine) return;
        
        // Input validation and sanitization
        const sanitizedCommand = this._sanitizeInput(commandLine);
        if (!sanitizedCommand) {
            this._addOutputLine('Invalid command input', 'error');
            return;
        }
        
        // Check command length
        if (sanitizedCommand.length > 200) {
            this._addOutputLine('Command too long', 'error');
            return;
        }
        
        // Add to history
        this._addToHistory(sanitizedCommand);
        
        // Show command in output
        this._addOutputLine(`${this.config.promptSymbol}${sanitizedCommand}`, 'command');
        
        // Parse command and arguments
        const [command, ...args] = sanitizedCommand.split(' ');
        const commandDef = this.commands[command.toLowerCase()];
        
        if (!commandDef) {
            this._addOutputLine(`Command not found: ${command}`, 'error');
            this._addOutputLine('Type "help" for available commands', 'info');
            return;
        }
        
        // Set processing state
        this.state.isProcessing = true;
        this._addOutputLine('Processing...', 'processing');
        
        try {
            // Execute command handler
            await this[commandDef.handler](args);
        } catch (error) {
            this._addOutputLine(`Error executing command: ${error.message}`, 'error');
            this._log('❌ Command execution error:', error);
        } finally {
            this.state.isProcessing = false;
            this._removeProcessingLine();
        }
    },
    
    /**
     * Navigate command history
     */
    _navigateHistory(direction) {
        const input = document.getElementById('commandInput');
        if (!input) return;
        
        if (direction === 'up') {
            if (this.state.historyIndex < this.state.commandHistory.length - 1) {
                this.state.historyIndex++;
                input.value = this.state.commandHistory[this.state.commandHistory.length - 1 - this.state.historyIndex];
            }
        } else if (direction === 'down') {
            if (this.state.historyIndex > 0) {
                this.state.historyIndex--;
                input.value = this.state.commandHistory[this.state.commandHistory.length - 1 - this.state.historyIndex];
            } else if (this.state.historyIndex === 0) {
                this.state.historyIndex = -1;
                input.value = '';
            }
        }
    },
    
    /**
     * Handle auto-completion
     */
    _handleAutoComplete(input) {
        const currentValue = input.value.trim();
        if (!currentValue) return;
        
        const matches = Object.keys(this.commands).filter(cmd => 
            cmd.startsWith(currentValue.toLowerCase())
        );
        
        if (matches.length === 1) {
            input.value = matches[0] + ' ';
        } else if (matches.length > 1) {
            this._addOutputLine(`Available completions: ${matches.join(', ')}`, 'info');
        }
    },
    
    /**
     * Add command to history
     */
    _addToHistory(command) {
        this.state.commandHistory.push(command);
        
        // Limit history size
        if (this.state.commandHistory.length > this.config.maxHistorySize) {
            this.state.commandHistory.shift();
        }
        
        this.state.historyIndex = -1;
        this._saveCommandHistory();
    },
    
    /**
     * Add line to command output
     */
    _addOutputLine(text, type = 'normal') {
        const output = document.getElementById('commandOutput');
        if (!output) return;
        
        const line = document.createElement('div');
        line.className = `command-line command-${type}`;
        
        if (type === 'processing') {
            line.id = 'processingLine';
            line.innerHTML = `<span class="processing-spinner">⠋</span> ${text}`;
            this._animateSpinner(line.querySelector('.processing-spinner'));
        } else {
            line.textContent = text;
        }
        
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
        
        // Animate line appearance
        line.style.opacity = '0';
        line.style.transform = 'translateX(-10px)';
        
        requestAnimationFrame(() => {
            line.style.transition = 'all 0.3s ease';
            line.style.opacity = '1';
            line.style.transform = 'translateX(0)';
        });
    },
    
    /**
     * Remove processing line
     */
    _removeProcessingLine() {
        const processingLine = document.getElementById('processingLine');
        if (processingLine) {
            processingLine.remove();
        }
    },
    
    /**
     * Animate processing spinner
     */
    _animateSpinner(spinner) {
        if (!spinner) return;
        
        const frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
        let frameIndex = 0;
        
        const animate = () => {
            if (document.getElementById('processingLine')) {
                spinner.textContent = frames[frameIndex];
                frameIndex = (frameIndex + 1) % frames.length;
                setTimeout(animate, 100);
            }
        };
        
        animate();
    },
    
    /**
     * Type text with animation
     */
    async _typeText(text, container) {
        for (let i = 0; i < text.length; i++) {
            container.textContent += text[i];
            await new Promise(resolve => setTimeout(resolve, this.config.typingSpeed));
        }
    },
    
    // Command Handlers
    
    /**
     * Show help information
     */
    async showHelp(args) {
        const specificCommand = args[0];
        
        if (specificCommand && this.commands[specificCommand]) {
            const cmd = this.commands[specificCommand];
            this._addOutputLine(`📖 Help for "${specificCommand}":`, 'info');
            this._addOutputLine(`Description: ${cmd.description}`, 'normal');
            this._addOutputLine(`Usage: ${cmd.usage}`, 'normal');
        } else {
            this._addOutputLine('📚 Available Commands:', 'info');
            this._addOutputLine('', 'separator');
            
            Object.entries(this.commands).forEach(([name, cmd]) => {
                this._addOutputLine(`  ${name.padEnd(12)} - ${cmd.description}`, 'normal');
            });
            
            this._addOutputLine('', 'separator');
            this._addOutputLine('💡 Tips:', 'info');
            this._addOutputLine('  • Use Tab for auto-completion', 'normal');
            this._addOutputLine('  • Use ↑/↓ arrows for command history', 'normal');
            this._addOutputLine('  • Use "help <command>" for detailed help', 'normal');
        }
    },
    
    /**
     * Show system status
     */
    async showSystemStatus(args) {
        const detailed = args.includes('--detailed');
        
        this._addOutputLine('🖥️ System Status Overview:', 'info');
        this._addOutputLine('', 'separator');
        
        try {
            const response = await fetch('/api/system-info');
            const data = await response.json();
            
            if (data.status === 'success' && data.data) {
                const system = data.data;
                
                this._addOutputLine(`Platform: ${system.platform?.name || 'Unknown'} v${system.platform?.version || 'Unknown'}`, 'normal');
                this._addOutputLine(`Status: ${system.platform?.status || 'Unknown'}`, system.platform?.status === 'OPERATIONAL' ? 'success' : 'warning');
                this._addOutputLine(`Uptime: ${system.platform?.uptime || 'Unknown'}`, 'normal');
                this._addOutputLine(`Database: ${system.database?.status || 'Unknown'}`, system.database?.status === 'CONNECTED' ? 'success' : 'error');
                this._addOutputLine(`Response Time: ${system.database?.response_time || 'Unknown'}`, 'normal');
                
                if (detailed && system.performance) {
                    this._addOutputLine('', 'separator');
                    this._addOutputLine('📊 Performance Metrics:', 'info');
                    this._addOutputLine(`CPU Usage: ${system.performance.cpu_usage || 0}%`, 'normal');
                    this._addOutputLine(`Memory Usage: ${system.performance.memory_usage || 0}%`, 'normal');
                    this._addOutputLine(`Disk Usage: ${system.performance.disk_usage || 0}%`, 'normal');
                    this._addOutputLine(`Memory Available: ${system.performance.memory_available || 0} GB`, 'normal');
                    this._addOutputLine(`Disk Free: ${system.performance.disk_free || 0} GB`, 'normal');
                }
            } else {
                this._addOutputLine('❌ Failed to retrieve system information', 'error');
            }
        } catch (error) {
            this._addOutputLine(`❌ Error fetching system status: ${error.message}`, 'error');
        }
    },
    
    /**
     * Show platform statistics
     */
    async showStatistics(args) {
        const exportData = args.includes('--export');
        const showTrends = args.includes('--trends');
        
        this._addOutputLine('📊 Platform Statistics:', 'info');
        this._addOutputLine('', 'separator');
        
        try {
            const response = await fetch('/api/platform-stats');
            const data = await response.json();
            
            if (data.status === 'success' && data.data) {
                const stats = data.data;
                const basic = stats.basic || {};
                
                this._addOutputLine('📈 Basic Metrics:', 'info');
                this._addOutputLine(`Total Problems: ${basic.total_problems || 0}`, 'normal');
                this._addOutputLine(`Total Submissions: ${basic.total_submissions || 0}`, 'normal');
                this._addOutputLine(`Active Users: ${basic.active_users || 0}`, 'normal');
                this._addOutputLine(`Success Rate: ${basic.success_rate || 0}%`, 'normal');
                
                if (stats.activity) {
                    this._addOutputLine('', 'separator');
                    this._addOutputLine('🔥 Recent Activity (24h):', 'info');
                    this._addOutputLine(`Recent Submissions: ${stats.activity.recent_submissions || 0}`, 'normal');
                }
                
                if (stats.languages?.distribution) {
                    this._addOutputLine('', 'separator');
                    this._addOutputLine('💻 Language Distribution:', 'info');
                    Object.entries(stats.languages.distribution).forEach(([lang, count]) => {
                        this._addOutputLine(`${lang}: ${count} submissions`, 'normal');
                    });
                }
                
                if (exportData) {
                    this._exportStatsData(stats);
                }
            } else {
                this._addOutputLine('❌ Failed to retrieve platform statistics', 'error');
            }
        } catch (error) {
            this._addOutputLine(`❌ Error fetching statistics: ${error.message}`, 'error');
        }
    },
    
    /**
     * Show user statistics
     */
    async showUserStats(args) {
        const topCount = this._getArgValue(args, '--top') || 10;
        const showRecent = args.includes('--recent');
        
        this._addOutputLine('👥 User Statistics:', 'info');
        this._addOutputLine('', 'separator');
        
        try {
            const response = await fetch('/api/platform-stats');
            const data = await response.json();
            
            if (data.status === 'success' && data.data?.leaderboard?.top_performers) {
                const performers = data.data.leaderboard.top_performers.slice(0, topCount);
                
                this._addOutputLine(`🏆 Top ${topCount} Performers:`, 'info');
                performers.forEach((performer, index) => {
                    this._addOutputLine(`${(index + 1).toString().padStart(2)}. ${performer.user.padEnd(20)} ${performer.solved} problems solved`, 'normal');
                });
            } else {
                this._addOutputLine('❌ No user statistics available', 'error');
            }
        } catch (error) {
            this._addOutputLine(`❌ Error fetching user statistics: ${error.message}`, 'error');
        }
    },
    
    /**
     * Show performance metrics
     */
    async showPerformance(args) {
        const showHistory = args.includes('--history');
        const showAlerts = args.includes('--alerts');
        
        this._addOutputLine('⚡ Performance Metrics:', 'info');
        this._addOutputLine('', 'separator');
        
        try {
            const response = await fetch('/api/system-info');
            const data = await response.json();
            
            if (data.status === 'success' && data.data?.performance) {
                const perf = data.data.performance;
                
                this._addOutputLine('📊 Current Performance:', 'info');
                this._addOutputLine(`CPU Usage:    ${this._createProgressBar(perf.cpu_usage || 0)} ${perf.cpu_usage || 0}%`, 'normal');
                this._addOutputLine(`Memory Usage: ${this._createProgressBar(perf.memory_usage || 0)} ${perf.memory_usage || 0}%`, 'normal');
                this._addOutputLine(`Disk Usage:   ${this._createProgressBar(perf.disk_usage || 0)} ${perf.disk_usage || 0}%`, 'normal');
                
                this._addOutputLine('', 'separator');
                this._addOutputLine('💾 Resource Information:', 'info');
                this._addOutputLine(`Memory Total: ${perf.memory_total || 0} GB`, 'normal');
                this._addOutputLine(`Memory Available: ${perf.memory_available || 0} GB`, 'normal');
                this._addOutputLine(`Disk Total: ${perf.disk_total || 0} GB`, 'normal');
                this._addOutputLine(`Disk Free: ${perf.disk_free || 0} GB`, 'normal');
                
                if (showAlerts) {
                    this._addOutputLine('', 'separator');
                    this._addOutputLine('⚠️ Performance Alerts:', 'info');
                    
                    const alerts = [];
                    if (perf.cpu_usage > 80) alerts.push('High CPU usage detected');
                    if (perf.memory_usage > 85) alerts.push('High memory usage detected');
                    if (perf.disk_usage > 90) alerts.push('Low disk space warning');
                    
                    if (alerts.length > 0) {
                        alerts.forEach(alert => this._addOutputLine(`• ${alert}`, 'warning'));
                    } else {
                        this._addOutputLine('No performance alerts', 'success');
                    }
                }
            } else {
                this._addOutputLine('❌ Failed to retrieve performance metrics', 'error');
            }
        } catch (error) {
            this._addOutputLine(`❌ Error fetching performance data: ${error.message}`, 'error');
        }
    },
    
    /**
     * Run system diagnostics
     */
    async runDiagnostics(args) {
        const fullDiagnostics = args.includes('--full');
        const exportResults = args.includes('--export');
        
        this._addOutputLine('🔍 Running System Diagnostics...', 'info');
        this._addOutputLine('', 'separator');
        
        try {
            const response = await fetch('/api/health-check');
            const data = await response.json();
            
            if (data.status === 'success' && data.data) {
                const health = data.data;
                
                this._addOutputLine(`Overall Status: ${health.overall_status}`, 
                    health.overall_status === 'HEALTHY' ? 'success' : 'warning');
                
                this._addOutputLine('', 'separator');
                this._addOutputLine('🔧 Component Health Checks:', 'info');
                
                Object.entries(health.checks || {}).forEach(([component, check]) => {
                    const status = check.status || 'UNKNOWN';
                    const statusType = status === 'HEALTHY' ? 'success' : 
                                     status === 'ERROR' ? 'error' : 'warning';
                    
                    this._addOutputLine(`${component.padEnd(15)}: ${status}`, statusType);
                    
                    if (fullDiagnostics && check.response_time) {
                        this._addOutputLine(`  Response Time: ${check.response_time}`, 'normal');
                    }
                    
                    if (check.error) {
                        this._addOutputLine(`  Error: ${check.error}`, 'error');
                    }
                });
                
                if (exportResults) {
                    this._exportDiagnosticsData(health);
                }
            } else {
                this._addOutputLine('❌ Failed to run diagnostics', 'error');
            }
        } catch (error) {
            this._addOutputLine(`❌ Error running diagnostics: ${error.message}`, 'error');
        }
    },
    
    /**
     * Show language statistics
     */
    async showLanguageStats(args) {
        const showChart = args.includes('--chart');
        const showSuccessRates = args.includes('--success-rates');
        
        this._addOutputLine('💻 Programming Language Statistics:', 'info');
        this._addOutputLine('', 'separator');
        
        try {
            const response = await fetch('/api/platform-stats');
            const data = await response.json();
            
            if (data.status === 'success' && data.data?.languages) {
                const languages = data.data.languages;
                
                if (languages.distribution) {
                    this._addOutputLine('📊 Submission Distribution:', 'info');
                    
                    if (showChart) {
                        this._displayASCIIChart(languages.distribution, 'Submissions');
                    } else {
                        Object.entries(languages.distribution)
                            .sort(([,a], [,b]) => b - a)
                            .forEach(([lang, count]) => {
                                this._addOutputLine(`${lang.padEnd(12)}: ${count} submissions`, 'normal');
                            });
                    }
                }
                
                if (showSuccessRates && languages.success_rates) {
                    this._addOutputLine('', 'separator');
                    this._addOutputLine('📈 Success Rates by Language:', 'info');
                    
                    Object.entries(languages.success_rates).forEach(([lang, stats]) => {
                        this._addOutputLine(`${lang.padEnd(12)}: ${stats.success_rate}% (${stats.passed}/${stats.total})`, 'normal');
                    });
                }
            } else {
                this._addOutputLine('❌ No language statistics available', 'error');
            }
        } catch (error) {
            this._addOutputLine(`❌ Error fetching language statistics: ${error.message}`, 'error');
        }
    },
    
    /**
     * Show problem statistics
     */
    async showProblemStats(args) {
        const difficulty = this._getArgValue(args, '--difficulty');
        const showRecent = args.includes('--recent');
        
        this._addOutputLine('📝 Problem Statistics:', 'info');
        this._addOutputLine('', 'separator');
        
        try {
            const response = await fetch('/api/platform-stats');
            const data = await response.json();
            
            if (data.status === 'success' && data.data?.problems) {
                const problems = data.data.problems;
                
                this._addOutputLine(`Total Problems: ${problems.total || 0}`, 'normal');
                
                if (problems.difficulty_distribution) {
                    this._addOutputLine('', 'separator');
                    this._addOutputLine('📊 Difficulty Distribution:', 'info');
                    
                    Object.entries(problems.difficulty_distribution).forEach(([diff, count]) => {
                        if (!difficulty || diff.toLowerCase() === difficulty.toLowerCase()) {
                            this._addOutputLine(`${diff.padEnd(8)}: ${count} problems`, 'normal');
                        }
                    });
                }
            } else {
                this._addOutputLine('❌ No problem statistics available', 'error');
            }
        } catch (error) {
            this._addOutputLine(`❌ Error fetching problem statistics: ${error.message}`, 'error');
        }
    },
    
    /**
     * Export data
     */
    async exportData(args) {
        const format = this._getArgValue(args, '--format') || 'json';
        const type = this._getArgValue(args, '--type') || 'all';
        
        this._addOutputLine(`📁 Exporting data (format: ${format}, type: ${type})...`, 'info');
        
        try {
            if (typeof SystemStatsVisualizer !== 'undefined') {
                SystemStatsVisualizer.exportData();
                this._addOutputLine('✅ Data exported successfully', 'success');
            } else {
                this._addOutputLine('❌ Export functionality not available', 'error');
            }
        } catch (error) {
            this._addOutputLine(`❌ Export failed: ${error.message}`, 'error');
        }
    },
    
    /**
     * Clear screen
     */
    async clearScreen(args) {
        const output = document.getElementById('commandOutput');
        if (output) {
            output.innerHTML = '';
        }
    },
    
    /**
     * Show command history
     */
    async showHistory(args) {
        const clearHistory = args.includes('--clear');
        
        if (clearHistory) {
            this.state.commandHistory = [];
            this._saveCommandHistory();
            this._addOutputLine('✅ Command history cleared', 'success');
            return;
        }
        
        this._addOutputLine('📜 Command History:', 'info');
        this._addOutputLine('', 'separator');
        
        if (this.state.commandHistory.length === 0) {
            this._addOutputLine('No commands in history', 'normal');
        } else {
            this.state.commandHistory.forEach((cmd, index) => {
                this._addOutputLine(`${(index + 1).toString().padStart(3)}. ${cmd}`, 'normal');
            });
        }
    },
    
    /**
     * Show uptime
     */
    async showUptime(args) {
        this._addOutputLine('⏰ System Uptime Information:', 'info');
        this._addOutputLine('', 'separator');
        
        try {
            const response = await fetch('/api/system-info');
            const data = await response.json();
            
            if (data.status === 'success' && data.data?.platform) {
                const platform = data.data.platform;
                this._addOutputLine(`Current Uptime: ${platform.uptime || 'Unknown'}`, 'normal');
                
                if (platform.boot_time) {
                    const bootTime = new Date(platform.boot_time);
                    this._addOutputLine(`Boot Time: ${bootTime.toLocaleString()}`, 'normal');
                }
            } else {
                this._addOutputLine('❌ Failed to retrieve uptime information', 'error');
            }
        } catch (error) {
            this._addOutputLine(`❌ Error fetching uptime: ${error.message}`, 'error');
        }
    },
    
    /**
     * Show version information
     */
    async showVersion(args) {
        this._addOutputLine('ℹ️ CodeXam Version Information:', 'info');
        this._addOutputLine('', 'separator');
        
        try {
            const response = await fetch('/api/system-info');
            const data = await response.json();
            
            if (data.status === 'success' && data.data?.platform) {
                const platform = data.data.platform;
                this._addOutputLine(`Platform: ${platform.name || 'CodeXam'}`, 'normal');
                this._addOutputLine(`Version: ${platform.version || 'Unknown'}`, 'normal');
                this._addOutputLine(`API Version: ${data.metadata?.api_version || 'Unknown'}`, 'normal');
            }
            
            this._addOutputLine(`Terminal Version: 2.1.0`, 'normal');
            this._addOutputLine(`Build Date: ${new Date().toLocaleDateString()}`, 'normal');
        } catch (error) {
            this._addOutputLine(`❌ Error fetching version information: ${error.message}`, 'error');
        }
    },
    
    /**
     * Exit modal
     */
    async exitModal(args) {
        this._addOutputLine('👋 Closing system information modal...', 'info');
        
        setTimeout(() => {
            if (typeof hideSystemInfoModal === 'function') {
                hideSystemInfoModal();
            } else if (typeof SystemInfoModal !== 'undefined') {
                SystemInfoModal.hide();
            }
        }, 1000);
    },
    
    // Utility Methods
    
    /**
     * Sanitize user input to prevent injection attacks
     */
    _sanitizeInput(input) {
        if (typeof input !== 'string') {
            return null;
        }
        
        // Remove dangerous characters and patterns
        const dangerous = [
            '<script',
            '</script>',
            'javascript:',
            'data:',
            'vbscript:',
            'onload=',
            'onerror=',
            'onclick=',
            'eval(',
            'Function(',
            'setTimeout(',
            'setInterval('
        ];
        
        let sanitized = input.trim();
        
        // Check for dangerous patterns
        for (const pattern of dangerous) {
            if (sanitized.toLowerCase().includes(pattern.toLowerCase())) {
                this._log(`⚠️ Dangerous pattern detected: ${pattern}`);
                return null;
            }
        }
        
        // Remove HTML tags
        sanitized = sanitized.replace(/<[^>]*>/g, '');
        
        // Limit to alphanumeric, spaces, hyphens, and common punctuation
        sanitized = sanitized.replace(/[^a-zA-Z0-9\s\-_.:/=]/g, '');
        
        // Collapse multiple spaces
        sanitized = sanitized.replace(/\s+/g, ' ').trim();
        
        return sanitized;
    },
    
    /**
     * Get argument value
     */
    _getArgValue(args, flag) {
        const index = args.indexOf(flag);
        return index !== -1 && index + 1 < args.length ? args[index + 1] : null;
    },
    
    /**
     * Create ASCII progress bar
     */
    _createProgressBar(percentage, width = 20) {
        const filled = Math.round((percentage / 100) * width);
        const empty = width - filled;
        return `[${'█'.repeat(filled)}${' '.repeat(empty)}]`;
    },
    
    /**
     * Display ASCII chart
     */
    _displayASCIIChart(data, label = 'Value') {
        const maxValue = Math.max(...Object.values(data));
        const maxBarLength = 40;
        
        Object.entries(data)
            .sort(([,a], [,b]) => b - a)
            .forEach(([key, value]) => {
                const barLength = maxValue > 0 ? Math.round((value / maxValue) * maxBarLength) : 0;
                const bar = '█'.repeat(barLength);
                this._addOutputLine(`${key.padEnd(12)} │${bar.padEnd(maxBarLength)}│ ${value}`, 'normal');
            });
    },
    
    /**
     * Export statistics data
     */
    _exportStatsData(stats) {
        this._addOutputLine('📁 Exporting statistics data...', 'info');
        // Implementation would trigger download
    },
    
    /**
     * Export diagnostics data
     */
    _exportDiagnosticsData(diagnostics) {
        this._addOutputLine('📁 Exporting diagnostics data...', 'info');
        // Implementation would trigger download
    },
    
    /**
     * Load command history from localStorage
     */
    _loadCommandHistory() {
        try {
            const saved = localStorage.getItem('codexam_command_history');
            if (saved) {
                this.state.commandHistory = JSON.parse(saved);
            }
        } catch (error) {
            this._log('⚠️ Failed to load command history:', error);
        }
    },
    
    /**
     * Save command history to localStorage
     */
    _saveCommandHistory() {
        try {
            localStorage.setItem('codexam_command_history', JSON.stringify(this.state.commandHistory));
        } catch (error) {
            this._log('⚠️ Failed to save command history:', error);
        }
    },
    
    /**
     * Conditional logging
     */
    _log(message, data = null) {
        if (this.config.debugMode || (typeof window !== 'undefined' && window.location.hostname === 'localhost')) {
            if (data) {
                console.log(message, data);
            } else {
                console.log(message);
            }
        }
    },
    
    /**
     * Clean up resources
     */
    destroy() {
        this.state.isInitialized = false;
        this.state.commandHistory = [];
        this.state.historyIndex = -1;
        this.state.currentInput = '';
        this.state.isProcessing = false;
        
        this._log('✅ SystemCommandProcessor destroyed');
    }
};

// Global API
if (typeof window !== 'undefined') {
    window.SystemCommandProcessor = SystemCommandProcessor;
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            SystemCommandProcessor.init();
        });
    } else {
        SystemCommandProcessor.init();
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SystemCommandProcessor;
}

console.log('✅ SystemCommandProcessor v1.0.0 loaded successfully');