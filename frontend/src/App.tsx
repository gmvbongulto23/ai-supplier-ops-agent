import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { OpsDashboard } from './pages/OpsDashboard'
import { SuppliersPage } from './pages/SuppliersPage'
import { OrdersPage } from './pages/OrdersPage'
import { DeliveriesPage } from './pages/DeliveriesPage'
import { InventoryPage } from './pages/InventoryPage'
import { RisksPage } from './pages/RisksPage'
import { RecommendationsPage } from './pages/RecommendationsPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<OpsDashboard />} />
          <Route path="suppliers" element={<SuppliersPage />} />
          <Route path="orders" element={<OrdersPage />} />
          <Route path="deliveries" element={<DeliveriesPage />} />
          <Route path="inventory" element={<InventoryPage />} />
          <Route path="risks" element={<RisksPage />} />
          <Route path="recommendations" element={<RecommendationsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
