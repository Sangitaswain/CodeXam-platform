/**
 * Enhanced Client-Side Form Validation for CodeXam Platform
 * Provides real-time validation and user feedback
 */

class CodeXamValidator {
    constructor() {
        this.initialized = false;
        this.validationRules = {
            code: {
                maxLength: 50000,
                minLength: 1,
                required: true
            },
            language: {
                required: true,
                allowedValues: ['python', 'javascript', 'java', 'cpp']
            },
            problemId: {
                required: true,
                type: 'number',
                min: 1
            },
            userName: {
                maxLength: 50,
                minLength: 2,
                pattern: /^[a-zA-Z0-9\s\-_.]+$/,
                required: true
            }
        };
        
        this.errorMessages = {
            required: 'This field is required',
            maxLength: 'Input exceeds maximum allowed length',
            minLength: 'Input is too short',
            pattern: 'Invalid characters detected',
            invalidLanguage: 'Please select a supported programming language',
            invalidProblemId: 'Invalid problem ID',
            emptyCode: 'Please enter your code solution',
            codeTooLong: 'Code exceeds maximum length of 50,000 characters',
            securityViolation: 'Code contains restricted operations',
            maliciousContent: 'Potentially unsafe content detected'
        };
        
        this.securityPatterns = [
            /import\s+(os|sys|subprocess|socket|urllib|requests|http|ftplib|smtplib|webbrowser|tempfile|shutil|glob|pickle|marshal)/gi,
            /from\s+(os|sys|subprocess|socket|urllib|requests|http|ftplib|smtplib|webbrowser|tempfile|shutil|glob|pickle|marshal)/gi,
            /(open|file|input|eval|exec)\s*\(/gi,
            /require\s*\(['"][^'"]*fs['"]\)/gi,
            /require\s*\(['"][^'"]*child_process['"]\)/gi,
            /process\./gi,
            /__dirname|__filename/gi,
            /<script[^>]*>.*?<\/script>/gi,
            /javascript:/gi,
            /on\w+\s*=/gi
        ];
        
        this.init();
    }
    
    init() {
        if (this.initialized) return;
        
        // Initialize validation on form elements
        this.setupFormValidation();
        this.setupRealTimeValidation();
        this.setupSecurityChecks();
        
        this.initialized = true;
        console.log('CodeXam Validator initialized');
    }
    
    setupFormValidation() {
        // Main submission form
        const submitForm = document.querySelector('#submission-form, .submission-form');
        if (submitForm) {
            submitForm.addEventListener('submit', (e) => {
                if (!this.validateSubmissionForm(submitForm)) {
                    e.preventDefault();
                }
            });
        }
        
        // User name form
        const nameForm = document.querySelector('#name-form, .name-form');
        if (nameForm) {
            nameForm.addEventListener('submit', (e) => {
                if (!this.validateNameForm(nameForm)) {
                    e.preventDefault();
                }
            });
        }
        
        // Admin forms
        const adminForms = document.querySelectorAll('.admin-form');
        adminForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateAdminForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }
    
    setupRealTimeValidation() {
        // Code editor validation
        const codeEditor = document.querySelector('#code-editor, .code-editor, textarea[name="code"]');
        if (codeEditor) {
            let debounceTimer;
            codeEditor.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    this.validateCodeInput(codeEditor);
                }, 300);
            });
            
            codeEditor.addEventListener('blur', () => {
                this.validateCodeInput(codeEditor);
            });
        }
        
        // Language selection validation
        const languageSelect = document.querySelector('select[name="language"], #language-select');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.validateLanguageSelection(languageSelect);
                this.updateCodeTemplate(languageSelect.value);
            });
        }
        
        // User name validation
        const nameInput = document.querySelector('input[name="user_name"], #user-name');
        if (nameInput) {
            nameInput.addEventListener('input', (e) => {
                this.validateUserNameInput(nameInput);
            });
        }
    }
    
    setupSecurityChecks() {
        // Monitor for potential security issues
        document.addEventListener('paste', (e) => {
            const target = e.target;
            if (target.matches('textarea[name="code"], .code-editor')) {
                setTimeout(() => {
                    this.performSecurityCheck(target.value);
                }, 100);
            }
        });
    }
    
    validateSubmissionForm(form) {
        const data = new FormData(form);
        const code = data.get('code') || '';
        const language = data.get('language') || '';
        const problemId = data.get('problem_id') || '';
        
        let isValid = true;
        this.clearErrors(form);
        
        // Validate problem ID
        if (!this.validateProblemId(problemId)) {
            this.showError(form, 'problem_id', this.errorMessages.invalidProblemId);
            isValid = false;
        }
        
        // Validate language
        if (!this.validateLanguage(language)) {
            this.showError(form, 'language', this.errorMessages.invalidLanguage);
            isValid = false;
        }
        
        // Validate code
        const codeValidation = this.validateCode(code, language);
        if (!codeValidation.valid) {
            this.showError(form, 'code', codeValidation.message);
            isValid = false;
        }
        
        // Security check
        const securityCheck = this.performSecurityCheck(code);
        if (!securityCheck.safe) {
            this.showError(form, 'code', securityCheck.message);
            isValid = false;
        }
        
        return isValid;
    }
    
    validateNameForm(form) {
        const data = new FormData(form);
        const name = data.get('user_name') || data.get('name') || '';
        
        let isValid = true;
        this.clearErrors(form);
        
        const nameValidation = this.validateUserName(name);
        if (!nameValidation.valid) {
            this.showError(form, 'user_name', nameValidation.message);
            isValid = false;
        }
        
        return isValid;
    }
    
    validateAdminForm(form) {
        let isValid = true;
        this.clearErrors(form);
        
        // Validate title
        const title = form.querySelector('input[name="title"]');
        if (title && !this.validateTitle(title.value)) {
            this.showError(form, 'title', 'Title must be at least 3 characters long');
            isValid = false;
        }
        
        // Validate description
        const description = form.querySelector('textarea[name="description"]');
        if (description && !this.validateDescription(description.value)) {
            this.showError(form, 'description', 'Description must be at least 10 characters long');
            isValid = false;
        }
        
        return isValid;
    }
    
    validateCode(code, language) {
        if (!code || code.trim().length === 0) {
            return { valid: false, message: this.errorMessages.emptyCode };
        }
        
        if (code.length > this.validationRules.code.maxLength) {
            return { 
                valid: false, 
                message: `Code exceeds maximum length of ${this.validationRules.code.maxLength.toLocaleString()} characters (current: ${code.length.toLocaleString()})` 
            };
        }
        
        // Language-specific validation
        if (language === 'python') {
            const pythonValidation = this.validatePythonCode(code);
            if (!pythonValidation.valid) return pythonValidation;
        } else if (language === 'javascript') {
            const jsValidation = this.validateJavaScriptCode(code);
            if (!jsValidation.valid) return jsValidation;
        }
        
        return { valid: true };
    }
    
    validatePythonCode(code) {
        // Check for dangerous imports
        const dangerousImports = [
            'import os', 'import sys', 'import subprocess', 'import socket',
            'import urllib', 'import requests', 'import tempfile', 'import shutil',
            'from os', 'from sys', 'from subprocess', 'from socket'
        ];
        
        for (const dangerous of dangerousImports) {
            if (code.toLowerCase().includes(dangerous.toLowerCase())) {
                return {
                    valid: false,
                    message: `Restricted import detected: ${dangerous.split(' ')[1]}. File operations and network access are not allowed.`
                };
            }
        }
        
        // Check for dangerous functions
        const dangerousFunctions = ['open(', 'file(', 'input(', 'eval(', 'exec('];
        for (const func of dangerousFunctions) {
            if (code.includes(func)) {
                return {
                    valid: false,
                    message: `Restricted function detected: ${func.replace('(', '')}. This function is not allowed for security reasons.`
                };
            }
        }
        
        return { valid: true };
    }
    
    validateJavaScriptCode(code) {
        const dangerousPatterns = [
            'require(', 'import(', 'eval(', 'process.', 'global.',
            '__dirname', '__filename', 'fs.', 'child_process'
        ];
        
        for (const pattern of dangerousPatterns) {
            if (code.includes(pattern)) {
                return {
                    valid: false,
                    message: `Restricted operation detected: ${pattern.replace('.', '')}. File operations and network access are not allowed.`
                };
            }
        }
        
        return { valid: true };
    }
    
    validateLanguage(language) {
        return this.validationRules.language.allowedValues.includes(language);
    }
    
    validateProblemId(problemId) {
        const id = parseInt(problemId);
        return !isNaN(id) && id > 0;
    }
    
    validateUserName(name) {
        if (!name || name.trim().length === 0) {
            return { valid: false, message: this.errorMessages.required };
        }
        
        if (name.length < this.validationRules.userName.minLength) {
            return { valid: false, message: `Name must be at least ${this.validationRules.userName.minLength} characters long` };
        }
        
        if (name.length > this.validationRules.userName.maxLength) {
            return { valid: false, message: `Name cannot exceed ${this.validationRules.userName.maxLength} characters` };
        }
        
        if (!this.validationRules.userName.pattern.test(name)) {
            return { valid: false, message: 'Name can only contain letters, numbers, spaces, hyphens, underscores, and periods' };
        }
        
        return { valid: true };
    }
    
    validateTitle(title) {
        return title && title.trim().length >= 3;
    }
    
    validateDescription(description) {
        return description && description.trim().length >= 10;
    }
    
    performSecurityCheck(content) {
        for (const pattern of this.securityPatterns) {
            if (pattern.test(content)) {
                return {
                    safe: false,
                    message: 'Code contains restricted operations that are not allowed for security reasons.'
                };
            }
        }
        
        return { safe: true };
    }
    
    validateCodeInput(element) {
        const code = element.value;
        const language = this.getCurrentLanguage();
        
        // Update character count
        this.updateCharacterCount(element, code);
        
        // Validate code
        const validation = this.validateCode(code, language);
        if (!validation.valid) {
            this.showFieldError(element, validation.message);
        } else {
            this.clearFieldError(element);
        }
        
        // Security check
        const securityCheck = this.performSecurityCheck(code);
        if (!securityCheck.safe) {
            this.showFieldWarning(element, securityCheck.message);
        }
    }
    
    validateLanguageSelection(element) {
        const language = element.value;
        
        if (!this.validateLanguage(language)) {
            this.showFieldError(element, this.errorMessages.invalidLanguage);
        } else {
            this.clearFieldError(element);
        }
    }
    
    validateUserNameInput(element) {
        const name = element.value;
        const validation = this.validateUserName(name);
        
        if (!validation.valid) {
            this.showFieldError(element, validation.message);
        } else {
            this.clearFieldError(element);
        }
    }
    
    getCurrentLanguage() {
        const languageSelect = document.querySelector('select[name="language"], #language-select');
        return languageSelect ? languageSelect.value : 'python';
    }
    
    updateCharacterCount(element, text) {
        const counter = element.parentElement.querySelector('.character-count');
        if (counter) {
            const maxLength = this.validationRules.code.maxLength;
            const currentLength = text.length;
            const percentage = (currentLength / maxLength) * 100;
            
            counter.textContent = `${currentLength.toLocaleString()} / ${maxLength.toLocaleString()} characters`;
            
            if (percentage > 90) {
                counter.className = 'character-count text-danger';
            } else if (percentage > 75) {
                counter.className = 'character-count text-warning';
            } else {
                counter.className = 'character-count text-muted';
            }
        }
    }
    
    updateCodeTemplate(language) {
        const codeEditor = document.querySelector('#code-editor, .code-editor, textarea[name="code"]');
        if (!codeEditor || codeEditor.value.trim().length > 0) return;
        
        const templates = {
            python: 'def solution(args):\n    # Your code here\n    pass',
            javascript: 'function solution(args) {\n    // Your code here\n    return null;\n}',
            java: 'public class Solution {\n    public static Object solution(Object args) {\n        // Your code here\n        return null;\n    }\n}',
            cpp: '#include <iostream>\n\nusing namespace std;\n\nint solution(int args) {\n    // Your code here\n    return 0;\n}'
        };
        
        if (templates[language]) {
            codeEditor.value = templates[language];
            this.updateCharacterCount(codeEditor, templates[language]);
        }
    }
    
    showError(form, fieldName, message) {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            this.showFieldError(field, message);
        }
    }
    
    showFieldError(field, message) {
        this.clearFieldError(field);
        
        field.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        field.parentElement.appendChild(errorDiv);
    }
    
    showFieldWarning(field, message) {
        const existingWarning = field.parentElement.querySelector('.text-warning');
        if (existingWarning) return;
        
        const warningDiv = document.createElement('div');
        warningDiv.className = 'text-warning small mt-1';
        warningDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        
        field.parentElement.appendChild(warningDiv);
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorFeedback = field.parentElement.querySelector('.invalid-feedback');
        if (errorFeedback) {
            errorFeedback.remove();
        }
        
        const warning = field.parentElement.querySelector('.text-warning');
        if (warning) {
            warning.remove();
        }
    }
    
    clearErrors(form) {
        const invalidFields = form.querySelectorAll('.is-invalid');
        invalidFields.forEach(field => {
            this.clearFieldError(field);
        });
    }
}

// Initialize validator when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.codexamValidator = new CodeXamValidator();
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CodeXamValidator;
}
