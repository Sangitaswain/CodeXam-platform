/**
 * SystemStatsVisualizer - Advanced statistics visualization for System Info Modal
 * 
 * Features:
 * - ASCII-style charts and tables
 * - Real-time data updates
 * - Trend analysis
 * - Interactive command system
 * - Performance optimized rendering
 * 
 * @version 1.0.0
 * @author CodeXam Development Team
 */

const SystemStatsVisualizer = {
    // Configuration
    config: {
        updateInterval: 5000, // 5 seconds
        maxDataPoints: 50,
        chartWidth: 60,
        animationSpeed: 50,
        debugMode: false
    },
    
    // State management
    state: {
        isInitialized: false,
        isUpdating: false,
        updateTimer: null,
        cachedData: {},
        lastUpdate: null
    },
    
    // Data cache for trend analysis
    dataHistory: {
        systemInfo: [],
        platformStats: [],
        healthChecks: []
    },
    
    /**
     * Initialize the statistics visualizer
     */
    init() {
        if (this.state.isInitialized) {
            console.warn('⚠️ SystemStatsVisualizer already initialized');
            return;
        }
        
        this.state.isInitialized = true;
        this._log('✅ SystemStatsVisualizer initialized');
    },
    
    /**
     * Start real-time data updates
     */
    startUpdates() {
        if (this.state.isUpdating) {
            return;
        }
        
        this.state.isUpdating = true;
        this._updateData();
        
        this.state.updateTimer = setInterval(() => {
            this._updateData();
        }, this.config.updateInterval);
        
        this._log('🔄 Started real-time updates');
    },
    
    /**
     * Stop real-time data updates
     */
    stopUpdates() {
        if (this.state.updateTimer) {
            clearInterval(this.state.updateTimer);
            this.state.updateTimer = null;
        }
        
        this.state.isUpdating = false;
        this._log('⏹️ Stopped real-time updates');
    },
    
    /**
     * Render system status panel
     */
    renderSystemStatus() {
        const panel = document.getElementById('systemStatusPanel');
        if (!panel) return;
        
        const data = this.state.cachedData.systemInfo;
        if (!data) {
            panel.innerHTML = '<div class="status-loading">Loading system information...</div>';
            return;
        }
        
        const html = `
            <div class="status-line">
                <span class="status-label">Platform Status</span>
                <span class="status-value status-${data.platform?.status?.toLowerCase() || 'unknown'}">${data.platform?.status || 'UNKNOWN'}</span>
            </div>
            <div class="status-line">
                <span class="status-label">Uptime</span>
                <span class="status-value">${data.platform?.uptime || 'N/A'}</span>
            </div>
            <div class="status-line">
                <span class="status-label">Version</span>
                <span class="status-value">${data.platform?.version || 'N/A'}</span>
            </div>
            <div class="status-line">
                <span class="status-label">Database</span>
                <span class="status-value status-${data.database?.status?.toLowerCase() || 'unknown'}">${data.database?.status || 'UNKNOWN'}</span>
            </div>
            <div class="status-line">
                <span class="status-label">Response Time</span>
                <span class="status-value">${data.database?.response_time || 'N/A'}</span>
            </div>
        `;
        
        panel.innerHTML = html;
    },
    
    /**
     * Render performance metrics panel
     */
    renderPerformanceMetrics() {
        const panel = document.getElementById('performancePanel');
        if (!panel) return;
        
        const data = this.state.cachedData.systemInfo;
        if (!data?.performance) {
            panel.innerHTML = '<div class="status-loading">Loading performance metrics...</div>';
            return;
        }
        
        const perf = data.performance;
        const html = `
            <div class="metric-item">
                <span class="metric-label">CPU Usage</span>
                <span class="metric-value">${perf.cpu_usage || 0}%</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${perf.cpu_usage || 0}%"></div>
                </div>
            </div>
            <div class="metric-item">
                <span class="metric-label">Memory Usage</span>
                <span class="metric-value">${perf.memory_usage || 0}%</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${perf.memory_usage || 0}%"></div>
                </div>
            </div>
            <div class="metric-item">
                <span class="metric-label">Disk Usage</span>
                <span class="metric-value">${perf.disk_usage || 0}%</span>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${perf.disk_usage || 0}%"></div>
                </div>
            </div>
            <div class="metric-item">
                <span class="metric-label">Memory Available</span>
                <span class="metric-value">${perf.memory_available || 0} GB</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">Disk Free</span>
                <span class="metric-value">${perf.disk_free || 0} GB</span>
            </div>
        `;
        
        panel.innerHTML = html;
    },
    
    /**
     * Render platform statistics panel
     */
    renderPlatformStats() {
        const panel = document.getElementById('platformStatsPanel');
        if (!panel) return;
        
        const data = this.state.cachedData.platformStats;
        if (!data) {
            panel.innerHTML = '<div class="status-loading">Loading platform statistics...</div>';
            return;
        }
        
        const basic = data.basic || {};
        const html = `
            <div class="stat-item">
                <span class="stat-label">Total Problems</span>
                <span class="stat-value">${basic.total_problems || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Submissions</span>
                <span class="stat-value">${basic.total_submissions || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Active Users</span>
                <span class="stat-value">${basic.active_users || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Success Rate</span>
                <span class="stat-value">${basic.success_rate || 0}%</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Recent Activity</span>
                <span class="stat-value">${data.activity?.recent_submissions || 0} submissions (24h)</span>
            </div>
        `;
        
        panel.innerHTML = html;
    },
    
    /**
     * Render language statistics with ASCII chart
     */
    renderLanguageStats() {
        const panel = document.getElementById('languageStatsPanel');
        if (!panel) return;
        
        const data = this.state.cachedData.platformStats;
        if (!data?.languages) {
            panel.innerHTML = '<div class="status-loading">Loading language statistics...</div>';
            return;
        }
        
        const distribution = data.languages.distribution || {};
        const successRates = data.languages.success_rates || {};
        
        let html = '<div class="chart-title">📊 Language Distribution</div>';
        html += this._createASCIIChart(distribution, 'Submissions');
        
        html += '<div class="chart-title" style="margin-top: 2rem;">📈 Success Rates by Language</div>';
        const successData = {};
        Object.keys(successRates).forEach(lang => {
            successData[lang] = successRates[lang].success_rate || 0;
        });
        html += this._createASCIIChart(successData, 'Success %', '%');
        
        panel.innerHTML = html;
    },
    
    /**
     * Create ASCII-style bar chart
     */
    _createASCIIChart(data, label = 'Value', unit = '') {
        if (!data || Object.keys(data).length === 0) {
            return '<div class="chart-empty">No data available</div>';
        }
        
        const maxValue = Math.max(...Object.values(data));
        const maxBarLength = this.config.chartWidth;
        
        let html = '<div class="ascii-chart">';
        
        Object.entries(data)
            .sort(([,a], [,b]) => b - a)
            .forEach(([key, value]) => {
                const barLength = maxValue > 0 ? Math.round((value / maxValue) * maxBarLength) : 0;
                const bar = '█'.repeat(barLength);
                const padding = ' '.repeat(Math.max(0, maxBarLength - barLength));
                
                html += `
                    <div class="chart-row">
                        <span class="chart-label">${key.padEnd(12)}</span>
                        <span class="chart-bar">│${bar}${padding}│</span>
                        <span class="chart-value">${value}${unit}</span>
                    </div>
                `;
            });
        
        html += '</div>';
        return html;
    },
    
    /**
     * Create ASCII table
     */
    _createASCIITable(data, headers) {
        if (!data || data.length === 0) {
            return '<div class="table-empty">No data available</div>';
        }
        
        // Calculate column widths
        const colWidths = headers.map((header, i) => {
            let maxWidth = header.length;
            data.forEach(row => {
                if (row[i] && row[i].toString().length > maxWidth) {
                    maxWidth = row[i].toString().length;
                }
            });
            return Math.min(maxWidth + 2, 20); // Max width of 20
        });
        
        let html = '<div class="ascii-table">';
        
        // Header
        html += '<div class="table-row table-header">';
        headers.forEach((header, i) => {
            html += `<span class="table-cell" style="width: ${colWidths[i] * 0.6}rem">${header}</span>`;
        });
        html += '</div>';
        
        // Separator
        html += '<div class="table-separator">';
        colWidths.forEach(width => {
            html += `<span class="table-cell" style="width: ${width * 0.6}rem">${'─'.repeat(width)}</span>`;
        });
        html += '</div>';
        
        // Data rows
        data.forEach(row => {
            html += '<div class="table-row">';
            row.forEach((cell, i) => {
                html += `<span class="table-cell" style="width: ${colWidths[i] * 0.6}rem">${cell || ''}</span>`;
            });
            html += '</div>';
        });
        
        html += '</div>';
        return html;
    },
    
    /**
     * Render top performers leaderboard
     */
    renderTopPerformers() {
        const panel = document.getElementById('topPerformersPanel');
        if (!panel) return;
        
        const data = this.state.cachedData.platformStats;
        if (!data?.leaderboard?.top_performers) {
            panel.innerHTML = '<div class="status-loading">Loading leaderboard...</div>';
            return;
        }
        
        const performers = data.leaderboard.top_performers;
        if (performers.length === 0) {
            panel.innerHTML = '<div class="chart-empty">No performance data available</div>';
            return;
        }
        
        const tableData = performers.map((performer, index) => [
            `#${index + 1}`,
            performer.user,
            performer.solved.toString()
        ]);
        
        const html = `
            <div class="chart-title">🏆 Top Performers</div>
            ${this._createASCIITable(tableData, ['Rank', 'User', 'Solved'])}
        `;
        
        panel.innerHTML = html;
    },
    
    /**
     * Render problem difficulty distribution
     */
    renderDifficultyDistribution() {
        const panel = document.getElementById('difficultyPanel');
        if (!panel) return;
        
        const data = this.state.cachedData.platformStats;
        if (!data?.problems?.difficulty_distribution) {
            panel.innerHTML = '<div class="status-loading">Loading difficulty distribution...</div>';
            return;
        }
        
        const distribution = data.problems.difficulty_distribution;
        const html = `
            <div class="chart-title">📊 Problem Difficulty Distribution</div>
            ${this._createASCIIChart(distribution, 'Problems')}
        `;
        
        panel.innerHTML = html;
    },
    
    /**
     * Update all data from APIs with comprehensive error handling
     */
    async _updateData() {
        const maxRetries = 3;
        let retryCount = 0;
        
        while (retryCount < maxRetries) {
            try {
                // Use Promise.allSettled to handle partial failures
                const results = await Promise.allSettled([
                    this._fetchSystemInfo(),
                    this._fetchPlatformStats(),
                    this._fetchHealthCheck()
                ]);
                
                // Process results and handle partial failures
                const [systemInfoResult, platformStatsResult, healthCheckResult] = results;
                
                // Update cache with available data
                this.state.cachedData = {
                    systemInfo: systemInfoResult.status === 'fulfilled' ? systemInfoResult.value?.data : null,
                    platformStats: platformStatsResult.status === 'fulfilled' ? platformStatsResult.value?.data : null,
                    healthCheck: healthCheckResult.status === 'fulfilled' ? healthCheckResult.value?.data : null
                };
                
                // Log any failures
                results.forEach((result, index) => {
                    if (result.status === 'rejected') {
                        const endpoints = ['system-info', 'platform-stats', 'health-check'];
                        console.warn(`⚠️ Failed to fetch ${endpoints[index]}: ${result.reason.message}`);
                    }
                });
                
                // Store in history for trend analysis (only if we have some data)
                if (Object.values(this.state.cachedData).some(data => data !== null)) {
                    this._updateHistory();
                }
                
                // Update all panels
                this._updateAllPanels();
                
                this.state.lastUpdate = new Date();
                this._log('📊 Data updated successfully');
                
                // Reset retry count on success
                retryCount = 0;
                break;
                
            } catch (error) {
                retryCount++;
                console.error(`❌ Error updating data (attempt ${retryCount}/${maxRetries}):`, error);
                
                if (retryCount >= maxRetries) {
                    // Show error in panels
                    this._showErrorInPanels(error.message);
                    
                    // Use cached data if available
                    if (Object.keys(this.state.cachedData).length > 0) {
                        this._log('📊 Using cached data due to fetch errors');
                        this._updateAllPanels();
                    }
                } else {
                    // Wait before retry (exponential backoff)
                    const delay = Math.pow(2, retryCount) * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
    },
    
    /**
     * Show error message in all panels
     */
    _showErrorInPanels(errorMessage) {
        const panels = [
            'systemStatusPanel',
            'platformStatsPanel', 
            'performancePanel',
            'languageStatsPanel',
            'topPerformersPanel',
            'difficultyPanel'
        ];
        
        panels.forEach(panelId => {
            const panel = document.getElementById(panelId);
            if (panel) {
                panel.innerHTML = `
                    <div class="status-error">
                        ❌ Error loading data: ${errorMessage}
                    </div>
                    <div class="status-info" style="margin-top: 1rem;">
                        Retrying automatically...
                    </div>
                `;
            }
        });
    },
    
    /**
     * Fetch system information with error handling
     */
    async _fetchSystemInfo() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
            
            const response = await fetch('/api/system-info', {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error('Rate limit exceeded. Please wait before refreshing.');
                } else if (response.status >= 500) {
                    throw new Error('Server error. Please try again later.');
                } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            }
            
            const data = await response.json();
            
            // Validate response structure
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }
            
            return data;
            
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout. Please check your connection.');
            }
            throw error;
        }
    },
    
    /**
     * Fetch platform statistics with error handling
     */
    async _fetchPlatformStats() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000);
            
            const response = await fetch('/api/platform-stats', {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error('Rate limit exceeded. Please wait before refreshing.');
                } else if (response.status >= 500) {
                    throw new Error('Server error. Please try again later.');
                } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            }
            
            const data = await response.json();
            
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }
            
            return data;
            
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout. Please check your connection.');
            }
            throw error;
        }
    },
    
    /**
     * Fetch health check data with error handling
     */
    async _fetchHealthCheck() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000);
            
            const response = await fetch('/api/health-check', {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error('Rate limit exceeded. Please wait before refreshing.');
                } else if (response.status >= 500) {
                    throw new Error('Server error. Please try again later.');
                } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            }
            
            const data = await response.json();
            
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }
            
            return data;
            
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout. Please check your connection.');
            }
            throw error;
        }
    },
    
    /**
     * Update data history for trend analysis
     */
    _updateHistory() {
        const timestamp = new Date().toISOString();
        
        // Add to history with timestamp
        if (this.state.cachedData.systemInfo) {
            this.dataHistory.systemInfo.push({
                timestamp,
                data: this.state.cachedData.systemInfo
            });
        }
        
        if (this.state.cachedData.platformStats) {
            this.dataHistory.platformStats.push({
                timestamp,
                data: this.state.cachedData.platformStats
            });
        }
        
        if (this.state.cachedData.healthCheck) {
            this.dataHistory.healthChecks.push({
                timestamp,
                data: this.state.cachedData.healthCheck
            });
        }
        
        // Limit history size
        Object.keys(this.dataHistory).forEach(key => {
            if (this.dataHistory[key].length > this.config.maxDataPoints) {
                this.dataHistory[key] = this.dataHistory[key].slice(-this.config.maxDataPoints);
            }
        });
    },
    
    /**
     * Update all panels with new data
     */
    _updateAllPanels() {
        this.renderSystemStatus();
        this.renderPerformanceMetrics();
        this.renderPlatformStats();
        this.renderLanguageStats();
        this.renderTopPerformers();
        this.renderDifficultyDistribution();
        
        // Highlight changes
        this._highlightChanges();
    },
    
    /**
     * Highlight data changes with visual effects
     */
    _highlightChanges() {
        // Add visual indicators for data that has changed
        const panels = document.querySelectorAll('.terminal-panel');
        panels.forEach(panel => {
            panel.classList.add('data-updated');
            setTimeout(() => {
                panel.classList.remove('data-updated');
            }, 1000);
        });
    },
    
    /**
     * Get trend analysis for a specific metric
     */
    getTrendAnalysis(metric, dataType = 'systemInfo') {
        const history = this.dataHistory[dataType];
        if (!history || history.length < 2) {
            return { trend: 'insufficient_data', change: 0 };
        }
        
        const recent = history.slice(-5); // Last 5 data points
        const values = recent.map(entry => this._getNestedValue(entry.data, metric)).filter(v => v !== null);
        
        if (values.length < 2) {
            return { trend: 'no_data', change: 0 };
        }
        
        const first = values[0];
        const last = values[values.length - 1];
        const change = last - first;
        const percentChange = first !== 0 ? (change / first) * 100 : 0;
        
        let trend = 'stable';
        if (Math.abs(percentChange) > 5) {
            trend = change > 0 ? 'increasing' : 'decreasing';
        }
        
        return {
            trend,
            change: percentChange,
            values,
            timestamps: recent.map(entry => entry.timestamp)
        };
    },
    
    /**
     * Get nested object value by path
     */
    _getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key] !== undefined ? current[key] : null;
        }, obj);
    },
    
    /**
     * Generate comprehensive statistics report
     */
    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            system: this.state.cachedData.systemInfo,
            platform: this.state.cachedData.platformStats,
            health: this.state.cachedData.healthCheck,
            trends: {
                cpu_usage: this.getTrendAnalysis('performance.cpu_usage'),
                memory_usage: this.getTrendAnalysis('performance.memory_usage'),
                submissions: this.getTrendAnalysis('basic.total_submissions', 'platformStats')
            },
            summary: this._generateSummary()
        };
        
        return report;
    },
    
    /**
     * Generate summary of current system state
     */
    _generateSummary() {
        const system = this.state.cachedData.systemInfo;
        const platform = this.state.cachedData.platformStats;
        
        const summary = {
            overall_health: 'good',
            alerts: [],
            recommendations: []
        };
        
        // Check for issues
        if (system?.performance?.cpu_usage > 80) {
            summary.alerts.push('High CPU usage detected');
            summary.overall_health = 'warning';
        }
        
        if (system?.performance?.memory_usage > 85) {
            summary.alerts.push('High memory usage detected');
            summary.overall_health = 'warning';
        }
        
        if (system?.database?.status !== 'CONNECTED') {
            summary.alerts.push('Database connection issues');
            summary.overall_health = 'critical';
        }
        
        // Generate recommendations
        if (platform?.basic?.success_rate < 50) {
            summary.recommendations.push('Consider reviewing problem difficulty balance');
        }
        
        if (platform?.activity?.recent_submissions < 10) {
            summary.recommendations.push('Low recent activity - consider engagement strategies');
        }
        
        return summary;
    },
    
    /**
     * Export data as JSON
     */
    exportData() {
        const exportData = {
            timestamp: new Date().toISOString(),
            current_data: this.state.cachedData,
            history: this.dataHistory,
            report: this.generateReport()
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `codexam-stats-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this._log('📁 Data exported successfully');
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
        this.stopUpdates();
        this.state.isInitialized = false;
        this.state.cachedData = {};
        this.dataHistory = {
            systemInfo: [],
            platformStats: [],
            healthChecks: []
        };
        
        this._log('✅ SystemStatsVisualizer destroyed');
    }
};

// Global API
if (typeof window !== 'undefined') {
    window.SystemStatsVisualizer = SystemStatsVisualizer;
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            SystemStatsVisualizer.init();
        });
    } else {
        SystemStatsVisualizer.init();
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SystemStatsVisualizer;
}

console.log('✅ SystemStatsVisualizer v1.0.0 loaded successfully');