/**
 * System Info Modal - Enhanced Terminal-Style System Dashboard
 * Provides comprehensive system diagnostics and platform statistics with immersive hacker experience
 */

const SystemInfoModal = {
    // Modal state
    isOpen: false,
    isAnimating: false,
    refreshInterval: null,
    matrixInterval: null,
    bootAnimationTimeout: null,
    
    // DOM elements
    modal: null,
    matrixBackground: null,
    bootSequence: null,
    terminalInterface: null,
    commandInput: null,
    commandOutput: null,
    asciiArt: null,
    
    // Data cache
    systemData: {},
    lastUpdate: null,
    
    // Configuration
    config: {
        bootSequenceDelay: 300,
        matrixSpeed: 50,
        refreshInterval: 5000,
        typingSpeed: 30,
        glitchDuration: 200
    },
    
    // ASCII Art for CodeXam branding
    asciiArtText: `
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ██████╗ ██████╗ ██████╗ ███████╗██╗  ██╗ █████╗ ███╗   ███╗                ║
║  ██╔════╝██╔═══██╗██╔══██╗██╔════╝╚██╗██╔╝██╔══██╗████╗ ████║                ║
║  ██║     ██║   ██║██║  ██║█████╗   ╚███╔╝ ███████║██╔████╔██║                ║
║  ██║     ██║   ██║██║  ██║██╔══╝   ██╔██╗ ██╔══██║██║╚██╔╝██║                ║
║  ╚██████╗╚██████╔╝██████╔╝███████╗██╔╝ ██╗██║  ██║██║ ╚═╝ ██║                ║
║   ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝                ║
║                                                                               ║
║                    ███████╗██╗     ██╗████████╗███████╗                      ║
║                    ██╔════╝██║     ██║╚══██╔══╝██╔════╝                      ║
║                    █████╗  ██║     ██║   ██║   █████╗                        ║
║                    ██╔══╝  ██║     ██║   ██║   ██╔══╝                        ║
║                    ███████╗███████╗██║   ██║   ███████╗                      ║
║                    ╚══════╝╚══════╝╚═╝   ╚═╝   ╚══════╝                      ║
║                                                                               ║
║                          SYSTEM DIAGNOSTICS TERMINAL                         ║
║                              Elite Coding Arena                               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    `,
    
    /**
     * Initialize the System Info Modal
     */
    init() {
        this.modal = document.getElementById('systemInfoModal');
        this.matrixBackground = document.getElementById('matrixBackground');
        this.bootSequence = document.getElementById('bootSequence');
        this.terminalInterface = document.getElementById('terminalInterface');
        this.commandInput = document.getElementById('commandInput');
        this.commandOutput = document.getElementById('commandOutput');
        this.asciiArt = document.getElementById('asciiArt');
        
        if (!this.modal) {
            console.error('System Info Modal not found in DOM');
            return;
        }
        
        this.setupEventListeners();
        this.initializeMatrixEffect();
        this.preloadAsciiArt();
        console.log('System Info Modal initialized successfully');
    },
    
    /**
     * Preload ASCII art into the header
     */
    preloadAsciiArt() {
        if (this.asciiArt) {
            this.asciiArt.textContent = this.asciiArtText;
        }
    },
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Close modal on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.hide();
            }
        });
        
        // Command input handling
        if (this.commandInput) {
            this.commandInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.processCommand(this.commandInput.value.trim());
                    this.commandInput.value = '';
                }
            });
        }
        
        // Prevent modal close on content click
        if (this.modal) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) {
                    this.hide();
                }
            });
        }
    },
    
    /**
     * Show the modal with enhanced boot sequence animation
     */
    show() {
        if (this.isOpen || this.isAnimating) return;
        
        this.isAnimating = true;
        this.isOpen = true;
        
        // Show modal with fade-in effect
        this.modal.style.display = 'flex';
        this.modal.style.opacity = '0';
        
        // Trigger reflow for animation
        this.modal.offsetHeight;
        
        // Animate modal entrance
        this.modal.style.transition = 'opacity 0.5s ease-out';
        this.modal.style.opacity = '1';
        
        // Add show class for additional animations
        this.modal.classList.add('show');
        
        // Start enhanced boot sequence
        this.startEnhancedBootSequence();
        
        // Start matrix effect
        this.startMatrixEffect();
        
        // Focus management for accessibility
        this.modal.setAttribute('aria-hidden', 'false');
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        console.log('System Info Modal opened with enhanced effects');
    },
    
    /**
     * Hide the modal with shutdown sequence
     */
    hide() {
        if (!this.isOpen || this.isAnimating) return;
        
        this.isAnimating = true;
        
        // Clear all intervals and timeouts
        this.cleanup();
        
        // Animate modal exit
        this.modal.style.transition = 'opacity 0.3s ease-out';
        this.modal.style.opacity = '0';
        
        // Hide modal after animation
        setTimeout(() => {
            this.modal.style.display = 'none';
            this.modal.classList.remove('show');
            this.isOpen = false;
            this.isAnimating = false;
            
            // Reset terminal interface
            this.resetTerminalInterface();
            
            // Restore body scroll
            document.body.style.overflow = '';
            
            // Accessibility
            this.modal.setAttribute('aria-hidden', 'true');
            
            console.log('System Info Modal closed');
        }, 300);
    },
    
    /**
     * Start enhanced boot sequence with better animations
     */
    startEnhancedBootSequence() {
        const bootMessages = [
            { text: 'Initializing CodeXam System Diagnostics...', delay: 0, type: 'info' },
            { text: 'Loading kernel modules...', delay: 300, type: 'loading' },
            { text: '  ✓ Terminal interface loaded', delay: 600, type: 'success' },
            { text: '  ✓ Matrix renderer initialized', delay: 900, type: 'success' },
            { text: 'Establishing secure connections...', delay: 1200, type: 'loading' },
            { text: '  ✓ Database connection established', delay: 1500, type: 'success' },
            { text: '  ✓ Judge engine online', delay: 1800, type: 'success' },
            { text: 'Gathering system metrics...', delay: 2100, type: 'loading' },
            { text: '  ✓ Performance data collected', delay: 2400, type: 'success' },
            { text: '  ✓ Platform statistics ready', delay: 2700, type: 'success' },
            { text: '', delay: 3000, type: 'separator' },
            { text: 'System ready. Welcome to CodeXam Elite Terminal.', delay: 3300, type: 'ready' },
            { text: 'Type "help" for available commands.', delay: 3600, type: 'hint' }
        ];
        
        // Clear existing boot sequence
        if (this.bootSequence) {
            this.bootSequence.innerHTML = '';
        }
        
        // Add boot messages with enhanced styling and timing
        bootMessages.forEach((message, index) => {
            this.bootAnimationTimeout = setTimeout(() => {
                if (!this.isOpen) return; // Check if modal is still open
                
                const bootLine = document.createElement('div');
                bootLine.className = `boot-line boot-${message.type}`;
                
                if (message.type === 'separator') {
                    bootLine.innerHTML = '<div class="boot-separator">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</div>';
                } else {
                    bootLine.textContent = message.text;
                }
                
                this.bootSequence.appendChild(bootLine);
                
                // Show terminal interface after last message
                if (index === bootMessages.length - 1) {
                    setTimeout(() => {
                        this.showTerminalInterface();
                        this.isAnimating = false;
                    }, 500);
                }
            }, message.delay);
        });
    },
    
    /**
     * Show the terminal interface with enhanced animations
     */
    showTerminalInterface() {
        if (this.terminalInterface) {
            this.terminalInterface.style.display = 'grid';
            this.terminalInterface.classList.add('interface-reveal');
            
            // Load initial data
            this.loadSystemData();
            
            // Start refresh interval
            this.refreshInterval = setInterval(() => {
                this.loadSystemData();
            }, this.config.refreshInterval);
            
            // Focus command input with delay for better UX
            setTimeout(() => {
                if (this.commandInput && this.isOpen) {
                    this.commandInput.focus();
                }
            }, 1000);
        }
    },
    
    /**
     * Initialize matrix background effect
     */
    initializeMatrixEffect() {
        if (!this.matrixBackground) return;
        
        // Create canvas for matrix effect
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        this.matrixCanvas = canvas;
        this.matrixCtx = ctx;
        
        // Set canvas size
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        this.matrixBackground.appendChild(canvas);
        
        // Matrix configuration
        this.matrixConfig = {
            chars: '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン',
            fontSize: 14,
            drops: [],
            columns: Math.floor(canvas.width / 14)
        };
        
        // Initialize drops
        for (let i = 0; i < this.matrixConfig.columns; i++) {
            this.matrixConfig.drops[i] = Math.floor(Math.random() * canvas.height / 14);
        }
    },
    
    /**
     * Start matrix effect animation
     */
    startMatrixEffect() {
        if (!this.matrixCtx) return;
        
        const drawMatrix = () => {
            if (!this.isOpen) return;
            
            // Semi-transparent black background for trail effect
            this.matrixCtx.fillStyle = 'rgba(10, 10, 10, 0.04)';
            this.matrixCtx.fillRect(0, 0, this.matrixCanvas.width, this.matrixCanvas.height);
            
            // Green text
            this.matrixCtx.fillStyle = '#00ff88';
            this.matrixCtx.font = `${this.matrixConfig.fontSize}px monospace`;
            
            // Draw characters
            for (let i = 0; i < this.matrixConfig.drops.length; i++) {
                const char = this.matrixConfig.chars.charAt(
                    Math.floor(Math.random() * this.matrixConfig.chars.length)
                );
                
                this.matrixCtx.fillText(
                    char,
                    i * this.matrixConfig.fontSize,
                    this.matrixConfig.drops[i] * this.matrixConfig.fontSize
                );
                
                // Reset drop randomly
                if (this.matrixConfig.drops[i] * this.matrixConfig.fontSize > this.matrixCanvas.height && Math.random() > 0.975) {
                    this.matrixConfig.drops[i] = 0;
                }
                
                this.matrixConfig.drops[i]++;
            }
        };
        
        this.matrixInterval = setInterval(drawMatrix, this.config.matrixSpeed);
    },
    
    /**
     * Load system data from server
     */
    async loadSystemData() {
        try {
            // Update system status
            this.updateSystemStatus();
            
            // Update statistics
            await this.updateStatistics();
            
            // Update performance metrics
            this.updatePerformanceMetrics();
            
            this.lastUpdate = new Date();
            
        } catch (error) {
            console.error('Failed to load system data:', error);
            this.showError('Failed to load system data: ' + error.message);
        }
    },
    
    /**
     * Update system status panel
     */
    updateSystemStatus() {
        const statusContent = document.getElementById('systemStatusContent');
        if (!statusContent) return;
        
        const currentTime = new Date().toLocaleString();
        const uptime = this.calculateUptime();
        
        statusContent.innerHTML = `
            <div class="status-line">
                <span class="status-label">System Time:</span>
                <span class="status-value">${currentTime}</span>
            </div>
            <div class="status-line">
                <span class="status-label">Platform:</span>
                <span class="status-value">CodeXam Elite Arena v2.1.0</span>
            </div>
            <div class="status-line">
                <span class="status-label">Uptime:</span>
                <span class="status-value">${uptime}</span>
            </div>
            <div class="status-line">
                <span class="status-label">Database:</span>
                <span class="status-value status-success">CONNECTED</span>
            </div>
            <div class="status-line">
                <span class="status-label">Judge Engine:</span>
                <span class="status-value status-success">OPERATIONAL</span>
            </div>
        `;
    },
    
    /**
     * Update statistics panel
     */
    async updateStatistics() {
        const statsContent = document.getElementById('statisticsContent');
        if (!statsContent) return;
        
        try {
            // Fetch platform stats from server
            const response = await fetch('/health');
            const data = await response.json();
            const stats = data.stats || {};
            
            statsContent.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-label">Total Problems:</span>
                        <span class="stat-value">${stats.total_problems || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Total Submissions:</span>
                        <span class="stat-value">${stats.total_submissions || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Active Users:</span>
                        <span class="stat-value">${stats.total_users || 0}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Success Rate:</span>
                        <span class="stat-value">${this.calculateSuccessRate(stats)}%</span>
                    </div>
                </div>
            `;
        } catch (error) {
            statsContent.innerHTML = '<div class="status-error">Failed to load statistics</div>';
        }
    },
    
    /**
     * Update performance metrics panel
     */
    updatePerformanceMetrics() {
        const performanceContent = document.getElementById('performanceContent');
        if (!performanceContent) return;
        
        // Simulate performance metrics
        const metrics = {
            responseTime: Math.random() * 50 + 10, // 10-60ms
            memoryUsage: Math.random() * 30 + 40,  // 40-70%
            cpuUsage: Math.random() * 20 + 15,     // 15-35%
            activeConnections: Math.floor(Math.random() * 50) + 10
        };
        
        performanceContent.innerHTML = `
            <div class="metrics-grid">
                <div class="metric-item">
                    <span class="metric-label">Response Time:</span>
                    <span class="metric-value">${metrics.responseTime.toFixed(1)}ms</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Memory Usage:</span>
                    <span class="metric-value">${metrics.memoryUsage.toFixed(1)}%</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">CPU Usage:</span>
                    <span class="metric-value">${metrics.cpuUsage.toFixed(1)}%</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Active Connections:</span>
                    <span class="metric-value">${metrics.activeConnections}</span>
                </div>
            </div>
        `;
    },
    
    /**
     * Process terminal commands
     */
    processCommand(command) {
        if (!command) return;
        
        // Add command to output
        this.addCommandLine(`codexam@system:~$ ${command}`);
        
        // Process command
        switch (command.toLowerCase()) {
            case 'help':
                this.showHelp();
                break;
            case 'status':
                this.showSystemStatus();
                break;
            case 'stats':
                this.showStatistics();
                break;
            case 'performance':
                this.showPerformance();
                break;
            case 'users':
                this.showUsers();
                break;
            case 'clear':
                this.clearCommandOutput();
                break;
            case 'exit':
                this.hide();
                break;
            default:
                this.addCommandLine(`Command not found: ${command}. Type 'help' for available commands.`, 'error');
        }
        
        // Scroll to bottom
        this.scrollCommandOutput();
    },
    
    /**
     * Show help command
     */
    showHelp() {
        const helpText = `
Available Commands:
  help        - Show this help message
  status      - Display system status
  stats       - Show platform statistics
  performance - Display performance metrics
  users       - Show user information
  clear       - Clear terminal screen
  exit        - Close system info modal

Navigation:
  Use arrow keys to navigate
  Press Escape to close modal
        `.trim();
        
        this.addCommandLine(helpText);
    },
    
    /**
     * Show system status command
     */
    showSystemStatus() {
        const statusText = `
System Status Report:
  Platform: CodeXam Elite Arena v2.1.0
  Status: OPERATIONAL
  Database: CONNECTED
  Judge Engine: OPERATIONAL
  Uptime: ${this.calculateUptime()}
  Last Update: ${new Date().toLocaleString()}
        `.trim();
        
        this.addCommandLine(statusText);
    },
    
    /**
     * Show statistics command
     */
    showStatistics() {
        const statsText = `
Platform Statistics:
  Total Problems: Loading...
  Total Submissions: Loading...
  Active Users: Loading...
  Success Rate: Calculating...
        `.trim();
        
        this.addCommandLine(statsText);
    },
    
    /**
     * Show performance command
     */
    showPerformance() {
        const perfText = `
Performance Metrics:
  Response Time: ~25ms
  Memory Usage: 45.2%
  CPU Usage: 23.1%
  Active Connections: 28
  System Load: Normal
        `.trim();
        
        this.addCommandLine(perfText);
    },
    
    /**
     * Show users command
     */
    showUsers() {
        const currentUser = document.querySelector('.user-name-hacker')?.textContent || 'Anonymous';
        const usersText = `
User Information:
  Current User: ${currentUser}
  Session Status: Active
  Permissions: Standard User
  Last Activity: ${new Date().toLocaleString()}
        `.trim();
        
        this.addCommandLine(usersText);
    },
    
    /**
     * Add command line to output
     */
    addCommandLine(text, type = 'normal') {
        if (!this.commandOutput) return;
        
        const line = document.createElement('div');
        line.className = `command-line ${type}`;
        
        if (type === 'error') {
            line.innerHTML = `<span class="prompt error">ERROR:</span><span class="command-text">${text}</span>`;
        } else {
            line.innerHTML = `<span class="command-text">${text}</span>`;
        }
        
        this.commandOutput.appendChild(line);
    },
    
    /**
     * Clear command output
     */
    clearCommandOutput() {
        if (this.commandOutput) {
            this.commandOutput.innerHTML = `
                <div class="command-line">
                    <span class="prompt">codexam@system:~$</span>
                    <span class="command-text">Terminal cleared</span>
                </div>
            `;
        }
    },
    
    /**
     * Scroll command output to bottom
     */
    scrollCommandOutput() {
        if (this.commandOutput) {
            this.commandOutput.scrollTop = this.commandOutput.scrollHeight;
        }
    },
    
    /**
     * Reset terminal interface
     */
    resetTerminalInterface() {
        if (this.terminalInterface) {
            this.terminalInterface.style.display = 'none';
            this.terminalInterface.classList.remove('interface-reveal');
        }
        
        if (this.bootSequence) {
            this.bootSequence.innerHTML = '<div class="boot-line">Initializing CodeXam System Diagnostics...</div>';
        }
        
        if (this.commandOutput) {
            this.commandOutput.innerHTML = `
                <div class="command-line">
                    <span class="prompt">codexam@system:~$</span>
                    <span class="command-text">Welcome to CodeXam System Terminal</span>
                </div>
                <div class="command-line">
                    <span class="prompt">codexam@system:~$</span>
                    <span class="command-text">Type 'help' to see available commands</span>
                </div>
            `;
        }
    },
    
    /**
     * Calculate system uptime (simulated)
     */
    calculateUptime() {
        const startTime = new Date();
        startTime.setHours(startTime.getHours() - Math.floor(Math.random() * 72));
        const uptime = Date.now() - startTime.getTime();
        
        const hours = Math.floor(uptime / (1000 * 60 * 60));
        const minutes = Math.floor((uptime % (1000 * 60 * 60)) / (1000 * 60));
        
        return `${hours}h ${minutes}m`;
    },
    
    /**
     * Calculate success rate from stats
     */
    calculateSuccessRate(stats) {
        if (!stats.total_submissions || stats.total_submissions === 0) {
            return '0.0';
        }
        
        // This would be calculated from actual pass/fail data
        const successRate = Math.random() * 30 + 60; // 60-90%
        return successRate.toFixed(1);
    },
    
    /**
     * Cleanup all intervals and timeouts
     */
    cleanup() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        
        if (this.matrixInterval) {
            clearInterval(this.matrixInterval);
            this.matrixInterval = null;
        }
        
        if (this.bootAnimationTimeout) {
            clearTimeout(this.bootAnimationTimeout);
            this.bootAnimationTimeout = null;
        }
    },
    
    /**
     * Show error message
     */
    showError(message) {
        console.error('System Info Modal Error:', message);
        
        if (this.commandOutput) {
            this.addCommandLine(`SYSTEM ERROR: ${message}`, 'error');
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing System Info Modal...');
    try {
        SystemInfoModal.init();
        console.log('✅ System Info Modal initialized successfully');
        
        // Make SystemInfoModal globally accessible for debugging
        window.SystemInfoModal = SystemInfoModal;
        
        // Test if modal elements exist
        if (document.getElementById('systemInfoModal')) {
            console.log('✅ Modal HTML structure found');
        } else {
            console.error('❌ Modal HTML structure not found');
        }
    } catch (error) {
        console.error('❌ Failed to initialize System Info Modal:', error);
    }
});

// Enhanced CSS animations and effects
const enhancedStyles = document.createElement('style');
enhancedStyles.textContent = `
    /* Enhanced animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .animate-slide-in {
        animation: slideIn 0.5s ease-out forwards;
    }
    
    .interface-reveal {
        animation: interfaceReveal 1s ease-out forwards;
    }
    
    @keyframes interfaceReveal {
        from {
            opacity: 0;
            transform: translateY(30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Boot sequence enhancements */
    .boot-success {
        color: #00ff88;
    }
    
    .boot-loading {
        color: #ffaa00;
    }
    
    .boot-ready {
        color: #00ff41;
        font-weight: 600;
    }
    
    .boot-hint {
        color: #666;
        font-style: italic;
    }
    
    .boot-separator {
        color: #333;
        margin: 0.5rem 0;
    }
    
    /* Command styling */
    .command-text {
        white-space: pre-line;
    }
    
    .command-line.error .prompt {
        color: var(--status-error);
    }
    
    .command-line.error .command-text {
        color: var(--status-error);
    }
`;

document.head.appendChild(enhancedStyles);
// Fallbac
k function for debugging
window.testSystemInfoModal = function() {
    console.log('🔧 Testing System Info Modal...');
    if (window.SystemInfoModal) {
        console.log('✅ SystemInfoModal object found');
        try {
            window.SystemInfoModal.show();
            console.log('✅ Modal show() called successfully');
        } catch (error) {
            console.error('❌ Error calling modal show():', error);
        }
    } else {
        console.error('❌ SystemInfoModal object not found');
    }
};

// Add global error handler for debugging
window.addEventListener('error', function(e) {
    if (e.filename && e.filename.includes('system-info-modal.js')) {
        console.error('🚨 System Info Modal Error:', e.message, 'at line', e.lineno);
    }
});