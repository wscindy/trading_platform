<template>
  <div>
    <div class="page-header">
      <h1>Trade</h1>
      <p>Buy and sell digital assets</p>
    </div>

    <div style="display:grid;grid-template-columns:1fr 360px;gap:24px">
      <!-- Price chart area -->
      <div class="card">
        <div class="card-header">
          <h2>
            <span style="font-size:18px">{{ currentAsset.icon }}</span>
            {{ selectedSymbol }} / USD
          </h2>
          <div class="flex gap-2">
            <button
              v-for="s in symbols" :key="s"
              class="btn btn-sm"
              :class="s === selectedSymbol ? 'btn-primary' : 'btn-outline'"
              @click="selectSymbol(s)"
            >{{ s }}</button>
          </div>
        </div>

        <div v-if="priceData">
          <div class="flex items-center gap-4 mb-4">
            <span class="kpi-value">${{ formatPrice(priceData.price) }}</span>
            <span class="badge" :class="priceData.change_24h_pct >= 0 ? 'badge-green' : 'badge-red'">
              {{ priceData.change_24h_pct >= 0 ? '+' : '' }}{{ priceData.change_24h_pct }}%
            </span>
          </div>
          <div style="height:280px">
            <canvas ref="chartCanvas"></canvas>
          </div>
        </div>
      </div>

      <!-- Order form -->
      <div class="card">
        <div class="side-tabs">
          <div class="side-tab" :class="{ 'active-buy': side === 'buy' }" @click="side = 'buy'">Buy</div>
          <div class="side-tab" :class="{ 'active-sell': side === 'sell' }" @click="side = 'sell'">Sell</div>
        </div>

        <div v-if="orderError" class="alert alert-error">{{ orderError }}</div>
        <div v-if="orderSuccess" class="alert alert-success">{{ orderSuccess }}</div>

        <div class="form-group">
          <label>Asset</label>
          <select v-model="selectedSymbol" @change="fetchPrice">
            <option v-for="s in symbols" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>

        <div class="form-group">
          <label>Quantity</label>
          <input
            type="number" v-model.number="quantity"
            :placeholder="'Amount of ' + selectedSymbol"
            step="any" min="0"
          />
        </div>

        <div v-if="priceData && quantity > 0" style="margin-bottom:20px">
          <div class="flex justify-between text-sm text-muted mb-4">
            <span>Price</span>
            <span class="text-mono">${{ formatPrice(priceData.price) }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span>Total</span>
            <span class="text-mono" style="font-weight:600">${{ formatNum(estimatedTotal) }}</span>
          </div>
        </div>

        <button
          class="btn" style="width:100%"
          :class="side === 'buy' ? 'btn-green' : 'btn-red'"
          :disabled="orderLoading || !quantity"
          @click="placeOrder"
        >
          <span v-if="orderLoading" class="spinner"></span>
          <span v-else>{{ side === 'buy' ? 'Buy' : 'Sell' }} {{ selectedSymbol }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

export default {
  name: 'TradeView',
  data() {
    return {
      symbols: ['BTC', 'ETH', 'SOL', 'MEMESTR'],
      selectedSymbol: 'BTC',
      side: 'buy',
      quantity: null,
      priceData: null,
      history: [],
      chart: null,
      orderLoading: false,
      orderError: '',
      orderSuccess: '',
    }
  },
  computed: {
    currentAsset() {
      const icons = { BTC: '₿', ETH: 'Ξ', SOL: '◎', MEMESTR: '🎭' }
      return { icon: icons[this.selectedSymbol] || '' }
    },
    estimatedTotal() {
      if (!this.priceData || !this.quantity) return 0
      return this.quantity * this.priceData.price
    },
  },
  async created() {
    await this.fetchPrice()
    await this.fetchHistory()
  },
  methods: {
    async selectSymbol(s) {
      this.selectedSymbol = s
      this.quantity = null
      this.orderError = ''
      this.orderSuccess = ''
      await this.fetchPrice()
      await this.fetchHistory()
    },
    async fetchPrice() {
      try {
        const res = await api.get(`/market/price/${this.selectedSymbol}`)
        this.priceData = res.data
      } catch (err) { console.error(err) }
    },
    async fetchHistory() {
      try {
        const res = await api.get(`/market/history/${this.selectedSymbol}`)
        this.history = res.data.history
        this.$nextTick(() => this.renderChart())
      } catch (err) { console.error(err) }
    },
    renderChart() {
      if (this.chart) this.chart.destroy()
      const canvas = this.$refs.chartCanvas
      if (!canvas) return

      const labels = this.history.map(h => h.date.slice(5))
      const data = this.history.map(h => h.price)
      const isUp = data[data.length - 1] >= data[0]

      this.chart = new Chart(canvas, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            data,
            borderColor: isUp ? '#0ecb81' : '#f6465d',
            backgroundColor: isUp ? 'rgba(14,203,129,0.08)' : 'rgba(246,70,93,0.08)',
            fill: true,
            tension: 0.3,
            pointRadius: 0,
            borderWidth: 2,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              grid: { color: 'rgba(43,51,64,0.5)' },
              ticks: { color: '#5e6673', font: { size: 11 }, maxTicksLimit: 8 },
            },
            y: {
              grid: { color: 'rgba(43,51,64,0.5)' },
              ticks: {
                color: '#5e6673',
                font: { size: 11, family: 'JetBrains Mono' },
                callback: v => '$' + v.toLocaleString(),
              },
            },
          },
        },
      })
    },
    async placeOrder() {
      this.orderError = ''
      this.orderSuccess = ''
      this.orderLoading = true

      try {
        const res = await api.post('/trade', {
          symbol: this.selectedSymbol,
          side: this.side,
          quantity: this.quantity,
        })
        const o = res.data.order
        this.orderSuccess = `${o.side.toUpperCase()} ${o.quantity} ${o.asset_symbol} @ $${this.formatPrice(o.price)} — Total: $${this.formatNum(o.total)}`
        this.quantity = null
        await this.fetchPrice()
      } catch (err) {
        const data = err.response?.data
        this.orderError = data?.error || 'Order failed'
        if (data?.details) {
          this.orderError += ': ' + Object.values(data.details).join(', ')
        }
      } finally {
        this.orderLoading = false
      }
    },
    formatPrice(p) {
      if (p < 0.01) return Number(p).toFixed(6)
      if (p < 1) return Number(p).toFixed(4)
      return Number(p).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    },
    formatNum(n) {
      return Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    },
  },
}
</script>
