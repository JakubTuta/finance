export const topCurrencies: string[] = [
  'USD', // United States Dollar
  'EUR', // Euro
  'JPY', // Japanese Yen
  'GBP', // British Pound Sterling
  'CNY', // Chinese Yuan
  'AUD', // Australian Dollar
  'CAD', // Canadian Dollar
  'CHF', // Swiss Franc
  'HKD', // Hong Kong Dollar
  'SGD', // Singapore Dollar
  'SEK', // Swedish Krona
  'KRW', // South Korean Won
  'NOK', // Norwegian Krone
  'NZD', // New Zealand Dollar
  'INR', // Indian Rupee
  'MXN', // Mexican Peso
  'TWD', // Taiwan New Dollar
  'ZAR', // South African Rand
  'BRL', // Brazilian Real
  'DKK', // Danish Krone
  'PLN', // Polish Zloty
  'THB', // Thai Baht
  'ILS', // Israeli New Shekel
  'IDR', // Indonesian Rupiah
  'CZK', // Czech Koruna
  'AED', // United Arab Emirates Dirham
  'TRY', // Turkish Lira
  'HUF', // Hungarian Forint
  'CLP', // Chilean Peso
  'SAR', // Saudi Riyal
  'PHP', // Philippine Peso
  'MYR', // Malaysian Ringgit
  'COP', // Colombian Peso
  'RUB', // Russian Ruble
  'RON', // Romanian Leu
  'PEN', // Peruvian Sol
  'BHD', // Bahraini Dinar
  'BGN', // Bulgarian Lev
  'ARS', // Argentine Peso
  'VND', // Vietnamese Dong
  'UAH', // Ukrainian Hryvnia
  'NGN', // Nigerian Naira
  'EGP', // Egyptian Pound
  'PKR', // Pakistani Rupee
  'QAR', // Qatari Riyal
  'KWD', // Kuwaiti Dinar
  'MAD', // Moroccan Dirham
  'DZD', // Algerian Dinar
  'OMR', // Omani Rial
  'CRC', // Costa Rican Colón
]

export const currencySymbolMap: Record<string, string> = {
  USD: '$',
  EUR: '€',
  JPY: '¥',
  GBP: '£',
  CNY: '¥',
  AUD: 'A$',
  CAD: 'C$',
  CHF: 'CHF',
  HKD: 'HK$',
  SGD: 'S$',
  SEK: 'kr',
  KRW: '₩',
  NOK: 'kr',
  NZD: 'NZ$',
  INR: '₹',
  MXN: 'Mex$',
  TWD: 'NT$',
  ZAR: 'R',
  BRL: 'R$',
  DKK: 'kr',
  PLN: 'zł',
  THB: '฿',
  ILS: '₪',
  IDR: 'Rp',
  CZK: 'Kč',
  AED: 'د.إ',
  TRY: '₺',
  HUF: 'Ft',
  CLP: 'CLP$',
  SAR: '﷼',
  PHP: '₱',
  MYR: 'RM',
  COP: 'COL$',
  RUB: '₽',
  RON: 'lei',
  PEN: 'S/',
  BHD: '.د.ب',
  BGN: 'лв',
  ARS: 'AR$',
  VND: '₫',
  UAH: '₴',
  NGN: '₦',
  EGP: 'E£',
  PKR: '₨',
  QAR: '﷼',
  KWD: 'د.ك',
  MAD: 'د.م.',
  DZD: 'د.ج',
  OMR: '﷼',
  CRC: '₡',
}

export function getCurrencySymbol(currencyCode: string): string {
  return currencySymbolMap[currencyCode] || currencyCode
}
