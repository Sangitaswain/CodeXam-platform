/**
 * Editor Module - Enhanced code editor with syntax highlighting and auto-completion
 */
class EditorModule {
    constructor(app) {
        this.app = app;
        this.state = {
            currentLanguage: 'python',
            isDirty: false,
            lastSaved: null
        };
        
        this.templates = {
            python: `def solution(nums, target):
    """
    Your solution here
    
    Args:
        nums: List of integers
        target: Target sum
    
    Returns:
        List of indices that sum to target
    """
    pass`,
            javascript: `function solution(nums, target) {
    /**
     * Your solution here
     * 
     * @param {number[]} nums - Array of integers
     * @param {number} target - Target sum
     * @returns {number[]} Array of indices that sum to target
     */
    return [];
}`,
            java: `public class Solution {
    /**
     * Your solution here
     * 
     * @param nums Array of integers
     * @param target Target sum
     * @return Array of indices that sum to target
     */
    public int[] solution(int[] nums, int target) {
        return new int[]{};
    }
}`,
            cpp: `#include <vector>
using namespace std;

class Solution {
public:
    /**
     * Your solution here
     * 
     * @param nums Vector of integers
     * @param target Target sum
     * @return Vector of indices that sum to target
     */
    vector<int> solution(vector<int>& nums, int target) {
        return {};
    }
};`
        };
        
        this.init();
    }
    
    init() {
        this.elements = this.getElements();
        if (!this.elements.editor) {
            this.app.log('warn', 'Code editor element not found');
            return;
        }
        
        this.setupEventListeners();
        this.setupAutoSave();
        this.loadSavedCode();
        this.setupAccessibility();
        
        this.app.log('info', '✅ Editor module initialized');
    }
    
    getElements() {
        return {
            editor: document.querySelector('#code-editor, .code-editor, textarea[name="code"]'),
            languageSelect: document.querySelector('#language-select, select[name="language"]'),
            submitButton: document.querySelector('button[type="submit"]'),
            resetButton: document.querySelector('#reset-code, .reset-button')
        };
    }
    
    setupEventListeners() {
        // Editor input events
        this.app.addEventListener(this.elements.editor, 'input', (e) => {
            this.handleInput(e);
        });
        
        this.app.addEventListener(this.elements.editor, 'keydown', (e) => {
            this.handleKeyDown(e);
        });
        
        this.app.addEventListener(this.elements.editor, 'focus', (e) => {
            this.handleFocus(e);
        });
        
        this.app.addEventListener(this.elements.editor, 'blur', (e) => {
            this.handleBlur(e);
        });
        
        // Language selection
        if (this.elements.languageSelect) {
            this.app.addEventListener(this.elements.languageSelect, 'change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }
        
        // Reset button
        if (this.elements.resetButton) {
            this.app.addEventListener(this.elements.resetButton, 'click', (e) => {
                e.preventDefault();
                this.resetCode();
            });
        }
        
        // Window events
        this.app.addEventListener(window, 'beforeunload', (e) => {
            if (this.state.isDirty) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
        
        // Keyboard shortcuts
        this.app.addEventListener(document, 'keydown', (e) => {
            this.handleGlobalKeyDown(e);
        });
    }
    
    handleInput(e) {
        this.state.isDirty = true;
        
        // Trigger validation through validator module
        const validator = this.app.getModule('validator');
        if (validator) {
            validator.validateCodeInput(e.target);
        }
    }
    
    handleKeyDown(e) {
        // Tab handling
        if (e.key === 'Tab') {
            e.preventDefault();
            this.insertTab();
            return;
        }
        
        // Auto-indentation
        if (e.key === 'Enter') {
            this.handleEnterKey(e);
        }
        
        // Bracket matching
        if (['(', '[', '{', '"', "'"].includes(e.key)) {
            this.handleBracketInsertion(e);
        }
    }
    
    handleGlobalKeyDown(e) {
        // Only handle shortcuts when editor is focused or no other input is focused
        const activeElement = document.activeElement;
        const isInputFocused = activeElement && ['INPUT', 'TEXTAREA', 'SELECT'].includes(activeElement.tagName);
        
        if (isInputFocused && activeElement !== this.elements.editor) {
            return;
        }
        
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 's':
                    e.preventDefault();
                    this.saveCode();
                    break;
                case 'Enter':
                    if (e.shiftKey) {
                        e.preventDefault();
                        this.submitCode();
                    }
                    break;
                case 'r':
                    if (e.shiftKey) {
                        e.preventDefault();
                        this.resetCode();
                    }
                    break;
            }
        }
    }
    
    insertTab() {
        const editor = this.elements.editor;
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        const spaces = ' '.repeat(this.app.config.editor.tabSize);
        
        editor.value = editor.value.substring(0, start) + spaces + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = start + this.app.config.editor.tabSize;
        
        this.handleInput({ target: editor });
    }
    
    handleEnterKey(e) {
        const editor = this.elements.editor;
        const start = editor.selectionStart;
        const lines = editor.value.substring(0, start).split('\n');
        const currentLine = lines[lines.length - 1];
        
        // Calculate indentation
        const indentMatch = currentLine.match(/^(\s*)/);
        let indent = indentMatch ? indentMatch[1] : '';
        
        // Add extra indentation for certain patterns
        const indentTriggers = {
            python: /:\s*$/,
            javascript: /{\s*$/,
            java: /{\s*$/,
            cpp: /{\s*$/
        };
        
        const trigger = indentTriggers[this.state.currentLanguage];
        if (trigger && trigger.test(currentLine)) {
            indent += ' '.repeat(this.app.config.editor.tabSize);
        }
        
        // Insert newline with indentation
        this.app.setTimeout(() => {
            const newStart = editor.selectionStart;
            editor.value = editor.value.substring(0, newStart) + indent + editor.value.substring(newStart);
            editor.selectionStart = editor.selectionEnd = newStart + indent.length;
            this.handleInput({ target: editor });
        }, 0);
    }
    
    handleBracketInsertion(e) {
        const editor = this.elements.editor;
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        
        const pairs = {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'"
        };
        
        const closing = pairs[e.key];
        if (!closing) return;
        
        // Check if we should auto-close
        const selectedText = editor.value.substring(start, end);
        const shouldAutoClose = selectedText.length > 0 || this.shouldAutoCloseBracket(editor, start);
        
        if (shouldAutoClose) {
            e.preventDefault();
            
            const newValue = editor.value.substring(0, start) + 
                           e.key + selectedText + closing + 
                           editor.value.substring(end);
            
            editor.value = newValue;
            editor.selectionStart = editor.selectionEnd = start + 1 + selectedText.length;
            
            this.handleInput({ target: editor });
        }
    }
    
    shouldAutoCloseBracket(editor, position) {
        const nextChar = editor.value.charAt(position);
        return !nextChar || /\s/.test(nextChar) || [')', ']', '}', ',', ';'].includes(nextChar);
    }
    
    changeLanguage(language) {
        if (this.state.currentLanguage === language) return;
        
        const hasContent = this.elements.editor.value.trim().length > 0;
        
        if (hasContent) {
            const confirmed = confirm(`Changing language will reset your code. Continue?`);
            if (!confirmed) {
                this.elements.languageSelect.value = this.state.currentLanguage;
                return;
            }
        }
        
        this.state.currentLanguage = language;
        this.loadTemplate();
        
        // Announce to screen readers
        this.app.announceToScreenReader(`Language changed to ${language}`);
    }
    
    loadTemplate() {
        const template = this.templates[this.state.currentLanguage] || '';
        this.elements.editor.value = template;
        this.state.isDirty = false;
        
        // Trigger validation
        const validator = this.app.getModule('validator');
        if (validator) {
            validator.validateCodeInput(this.elements.editor);
        }
    }
    
    async submitCode() {
        const submission = this.app.getModule('submission');
        if (submission) {
            const form = document.querySelector('.submission-form, #submission-form');
            if (form) {
                await submission.handleFormSubmission(form);
            }
        }
    }
    
    resetCode() {
        const confirmed = confirm('Are you sure you want to reset your code? This action cannot be undone.');
        if (!confirmed) return;
        
        this.loadTemplate();
        this.app.showNotification('Code reset to template', 'info');
        this.app.announceToScreenReader('Code has been reset to template');
    }
    
    saveCode() {
        if (!this.app.isFeatureEnabled('autoSave')) return;
        
        const code = this.elements.editor.value;
        const saveData = {
            code,
            language: this.state.currentLanguage,
            timestamp: Date.now(),
            problemId: this.getProblemId()
        };
        
        try {
            localStorage.setItem('codexam_editor_save', JSON.stringify(saveData));
            this.state.isDirty = false;
            this.state.lastSaved = Date.now();
            this.app.showNotification('Code saved', 'success');
        } catch (error) {
            this.app.handleError(error, 'Failed to save code');
            this.app.showNotification('Failed to save code', 'error');
        }
    }
    
    loadSavedCode() {
        if (!this.app.isFeatureEnabled('autoSave')) return;
        
        try {
            const saved = localStorage.getItem('codexam_editor_save');
            if (!saved) return;
            
            const saveData = JSON.parse(saved);
            const currentProblemId = this.getProblemId();
            
            // Only load if it's for the same problem
            if (saveData.problemId === currentProblemId && saveData.code.trim()) {
                const confirmed = confirm('Found saved code for this problem. Would you like to restore it?');
                if (confirmed) {
                    this.elements.editor.value = saveData.code;
                    this.state.currentLanguage = saveData.language || 'python';
                    if (this.elements.languageSelect) {
                        this.elements.languageSelect.value = this.state.currentLanguage;
                    }
                    this.state.lastSaved = saveData.timestamp;
                    
                    // Trigger validation
                    const validator = this.app.getModule('validator');
                    if (validator) {
                        validator.validateCodeInput(this.elements.editor);
                    }
                }
            }
        } catch (error) {
            this.app.handleError(error, 'Failed to load saved code');
        }
    }
    
    setupAutoSave() {
        if (!this.app.isFeatureEnabled('autoSave')) return;
        
        const autoSaveInterval = this.app.config.editor.autoSaveInterval;
        
        this.app.setTimeout(() => {
            if (this.state.isDirty) {
                this.saveCode();
            }
            // Reschedule
            this.setupAutoSave();
        }, autoSaveInterval, 'editor-autosave');
    }
    
    setupAccessibility() {
        const editor = this.elements.editor;
        
        // ARIA attributes
        editor.setAttribute('role', 'textbox');
        editor.setAttribute('aria-label', 'Code editor');
        editor.setAttribute('aria-multiline', 'true');
        
        // Keyboard navigation help
        editor.setAttribute('title', 'Code editor. Use Tab to indent, Ctrl+S to save, Ctrl+Shift+Enter to submit');
    }
    
    handleFocus(e) {
        e.target.parentElement?.classList.add('editor-focused');
    }
    
    handleBlur(e) {
        e.target.parentElement?.classList.remove('editor-focused');
    }
    
    getProblemId() {
        // Try to get problem ID from various sources
        const problemIdInput = document.querySelector('input[name="problem_id"]');
        if (problemIdInput) return problemIdInput.value;
        
        const urlMatch = window.location.pathname.match(/\/problem\/(\d+)/);
        if (urlMatch) return urlMatch[1];
        
        return null;
    }
    
    resume() {
        // Resume auto-save when app resumes
        this.setupAutoSave();
    }
    
    destroy() {
        // Save before destroying
        if (this.state.isDirty) {
            this.saveCode();
        }
        
        this.app.log('info', '✅ Editor module destroyed');
    }
}

/**
 * Submission Module - Handles code submissions with rate limiting and feedback
 */
class SubmissionModule {
    constructor(app) {
        this.app = app;
        this.state = {
            submissionCount: 0,
            lastSubmissionTime: 0,
            isSubmitting: false,
            submissionHistory: []
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadSubmissionHistory();
        this.setupRateLimiting();
        
        this.app.log('info', '✅ Submission module initialized');
    }
    
    setupEventListeners() {
        // Form submission
        this.app.addEventListener(document, 'submit', (e) => {
            if (e.target.matches('.submission-form, #submission-form')) {
                e.preventDefault();
                this.handleFormSubmission(e.target);
            }
        });
    }
    
    async handleFormSubmission(form) {
        if (this.state.isSubmitting) {
            this.app.showNotification('Please wait for the current submission to complete', 'warning');
            return;
        }
        
        // Rate limiting check
        if (!this.checkRateLimit()) {
            this.app.showNotification('Too many submissions. Please wait before submitting again.', 'warning');
            return;
        }
        
        // Validate form data
        const validator = this.app.getModule('validator');
        if (validator && !validator.validateSubmissionForm(form)) {
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
    
    async submitCode(form) {
        const ajax = this.app.getModule('ajax');
        if (!ajax) {
            throw new Error('AJAX module not available');
        }
        
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
        this.addToSubmissionHistory(formData, result);
        
        return result;
    }
    
    handleSubmissionSuccess(result) {
        const data = result.data;
        
        // Show success notification
        this.app.showNotification(`Submission successful! Result: ${data.result}`, 'success');
        
        // Display detailed results
        this.displaySubmissionResults(data);
        
        // Update UI based on result
        this.updateResultUI(data);
        
        // Announce to screen readers
        this.app.announceToScreenReader(`Code submitted successfully. Result: ${data.result}`);
        
        // Auto-save successful submission
        if (data.result === 'PASS') {
            this.saveSuccessfulSubmission(data);
        }
        
        // Mark editor as clean
        const editor = this.app.getModule('editor');
        if (editor) {
            editor.state.isDirty = false;
        }
    }
    
    handleSubmissionError(error) {
        this.app.handleError(error, 'Submission failed');
        
        let message = 'Submission failed. Please try again.';
        
        if (error.message.includes('No internet connection')) {
            message = 'Network error. Please check your connection and try again.';
        } else if (error.message.includes('timeout')) {
            message = 'Submission timed out. Please try again.';
        } else if (error.message.includes('HTTP 429')) {
            message = 'Too many requests. Please wait before submitting again.';
        } else if (error.message.includes('HTTP 5')) {
            message = 'Server error. Please try again later.';
        }
        
        this.app.showNotification(message, 'error');
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
                <p class="result-message">${this.app.escapeHtml(data.message)}</p>
            </div>
            
            ${this.renderTestResults(data.test_results)}
            ${this.renderPerformanceMetrics(data)}
            ${this.renderSubmissionDetails(data)}
        `;
        
        // Scroll to results
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Add animation
        resultsPanel.classList.add('results-animate-in');
        this.app.setTimeout(() => {
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
                                    <div class="test-expected">Expected: ${this.app.escapeHtml(test.expected)}</div>
                                    <div class="test-actual">Got: ${this.app.escapeHtml(test.actual)}</div>
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
        if (timeSinceLastSubmission > this.app.config.submission.cooldownPeriod) {
            this.state.submissionCount = 0;
        }
        
        return this.state.submissionCount < this.app.config.submission.maxRate;
    }
    
    updateRateLimit() {
        this.state.submissionCount++;
        this.state.lastSubmissionTime = Date.now();
        
        // Save rate limiting data
        try {
            localStorage.setItem('codexam_rate_limit', JSON.stringify({
                count: this.state.submissionCount,
                lastTime: this.state.lastSubmissionTime
            }));
        } catch (error) {
            this.app.handleError(error, 'Failed to save rate limiting data');
        }
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
            this.app.handleError(error, 'Failed to load rate limiting data');
        }
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
    
    updateResultUI(data) {
        // Update page title temporarily
        const originalTitle = document.title;
        document.title = `${data.result} - ${originalTitle}`;
        
        // Reset title after 5 seconds
        this.app.setTimeout(() => {
            document.title = originalTitle;
        }, 5000);
        
        // Update submit button text temporarily
        const submitButton = document.querySelector('button[type="submit"]');
        if (submitButton) {
            const originalText = submitButton.textContent;
            submitButton.textContent = `${data.result}!`;
            submitButton.classList.add(`result-${data.result.toLowerCase()}`);
            
            this.app.setTimeout(() => {
                submitButton.textContent = originalText;
                submitButton.classList.remove(`result-${data.result.toLowerCase()}`);
            }, 3000);
        }
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
            this.app.handleError(error, 'Failed to load submission history');
        }
    }
    
    saveSubmissionHistory() {
        try {
            localStorage.setItem('codexam_submission_history', JSON.stringify(this.state.submissionHistory));
        } catch (error) {
            this.app.handleError(error, 'Failed to save submission history');
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
            this.app.handleError(error, 'Failed to save successful submission');
        }
    }
    
    destroy() {
        // Save final state
        this.saveSubmissionHistory();
        this.app.log('info', '✅ Submission module destroyed');
    }
}

// Export modules for use in main app
if (typeof window !== 'undefined') {
    window.EditorModule = EditorModule;
    window.SubmissionModule = SubmissionModule;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EditorModule,
        SubmissionModule
    };
}