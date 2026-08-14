import type { ReactNode } from 'react'

const NAV_ITEMS = ['Suppliers', 'Orders', 'Deliveries', 'Inventory', 'Risks', 'Recommendations'] as const

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Supply Chain Ops</h1>
      </header>
      <div className="app-body">
        <nav className="app-nav" aria-label="Primary">
          <ul>
            {NAV_ITEMS.map((item) => (
              <li key={item}>
                <span className="nav-placeholder">{item}</span>
              </li>
            ))}
          </ul>
        </nav>
        <main className="app-main">{children}</main>
      </div>
    </div>
  )
}
