/** First validation message for a field returned by the API, or ''. */
export function fieldError(fields, name) {
  const messages = fields && fields[name]
  return messages && messages.length ? messages[0] : ''
}
