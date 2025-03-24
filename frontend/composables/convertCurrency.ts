const apiUrl = 'https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_ltkQVoCZeJLP5Pm0JKoEwqLjTbKBe20mDRb47cvD'

export async function convertCurrency(amount: number, from: string, to: string): Promise<number> {
  const fullApiUrl = `${apiUrl}&base_currency=${from}&currencies=${to}`
  const response = await fetch(fullApiUrl)

  if (!response.ok) {
    throw new Error('Failed to convert currency')
  }

  const data = await response.json()
  const rate = data.data[to]

  return amount * rate
}
