<template>
  <div>
    <div class="page-header">
      <h1>Order History</h1>
      <p>Your recent trades</p>
    </div>

    <div v-if="loading" class="loading-page"><div class="spinner"></div></div>

    <div v-else class="card">
      <div v-if="!orders.length" class="text-center text-muted" style="padding:40px">
        No orders yet. Go to <router-link to="/trade" class="text-gold">Trade</router-link> to place your first order.
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Pair</th>
            <th>Side</th>
            <th class="text-right">Quantity</th>
            <th class="text-right">Price</th>
            <th class="text-right">Total</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in orders" :key="o.id">
            <td class="text-sm text-muted">{{ formatDate(o.created_at) }}</td>
            <td><strong>{{ o.asset_symbol }}</strong>/USD</td>
            <td>
              <span class="badge" :class="o.side === 'buy' ? 'badge-green' : 'badge-red'">
                {{ o.side.toUpperCase() }}
              </span>
            </td>
            <td class="text-right text-mono">{{ formatQty(o.quantity, o.asset_symbol) }}</td>
            <td class="text-right text-mono">${{ formatPrice(o.price) }}</td>
            <td class="text-right text-mono">${{ formatNum(o.total) }}</td>
            <td><span class="badge badge-blue">{{ o.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'OrdersView',
  data() {
    return { orders: [], loading: true }
  },
  async created() {
    try {
      const res = await api.get('/orders')
      this.orders = res.data.orders
    } catch (err) { console.error(err) }
    finally { this.loading = false }
  },
  methods: {
    formatDate(iso) {
      if (!iso) return ''
      const d = new Date(iso)
      return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    },
    formatPrice(p) {
      if (p < 0.01) return Number(p).toFixed(6)
      if (p < 1) return Number(p).toFixed(4)
      return Number(p).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    },
    formatNum(n) {
      return Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    },
    formatQty(q, symbol) {
      if (symbol === 'MEMESTR') return Number(q).toLocaleString('en-US', { maximumFractionDigits: 0 })
      return Number(q).toLocaleString('en-US', { maximumFractionDigits: 6 })
    },
  },
}
</script>
