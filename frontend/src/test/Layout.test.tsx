import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { Layout } from '../components/Layout'

function renderLayout() {
  render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<p>content</p>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

describe('Layout', () => {
  it('renders the app heading and children', () => {
    renderLayout()

    expect(screen.getByRole('heading', { name: 'Supply Chain Ops' })).toBeInTheDocument()
    expect(screen.getByText('content')).toBeInTheDocument()
  })

  it('renders a navigation placeholder for every core operational area', () => {
    renderLayout()

    const nav = screen.getByRole('navigation', { name: 'Primary' })
    for (const label of ['Suppliers', 'Orders', 'Deliveries', 'Inventory', 'Risks', 'Recommendations']) {
      expect(nav).toHaveTextContent(label)
    }
  })
})
