import { NavLink, Outlet } from 'react-router-dom'

const NAV_ITEMS: { label: string; to: string }[] = [
  { label: 'Suppliers', to: '/suppliers' },
  { label: 'Orders', to: '/orders' },
  { label: 'Deliveries', to: '/deliveries' },
  { label: 'Inventory', to: '/inventory' },
  { label: 'Risks', to: '/risks' },
  { label: 'Recommendations', to: '/recommendations' },
]

function CartIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="9" cy="21" r="1" />
      <circle cx="19" cy="21" r="1" />
      <path d="M1 1h4l2.6 13.4a2 2 0 0 0 2 1.6h9.8a2 2 0 0 0 2-1.6L23 6H6" />
    </svg>
  )
}

function NavDotIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
      <circle cx="5" cy="5" r="4" />
    </svg>
  )
}

export function Layout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <NavLink to="/" className="app-header-link">
          <span className="app-header-icon">
            <CartIcon />
          </span>
          <span className="app-header-text">
            <h1>SAHARA</h1>
            <span className="app-header-subtitle">Supply Access Hub</span>
          </span>
        </NavLink>
      </header>
      <div className="app-body">
        <nav className="app-nav" aria-label="Primary">
          <ul>
            {NAV_ITEMS.map((item) => (
              <li key={item.to}>
                <NavLink to={item.to} className={({ isActive }) => `nav-placeholder${isActive ? ' nav-active' : ''}`}>
                  <span className="nav-icon">
                    <NavDotIcon />
                  </span>
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <main className="app-main">
          <div className="ops-dashboard">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
