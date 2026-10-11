import { apiRequest } from './api'

const ENDPOINTS = {
  cv: { base: '/cvs', templates: '/cv-templates/' },
  portfolio: { base: '/portfolios', templates: '/portfolio-templates/' },
}

/** CRUD client for a document kind ('cv' | 'portfolio'). Ownership is enforced by the server. */
export function createDocumentApi(kind) {
  const { base, templates } = ENDPOINTS[kind]
  if (!base) throw new Error(`Unknown document kind: ${kind}`)
  return {
    list: (query) => apiRequest('GET', `${base}/`, { query }),
    get: (id) => apiRequest('GET', `${base}/${id}/`),
    create: (payload) => apiRequest('POST', `${base}/`, { body: payload }),
    update: (id, payload) => apiRequest('PATCH', `${base}/${id}/`, { body: payload }),
    duplicate: (id) => apiRequest('POST', `${base}/${id}/duplicate/`),
    remove: (id) => apiRequest('DELETE', `${base}/${id}/`),
    templates: () => apiRequest('GET', templates),
  }
}

export const cvApi = createDocumentApi('cv')
export const portfolioApi = createDocumentApi('portfolio')
