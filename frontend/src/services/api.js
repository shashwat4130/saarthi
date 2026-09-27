import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// --------------------------------------------------
// HEALTH
// --------------------------------------------------

export const checkHealth = async () => {
  const response = await apiClient.get('/health')
  return response.data
}

// --------------------------------------------------
// DEMO SCENARIOS
// --------------------------------------------------

export const runScenario = async (scenarioKey) => {
  const response = await apiClient.post(
    `/v1/demo/run/${scenarioKey}`,
  )

  return response.data
}

// --------------------------------------------------
// GOVERNANCE INTERCEPT
// --------------------------------------------------

export const interceptAction = async (manifest) => {
  const response = await apiClient.post(
    '/v1/governance/intercept',
    manifest,
  )

  return response.data
}

// --------------------------------------------------
// AUDIT EVENTS
// --------------------------------------------------

export const getAuditEvents = async (limit = 50) => {
  const response = await apiClient.get('/v1/audit', {
    params: {
      limit,
    },
  })

  return response.data
}

// --------------------------------------------------
// AUDIT CHAIN VERIFICATION
// --------------------------------------------------

export const verifyAuditChain = async () => {
  const response = await apiClient.get('/v1/audit/verify')
  return response.data
}

export default apiClient