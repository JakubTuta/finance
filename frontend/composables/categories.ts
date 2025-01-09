export type categories = 'entertainment' | 'food' | 'groceries' | 'payment' | 'others'

export const mapCategories: Record<categories, string> = {
  entertainment: 'Entertainment',
  food: 'Food',
  groceries: 'Groceries',
  payment: 'Payment',
  others: 'Others',
}

export const mapCategoriesColor: Record<categories, string> = {
  entertainment: 'blue',
  food: 'yellow',
  groceries: 'orange',
  payment: 'green',
  others: 'grey',
}
