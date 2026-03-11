<template>
  <div>
    <div class="page-header">
      <h1>Portfolio Dashboard</h1>
      <p>Overview of your digital assets</p>
    </div>

    <div v-if="loading" class="loading-page"><div class="spinner"></div></div>

    <template v-else>
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-label">Total Portfolio Value</div>
          <div class="kpi-value text-gold">${{ formatNum(totalValue) }}</div>
        </div>
        <div class="kpi-card" v-for="item in cryptoAssets" :key="item.asset_symbol">
          <div class="kpi-label">{{ item.name }}</div>
          <div class="kpi-value">{{ formatBalance(item.balance, item.asset_symbol) }}</div>
          <div class="text-sm text-muted mt-2">${{ formatNum(item.value_usd) }}</div>
        </div>
      </div>

      <div class="card mb-6">
        <div class="card-header">
          <h2>Assets</h2>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Asset</th>
              <th class="text-right">Balance</th>
              <th class="text-right">Price</th>
              <th class="text-right">Value (USD)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in portfolio" :key="item.asset_symbol">
              <td>
                <span class="flex items-center gap-2">
                  <span style="font-size:18px">{{ item.icon }}</span>
                  <span>
                    <strong>{{ item.asset_symbol }}</strong>
                    <span class="text-muted text-sm" style="margin-left:6px">{{ item.name }}</span>
                  </span>
                </span>
              </td>
              <td class="text-right text-mono">{{ formatBalance(item.balance, item.asset_symbol) }}</td>
              <td class="text-right text-mono">${{ formatNum(item.current_price) }}</td>
              <td class="text-right text-mono">${{ formatNum(item.value_usd) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card" v-if="fundHoldings.length">
        <div class="card-header">
          <h2>Fund Holdings</h2>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Fund</th>
              <th class="text-right">Tokens</th>
              <th class="text-right">NAV</th>
              <th class="text-right">Value</th>
              <th class="text-right">P&L</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in fundHoldings" :key="h.id">
              <td><span class="badge badge-gold">{{ h.fund_id }}</span></td>
              <td class="text-right text-mono">{{ h.tokens }}</td>
              <td class="text-right text-mono">${{ h.current_nav }}</td>
              <td class="text-right text-mono">${{ formatNum(h.current_value) }}</td>
              <td class="text-right text-mono" :class="h.pnl >= 0 ? 'text-green' : 'text-red'">
                {{ h.pnl >= 0 ? '+' : '' }}${{ formatNum(h.pnl) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'DashboardView',
  data() {
    return {
      portfolio: [],
      totalValue: 0,
      fundHoldings: [],
      loading: true,
    }
  },
  computed: {
    cryptoAssets() {
      return this.portfolio.filter(a => a.asset_symbol !== 'USD')
    },
  },
  async created() { await this.fetchData() },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const [walletRes, fundRes] = await Promise.all([
          api.get('/wallet'),
          api.get('/fund/holdings'),
        ])
        this.portfolio = walletRes.data.portfolio
        this.totalValue = walletRes.data.total_value_usd
        this.fundHoldings = fundRes.data.holdings
      } catch (err) {
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    formatNum(n) {
      if (n == null) return '0.00'
      return Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    },
    formatBalance(bal, symbol) {
      if (symbol === 'USD') return this.formatNum(bal)
      if (symbol === 'MEMESTR') return Number(bal).toLocaleString('en-US', { maximumFractionDigits: 0 })
      return Number(bal).toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 6 })
    },
  },
}
</script>
