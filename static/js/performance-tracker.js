/**
 * Frontend Performance Tracking for CodeXam Platform
 * 
 * This script monitors and reports frontend performance metrics including:
 * - Page load times
 * - Asset loading performance
 * - User interaction responsiveness
 * - Core Web Vitals
 * 
 * Version: 2.0.0
 * Author: CodeXam Development Team
 */

(function() {
    'use strict';
    
    // Performance tracking configuration
    const config = {
        apiEndpoint: '/api/performance/metrics',
        batchSize: 10,
        flushInterval: 30000, // 30 seconds
        enableConsoleLogging: false
    };
    
    // Metrics storage
    let metrics = [];
    let navigationStart = performance.timing.navigationStart;
    
    /**
     * Performance Metrics Collector
     */
    class PerformanceTracker {
        constructor() {
            this.metrics = [];
            this.observers = {};
            this.startTime = performance.now();
            
            this.init();
        }
        
        init() {
            // Wait for page to load before collecting metrics
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    this.collectInitialMetrics();
                    this.setupObservers();
                });
            } else {
                this.collectInitialMetrics();
                this.setupObservers();
            }
            
            // Setup periodic flushing
            setInterval(() => this.flushMetrics(), config.flushInterval);
            
            // Flush metrics before page unload
            window.addEventListener('beforeunload', () => this.flushMetrics());
        }
        
        collectInitialMetrics() {
            // Navigation Timing metrics
            this.collectNavigationTiming();
            
            // Resource Timing metrics
            this.collectResourceTiming();
            
            // Paint Timing metrics
            this.collectPaintTiming();
            
            // Layout Shift metrics
            this.collectLayoutShift();
        }
        
        collectNavigationTiming() {
            const timing = performance.timing;
            const navigation = performance.navigation;
            
            const metrics = {
                type: 'navigation',
                timestamp: Date.now(),
                data: {
                    // DNS lookup time
                    dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
                    
                    // TCP connection time
                    tcpConnection: timing.connectEnd - timing.connectStart,
                    
                    // Server response time
                    serverResponse: timing.responseEnd - timing.requestStart,
                    
                    // DOM processing time
                    domProcessing: timing.domComplete - timing.domLoading,
                    
                    // Total page load time
                    pageLoad: timing.loadEventEnd - timing.navigationStart,
                    
                    // DOM ready time
                    domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                    
                    // Navigation type
                    navigationType: navigation.type,
                    
                    // Redirect count
                    redirectCount: navigation.redirectCount
                }
            };
            
            this.addMetric(metrics);
        }
        
        collectResourceTiming() {
            const resources = performance.getEntriesByType('resource');
            
            resources.forEach(resource => {
                // Only track static assets
                if (this.isStaticAsset(resource.name)) {
                    const metrics = {
                        type: 'resource',
                        timestamp: Date.now(),
                        data: {
                            name: resource.name,
                            type: this.getResourceType(resource.name),
                            duration: resource.duration,
                            size: resource.transferSize || resource.encodedBodySize,
                            cached: resource.transferSize === 0,
                            startTime: resource.startTime,
                            responseEnd: resource.responseEnd
                        }
                    };
                    
                    this.addMetric(metrics);
                }
            });
        }
        
        collectPaintTiming() {
            const paintEntries = performance.getEntriesByType('paint');
            
            paintEntries.forEach(entry => {
                const metrics = {
                    type: 'paint',
                    timestamp: Date.now(),
                    data: {
                        name: entry.name,
                        startTime: entry.startTime,
                        duration: entry.duration
                    }
                };
                
                this.addMetric(metrics);
            });
        }
        
        collectLayoutShift() {
            if ('LayoutShift' in window) {
                let cumulativeLayoutShift = 0;
                
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            cumulativeLayoutShift += entry.value;
                        }
                    }
                    
                    const metrics = {
                        type: 'layout-shift',
                        timestamp: Date.now(),
                        data: {
                            value: entry.value,
                            cumulativeScore: cumulativeLayoutShift,
                            hadRecentInput: entry.hadRecentInput
                        }
                    };
                    
                    this.addMetric(metrics);
                });
                
                observer.observe({ entryTypes: ['layout-shift'] });
                this.observers.layoutShift = observer;
            }
        }
        
        setupObservers() {
            // Largest Contentful Paint
            if ('LargestContentfulPaint' in window) {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    
                    const metrics = {
                        type: 'lcp',
                        timestamp: Date.now(),
                        data: {
                            startTime: lastEntry.startTime,
                            size: lastEntry.size,
                            element: lastEntry.element ? lastEntry.element.tagName : null
                        }
                    };
                    
                    this.addMetric(metrics);
                });
                
                observer.observe({ entryTypes: ['largest-contentful-paint'] });
                this.observers.lcp = observer;
            }
            
            // First Input Delay
            if ('PerformanceEventTiming' in window) {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.name === 'first-input') {
                            const metrics = {
                                type: 'fid',
                                timestamp: Date.now(),
                                data: {
                                    delay: entry.processingStart - entry.startTime,
                                    duration: entry.duration,
                                    startTime: entry.startTime
                                }
                            };
                            
                            this.addMetric(metrics);
                        }
                    }
                });
                
                observer.observe({ entryTypes: ['first-input'] });
                this.observers.fid = observer;
            }
        }
        
        // Track custom user interactions
        trackInteraction(action, element, duration) {
            const metrics = {
                type: 'interaction',
                timestamp: Date.now(),
                data: {
                    action: action,
                    element: element,
                    duration: duration,
                    page: window.location.pathname
                }
            };
            
            this.addMetric(metrics);
        }
        
        // Track code editor performance
        trackEditorPerformance(operation, duration, linesOfCode) {
            const metrics = {
                type: 'editor',
                timestamp: Date.now(),
                data: {
                    operation: operation,
                    duration: duration,
                    linesOfCode: linesOfCode,
                    page: window.location.pathname
                }
            };
            
            this.addMetric(metrics);
        }
        
        // Track form submission performance
        trackFormSubmission(formName, duration, success) {
            const metrics = {
                type: 'form',
                timestamp: Date.now(),
                data: {
                    formName: formName,
                    duration: duration,
                    success: success,
                    page: window.location.pathname
                }
            };
            
            this.addMetric(metrics);
        }
        
        addMetric(metric) {
            this.metrics.push(metric);
            
            if (config.enableConsoleLogging) {
                console.log('Performance Metric:', metric);
            }
            
            // Auto-flush if batch size reached
            if (this.metrics.length >= config.batchSize) {
                this.flushMetrics();
            }
        }
        
        flushMetrics() {
            if (this.metrics.length === 0) return;
            
            const metricsToSend = [...this.metrics];
            this.metrics = [];
            
            // Send metrics to server
            this.sendMetrics(metricsToSend);
        }
        
        sendMetrics(metrics) {
            // Use sendBeacon for reliability, fallback to fetch
            const data = JSON.stringify({
                metrics: metrics,
                userAgent: navigator.userAgent,
                url: window.location.href,
                timestamp: Date.now()
            });
            
            if (navigator.sendBeacon) {
                navigator.sendBeacon(config.apiEndpoint, data);
            } else {
                fetch(config.apiEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: data,
                    keepalive: true
                }).catch(error => {
                    console.warn('Failed to send performance metrics:', error);
                });
            }
        }
        
        isStaticAsset(url) {
            const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2'];
            return staticExtensions.some(ext => url.includes(ext));
        }
        
        getResourceType(url) {
            if (url.includes('.css')) return 'css';
            if (url.includes('.js')) return 'js';
            if (url.match(/\.(png|jpg|jpeg|gif|svg|webp)$/)) return 'image';
            if (url.match(/\.(woff|woff2|ttf|eot)$/)) return 'font';
            return 'other';
        }
        
        // Get current performance summary
        getPerformanceSummary() {
            const timing = performance.timing;
            
            return {
                pageLoadTime: timing.loadEventEnd - timing.navigationStart,
                domReadyTime: timing.domContentLoadedEventEnd - timing.navigationStart,
                firstPaintTime: this.getFirstPaintTime(),
                resourceCount: performance.getEntriesByType('resource').length,
                metricsCollected: this.metrics.length
            };
        }
        
        getFirstPaintTime() {
            const paintEntries = performance.getEntriesByType('paint');
            const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
            return firstPaint ? firstPaint.startTime : null;
        }
    }
    
    // Initialize performance tracker
    const performanceTracker = new PerformanceTracker();
    
    // Expose global interface
    window.CodeXamPerformance = {
        trackInteraction: (action, element, duration) => {
            performanceTracker.trackInteraction(action, element, duration);
        },
        
        trackEditorPerformance: (operation, duration, linesOfCode) => {
            performanceTracker.trackEditorPerformance(operation, duration, linesOfCode);
        },
        
        trackFormSubmission: (formName, duration, success) => {
            performanceTracker.trackFormSubmission(formName, duration, success);
        },
        
        getSummary: () => {
            return performanceTracker.getPerformanceSummary();
        },
        
        flushMetrics: () => {
            performanceTracker.flushMetrics();
        }
    };
    
    // Auto-track common interactions
    document.addEventListener('click', function(event) {
        const startTime = performance.now();
        
        // Track button clicks
        if (event.target.tagName === 'BUTTON' || event.target.type === 'submit') {
            setTimeout(() => {
                const duration = performance.now() - startTime;
                performanceTracker.trackInteraction('click', event.target.tagName, duration);
            }, 0);
        }
    });
    
    // Track form submissions
    document.addEventListener('submit', function(event) {
        const startTime = performance.now();
        const formName = event.target.name || event.target.id || 'unknown';
        
        // Track submission timing
        const originalSubmit = event.target.onsubmit;
        event.target.onsubmit = function() {
            const duration = performance.now() - startTime;
            performanceTracker.trackFormSubmission(formName, duration, true);
            
            if (originalSubmit) {
                return originalSubmit.apply(this, arguments);
            }
        };
    });
    
    // Track page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            performanceTracker.flushMetrics();
        }
    });
    
    // Debug helper
    if (config.enableConsoleLogging) {
        console.log('CodeXam Performance Tracker initialized');
        
        // Expose debug methods
        window.debugPerformance = {
            getSummary: () => performanceTracker.getPerformanceSummary(),
            getMetrics: () => performanceTracker.metrics,
            flushNow: () => performanceTracker.flushMetrics()
        };
    }
    
})();