/**
 * Simple i18n composable for multi-language support
 */

import { ref, computed } from 'vue'
import zhLocale from '../locales/zh'
import enLocale from '../locales/en'

const locales = {
  zh: zhLocale,
  en: enLocale,
}

// Default to English
const currentLocale = ref('en')

export function useI18n() {
  /**
   * Get the current locale code
   */
  const locale = computed(() => currentLocale.value)

  /**
   * Get all available locales
   */
  const availableLocales = [
    { code: 'en', name: 'English' },
    { code: 'zh', name: '中文' },
  ]

  /**
   * Set the current locale
   * @param {string} code - Locale code (en, zh)
   */
  function setLocale(code) {
    if (locales[code]) {
      currentLocale.value = code
      // Save to localStorage for persistence
      localStorage.setItem('locale', code)
    }
  }

  /**
   * Get a translated string
   * @param {string} key - Translation key
   * @param {Object} params - Parameters for interpolation
   * @returns {string} Translated string
   */
  function t(key, params = {}) {
    const messages = locales[currentLocale.value] || locales.en
    let text = messages[key] || key

    // Simple parameter interpolation: {param} -> value
    Object.entries(params).forEach(([param, value]) => {
      text = text.replace(new RegExp(`\\{${param}\\}`, 'g'), value)
    })

    return text
  }

  /**
   * Initialize locale from localStorage or browser preference
   */
  function initLocale() {
    const saved = localStorage.getItem('locale')
    if (saved && locales[saved]) {
      currentLocale.value = saved
    } else {
      // Check browser language, default to English
      const browserLang = navigator.language.split('-')[0]
      currentLocale.value = locales[browserLang] ? browserLang : 'en'
    }
  }

  return {
    locale,
    availableLocales,
    setLocale,
    t,
    initLocale,
  }
}
