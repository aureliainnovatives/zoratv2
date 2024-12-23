export const environment = {
  production: true,
  apiUrl: 'https://api.zorat.ai/api',
  auth: {
    tokenKey: 'auth_token',
    refreshTokenKey: 'refresh_token',
    tokenExpiryKey: 'token_expiry',
  },
  oauth: {
    google: {
      clientId: 'your-google-client-id',
      redirectUri: 'https://zorat.ai/auth/callback/google'
    },
    facebook: {
      clientId: 'your-facebook-client-id',
      redirectUri: 'https://zorat.ai/auth/callback/facebook'
    },
    github: {
      clientId: 'your-github-client-id',
      redirectUri: 'https://zorat.ai/auth/callback/github'
    },
    linkedin: {
      clientId: 'your-linkedin-client-id',
      redirectUri: 'https://zorat.ai/auth/callback/linkedin'
    },
    x: {
      clientId: 'your-x-client-id',
      redirectUri: 'https://zorat.ai/auth/callback/x'
    }
  },
  theme: {
    default: 'light',
    storageKey: 'theme_preference',
    options: {
      light: {
        primary: '#10B981',
        'primary-hover': '#059669',
        background: '#F9FAFB',
        text: '#111827',
        'text-secondary': '#4B5563',
        border: '#E5E7EB',
        panel: '#FFFFFF',
        error: '#EF4444',
        success: '#10B981',
        warning: '#F59E0B'
      },
      dark: {
        primary: '#10B981',
        'primary-hover': '#059669',
        background: '#111827',
        text: '#F9FAFB',
        'text-secondary': '#9CA3AF',
        border: '#374151',
        panel: '#1F2937',
        error: '#EF4444',
        success: '#10B981',
        warning: '#F59E0B'
      }
    }
  },
  i18n: {
    defaultLanguage: 'en',
    storageKey: 'language_preference',
    supportedLanguages: ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'],
    fallbackLanguage: 'en'
  },
  pagination: {
    defaultPageSize: 10,
    pageSizeOptions: [5, 10, 25, 50, 100]
  },
  dateFormat: 'MMM dd, yyyy',
  timeFormat: 'HH:mm',
  timezone: 'UTC',
  notifications: {
    position: 'top-right',
    duration: 3000,
    showProgressBar: true
  },
  logging: {
    level: 'error',
    enableConsoleLogging: false,
    enableErrorReporting: true
  },
  security: {
    enableCSRF: true,
    csrfCookieName: 'XSRF-TOKEN',
    csrfHeaderName: 'X-XSRF-TOKEN',
    passwordPolicy: {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true
    }
  },
  features: {
    enableOAuth: true,
    enablePasswordReset: true,
    enableEmailVerification: true,
    enableTwoFactorAuth: true,
    enableRememberMe: true,
    enableDarkMode: true,
    enableLanguageSelection: true,
    enableNotifications: true
  }
}; 