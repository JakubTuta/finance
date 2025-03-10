export interface IUser {
  id: string
  username: string
  currency: string
}

export function mapUser(user: Partial<IUser>): IUser {
  return {
    id: user?.id || '',
    username: user?.username || '',
    currency: user?.currency || 'USD',
  }
}
