/* ============================================
   THEME TOGGLE UTILITIES
   Version: 1.0
   Description: Theme switching functionality
   Last Updated: October 31, 2025
   ============================================ */

/**
 * Theme Manager
 * Handles theme switching between light and dark modes
 */
const ThemeManager = {
    // Theme storage key
    STORAGE_KEY: 'papertrail-theme',
    
    // Available themes
    THEMES: {
        LIGHT: 'light',
        DARK: 'dark',
        AUTO: 'auto'
    },
    
    /**
     * Initialize theme manager
     */
    init() {
        this.applyTheme(this.getTheme());
        this.setupListeners();
    },
    
    /**
     * Get current theme from localStorage or system preference
     * @returns {string} Current theme
     */
    getTheme() {
        const stored = localStorage.getItem(this.STORAGE_KEY);
        
        if (stored && Object.values(this.THEMES).includes(stored)) {
            return stored;
        }
        
        // Default to auto (follows system preference)
        return this.THEMES.AUTO;
    },
    
    /**
     * Set theme
     * @param {string} theme - Theme to set (light, dark, or auto)
     */
    setTheme(theme) {
        if (!Object.values(this.THEMES).includes(theme)) {
            console.error('Invalid theme:', theme);
            return;
        }
        
        localStorage.setItem(this.STORAGE_KEY, theme);
        this.applyTheme(theme);
        
        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme } 
        }));
    },
    
    /**
     * Apply theme to document
     * @param {string} theme - Theme to apply
     */
    applyTheme(theme) {
        const root = document.documentElement;
        
        // Add transitioning class to prevent flash
        root.setAttribute('data-theme-transitioning', '');
        
        if (theme === this.THEMES.AUTO) {
            // Remove theme attribute to let CSS media query handle it
            root.removeAttribute('data-theme');
        } else {
            root.setAttribute('data-theme', theme);
        }
        
        // Remove transitioning class after a brief delay
        setTimeout(() => {
            root.removeAttribute('data-theme-transitioning');
        }, 50);
        
        // Update theme toggle buttons if they exist
        this.updateToggleButtons(theme);
    },
    
    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const current = this.getTheme();
        const currentResolved = this.resolveTheme(current);
        
        // Toggle between light and dark
        const newTheme = currentResolved === this.THEMES.DARK 
            ? this.THEMES.LIGHT 
            : this.THEMES.DARK;
        
        this.setTheme(newTheme);
    },
    
    /**
     * Resolve theme considering system preference
     * @param {string} theme - Theme to resolve
     * @returns {string} Resolved theme (light or dark)
     */
    resolveTheme(theme) {
        if (theme === this.THEMES.AUTO) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches 
                ? this.THEMES.DARK 
                : this.THEMES.LIGHT;
        }
        return theme;
    },
    
    /**
     * Setup event listeners
     */
    setupListeners() {
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            const current = this.getTheme();
            if (current === this.THEMES.AUTO) {
                this.applyTheme(this.THEMES.AUTO);
            }
        });
    },
    
    /**
     * Update theme toggle buttons
     * @param {string} theme - Current theme
     */
    updateToggleButtons(theme) {
        const buttons = document.querySelectorAll('[data-theme-toggle]');
        const resolved = this.resolveTheme(theme);
        
        buttons.forEach(button => {
            const icon = button.querySelector('i');
            if (icon) {
                // Update icon
                icon.className = resolved === this.THEMES.DARK 
                    ? 'fas fa-sun' 
                    : 'fas fa-moon';
            }
            
            // Update aria-label
            button.setAttribute('aria-label', 
                resolved === this.THEMES.DARK 
                    ? 'Switch to light mode' 
                    : 'Switch to dark mode'
            );
            
            // Update tooltip if it exists
            const tooltip = button.getAttribute('data-bs-original-title');
            if (tooltip) {
                button.setAttribute('data-bs-original-title',
                    resolved === this.THEMES.DARK 
                        ? 'Light Mode' 
                        : 'Dark Mode'
                );
            }
        });
    }
};

/**
 * Initialize theme manager when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    
    // Setup toggle buttons
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
        button.addEventListener('click', () => {
            ThemeManager.toggleTheme();
        });
    });
    
    // Setup theme select dropdowns (if any)
    document.querySelectorAll('[data-theme-select]').forEach(select => {
        select.value = ThemeManager.getTheme();
        select.addEventListener('change', (e) => {
            ThemeManager.setTheme(e.target.value);
        });
    });
});

/**
 * Export for use in other modules
 */
window.ThemeManager = ThemeManager;

/* ===== USAGE EXAMPLES ===== */

/*
Example 1: Toggle Theme Button (HTML)
<button data-theme-toggle aria-label="Toggle theme">
    <i class="fas fa-moon"></i>
</button>

Example 2: Theme Select Dropdown (HTML)
<select data-theme-select class="form-select">
    <option value="light">Light</option>
    <option value="dark">Dark</option>
    <option value="auto">Auto</option>
</select>

Example 3: Programmatic Theme Change (JavaScript)
ThemeManager.setTheme('dark');
ThemeManager.toggleTheme();

Example 4: Listen for Theme Changes (JavaScript)
window.addEventListener('themeChanged', (e) => {
    console.log('Theme changed to:', e.detail.theme);
});

Example 5: Get Current Theme (JavaScript)
const currentTheme = ThemeManager.getTheme();
const resolvedTheme = ThemeManager.resolveTheme(currentTheme);
*/
