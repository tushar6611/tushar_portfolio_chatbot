export const USERNAME_STORAGE_KEY = 'portfolio_username'

export function getStoredUsername(): string | null {
  if (typeof sessionStorage === 'undefined') return null
  return sessionStorage.getItem(USERNAME_STORAGE_KEY)
}

export function setStoredUsername(username: string): void {
  sessionStorage.setItem(USERNAME_STORAGE_KEY, username)
}
