/**
 * Enhanced Code Editor for CodeXam Platform
 * Provides advanced code editing functionality with real-time validation,
 * syntax highlighting, auto-completion, and accessibility features.
 * 
 * @version 2.0.0
 * @author CodeXam Development Team
 */

class CodeXamEditor {
    constructor(options = {}) {
        this.config = {
            editorId: 'code-editor',
            languageSelectId: 'language-select',
            submitButtonId: 'submit-code',
            resetButtonId: 'reset-code',
            lineNumbersId: 'line-numbers',
            syntaxHighlightId: 'syntax-highlight',
            autoSave: true,
            autoSaveInterval: 30000, // 30 seconds
            maxCodeLength: 50000,
            tabSize: 4,
            enableAutoComplete: true,
            enableSyntaxHighlighting: true,
            enableLineNumbers: true,
            enableErrorChecking: true,
            ...options
        };
        
        this.state = {
            initialized: false,
            currentLanguage: 'python',
            isDirty: false,
            lastSaved: null,
            autoSaveTimer: null,
            validationTimer: null,
            isSubmitting: false
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
        
        this.keywords = {
            python: ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'import', 'from', 'return', 'yield', 'pass', 'break', 'continue', 'and', 'or', 'not', 'in', 'is', 'lambda', 'global', 'nonlocal'],
            javascript: ['function', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'new', 'this', 'typeof', 'instanceof', 'class', 'extends', 'super'],
            java: ['public', 'private', 'protected', 'static', 'final', 'abstract', 'class', 'interface', 'extends', 'implements', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'finally', 'throw', 'throws', 'new', 'this', 'super'],
            cpp: ['#include', '#define', 'using', 'namespace', 'class', 'struct', 'public', 'private', 'protected', 'virtual', 'static', 'const', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break', 'continue', 'return', 'try', 'catch', 'throw', 'new', 'delete', 'this']
        };
        
        this.init();
    }
    
    init() {
        if (this.state.initialized) {
            console.warn('CodeXamEditor already initialized');
            return;
        }
        
        this.elements = this.getElements();
        if (!this.elements.editor) {
            console.error('Code editor element not found');
            return;
        }
        
        this.setupEventListeners();
        this.setupAutoSave();
        this.setupValidation();
        this.setupAccessibility();
        this.loadSavedCode();
        
        this.state.initialized = true;
        console.log('✅ CodeXamEditor initialized');
    }
    
    getElements() {
        return {
            editor: document.getElementById(this.config.editorId),
            languageSelect: document.getElementById(this.config.languageSelectId),
            submitButton: document.getElementById(this.config.submitButtonId),
            resetButton: document.getElementById(this.config.resetButtonId),
            lineNumbers: document.getElementById(this.config.lineNumbersId),
            syntaxHighlight: document.getElementById(this.config.syntaxHighlightId)
        };
    }
    
    setupEventListeners() {
        // Editor input events
        this.elements.editor.addEventListener('input', (e) => {
            this.handleInput(e);
        });
        
        this.elements.editor.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });
        
        this.elements.editor.addEventListener('scroll', (e) => {
            this.syncScroll();
        });
        
        this.elements.editor.addEventListener('focus', (e) => {
            this.handleFocus(e);
        });
        
        this.elements.editor.addEventListener('blur', (e) => {
            this.handleBlur(e);
        });
        
        // Language selection
        if (this.elements.languageSelect) {
            this.elements.languageSelect.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }
        
        // Button events
        if (this.elements.submitButton) {
            this.elements.submitButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.submitCode();
            });
        }
        
        if (this.elements.resetButton) {
            this.elements.resetButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.resetCode();
            });
        }
        
        // Window events
        window.addEventListener('beforeunload', (e) => {
            if (this.state.isDirty) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleGlobalKeyDown(e);
        });
    }
    
    handleInput(e) {
        this.state.isDirty = true;
        this.updateCharacterCount();
        
        if (this.config.enableSyntaxHighlighting) {
            this.updateSyntaxHighlighting();
        }
        
        if (this.config.enableLineNumbers) {
            this.updateLineNumbers();
        }
        
        // Debounced validation
        clearTimeout(this.state.validationTimer);
        this.state.validationTimer = setTimeout(() => {
            this.validateCode();
        }, 500);
        
        // Auto-completion
        if (this.config.enableAutoComplete) {
            this.handleAutoComplete(e);
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
        
        // Undo/Redo
        if (e.ctrlKey || e.metaKey) {
            if (e.key === 'z' && !e.shiftKey) {
                // Undo handled by browser
            } else if ((e.key === 'z' && e.shiftKey) || e.key === 'y') {
                // Redo handled by browser
            }
        }
    }
    
    handleGlobalKeyDown(e) {
        // Global shortcuts
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
        const spaces = ' '.repeat(this.config.tabSize);
        
        editor.value = editor.value.substring(0, start) + spaces + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = start + this.config.tabSize;
        
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
            indent += ' '.repeat(this.config.tabSize);
        }
        
        // Insert newline with indentation
        setTimeout(() => {
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
        this.updateSyntaxHighlighting();
        
        // Announce to screen readers
        this.announceToScreenReader(`Language changed to ${language}`);
    }
    
    loadTemplate() {
        const template = this.templates[this.state.currentLanguage] || '';
        this.elements.editor.value = template;
        this.state.isDirty = false;
        this.updateCharacterCount();
        this.updateLineNumbers();
        this.updateSyntaxHighlighting();
    }
    
    updateSyntaxHighlighting() {
        if (!this.config.enableSyntaxHighlighting || !this.elements.syntaxHighlight) return;
        
        const code = this.elements.editor.value;
        const highlightedCode = this.highlightSyntax(code, this.state.currentLanguage);
        this.elements.syntaxHighlight.innerHTML = highlightedCode;
    }
    
    highlightSyntax(code, language) {
        if (!code) return '';
        
        // Escape HTML
        let highlighted = code
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        
        const keywords = this.keywords[language] || [];
        
        // Highlight keywords
        keywords.forEach(keyword => {
            const regex = new RegExp(`\\b${keyword}\\b`, 'g');
            highlighted = highlighted.replace(regex, `<span class="keyword">${keyword}</span>`);
        });
        
        // Highlight strings
        highlighted = highlighted.replace(/(["'])((?:\\.|(?!\1)[^\\])*?)\1/g, '<span class="string">$1$2$1</span>');
        
        // Highlight comments
        const commentPatterns = {
            python: /#.*$/gm,
            javascript: /\/\/.*$/gm,
            java: /\/\/.*$/gm,
            cpp: /\/\/.*$/gm
        };
        
        const commentPattern = commentPatterns[language];
        if (commentPattern) {
            highlighted = highlighted.replace(commentPattern, '<span class="comment">$&</span>');
        }
        
        // Highlight numbers
        highlighted = highlighted.replace(/\b\d+\.?\d*\b/g, '<span class="number">$&</span>');
        
        return highlighted;
    }
    
    updateLineNumbers() {
        if (!this.config.enableLineNumbers || !this.elements.lineNumbers) return;
        
        const lines = this.elements.editor.value.split('\n');
        const lineNumbers = lines.map((_, index) => index + 1).join('\n');
        this.elements.lineNumbers.textContent = lineNumbers;
    }
    
    updateCharacterCount() {
        const counter = document.querySelector('.character-count');
        if (!counter) return;
        
        const currentLength = this.elements.editor.value.length;
        const maxLength = this.config.maxCodeLength;
        const percentage = (currentLength / maxLength) * 100;
        
        counter.textContent = `${currentLength.toLocaleString()} / ${maxLength.toLocaleString()} characters`;
        
        // Update styling based on usage
        counter.className = 'character-count';
        if (percentage > 90) {
            counter.classList.add('text-danger');
        } else if (percentage > 75) {
            counter.classList.add('text-warning');
        } else {
            counter.classList.add('text-muted');
        }
    }
    
    syncScroll() {
        if (this.elements.syntaxHighlight) {
            this.elements.syntaxHighlight.scrollTop = this.elements.editor.scrollTop;
            this.elements.syntaxHighlight.scrollLeft = this.elements.editor.scrollLeft;
        }
        
        if (this.elements.lineNumbers) {
            this.elements.lineNumbers.scrollTop = this.elements.editor.scrollTop;
        }
    }
    
    validateCode() {
        if (!this.config.enableErrorChecking) return;
        
        const code = this.elements.editor.value;
        const errors = this.checkForErrors(code);
        
        this.displayErrors(errors);
    }
    
    checkForErrors(code) {
        const errors = [];
        
        // Basic syntax checks
        if (code.length > this.config.maxCodeLength) {
            errors.push({
                line: 0,
                message: `Code exceeds maximum length of ${this.config.maxCodeLength} characters`,
                type: 'error'
            });
        }
        
        // Language-specific checks
        if (this.state.currentLanguage === 'python') {
            errors.push(...this.checkPythonSyntax(code));
        } else if (this.state.currentLanguage === 'javascript') {
            errors.push(...this.checkJavaScriptSyntax(code));
        }
        
        return errors;
    }
    
    checkPythonSyntax(code) {
        const errors = [];
        const lines = code.split('\n');
        
        lines.forEach((line, index) => {
            // Check for common Python issues
            if (line.trim().endsWith(':') && lines[index + 1] && !lines[index + 1].match(/^\s+/)) {
                errors.push({
                    line: index + 2,
                    message: 'Expected indented block',
                    type: 'error'
                });
            }
            
            // Check for dangerous imports
            if (line.includes('import os') || line.includes('import sys')) {
                errors.push({
                    line: index + 1,
                    message: 'Restricted import detected',
                    type: 'warning'
                });
            }
        });
        
        return errors;
    }
    
    checkJavaScriptSyntax(code) {
        const errors = [];
        
        // Basic bracket matching
        const brackets = { '(': ')', '[': ']', '{': '}' };
        const stack = [];
        
        for (let i = 0; i < code.length; i++) {
            const char = code[i];
            if (brackets[char]) {
                stack.push({ char: brackets[char], pos: i });
            } else if (Object.values(brackets).includes(char)) {
                if (stack.length === 0 || stack.pop().char !== char) {
                    errors.push({
                        line: code.substring(0, i).split('\n').length,
                        message: 'Mismatched brackets',
                        type: 'error'
                    });
                }
            }
        }
        
        if (stack.length > 0) {
            errors.push({
                line: code.split('\n').length,
                message: 'Unclosed brackets',
                type: 'error'
            });
        }
        
        return errors;
    }
    
    displayErrors(errors) {
        // Remove existing error indicators
        document.querySelectorAll('.error-indicator').forEach(el => el.remove());
        
        if (errors.length === 0) return;
        
        // Create error panel
        let errorPanel = document.querySelector('.error-panel');
        if (!errorPanel) {
            errorPanel = document.createElement('div');
            errorPanel.className = 'error-panel';
            this.elements.editor.parentNode.appendChild(errorPanel);
        }
        
        errorPanel.innerHTML = errors.map(error => `
            <div class="error-item error-${error.type}">
                <span class="error-line">Line ${error.line}:</span>
                <span class="error-message">${error.message}</span>
            </div>
        `).join('');
    }
    
    async submitCode() {
        if (this.state.isSubmitting) return;
        
        const code = this.elements.editor.value.trim();
        if (!code) {
            this.showNotification('Please enter your code before submitting', 'error');
            return;
        }
        
        // Validate code
        const errors = this.checkForErrors(code);
        const criticalErrors = errors.filter(e => e.type === 'error');
        
        if (criticalErrors.length > 0) {
            this.showNotification('Please fix the errors in your code before submitting', 'error');
            return;
        }
        
        this.state.isSubmitting = true;
        this.updateSubmitButton(true);
        
        try {
            const formData = new FormData();
            formData.append('code', code);
            formData.append('language', this.state.currentLanguage);
            formData.append('problem_id', this.getProblemId());
            
            // Add CSRF token
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            if (csrfToken) {
                formData.append('csrf_token', csrfToken);
            }
            
            const response = await fetch('/submit', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.status === 'success') {
                this.handleSubmissionSuccess(result);
                this.state.isDirty = false;
            } else {
                this.handleSubmissionError(result);
            }
            
        } catch (error) {
            console.error('Submission error:', error);
            this.showNotification('Submission failed. Please try again.', 'error');
        } finally {
            this.state.isSubmitting = false;
            this.updateSubmitButton(false);
        }
    }
    
    handleSubmissionSuccess(result) {
        const data = result.data;
        
        this.showNotification(`Submission successful! Result: ${data.result}`, 'success');
        
        // Show detailed results
        this.displaySubmissionResults(data);
        
        // Announce to screen readers
        this.announceToScreenReader(`Code submitted successfully. Result: ${data.result}`);
    }
    
    handleSubmissionError(result) {
        const message = result.error?.message || 'Submission failed';
        this.showNotification(message, 'error');
        
        if (result.error?.details) {
            console.error('Submission error details:', result.error.details);
        }
    }
    
    displaySubmissionResults(data) {
        // Create or update results panel
        let resultsPanel = document.querySelector('.submission-results');
        if (!resultsPanel) {
            resultsPanel = document.createElement('div');
            resultsPanel.className = 'submission-results';
            this.elements.editor.parentNode.appendChild(resultsPanel);
        }
        
        const resultClass = data.result.toLowerCase();
        resultsPanel.innerHTML = `
            <div class="result-header result-${resultClass}">
                <h3>Submission Result: ${data.result}</h3>
                <p>${data.message}</p>
            </div>
            
            ${data.test_results ? `
                <div class="test-results">
                    <h4>Test Cases:</h4>
                    ${data.test_results.map((test, index) => `
                        <div class="test-case ${test.passed ? 'passed' : 'failed'}">
                            <span class="test-number">Test ${index + 1}:</span>
                            <span class="test-status">${test.passed ? '✅ PASS' : '❌ FAIL'}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            ${data.execution_time ? `
                <div class="performance-metrics">
                    <span>Execution Time: ${data.execution_time}ms</span>
                    ${data.memory_used ? `<span>Memory Used: ${data.memory_used} bytes</span>` : ''}
                </div>
            ` : ''}
        `;
        
        // Scroll to results
        resultsPanel.scrollIntoView({ behavior: 'smooth' });
    }
    
    resetCode() {
        const confirmed = confirm('Are you sure you want to reset your code? This action cannot be undone.');
        if (!confirmed) return;
        
        this.loadTemplate();
        this.showNotification('Code reset to template', 'info');
        this.announceToScreenReader('Code has been reset to template');
    }
    
    saveCode() {
        if (!this.config.autoSave) return;
        
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
            this.showNotification('Code saved', 'success');
        } catch (error) {
            console.error('Failed to save code:', error);
            this.showNotification('Failed to save code', 'error');
        }
    }
    
    loadSavedCode() {
        if (!this.config.autoSave) return;
        
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
                    this.updateSyntaxHighlighting();
                    this.updateLineNumbers();
                    this.updateCharacterCount();
                    this.state.lastSaved = saveData.timestamp;
                }
            }
        } catch (error) {
            console.error('Failed to load saved code:', error);
        }
    }
    
    setupAutoSave() {
        if (!this.config.autoSave) return;
        
        this.state.autoSaveTimer = setInterval(() => {
            if (this.state.isDirty) {
                this.saveCode();
            }
        }, this.config.autoSaveInterval);
    }
    
    setupValidation() {
        // Real-time validation setup is handled in handleInput
    }
    
    setupAccessibility() {
        const editor = this.elements.editor;
        
        // ARIA attributes
        editor.setAttribute('role', 'textbox');
        editor.setAttribute('aria-label', 'Code editor');
        editor.setAttribute('aria-multiline', 'true');
        
        // Keyboard navigation help
        editor.setAttribute('title', 'Code editor. Use Tab to indent, Ctrl+S to save, Ctrl+Shift+Enter to submit');
        
        // Screen reader announcements for important events
        this.createAriaLiveRegion();
    }
    
    createAriaLiveRegion() {
        if (document.getElementById('editor-announcements')) return;
        
        const liveRegion = document.createElement('div');
        liveRegion.id = 'editor-announcements';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        document.body.appendChild(liveRegion);
    }
    
    announceToScreenReader(message) {
        const liveRegion = document.getElementById('editor-announcements');
        if (liveRegion) {
            liveRegion.textContent = message;
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }
    
    showNotification(message, type = 'info') {
        // Use existing notification system or create simple one
        if (typeof showAlert === 'function') {
            showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    updateSubmitButton(isSubmitting) {
        if (!this.elements.submitButton) return;
        
        if (isSubmitting) {
            this.elements.submitButton.disabled = true;
            this.elements.submitButton.innerHTML = `
                <span class="loading-spinner"></span>
                Submitting...
            `;
        } else {
            this.elements.submitButton.disabled = false;
            this.elements.submitButton.innerHTML = `
                <span class="submit-icon">🚀</span>
                Submit Code
            `;
        }
    }
    
    getProblemId() {
        // Try to get problem ID from various sources
        const problemIdInput = document.querySelector('input[name="problem_id"]');
        if (problemIdInput) return problemIdInput.value;
        
        const urlMatch = window.location.pathname.match(/\/problem\/(\d+)/);
        if (urlMatch) return urlMatch[1];
        
        return null;
    }
    
    handleFocus(e) {
        // Add focus styling
        e.target.parentElement?.classList.add('editor-focused');
    }
    
    handleBlur(e) {
        // Remove focus styling
        e.target.parentElement?.classList.remove('editor-focused');
        
        // Save on blur if auto-save is enabled
        if (this.config.autoSave && this.state.isDirty) {
            this.saveCode();
        }
    }
    
    handleAutoComplete(e) {
        // Simple auto-completion for common patterns
        const editor = this.elements.editor;
        const cursorPos = editor.selectionStart;
        const textBeforeCursor = editor.value.substring(0, cursorPos);
        
        // Check for completion triggers
        if (textBeforeCursor.endsWith('def ') && this.state.currentLanguage === 'python') {
            // Python function completion
            this.insertCompletion('function_name():\n    pass', 'function_name'.length);
        }
    }
    
    insertCompletion(completion, selectLength = 0) {
        const editor = this.elements.editor;
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        
        editor.value = editor.value.substring(0, start) + completion + editor.value.substring(end);
        
        if (selectLength > 0) {
            editor.selectionStart = start;
            editor.selectionEnd = start + selectLength;
        } else {
            editor.selectionStart = editor.selectionEnd = start + completion.length;
        }
        
        this.handleInput({ target: editor });
    }
    
    destroy() {
        // Clean up timers
        if (this.state.autoSaveTimer) {
            clearInterval(this.state.autoSaveTimer);
        }
        
        if (this.state.validationTimer) {
            clearTimeout(this.state.validationTimer);
        }
        
        // Remove event listeners (modern browsers handle this automatically when elements are removed)
        
        // Reset state
        this.state.initialized = false;
        
        console.log('✅ CodeXamEditor destroyed');
    }
}

// Initialize editor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('code-editor')) {
        window.codexamEditor = new CodeXamEditor();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CodeXamEditor;
}