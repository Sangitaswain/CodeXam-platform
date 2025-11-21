/**
 * CodeXam Performance Monitor
 * Task 5.3: Add performance monitoring and metrics
 */

(function() {
    'use strict';
    
    // Performance metrics collection
    const performanceMetrics = {
        pageLoadStart: performance.now(),
        navigationStart: performance.timing.navigationStart,
        domContentLoaded: null,
        windowLoaded: null,
        firstPaint: null,
        firstContentfulPaint: null
    };
    
    // Initialize performance monitoring
    function initPerformanceMonitoring() {
        // Collect basic timing metrics
        collectTimingMetrics();
        
        // Monitor resource loading
        monitorResourceLoading();
        
        // Track user interactions
        trackUserInteractions();
        
        // Report metrics when page is fully loaded
        window.addEventListener('load', function() {
            setTimeout(reportMetrics, 100);
        });
    }
    
    function collectTimingMetrics() {
        // DOM Content Loaded
        document.addEventListener('DOMContentLoaded', function() {
            performanceMetrics.domContentLoaded = performance.now();
        });
        
        // Window Load
        window.addEventListener('load', function() {
            performanceMetrics.windowLoaded = performance.now();
        });
        
        // Paint Timing API (if supported)
        if ('getEntriesByType' in performance) {
            const paintEntries = performance.getEntriesByType('paint');
            paintEntries.forEach(function(entry) {
                if (entry.name === 'first-paint') {
                    performanceMetrics.firstPaint = entry.startTime;
                } else if (entry.name === 'first-contentful-paint') {
                    performanceMetrics.firstContentfulPaint = entry.startTime;
                }
            });
        }
    }
    
    function monitorResourceLoading() {
        // Monitor slow-loading resources
        window.addEventListener('load', function() {
            const resources = performance.getEntriesByType('resource');
            const slowResources = resources.filter(function(resource) {
                return resource.duration > 1000; // Resources taking more than 1 second
            });
            
            if (slowResources.length > 0) {
                console.warn('Slow loading resources detected:', slowResources);
            }
        });
    }
    
    function trackUserInteractions() {
        // Track time to first interaction
        let firstInteraction = null;
        
        const interactionEvents = ['click', 'keydown', 'touchstart'];
        
        interactionEvents.forEach(function(event) {
            document.addEventListener(event, function() {
                if (!firstInteraction) {
                    firstInteraction = performance.now();
                    performanceMetrics.firstInteraction = firstInteraction;
                }
            }, { once: true });
        });
    }
    
    function reportMetrics() {
        const timing = performance.timing;
        
        const metrics = {
            // Page Load Metrics
            pageLoadTime: performanceMetrics.windowLoaded || performance.now(),
            domContentLoadedTime: performanceMetrics.domContentLoaded,
            
            // Navigation Timing
            dnsLookup: timing.domainLookupEnd - timing.domainLookupStart,
            tcpConnect: timing.connectEnd - timing.connectStart,
            serverResponse: timing.responseEnd - timing.requestStart,
            domProcessing: timing.domComplete - timing.domLoading,
            
            // Paint Metrics
            firstPaint: performanceMetrics.firstPaint,
            firstContentfulPaint: performanceMetrics.firstContentfulPaint,
            
            // User Interaction
            firstInteraction: performanceMetrics.firstInteraction,
            
            // Resource Metrics
            resourceCount: performance.getEntriesByType('resource').length,
            
            // Page Info
            url: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };
        
        // Log metrics to console in development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.group('🚀 CodeXam Performance Metrics');
            console.log('Page Load Time:', metrics.pageLoadTime.toFixed(2) + 'ms');
            console.log('DOM Content Loaded:', metrics.domContentLoadedTime ? metrics.domContentLoadedTime.toFixed(2) + 'ms' : 'N/A');
            console.log('First Paint:', metrics.firstPaint ? metrics.firstPaint.toFixed(2) + 'ms' : 'N/A');
            console.log('First Contentful Paint:', metrics.firstContentfulPaint ? metrics.firstContentfulPaint.toFixed(2) + 'ms' : 'N/A');
            console.log('DNS Lookup:', metrics.dnsLookup + 'ms');
            console.log('Server Response:', metrics.serverResponse + 'ms');
            console.log('Resource Count:', metrics.resourceCount);
            console.groupEnd();
        }
        
        // Send metrics to server (in production)
        if (typeof sendMetricsToServer === 'function') {
            sendMetricsToServer(metrics);
        }
        
        // Store metrics in localStorage for debugging
        try {
            localStorage.setItem('codexam_performance_metrics', JSON.stringify(metrics));
        } catch (e) {
            // Storage might be disabled
        }
    }
    
    // Performance budget checker
    function checkPerformanceBudget() {
        const budget = {
            pageLoadTime: 3000,  // 3 seconds
            firstContentfulPaint: 1500,  // 1.5 seconds
            resourceCount: 50  // Maximum 50 resources
        };
        
        const current = {
            pageLoadTime: performanceMetrics.windowLoaded || performance.now(),
            firstContentfulPaint: performanceMetrics.firstContentfulPaint,
            resourceCount: performance.getEntriesByType('resource').length
        };
        
        const warnings = [];
        
        if (current.pageLoadTime > budget.pageLoadTime) {
            warnings.push(`Page load time (${current.pageLoadTime.toFixed(2)}ms) exceeds budget (${budget.pageLoadTime}ms)`);
        }
        
        if (current.firstContentfulPaint && current.firstContentfulPaint > budget.firstContentfulPaint) {
            warnings.push(`First Contentful Paint (${current.firstContentfulPaint.toFixed(2)}ms) exceeds budget (${budget.firstContentfulPaint}ms)`);
        }
        
        if (current.resourceCount > budget.resourceCount) {
            warnings.push(`Resource count (${current.resourceCount}) exceeds budget (${budget.resourceCount})`);
        }
        
        if (warnings.length > 0) {
            console.warn('⚠️ Performance Budget Warnings:');
            warnings.forEach(function(warning) {
                console.warn('  -', warning);
            });
        } else {
            console.log('✅ Performance budget met');
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPerformanceMonitoring);
    } else {
        initPerformanceMonitoring();
    }
    
    // Check performance budget after page load
    window.addEventListener('load', function() {
        setTimeout(checkPerformanceBudget, 1000);
    });
    
    // Expose metrics for external access
    window.CodeXamPerformance = {
        getMetrics: function() {
            return performanceMetrics;
        },
        checkBudget: checkPerformanceBudget
    };
    
})();
