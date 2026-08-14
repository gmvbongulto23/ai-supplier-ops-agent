export interface HealthResponse {
  status: string
  service: string
  version: string
}

export interface InventoryView {
  product: string
  current_quantity: number
  avg_usage_per_hour: number
  minimum_required_quantity: number
  estimated_remaining_hours: number
  status: 'healthy' | 'at_risk' | 'critical'
}

export interface OrderView {
  id: string
  supplier_name: string
  product: string
  quantity: number
  expected_delivery: string
  current_eta: string
  status: 'on_time' | 'delayed' | 'at_risk' | 'delivered'
  delay_info: string | null
}

export interface Recommendation {
  id: string
  product: string
  order_id: string | null
  severity: string
  message: string
  reason: string
  backup_supplier_id: string | null
  status: 'pending' | 'accepted'
  created_at: string
  accepted_at: string | null
}

export interface DashboardResponse {
  delivery_summary: Record<string, number>
  inventory: InventoryView[]
  orders: OrderView[]
  recommendations: Recommendation[]
}

export type ApiErrorKind = 'config' | 'network' | 'timeout' | 'http' | 'parse'

export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly status?: number

  constructor(message: string, kind: ApiErrorKind, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = status
  }
}
