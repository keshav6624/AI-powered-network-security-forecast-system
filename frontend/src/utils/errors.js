export function getErrorMessage(error, fallback = 'The request could not be completed.') {
  return error?.response?.data?.detail || error?.message || fallback
}
