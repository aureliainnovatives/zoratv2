import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { firstValueFrom } from 'rxjs';

type LanguageCode = typeof environment.i18n.supportedLanguages[number];
type TranslationData = Record<string, any>;

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private translations = signal<TranslationData>({});
  private currentLanguage = signal<LanguageCode>(this.getInitialLanguage());

  language = computed(() => this.currentLanguage());

  constructor(private http: HttpClient) {
    this.loadTranslations(this.currentLanguage());
  }

  async setLanguage(lang: LanguageCode): Promise<void> {
    if (lang !== this.currentLanguage()) {
      await this.loadTranslations(lang);
      this.currentLanguage.set(lang);
      this.saveLanguagePreference(lang);
      document.documentElement.lang = lang;
    }
  }

  translate(key: string, params: Record<string, any> = {}): string {
    const value = this.getNestedTranslation(this.translations(), key);
    if (typeof value !== 'string') {
      console.warn(`Translation key not found: ${key}`);
      return key;
    }
    return this.interpolateParams(value, params);
  }

  getSupportedLanguages(): LanguageCode[] {
    return environment.i18n.supportedLanguages;
  }

  private async loadTranslations(lang: LanguageCode): Promise<void> {
    try {
      const translations = await firstValueFrom(
        this.http.get<TranslationData>(`/assets/i18n/${lang}.json`)
      );
      this.translations.set(translations);
    } catch (error) {
      console.error(`Failed to load translations for ${lang}:`, error);
      
      // If loading fails and it's not the fallback language, try loading fallback
      if (lang !== environment.i18n.fallbackLanguage) {
        await this.loadTranslations(environment.i18n.fallbackLanguage as LanguageCode);
      }
    }
  }

  private getInitialLanguage(): LanguageCode {
    // Check for saved preference
    const savedLang = localStorage.getItem(environment.i18n.storageKey);
    if (savedLang && this.isValidLanguage(savedLang)) {
      return savedLang as LanguageCode;
    }

    // Check browser language
    const browserLang = navigator.language.split('-')[0];
    if (this.isValidLanguage(browserLang)) {
      return browserLang as LanguageCode;
    }

    // Fall back to default language
    return environment.i18n.defaultLanguage as LanguageCode;
  }

  private saveLanguagePreference(lang: LanguageCode): void {
    localStorage.setItem(environment.i18n.storageKey, lang);
  }

  private isValidLanguage(lang: string): boolean {
    return environment.i18n.supportedLanguages.includes(lang as LanguageCode);
  }

  private getNestedTranslation(obj: TranslationData, path: string): any {
    return path.split('.').reduce((prev, curr) => {
      return prev ? prev[curr] : null;
    }, obj);
  }

  private interpolateParams(text: string, params: Record<string, any>): string {
    return text.replace(/{{([^}]+)}}/g, (_, key) => {
      const value = params[key.trim()];
      return value !== undefined ? value : `{{${key}}}`;
    });
  }
} 