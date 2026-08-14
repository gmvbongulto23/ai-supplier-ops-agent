import { describe, expect, it } from 'vitest'

const FORBIDDEN_PATTERNS = [
  /mock(Suppliers|Orders|Deliveries|Inventory|Risks|Recommendations)/i,
  /sample(Suppliers|Orders|Deliveries|Inventory|Risks|Recommendations)/i,
  /fake(Suppliers|Orders|Deliveries|Inventory|Risks|Recommendations)/i,
]

const productionModules = import.meta.glob('../{components,pages}/**/*.{ts,tsx}', {
  eager: true,
  query: '?raw',
  import: 'default',
}) as Record<string, string>

describe('production source audit', () => {
  it('does not hardcode supplier, order, delivery, inventory, risk, or recommendation datasets', () => {
    const entries = Object.entries(productionModules)
    expect(entries.length).toBeGreaterThan(0)

    for (const [file, content] of entries) {
      for (const pattern of FORBIDDEN_PATTERNS) {
        expect(content, `${file} appears to reference a forbidden mock dataset: ${pattern}`).not.toMatch(pattern)
      }
    }
  })
})
