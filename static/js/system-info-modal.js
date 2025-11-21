/**
 * SystemInfoModal - Enhanced modal management for CodeXam
 * 
 * Features:
 * - Namespaced to avoid global pollution
 * - Comprehensive error handling
 * - Full accessibility support (WCAG 2.1 AA)
 * - Configurable behavior
 * - Focus management and keyboard navigation
 * - Screen reader announcements
 * - Memory leak prevention
 * 
 * @version 2.0.0
 * @author CodeXam Development Team
 */

const SystemInfoModal = {
    // Default configuration
    defaultConfig: {
        modalId: 'systemInfoModal',
        escapeKey: 'Escape',
        zIndex: 99999,
        closeOnClickOutside: true,
        closeOnEscape: true,
        trapFocus: true,
        announceToScreenReader: true,
        animationDuration: 300,
        debugMode: false
    },
    
    // Internal state
    state: {
        isVisible: false,
        isInitialized: false,
        originalBodyOverflow: '',
        previousActiveElement: null
    },
    
    // Event handlers (stored for cleanup)
    _handlers: {},
    
    /**
     * Initialize the modal system
     * @param {Object} customConfig - Custom configuration options
     */
    init(customConfig = {}) {
        if (this.state.isInitialized) {
            console.warn('⚠️ SystemInfoModal already initialized');
            return;
        }
        
        this.config = { ...this.defaultConfig, ...customConfig };
        this._setupEventListeners();
        this.state.isInitialized = true;
        
        this._log('✅ SystemInfoModal initialized', this.config);
    },
    
    /**
     * Show the system info modal
     * @returns {boolean} Success status
     */
    show() {
        try {
            this._log('🚀 SystemInfoModal.show() called');
            
            if (!this.state.isInitialized) {
                this.init();
            }
            
            const modal = this._getModal();
            if (!modal) {
                throw new Error(`Modal with ID '${this.config.modalId}' not found in DOM`);
            }
            
            if (this.state.isVisible) {
                this._log('⚠️ Modal is already visible');
                return true;
            }
            
            this._showModal(modal);
            return true;
            
        } catch (error) {
            this._handleError('Error showing modal', error);
            return false;
        }
    },
    
    /**
     * Hide the system info modal
     * @returns {boolean} Success status
     */
    hide() {
        try {
            this._log('🔧 SystemInfoModal.hide() called');
            
            const modal = this._getModal();
            if (modal && this.state.isVisible) {
                this._hideModal(modal);
            }
            
            return true;
            
        } catch (error) {
            this._handleError('Error hiding modal', error);
            return false;
        }
    },
    
    /**
     * Toggle modal visibility
     * @returns {boolean} Success status
     */
    toggle() {
        return this.state.isVisible ? this.hide() : this.show();
    },
    
    /**
     * Update configuration
     * @param {Object} newConfig - New configuration options
     */
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        this._log('🔧 Configuration updated', this.config);
    },
    
    /**
     * Clean up event listeners and reset state
     */
    destroy() {
        // Remove event listeners
        Object.entries(this._handlers).forEach(([event, handler]) => {
            document.removeEventListener(event, handler);
        });
        
        // Hide modal if visible
        if (this.state.isVisible) {
            this.hide();
        }
        
        // Reset state
        this.state.isInitialized = false;
        this._handlers = {};
        
        this._log('✅ SystemInfoModal destroyed');
    },
    
    // Private methods
    
    /**
     * Get the modal element
     * @returns {HTMLElement|null} Modal element
     * @private
     */
    _getModal() {
        return document.getElementById(this.config.modalId);
    },
    
    /**
     * Show the modal with all accessibility features
     * @param {HTMLElement} modal - Modal element
     * @private
     */
    _showModal(modal) {
        // Store original state
        this.state.originalBodyOverflow = document.body.style.overflow;
        this.state.previousActiveElement = document.activeElement;
        
        // Set ARIA attributes for accessibility
        modal.setAttribute('aria-hidden', 'false');
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        
        // Ensure modal has proper labeling
        if (!modal.hasAttribute('aria-labelledby') && !modal.hasAttribute('aria-label')) {
            modal.setAttribute('aria-label', 'System Information');
        }
        
        // Show modal with smooth transition
        modal.style.display = 'flex';
        modal.style.visibility = 'visible';
        modal.style.opacity = '1';
        modal.style.zIndex = this.config.zIndex;
        modal.classList.add('show');
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Focus management
        if (this.config.trapFocus) {
            this._trapFocus(modal);
        }
        
        // Update state
        this.state.isVisible = true;
        
        // Screen reader announcement
        if (this.config.announceToScreenReader) {
            this._announceToScreenReader('System information modal opened');
        }
        
        this._log('✅ Modal displayed successfully');
    },
    
    /**
     * Hide the modal and restore previous state
     * @param {HTMLElement} modal - Modal element
     * @private
     */
    _hideModal(modal) {
        // Set ARIA attributes
        modal.setAttribute('aria-hidden', 'true');
        
        // Hide modal
        modal.style.display = 'none';
        modal.classList.remove('show');
        
        // Restore body scroll
        document.body.style.overflow = this.state.originalBodyOverflow;
        
        // Restore focus
        if (this.state.previousActiveElement && typeof this.state.previousActiveElement.focus === 'function') {
            try {
                this.state.previousActiveElement.focus();
            } catch (error) {
                this._log('⚠️ Could not restore focus to previous element');
            }
        }
        
        // Clean up focus trap
        if (this._tabHandler) {
            modal.removeEventListener('keydown', this._tabHandler);
            this._tabHandler = null;
        }
        
        // Update state
        this.state.isVisible = false;
        
        // Screen reader announcement
        if (this.config.announceToScreenReader) {
            this._announceToScreenReader('System information modal closed');
        }
        
        this._log('✅ Modal hidden successfully');
    },
    
    /**
     * Set up event listeners for modal interaction
     * @private
     */
    _setupEventListeners() {
        // Escape key handler
        if (this.config.closeOnEscape) {
            this._handlers.keydown = (e) => {
                if (e.key === this.config.escapeKey && this.state.isVisible) {
                    e.preventDefault();
                    this.hide();
                }
            };
            document.addEventListener('keydown', this._handlers.keydown);
        }
        
        // Click outside to close
        if (this.config.closeOnClickOutside) {
            this._handlers.click = (e) => {
                const modal = this._getModal();
                if (modal && this.state.isVisible && e.target === modal) {
                    this.hide();
                }
            };
            document.addEventListener('click', this._handlers.click);
        }
    },
    
    /**
     * Implement focus trapping for accessibility
     * @param {HTMLElement} modal - Modal element
     * @private
     */
    _trapFocus(modal) {
        const focusableElements = modal.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length === 0) {
            // If no focusable elements, focus the modal itself
            modal.setAttribute('tabindex', '-1');
            modal.focus();
            return;
        }
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        // Focus first element
        firstElement.focus();
        
        // Tab key handler for focus trapping
        this._tabHandler = (e) => {
            if (e.key !== 'Tab') return;
            
            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        };
        
        modal.addEventListener('keydown', this._tabHandler);
    },
    
    /**
     * Announce messages to screen readers
     * @param {string} message - Message to announce
     * @private
     */
    _announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.style.cssText = `
            position: absolute !important;
            width: 1px !important;
            height: 1px !important;
            padding: 0 !important;
            margin: -1px !important;
            overflow: hidden !important;
            clip: rect(0, 0, 0, 0) !important;
            white-space: nowrap !important;
            border: 0 !important;
        `;
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            if (document.body.contains(announcement)) {
                document.body.removeChild(announcement);
            }
        }, 1000);
    },
    
    /**
     * Handle errors with logging and user feedback
     * @param {string} context - Error context
     * @param {Error} error - Error object
     * @private
     */
    _handleError(context, error) {
        const errorInfo = {
            context,
            message: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString(),
            config: this.config,
            state: this.state
        };
        
        console.error('❌ SystemInfoModal Error:', errorInfo);
        
        // Show user-friendly message
        this._showFallbackAlert('Unable to display system information. Please try again.');
        
        // In production, could send to error monitoring service
        // this._reportError(errorInfo);
    },
    
    /**
     * Show fallback alert for critical errors
     * @param {string} message - Alert message
     * @private
     */
    _showFallbackAlert(message) {
        // In production, this could be replaced with a toast notification
        if (typeof alert === 'function') {
            alert(message);
        } else {
            console.error('Fallback alert:', message);
        }
    },
    
    /**
     * Conditional logging based on debug mode
     * @param {string} message - Log message
     * @param {*} data - Additional data to log
     * @private
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
    
    // Testing and debugging methods
    
    /**
     * Run comprehensive test suite
     */
    test() {
        console.group('🔧 SystemInfoModal Test Suite');
        
        const tests = [
            { name: 'Modal Element Exists', fn: this._testModalExists },
            { name: 'Required Methods Exist', fn: this._testMethodsExist },
            { name: 'Show/Hide Functionality', fn: this._testShowHide },
            { name: 'Accessibility Features', fn: this._testAccessibility },
            { name: 'Event Handling', fn: this._testEventHandling }
        ];
        
        let passed = 0;
        let failed = 0;
        
        tests.forEach(test => {
            try {
                console.group(`Testing: ${test.name}`);
                test.fn.call(this);
                console.log('✅ PASSED');
                passed++;
            } catch (error) {
                console.error('❌ FAILED:', error.message);
                failed++;
            } finally {
                console.groupEnd();
            }
        });
        
        console.log(`\n📊 Test Results: ${passed} passed, ${failed} failed`);
        console.groupEnd();
        
        return { passed, failed, total: tests.length };
    },
    
    /**
     * Get debug information
     * @returns {Object} Debug information
     */
    getDebugInfo() {
        return {
            version: '2.0.0',
            config: this.config,
            state: this.state,
            modalExists: !!this._getModal(),
            isVisible: this.state.isVisible,
            isInitialized: this.state.isInitialized,
            handlersCount: Object.keys(this._handlers).length,
            timestamp: new Date().toISOString()
        };
    },
    
    // Test methods
    _testModalExists() {
        const modal = this._getModal();
        if (!modal) {
            throw new Error('Modal element not found in DOM');
        }
    },
    
    _testMethodsExist() {
        const requiredMethods = ['show', 'hide', 'toggle', 'init', 'destroy'];
        requiredMethods.forEach(method => {
            if (typeof this[method] !== 'function') {
                throw new Error(`Required method '${method}' is missing`);
            }
        });
    },
    
    _testShowHide() {
        const initialState = this.state.isVisible;
        
        // Test show
        const showResult = this.show();
        if (!showResult) {
            throw new Error('Show method returned false');
        }
        if (!this.state.isVisible) {
            throw new Error('State not updated after show');
        }
        
        // Test hide
        const hideResult = this.hide();
        if (!hideResult) {
            throw new Error('Hide method returned false');
        }
        if (this.state.isVisible) {
            throw new Error('State not updated after hide');
        }
        
        // Restore initial state
        if (initialState) {
            this.show();
        }
    },
    
    _testAccessibility() {
        const modal = this._getModal();
        if (!modal) return;
        
        const wasVisible = this.state.isVisible;
        
        this.show();
        
        const requiredAttributes = ['aria-hidden', 'role', 'aria-modal'];
        requiredAttributes.forEach(attr => {
            if (!modal.hasAttribute(attr)) {
                throw new Error(`Missing required accessibility attribute: ${attr}`);
            }
        });
        
        if (!wasVisible) {
            this.hide();
        }
    },
    
    _testEventHandling() {
        if (!this.state.isInitialized) {
            throw new Error('Modal not initialized - event handlers not set up');
        }
        
        const expectedHandlers = [];
        if (this.config.closeOnEscape) expectedHandlers.push('keydown');
        if (this.config.closeOnClickOutside) expectedHandlers.push('click');
        
        expectedHandlers.forEach(event => {
            if (!this._handlers[event]) {
                throw new Error(`Expected event handler '${event}' not found`);
            }
        });
    }
};

// Global API for backward compatibility and external access
if (typeof window !== 'undefined') {
    // Expose main functions
    window.showSystemInfoModal = () => SystemInfoModal.show();
    window.hideSystemInfoModal = () => SystemInfoModal.hide();
    
    // Development/testing functions
    window.testSystemInfoModal = () => SystemInfoModal.test();
    window.debugSystemInfoModal = () => console.table(SystemInfoModal.getDebugInfo());
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            SystemInfoModal.init();
        });
    } else {
        SystemInfoModal.init();
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SystemInfoModal;
}

console.log('✅ SystemInfoModal v2.0.0 loaded successfully');