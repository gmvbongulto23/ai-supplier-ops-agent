import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Layout } from '../components/Layout'

describe('Layout', () => {
  it('renders the app heading and children', () => {
    render(
      <Layout>
        <p>content</p>
      </Layout>,
    )

    expect(screen.getByRole('heading', { name: 'Supply Chain Ops' })).toBeInTheDocument()
    expect(screen.getByText('content')).toBeInTheDocument()
  })

  it('renders a navigation placeholder for every core operational area', () => {
    render(
      <Layout>
        <p>content</p>
      </Layout>,
    )

    const nav = screen.getByRole('navigation', { name: 'Primary' })
    for (const label of ['Suppliers', 'Orders', 'Deliveries', 'Inventory', 'Risks', 'Recommendations']) {
      expect(nav).toHaveTextContent(label)
    }
  })
})
