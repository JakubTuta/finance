export function stringToDate(date: string): Date {
  return new Date(date)
}

export function dateToString(date: Date): string {
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear()

  return `${day}.${month}.${year}`
}

export function dateToStringDash(date: Date): string {
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear()

  return `${year}-${month}-${day}`
}

export function fullDateToString(date: Date): string {
  const day = date.getDate().toString().padStart(2, '0')
  const month = (date.getMonth() + 1).toString().padStart(2, '0')
  const year = date.getFullYear()

  const [hours, minutes] = date.toLocaleTimeString().split(':')

  return `${year}-${month}-${day} ${hours}:${minutes}`
}

export function isSameDay(date1: Date, date2: Date): boolean {
  return date1.getDate() === date2.getDate()
    && date1.getMonth() === date2.getMonth()
    && date1.getFullYear() === date2.getFullYear()
}

export function addDays(date: Date, days: number): Date {
  const newDate = new Date(date)
  newDate.setDate(date.getDate() + days)

  return newDate
}

export function startOfDay(date: Date): Date {
  const newDate = new Date(date)
  newDate.setHours(0, 0, 0, 0)

  return newDate
}

export function endOfDay(date: Date): Date {
  const newDate = new Date(date)
  newDate.setHours(23, 59, 59, 999)

  return newDate
}

export function startOfMonth(date: Date): Date {
  const newDate = new Date(date)
  newDate.setDate(1)
  newDate.setHours(0, 0, 0, 0)

  return newDate
}

export function endOfMonth(date: Date): Date {
  const newDate = new Date(date)
  newDate.setMonth(date.getMonth() + 1)
  newDate.setDate(0)
  newDate.setHours(23, 59, 59, 999)

  return newDate
}
