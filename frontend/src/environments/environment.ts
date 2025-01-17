export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
  socketUrl: 'http://localhost:3000',
  aiApiUrl: 'http://localhost:5001/api/v1',
  chat: {
    useStreaming: true,
    streamingEndpoint: '/api/v1/agent/chat/stream',
    plainEndpoint: '/api/v1/agent/chat',
    defaultLLM: 'GPT-3.5 Turbo',
    reconnectAttempts: 3,
    reconnectInterval: 3000,
    typingIndicatorDelay: 500,
    socketNamespace: '/agent-chat'
  },
  auth: {
    tokenKey: 'auth_token',
    refreshTokenKey: 'refresh_token',
    tokenExpiryKey: 'token_expiry',
  },
  oauth: {
    google: {
      clientId: 'your-google-client-id',
      redirectUri: 'http://localhost:4200/auth/callback/google'
    },
    facebook: {
      clientId: 'your-facebook-client-id',
      redirectUri: 'http://localhost:4200/auth/callback/facebook'
    },
    github: {
      clientId: 'your-github-client-id',
      redirectUri: 'http://localhost:4200/auth/callback/github'
    },
    linkedin: {
      clientId: 'your-linkedin-client-id',
      redirectUri: 'http://localhost:4200/auth/callback/linkedin'
    },
    x: {
      clientId: 'your-x-client-id',
      redirectUri: 'http://localhost:4200/auth/callback/x'
    }
  },
  theme: {
    default: 'dark',
    storageKey: 'theme_preference',
    options: {
      light: {
        primary: '#10a37f',
        'primary-hover': '#0e906f',
        background: '#ffffff',
        text: '#666666',
        'text-secondary': '#666666',
        border: '#e5e7eb',
        panel: '#ffffff',
        error: '#ef4444',
        success: '#10b981',
        warning: '#f59e0b',
        'menu-active': '#3dd6b3',
        'menu-hover': '#34d399',
        'menu-text': '#666666',
        'menu-text-active': '#10b981',
        'menu-text-hover': '#34d399',
        'menu-bg-active': 'rgba(16, 185, 129, 0.1)',
        'menu-bg-hover': 'rgba(52, 211, 153, 0.05)'
      },
      dark: {
        primary: '#10a37f',
        'primary-hover': '#0e906f',
        background: '#202123',
        text: '#c5c5d2',
        'text-secondary': '#a0a0a0',
        border: '#4a4b4d',
        panel: '#2d2d2d',
        error: '#ef4444',
        success: '#10b981',
        warning: '#f59e0b',
        'menu-active': '#3dd6b3',
        'menu-hover': '#34d399',
        'menu-text': '#f1f1f1',
        'menu-text-active': '#10b981',
        'menu-text-hover': '#34d399',
        'menu-bg-active': 'rgba(16, 185, 129, 0.1)',
        'menu-bg-hover': 'rgba(52, 211, 153, 0.05)',
        heading: '#ffffff'
      }
    }
  },
  i18n: {
    defaultLanguage: 'en',
    storageKey: 'language_preference',
    supportedLanguages: ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'],
    fallbackLanguage: 'en'
  },
  table: {
    defaultItemsPerPage: 5,
    itemsPerPageOptions: [5, 10, 25, 50]
  },
  security: {
    enableCSRF: true,
    csrfCookieName: 'XSRF-TOKEN',
    csrfHeaderName: 'X-XSRF-TOKEN',
    passwordPolicy: {
      minLength: 1,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true
    }
  }
}; 