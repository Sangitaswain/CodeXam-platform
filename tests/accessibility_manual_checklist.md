# Manual Accessibility Testing Checklist

This checklist provides a comprehensive guide for manual accessibility testing of the CodeXam UI templates to ensure WCAG 2.1 AA compliance.

## Pre-Testing Setup

### Required Tools
- [ ] Screen reader software (NVDA, JAWS, or VoiceOver)
- [ ] Browser developer tools
- [ ] Color contrast analyzer (WebAIM, Colour Contrast Analyser)
- [ ] Keyboard (for navigation testing)
- [ ] Mobile device or responsive testing tools

### Browser Extensions (Recommended)
- [ ] axe DevTools
- [ ] WAVE Web Accessibility Evaluator
- [ ] Lighthouse accessibility audit
- [ ] Color Oracle (color blindness simulator)

## 1. Keyboard Navigation Testing

### Navigation Requirements
- [ ] All interactive elements are keyboard accessible
- [ ] Tab order is logical and intuitive
- [ ] Focus indicators are clearly visible
- [ ] No keyboard traps exist
- [ ] Skip links are available and functional

### Test Procedure
1. **Tab Navigation Test**
   - [ ] Start at the top of the page
   - [ ] Press Tab to navigate through all interactive elements
   - [ ] Verify logical tab order (left-to-right, top-to-bottom)
   - [ ] Ensure all buttons, links, and form controls are reachable
   - [ ] Check that focus indicators are visible and clear

2. **Reverse Tab Navigation**
   - [ ] Use Shift+Tab to navigate backwards
   - [ ] Verify reverse order matches forward order
   - [ ] Ensure no elements are skipped

3. **Skip Links Test**
   - [ ] Press Tab on page load
   - [ ] Verify skip link appears (e.g., "Skip to main content")
   - [ ] Activate skip link and verify it moves focus correctly

4. **Keyboard Shortcuts**
   - [ ] Test any custom keyboard shortcuts
   - [ ] Verify they don't conflict with browser/screen reader shortcuts

### Pages to Test
- [ ] Homepage (/)
- [ ] Problems list (/problems)
- [ ] Problem detail (/problem/1)
- [ ] Submissions history (/submissions)
- [ ] Leaderboard (/leaderboard)

## 2. Screen Reader Testing

### Screen Reader Compatibility
- [ ] Content is announced in logical order
- [ ] Headings create proper document outline
- [ ] Links have descriptive text
- [ ] Form labels are properly associated
- [ ] Status messages are announced

### Test Procedure with NVDA/JAWS
1. **Document Structure**
   - [ ] Navigate by headings (H key)
   - [ ] Verify heading hierarchy (H1 → H2 → H3)
   - [ ] Check for proper heading text

2. **Navigation Elements**
   - [ ] Navigate by landmarks (D key)
   - [ ] Verify main, navigation, header, footer landmarks
   - [ ] Test landmark labels are descriptive

3. **Interactive Elements**
   - [ ] Navigate by links (K key)
   - [ ] Navigate by buttons (B key)
   - [ ] Navigate by form controls (F key)
   - [ ] Verify element descriptions are clear

4. **Tables (if present)**
   - [ ] Navigate by table (T key)
   - [ ] Navigate by table cells (Ctrl+Alt+Arrow keys)
   - [ ] Verify column/row headers are announced

### Test Procedure with VoiceOver (macOS)
1. **Basic Navigation**
   - [ ] Use VO+Right Arrow to navigate through content
   - [ ] Verify content is announced logically
   - [ ] Test VO+Command+H for heading navigation

2. **Web Rotor**
   - [ ] Use VO+U to open Web Rotor
   - [ ] Navigate by headings, links, form controls
   - [ ] Verify all elements are properly categorized

### Pages to Test
- [ ] Homepage - Test hero section, statistics, features
- [ ] Problems list - Test problem cards, filters
- [ ] Problem detail - Test problem description, code editor
- [ ] Submissions - Test table navigation, filters
- [ ] Leaderboard - Test ranking table, user information

## 3. Color Contrast Testing

### Contrast Requirements
- [ ] Normal text: 4.5:1 minimum ratio
- [ ] Large text (18pt+ or 14pt+ bold): 3:1 minimum ratio
- [ ] Non-text elements: 3:1 minimum ratio
- [ ] Focus indicators: 3:1 minimum ratio

### Test Procedure
1. **Automated Testing**
   - [ ] Run WebAIM WAVE tool
   - [ ] Use browser dev tools Lighthouse audit
   - [ ] Check axe DevTools results

2. **Manual Testing**
   - [ ] Use color picker to get exact color values
   - [ ] Calculate contrast ratios using WebAIM contrast checker
   - [ ] Test all text/background combinations

### Elements to Test
- [ ] Body text on background
- [ ] Navigation links (normal and hover states)
- [ ] Button text and backgrounds
- [ ] Form labels and inputs
- [ ] Status messages (success, error, warning)
- [ ] Difficulty badges (Easy, Medium, Hard)
- [ ] Code syntax highlighting
- [ ] Focus indicators

### Color Blindness Testing
- [ ] Test with Color Oracle or similar tool
- [ ] Verify information isn't conveyed by color alone
- [ ] Check difficulty indicators have text/icons
- [ ] Verify status indicators have text/icons

## 4. ARIA Labels and Semantic HTML

### ARIA Requirements
- [ ] All interactive elements have accessible names
- [ ] Form controls have proper labels
- [ ] Status messages use aria-live regions
- [ ] Complex widgets have proper ARIA attributes

### Test Procedure
1. **Form Controls**
   - [ ] All inputs have associated labels
   - [ ] Required fields are marked with aria-required
   - [ ] Error messages are associated with controls
   - [ ] Fieldsets have legends where appropriate

2. **Interactive Elements**
   - [ ] Buttons have descriptive text or aria-label
   - [ ] Links have descriptive text or aria-label
   - [ ] Images have appropriate alt text
   - [ ] Decorative images have empty alt attributes

3. **Dynamic Content**
   - [ ] Status messages use aria-live="polite" or "assertive"
   - [ ] Loading states are announced
   - [ ] Error messages are announced
   - [ ] Success messages are announced

### Elements to Test
- [ ] User name input modal
- [ ] Language selector dropdown
- [ ] Code editor textarea
- [ ] Submit button and loading states
- [ ] Filter dropdowns
- [ ] Search inputs
- [ ] Pagination controls

## 5. Mobile Accessibility Testing

### Mobile Requirements
- [ ] Touch targets are at least 44x44 pixels
- [ ] Content is accessible with screen reader
- [ ] Zoom up to 200% doesn't break functionality
- [ ] Orientation changes work properly

### Test Procedure
1. **Touch Target Testing**
   - [ ] Verify all buttons/links are large enough
   - [ ] Check spacing between interactive elements
   - [ ] Test with finger navigation

2. **Screen Reader Testing**
   - [ ] Test with VoiceOver on iOS
   - [ ] Test with TalkBack on Android
   - [ ] Verify swipe navigation works

3. **Zoom Testing**
   - [ ] Zoom to 200% in browser
   - [ ] Verify all content remains accessible
   - [ ] Check horizontal scrolling doesn't break layout

### Pages to Test
- [ ] All pages in mobile viewport (375px width)
- [ ] Test portrait and landscape orientations
- [ ] Verify responsive navigation menu

## 6. Focus Management

### Focus Requirements
- [ ] Focus is visible and clear
- [ ] Focus moves logically through page
- [ ] Focus is managed in dynamic content
- [ ] Focus returns appropriately after modal close

### Test Procedure
1. **Visual Focus Indicators**
   - [ ] All focusable elements have visible focus
   - [ ] Focus indicators meet contrast requirements
   - [ ] Focus style is consistent across site

2. **Focus Order**
   - [ ] Tab order follows visual layout
   - [ ] Hidden elements don't receive focus
   - [ ] Focus skips over disabled elements

3. **Modal Focus Management**
   - [ ] Focus moves to modal when opened
   - [ ] Focus is trapped within modal
   - [ ] Focus returns to trigger when closed
   - [ ] Escape key closes modal

### Elements to Test
- [ ] Navigation menu
- [ ] User profile dropdown
- [ ] Set name modal
- [ ] System info modal
- [ ] Code editor
- [ ] Filter dropdowns

## 7. Error Handling and Feedback

### Error Requirements
- [ ] Error messages are descriptive and helpful
- [ ] Errors are announced to screen readers
- [ ] Error states are visually distinct
- [ ] Success messages are also announced

### Test Procedure
1. **Form Validation**
   - [ ] Submit forms with invalid data
   - [ ] Verify error messages appear
   - [ ] Check errors are announced by screen reader
   - [ ] Test error message association with fields

2. **Code Submission Errors**
   - [ ] Submit invalid code
   - [ ] Verify error display is accessible
   - [ ] Check error messages are descriptive
   - [ ] Test with screen reader

3. **Network Errors**
   - [ ] Test with network disconnected
   - [ ] Verify error messages are accessible
   - [ ] Check retry mechanisms work

## 8. Performance and Loading States

### Loading Requirements
- [ ] Loading states are announced
- [ ] Long operations show progress
- [ ] Users can cancel long operations
- [ ] Timeouts are reasonable

### Test Procedure
1. **Loading Indicators**
   - [ ] Test code submission loading
   - [ ] Verify loading states are announced
   - [ ] Check loading doesn't block other interactions

2. **Progress Indicators**
   - [ ] Test any progress bars
   - [ ] Verify progress is announced
   - [ ] Check completion is announced

## 9. Content and Language

### Content Requirements
- [ ] Language is declared (lang attribute)
- [ ] Content is clear and understandable
- [ ] Instructions are provided where needed
- [ ] Abbreviations are explained

### Test Procedure
1. **Language Declaration**
   - [ ] Check HTML lang attribute is set
   - [ ] Verify lang changes for foreign content
   - [ ] Test with screen reader language switching

2. **Content Clarity**
   - [ ] Read all instructional text
   - [ ] Verify technical terms are explained
   - [ ] Check error messages are clear

## 10. Testing Documentation

### Test Results Documentation
For each page tested, document:
- [ ] Date and time of testing
- [ ] Tools and methods used
- [ ] Issues found with severity levels
- [ ] Screenshots of issues
- [ ] Recommendations for fixes

### Issue Tracking
- [ ] Critical issues (WCAG failures)
- [ ] Major issues (usability problems)
- [ ] Minor issues (enhancement opportunities)
- [ ] Fixed issues (retesting required)

## Severity Levels

### Critical Issues
- Complete barriers to access
- WCAG 2.1 AA failures
- Keyboard traps
- Missing alternative text for informative images
- Insufficient color contrast (below 4.5:1 for normal text)

### Major Issues
- Significant usability problems
- Missing or inadequate labels
- Poor focus management
- Confusing navigation
- Inconsistent behavior

### Minor Issues
- Enhancement opportunities
- Suboptimal but functional
- Style improvements
- Performance optimizations

## Final Checklist

Before completing accessibility testing:
- [ ] All critical issues resolved
- [ ] Major issues documented and prioritized
- [ ] Automated tests passing
- [ ] Manual testing completed on all pages
- [ ] Screen reader testing completed
- [ ] Mobile accessibility verified
- [ ] Documentation updated
- [ ] Team trained on accessibility requirements

## Resources

### WCAG 2.1 Guidelines
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM WCAG 2 Checklist](https://webaim.org/standards/wcag/checklist)

### Testing Tools
- [WAVE Web Accessibility Evaluator](https://wave.webaim.org/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [Color Contrast Analyzer](https://www.tpgi.com/color-contrast-checker/)
- [NVDA Screen Reader](https://www.nvaccess.org/download/)

### Screen Reader Guides
- [NVDA User Guide](https://www.nvaccess.org/files/nvda/documentation/userGuide.html)
- [VoiceOver User Guide](https://support.apple.com/guide/voiceover/welcome/mac)
- [JAWS User Guide](https://support.freedomscientific.com/teachers/jaws)