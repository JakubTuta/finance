const emailPattern
  = /^(?:[^<>()[\]\\.,;:\s@"]+(?:\.[^<>()[\]\\.,;:\s@"]+)*|".+")@(?:\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\]|(?:[a-z\-0-9]+\.)+[a-z]{2,})$/i

export const requiredRule = (fieldName: string) => (value: string | number | null, textError = `${fieldName} is required`) => Boolean(value) || textError

export const emailRule = () => (value: string, textError = 'Incorrect email format') => emailPattern.test(value) || textError

export const minLengthRule = (min: number) => (value: string, textError = `Min length is ${min}`) => value.length >= min || textError

export const maxLengthRule = (max: number) => (value: string, textError = `Max length is ${max}`) => value.length <= max || textError

export function numberRule(fieldName: string) {
  return (value: any, textError = `${fieldName} must be a valid number`) => /^-?(?:\d+(?:\.\d+)?|\.\d+)$/.test(value) || textError
}

export function positiveIntRule(fieldName: string) {
  return (value: number, textError = `${fieldName} must be a positive integer`) => (Number.isInteger(value) && value > 0) || textError
}
