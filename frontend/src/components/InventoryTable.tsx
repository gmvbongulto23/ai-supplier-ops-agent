import type { InventoryView } from '../api/types'
import { EmptyState } from './EmptyState'

interface InventoryTableProps {
  items: InventoryView[]
  emptyMessage?: string
}

export function InventoryTable({ items, emptyMessage = 'No inventory records yet.' }: InventoryTableProps) {
  if (items.length === 0) {
    return <EmptyState message={emptyMessage} />
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Product</th>
          <th>Current qty</th>
          <th>Usage/hr</th>
          <th>Min required</th>
          <th>Est. remaining</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.product}>
            <td>{item.product}</td>
            <td>{item.current_quantity}</td>
            <td>{item.avg_usage_per_hour}</td>
            <td>{item.minimum_required_quantity}</td>
            <td>{item.estimated_remaining_hours}h</td>
            <td>
              <span className={`status-pill status-${item.status}`}>{item.status.replace('_', ' ')}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
