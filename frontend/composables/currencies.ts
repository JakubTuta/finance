export const topCurrencies: string[] = [
  'PLN', // Polish Zloty
  'USD', // United States Dollar
  'EUR', // Euro
  'JPY', // Japanese Yen
  'GBP', // British Pound Sterling
  'CNY', // Chinese Yuan
  'AUD', // Australian Dollar
  'CAD', // Canadian Dollar
  'CHF', // Swiss Franc
]

export const currencySymbolMap: Record<string, string> = {
  PLN: 'zł',
  USD: '$',
  EUR: '€',
  JPY: '¥',
  GBP: '£',
  CNY: '¥',
  AUD: 'A$',
  CAD: 'C$',
  CHF: 'CHF',
}

export function getCurrencySymbol(currencyCode: string): string {
  return currencySymbolMap[currencyCode] || currencyCode
}
