import type { HealthResponse } from '../../api/types'

export const healthyResponseFixture: HealthResponse = {
  status: 'alive',
  service: 'supply-chain-ops-api',
  version: '0.1.0',
}
