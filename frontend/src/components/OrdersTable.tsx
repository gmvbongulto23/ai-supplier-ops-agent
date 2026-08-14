import type { OrderView } from '../api/types'
import { EmptyState } from './EmptyState'

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

interface OrdersTableProps {
  orders: OrderView[]
  emptyMessage?: string
}

export function OrdersTable({ orders, emptyMessage = 'No orders yet.' }: OrdersTableProps) {
  if (orders.length === 0) {
    return <EmptyState message={emptyMessage} />
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Supplier</th>
          <th>Product</th>
          <th>Qty</th>
          <th>Expected</th>
          <th>Current ETA</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {orders.map((order) => (
          <tr key={order.id}>
            <td>{order.supplier_name}</td>
            <td>{order.product}</td>
            <td>{order.quantity}</td>
            <td>{formatTime(order.expected_delivery)}</td>
            <td>{formatTime(order.current_eta)}</td>
            <td>
              <span className={`status-pill status-${order.status}`}>{order.status.replace('_', ' ')}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

interface DeliveriesTableProps {
  orders: OrderView[]
  emptyMessage?: string
}

export function DeliveriesTable({ orders, emptyMessage = 'No deliveries yet.' }: DeliveriesTableProps) {
  if (orders.length === 0) {
    return <EmptyState message={emptyMessage} />
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Product</th>
          <th>Supplier</th>
          <th>Current ETA</th>
          <th>Delay info</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {orders.map((order) => (
          <tr key={order.id}>
            <td>{order.product}</td>
            <td>{order.supplier_name}</td>
            <td>{formatTime(order.current_eta)}</td>
            <td>{order.delay_info ?? '—'}</td>
            <td>
              <span className={`status-pill status-${order.status}`}>{order.status.replace('_', ' ')}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
