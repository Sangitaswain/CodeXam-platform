/**
 * Enhanced Submission Handler for CodeXam Platform
 * Handles code submissions with real-time feedback, validation, and user experience enhancements.
 * 
 * @version 2.0.0
 * @author CodeXam Development Team
 */

class SubmissionHandler {
    constructor(options = {}) {
        this.config = {
            maxSubmissionRate: 5, // submissions per minute
            cooldownPeriod: 60000, // 1 minute
            validationDelay: 500, // ms
            showRealTimeValidation: true,
            enableSubmissionHistory: true,
            autoSaveSubmissions: true,
            ...options
        };
        
        this.state = {
            initialized: false,
            submissionCount: 0,
            lastSubmissionTime: 0,
            isSubmitting: false,
            validationTimer: null,
            submissionHistory: []
        };
        
        this.init();
    }
    
    init() {
        if (this.state.initialized) return;
        
        this.setupEventListeners();
        this.loadSubmissionHistory();
        this.setupRateLimiting();
        
        this.state.initialized = true;
        console.log('✅ SubmissionHandler initialized');
    }
    
    setupEventListeners() {
        // Form submission
        document.addEventListener('submit', (e) => {
            if (e.target.matches('.submission-form, #submission-form')) {
                e.preventDefault();
                this.handleFormSubmission(e.target);
            }
        });
        
        // Code validation on input
        document.addEventListener('input', (e) => {
            if (e.target.matches('#code-editor, .code-editor, textarea[name="code"]')) {
                this.handleCodeInput(e.target);
            }
        });
        
        // Language change
        document.addEventListener('change', (e) => {
            if (e.target.matches('#language-select, select[name="language"]')) {
                this.handleLanguageChange(e.target.value);
            }
        });
    }    

    async handleFormSubmission(form) {
        if (this.state.isSubmitting) {
            this.showNotification('Please wait for the current submission to complete', 'warning');
            return;
        }
        
        // Rate limiting check
        if (!this.checkRateLimit()) {
            this.showNotification('Too many submissions. Please wait before submitting again.', 'warning');
            return;
        }
        
        // Validate form data
        const validation = this.validateSubmission(form);
        if (!validation.valid) {
            this.showNotification(validation.message, 'error');
            return;
        }
        
        this.state.isSubmitting = true;
        this.updateSubmissionUI(true);
        
        try {
            const result = await this.submitCode(form);
            this.handleSubmissionSuccess(result);
        } catch (error) {
            this.handleSubmissionError(error);
        } finally {
            this.state.isSubmitting = false;
            this.updateSubmissionUI(false);
        }
    }
    
    validateSubmission(form) {
        const formData = new FormData(form);
        const code = formData.get('code')?.trim();
        const language = formData.get('language');
        const problemId = formData.get('problem_id');
        
        if (!code) {
            return { valid: false, message: 'Please enter your code before submitting' };
        }
        
        if (code.length > 50000) {
            return { valid: false, message: 'Code exceeds maximum length of 50,000 characters' };
        }
        
        if (!language || !['python', 'javascript', 'java', 'cpp'].includes(language)) {
            return { valid: false, message: 'Please select a valid programming language' };
        }
        
        if (!problemId) {
            return { valid: false, message: 'Problem ID is missing' };
        }
        
        // Security validation
        const securityCheck = this.performSecurityValidation(code, language);
        if (!securityCheck.safe) {
            return { valid: false, message: securityCheck.message };
        }
        
        return { valid: true };
    }
    
    performSecurityValidation(code, language) {
        const dangerousPatterns = {
            python: [
                /import\s+(os|sys|subprocess|socket|urllib|requests|tempfile|shutil)/gi,
                /from\s+(os|sys|subprocess|socket|urllib|requests|tempfile|shutil)/gi,
                /(open|file|input|eval|exec)\s*\(/gi
            ],
            javascript: [
                /require\s*\(['"][^'"]*fs['"]\)/gi,
                /require\s*\(['"][^'"]*child_process['"]\)/gi,
                /process\./gi,
                /(eval|Function)\s*\(/gi
            ],
            java: [
                /import\s+java\.io\./gi,
                /import\s+java\.nio\./gi,
                /Runtime\.getRuntime/gi,
                /ProcessBuilder/gi
            ],
            cpp: [
                /#include\s*<(fstream|iostream|cstdlib|system)>/gi,
                /system\s*\(/gi,
                /popen\s*\(/gi
            ]
        };
        
        const patterns = dangerousPatterns[language] || [];
        
        for (const pattern of patterns) {
            if (pattern.test(code)) {
                return {
                    safe: false,
                    message: 'Code contains restricted operations that are not allowed for security reasons'
                };
            }
        }
        
        return { safe: true };
    }
    
    async submitCode(form) {
        const formData = new FormData(form);
        
        // Add submission metadata
        formData.append('submission_time', new Date().toISOString());
        formData.append('user_agent', navigator.userAgent);
        
        const result = await ajax.submitForm(form, {
            loadingElement: form.querySelector('button[type="submit"]')
        });
        
        // Update rate limiting
        this.updateRateLimit();
        
        // Store in history
        if (this.config.enableSubmissionHistory) {
            this.addToSubmissionHistory(formData, result);
        }
        
        return result;
    }
    
    handleSubmissionSuccess(result) {
        const data = result.data;
        
        // Show success notification
        this.showNotification(`Submission successful! Result: ${data.result}`, 'success');
        
        // Display detailed results
        this.displaySubmissionResults(data);
        
        // Update UI based on result
        this.updateResultUI(data);
        
        // Announce to screen readers
        this.announceToScreenReader(`Code submitted successfully. Result: ${data.result}`);
        
        // Auto-save successful submission
        if (this.config.autoSaveSubmissions && data.result === 'PASS') {
            this.saveSuccessfulSubmission(data);
        }
    }
    
    handleSubmissionError(error) {
        console.error('Submission error:', error);
        
        let message = 'Submission failed. Please try again.';
        
        if (error.name === 'NetworkError') {
            message = 'Network error. Please check your connection and try again.';
        } else if (error.name === 'TimeoutError') {
            message = 'Submission timed out. Please try again.';
        } else if (error.name === 'HTTPError') {
            if (error.status === 429) {
                message = 'Too many requests. Please wait before submitting again.';
            } else if (error.status >= 500) {
                message = 'Server error. Please try again later.';
            }
        } else if (error.name === 'ApplicationError' && error.data?.error?.message) {
            message = error.data.error.message;
        }
        
        this.showNotification(message, 'error');
    }   
 
    displaySubmissionResults(data) {
        // Create or update results panel
        let resultsPanel = document.querySelector('.submission-results');
        if (!resultsPanel) {
            resultsPanel = document.createElement('div');
            resultsPanel.className = 'submission-results';
            resultsPanel.setAttribute('role', 'region');
            resultsPanel.setAttribute('aria-label', 'Submission Results');
            
            const editorContainer = document.querySelector('.editor-container, .code-editor-container');
            if (editorContainer) {
                editorContainer.parentNode.insertBefore(resultsPanel, editorContainer.nextSibling);
            } else {
                document.querySelector('.container, main').appendChild(resultsPanel);
            }
        }
        
        const resultClass = data.result.toLowerCase();
        const resultIcon = {
            'pass': '✅',
            'fail': '❌',
            'error': '⚠️'
        }[resultClass] || '❓';
        
        resultsPanel.innerHTML = `
            <div class="result-header result-${resultClass}">
                <h3>
                    <span class="result-icon" aria-hidden="true">${resultIcon}</span>
                    Submission Result: ${data.result}
                </h3>
                <p class="result-message">${data.message}</p>
            </div>
            
            ${this.renderTestResults(data.test_results)}
            ${this.renderPerformanceMetrics(data)}
            ${this.renderSubmissionDetails(data)}
        `;
        
        // Scroll to results
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Add animation
        resultsPanel.classList.add('results-animate-in');
        setTimeout(() => {
            resultsPanel.classList.remove('results-animate-in');
        }, 500);
    }
    
    renderTestResults(testResults) {
        if (!testResults || testResults.length === 0) {
            return '';
        }
        
        const passedCount = testResults.filter(test => test.passed).length;
        const totalCount = testResults.length;
        
        return `
            <div class="test-results">
                <h4>Test Cases (${passedCount}/${totalCount} passed)</h4>
                <div class="test-cases">
                    ${testResults.map((test, index) => `
                        <div class="test-case ${test.passed ? 'passed' : 'failed'}">
                            <div class="test-header">
                                <span class="test-number">Test ${index + 1}</span>
                                <span class="test-status">
                                    ${test.passed ? '✅ PASS' : '❌ FAIL'}
                                </span>
                            </div>
                            ${!test.passed && test.expected && test.actual ? `
                                <div class="test-details">
                                    <div class="test-expected">Expected: ${test.expected}</div>
                                    <div class="test-actual">Got: ${test.actual}</div>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    renderPerformanceMetrics(data) {
        if (!data.execution_time && !data.memory_used) {
            return '';
        }
        
        return `
            <div class="performance-metrics">
                <h4>Performance</h4>
                <div class="metrics-grid">
                    ${data.execution_time ? `
                        <div class="metric">
                            <span class="metric-label">Execution Time</span>
                            <span class="metric-value">${data.execution_time}ms</span>
                        </div>
                    ` : ''}
                    ${data.memory_used ? `
                        <div class="metric">
                            <span class="metric-label">Memory Used</span>
                            <span class="metric-value">${this.formatBytes(data.memory_used)}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    renderSubmissionDetails(data) {
        return `
            <div class="submission-details">
                <div class="details-grid">
                    <div class="detail">
                        <span class="detail-label">Language</span>
                        <span class="detail-value">${data.language || 'Unknown'}</span>
                    </div>
                    <div class="detail">
                        <span class="detail-label">Submitted</span>
                        <span class="detail-value">${new Date().toLocaleString()}</span>
                    </div>
                    ${data.submission_id ? `
                        <div class="detail">
                            <span class="detail-label">Submission ID</span>
                            <span class="detail-value">#${data.submission_id}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    checkRateLimit() {
        const now = Date.now();
        const timeSinceLastSubmission = now - this.state.lastSubmissionTime;
        
        // Reset counter if cooldown period has passed
        if (timeSinceLastSubmission > this.config.cooldownPeriod) {
            this.state.submissionCount = 0;
        }
        
        return this.state.submissionCount < this.config.maxSubmissionRate;
    }
    
    updateRateLimit() {
        this.state.submissionCount++;
        this.state.lastSubmissionTime = Date.now();
    }
    
    setupRateLimiting() {
        // Load rate limiting data from localStorage
        try {
            const saved = localStorage.getItem('codexam_rate_limit');
            if (saved) {
                const data = JSON.parse(saved);
                this.state.submissionCount = data.count || 0;
                this.state.lastSubmissionTime = data.lastTime || 0;
            }
        } catch (error) {
            console.error('Failed to load rate limiting data:', error);
        }
        
        // Save rate limiting data periodically
        setInterval(() => {
            try {
                localStorage.setItem('codexam_rate_limit', JSON.stringify({
                    count: this.state.submissionCount,
                    lastTime: this.state.lastSubmissionTime
                }));
            } catch (error) {
                console.error('Failed to save rate limiting data:', error);
            }
        }, 10000); // Every 10 seconds
    }
    
    handleCodeInput(codeEditor) {
        // Clear previous validation timer
        clearTimeout(this.state.validationTimer);
        
        // Debounced validation
        if (this.config.showRealTimeValidation) {
            this.state.validationTimer = setTimeout(() => {
                this.validateCodeRealTime(codeEditor);
            }, this.config.validationDelay);
        }
        
        // Update character count
        this.updateCharacterCount(codeEditor);
    }
    
    validateCodeRealTime(codeEditor) {
        const code = codeEditor.value;
        const language = this.getCurrentLanguage();
        
        // Clear previous validation indicators
        this.clearValidationIndicators(codeEditor);
        
        // Basic validation
        const issues = [];
        
        if (code.length > 50000) {
            issues.push({
                type: 'error',
                message: 'Code exceeds maximum length'
            });
        }
        
        // Security validation
        const securityCheck = this.performSecurityValidation(code, language);
        if (!securityCheck.safe) {
            issues.push({
                type: 'warning',
                message: 'Code contains restricted operations'
            });
        }
        
        // Display validation results
        this.displayValidationResults(codeEditor, issues);
    }
    
    displayValidationResults(codeEditor, issues) {
        if (issues.length === 0) return;
        
        // Create validation panel
        let validationPanel = codeEditor.parentNode.querySelector('.validation-panel');
        if (!validationPanel) {
            validationPanel = document.createElement('div');
            validationPanel.className = 'validation-panel';
            validationPanel.setAttribute('role', 'alert');
            validationPanel.setAttribute('aria-live', 'polite');
            codeEditor.parentNode.appendChild(validationPanel);
        }
        
        validationPanel.innerHTML = issues.map(issue => `
            <div class="validation-issue validation-${issue.type}">
                <span class="issue-icon" aria-hidden="true">
                    ${issue.type === 'error' ? '❌' : '⚠️'}
                </span>
                <span class="issue-message">${issue.message}</span>
            </div>
        `).join('');
    }
    
    clearValidationIndicators(codeEditor) {
        const validationPanel = codeEditor.parentNode.querySelector('.validation-panel');
        if (validationPanel) {
            validationPanel.innerHTML = '';
        }
    }
    
    updateCharacterCount(codeEditor) {
        const counter = document.querySelector('.character-count');
        if (!counter) return;
        
        const currentLength = codeEditor.value.length;
        const maxLength = 50000;
        const percentage = (currentLength / maxLength) * 100;
        
        counter.textContent = `${currentLength.toLocaleString()} / ${maxLength.toLocaleString()} characters`;
        
        // Update styling
        counter.className = 'character-count';
        if (percentage > 90) {
            counter.classList.add('text-danger');
        } else if (percentage > 75) {
            counter.classList.add('text-warning');
        } else {
            counter.classList.add('text-muted');
        }
    }
    
    handleLanguageChange(language) {
        // Clear validation when language changes
        const codeEditor = document.querySelector('#code-editor, .code-editor, textarea[name="code"]');
        if (codeEditor) {
            this.clearValidationIndicators(codeEditor);
        }
        
        // Announce language change
        this.announceToScreenReader(`Programming language changed to ${language}`);
    }
    
    getCurrentLanguage() {
        const languageSelect = document.querySelector('#language-select, select[name="language"]');
        return languageSelect ? languageSelect.value : 'python';
    }
    
    updateSubmissionUI(isSubmitting) {
        const submitButton = document.querySelector('button[type="submit"]');
        const form = document.querySelector('.submission-form, #submission-form');
        
        if (submitButton) {
            submitButton.disabled = isSubmitting;
            if (isSubmitting) {
                submitButton.innerHTML = `
                    <span class="loading-spinner" aria-hidden="true"></span>
                    Submitting...
                `;
            } else {
                submitButton.innerHTML = `
                    <span class="submit-icon" aria-hidden="true">🚀</span>
                    Submit Code
                `;
            }
        }
        
        if (form) {
            form.classList.toggle('submitting', isSubmitting);
        }
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showNotification(message, type = 'info') {
        if (typeof showAlert === 'function') {
            showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    announceToScreenReader(message) {
        const liveRegion = document.getElementById('submission-announcements') || 
                          document.getElementById('aria-live-region');
        
        if (liveRegion) {
            liveRegion.textContent = message;
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }
    
    addToSubmissionHistory(formData, result) {
        const submission = {
            id: Date.now(),
            code: formData.get('code'),
            language: formData.get('language'),
            problemId: formData.get('problem_id'),
            result: result.data.result,
            message: result.data.message,
            timestamp: new Date().toISOString()
        };
        
        this.state.submissionHistory.unshift(submission);
        
        // Limit history size
        if (this.state.submissionHistory.length > 50) {
            this.state.submissionHistory = this.state.submissionHistory.slice(0, 50);
        }
        
        this.saveSubmissionHistory();
    }
    
    loadSubmissionHistory() {
        try {
            const saved = localStorage.getItem('codexam_submission_history');
            if (saved) {
                this.state.submissionHistory = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Failed to load submission history:', error);
        }
    }
    
    saveSubmissionHistory() {
        try {
            localStorage.setItem('codexam_submission_history', JSON.stringify(this.state.submissionHistory));
        } catch (error) {
            console.error('Failed to save submission history:', error);
        }
    }
    
    saveSuccessfulSubmission(data) {
        const key = `codexam_success_${data.problem_id || 'unknown'}`;
        try {
            localStorage.setItem(key, JSON.stringify({
                code: data.code,
                language: data.language,
                result: data.result,
                timestamp: new Date().toISOString()
            }));
        } catch (error) {
            console.error('Failed to save successful submission:', error);
        }
    }
    
    updateResultUI(data) {
        // Update page title
        const originalTitle = document.title;
        document.title = `${data.result} - ${originalTitle}`;
        
        // Reset title after 5 seconds
        setTimeout(() => {
            document.title = originalTitle;
        }, 5000);
        
        // Update submit button text temporarily
        const submitButton = document.querySelector('button[type="submit"]');
        if (submitButton) {
            const originalText = submitButton.textContent;
            submitButton.textContent = `${data.result}!`;
            submitButton.classList.add(`result-${data.result.toLowerCase()}`);
            
            setTimeout(() => {
                submitButton.textContent = originalText;
                submitButton.classList.remove(`result-${data.result.toLowerCase()}`);
            }, 3000);
        }
    }
    
    destroy() {
        // Clear timers
        if (this.state.validationTimer) {
            clearTimeout(this.state.validationTimer);
        }
        
        // Save final state
        this.saveSubmissionHistory();
        
        this.state.initialized = false;
        console.log('✅ SubmissionHandler destroyed');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.submissionHandler = new SubmissionHandler();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SubmissionHandler;
}