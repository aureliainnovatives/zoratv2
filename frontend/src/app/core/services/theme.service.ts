import { Injectable, signal, computed, effect } from '@angular/core';
import { environment } from '../../../environments/environment';

type ThemeMode = 'light' | 'dark';
type ThemeColors = typeof environment.theme.options[ThemeMode];

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private themeSignal = signal<ThemeMode>(this.getInitialTheme());
  
  theme = computed(() => this.themeSignal());
  colors = computed(() => environment.theme.options[this.themeSignal()]);

  constructor() {
    console.log('ThemeService initialized');
    
    // Apply theme changes
    effect(() => {
      const currentTheme = this.themeSignal();
      console.log('Theme changed:', currentTheme);
      this.applyTheme(currentTheme);
    });

    // Listen for system theme changes if using system preference
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        console.log('System theme preference changed:', e.matches ? 'dark' : 'light');
        if (this.isUsingSystemTheme()) {
          this.themeSignal.set(e.matches ? 'dark' : 'light');
        }
      });
    }
  }

  isDarkMode(): boolean {
    const isDark = this.themeSignal() === 'dark';
    console.log('isDarkMode check:', isDark);
    return isDark;
  }

  toggleTheme(): void {
    const newTheme = this.themeSignal() === 'light' ? 'dark' : 'light';
    console.log('Toggling theme to:', newTheme);
    this.themeSignal.set(newTheme);
    this.saveThemePreference(newTheme);
  }

  setTheme(theme: ThemeMode): void {
    console.log('Setting theme to:', theme);
    this.themeSignal.set(theme);
    this.saveThemePreference(theme);
  }

  private getInitialTheme(): ThemeMode {
    console.log('Getting initial theme');
    
    // Step 1: Check localStorage
    const savedTheme = localStorage.getItem(environment.theme.storageKey);
    console.log('Saved theme from localStorage:', savedTheme);
    
    if (savedTheme === 'light' || savedTheme === 'dark') {
      console.log('Using theme from localStorage:', savedTheme);
      return savedTheme;
    }

    // Step 2: Use environment default
    const defaultTheme = environment.theme.default as ThemeMode;
    console.log('Using default theme from environment:', defaultTheme);
    return defaultTheme;
  }

  private saveThemePreference(theme: ThemeMode): void {
    console.log('Saving theme preference:', theme);
    localStorage.setItem(environment.theme.storageKey, theme);
  }

  private isUsingSystemTheme(): boolean {
    return !localStorage.getItem(environment.theme.storageKey);
  }

  private applyTheme(theme: ThemeMode): void {
    console.log('Applying theme:', theme);
    
    // Apply theme class to body
    document.body.classList.remove('light', 'dark');
    document.body.classList.add(theme);
    console.log('Body classes after update:', document.body.classList.toString());

    // Apply CSS variables
    const colors = environment.theme.options[theme];
    Object.entries(colors).forEach(([key, value]) => {
      document.documentElement.style.setProperty(`--${key}`, value);
    });

    // Update meta theme-color
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', colors.background);
    }
  }

  getColor(name: keyof ThemeColors): string {
    return this.colors()[name];
  }
} 