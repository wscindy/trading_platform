<template>
  <div>
    <div class="page-header">
      <h1>Pokemon Card Tokenized Fund</h1>
      <p>Invest in authenticated, insured Pokémon trading cards</p>
    </div>

    <div v-if="loading" class="loading-page"><div class="spinner"></div></div>

    <template v-else-if="fund">
      <!-- Fund hero -->
      <div class="fund-hero">
        <h2>{{ fund.name }}</h2>
        <p class="fund-desc">{{ fund.description }}</p>
        <div class="kpi-grid mt-4" style="margin-bottom:0">
          <div>
            <div class="kpi-label">Current NAV</div>
            <div class="kpi-value text-gold">${{ fund.current_nav }}</div>
          </div>
          <div>
            <div class="kpi-label">Card</div>
            <div style="font-weight:600">{{ fund.card_name }}</div>
            <div class="badge badge-gold mt-2">{{ fund.psa_grade }}</div>
          </div>
          <div>
            <div class="kpi-label">Cards Acquired</div>
            <div style="font-weight:600">{{ fund.cards_acquired.toLocaleString() }} / {{ fund.total_cards_target.toLocaleString() }}</div>
            <div class="progress-bar mt-2">
              <div class="progress-fill" :style="{ width: fund.acquisition_progress_pct + '%' }"></div>
            </div>
            <div class="text-xs text-muted mt-2">{{ fund.acquisition_progress_pct }}% of target</div>
          </div>
          <div>
            <div class="kpi-label">Tokens Available</div>
            <div style="font-weight:600">{{ fund.tokens_available.toLocaleString() }}</div>
            <div class="text-xs text-muted mt-2">of {{ fund.total_tokens.toLocaleString() }} total</div>
          </div>
        </div>
      </div>

      <!-- Fund details + Subscribe -->
      <div style="display:grid;grid-template-columns:1fr 360px;gap:24px">
        <div class="card">
          <div class="card-header"><h2>Fund Details</h2></div>
          <table class="data-table">
            <tbody>
              <tr><td class="text-muted">Fund ID</td><td class="text-mono">{{ fund.fund_id }}</td></tr>
              <tr><td class="text-muted">Vault Provider</td><td>{{ fund.vault_provider }}</td></tr>
              <tr><td class="text-muted">Audit Firm</td><td>{{ fund.audit_firm }}</td></tr>
              <tr><td class="text-muted">Next Audit</td><td>{{ fund.next_audit_date }}</td></tr>
              <tr><td class="text-muted">Min Investment</td><td>{{ fund.min_investment_tokens }} tokens</td></tr>
              <tr><td class="text-muted">Token Price (NAV)</td><td class="text-mono">${{ fund.current_nav }}</td></tr>
            </tbody>
          </table>

          <!-- Current Holdings -->
          <div v-if="holdings.length" class="mt-6">
            <h3 style="font-size:15px;font-weight:600;margin-bottom:12px">Your Holdings</h3>
            <div v-for="h in holdings" :key="h.id" class="flex justify-between items-center" style="padding:12px 0;border-top:1px solid var(--border)">
              <div>
                <div class="text-mono" style="font-weight:600">{{ h.tokens }} tokens</div>
                <div class="text-sm text-muted">Avg price: ${{ h.avg_price }}</div>
              </div>
              <div class="text-right">
                <div class="text-mono" style="font-weight:600">${{ formatNum(h.current_value) }}</div>
                <div class="text-sm" :class="h.pnl >= 0 ? 'text-green' : 'text-red'">
                  {{ h.pnl >= 0 ? '+' : '' }}${{ formatNum(h.pnl) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Subscribe / Redeem form -->
        <div>
          <div class="card mb-4">
            <h3 style="font-size:15px;font-weight:600;margin-bottom:16px">Subscribe</h3>
            <div v-if="subError" class="alert alert-error">{{ subError }}</div>
            <div v-if="subSuccess" class="alert alert-success">{{ subSuccess }}</div>

            <div class="form-group">
              <label>Tokens to buy</label>
              <input type="number" v-model.number="subTokens" placeholder="e.g. 100" min="1" step="1" />
            </div>

            <div v-if="subTokens > 0" class="flex justify-between text-sm mb-4">
              <span class="text-muted">Estimated cost</span>
              <span class="text-mono" style="font-weight:600">${{ formatNum(subTokens * fund.current_nav) }}</span>
            </div>

            <button class="btn btn-green" style="width:100%" :disabled="subLoading || !subTokens" @click="subscribe">
              <span v-if="subLoading" class="spinner"></span>
              <span v-else>Buy Tokens</span>
            </button>
          </div>

          <div class="card" v-if="holdings.length">
            <h3 style="font-size:15px;font-weight:600;margin-bottom:16px">Redeem</h3>
            <div v-if="redeemError" class="alert alert-error">{{ redeemError }}</div>
            <div v-if="redeemSuccess" class="alert alert-success">{{ redeemSuccess }}</div>

            <div class="form-group">
              <label>Tokens to redeem</label>
              <input type="number" v-model.number="redeemTokens" placeholder="e.g. 50" min="1" step="1" />
            </div>

            <button class="btn btn-red" style="width:100%" :disabled="redeemLoading || !redeemTokens" @click="redeem">
              <span v-if="redeemLoading" class="spinner"></span>
              <span v-else>Redeem Tokens</span>
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'FundView',
  data() {
    return {
      fund: null,
      holdings: [],
      loading: true,
      subTokens: null,
      subLoading: false,
      subError: '',
      subSuccess: '',
      redeemTokens: null,
      redeemLoading: false,
      redeemError: '',
      redeemSuccess: '',
    }
  },
  async created() { await this.fetchAll() },
  methods: {
    async fetchAll() {
      this.loading = true
      try {
        const [fundRes, holdRes] = await Promise.all([
          api.get('/fund/info'),
          api.get('/fund/holdings'),
        ])
        this.fund = fundRes.data.fund
        this.holdings = holdRes.data.holdings
      } catch (err) { console.error(err) }
      finally { this.loading = false }
    },
    async subscribe() {
      this.subError = ''
      this.subSuccess = ''
      this.subLoading = true
      try {
        const res = await api.post('/fund/subscribe', { tokens: this.subTokens })
        this.subSuccess = `Subscribed ${res.data.subscription.tokens} tokens @ $${res.data.subscription.nav_per_token}`
        this.subTokens = null
        await this.fetchAll()
      } catch (err) {
        const d = err.response?.data
        this.subError = d?.error || 'Subscription failed'
        if (d?.details) this.subError += ': ' + Object.values(d.details).join(', ')
      } finally { this.subLoading = false }
    },
    async redeem() {
      this.redeemError = ''
      this.redeemSuccess = ''
      this.redeemLoading = true
      try {
        const res = await api.post('/fund/redeem', { tokens: this.redeemTokens })
        this.redeemSuccess = `Redeemed ${res.data.redemption.tokens} tokens — received $${this.formatNum(res.data.redemption.total_proceeds)}`
        this.redeemTokens = null
        await this.fetchAll()
      } catch (err) {
        const d = err.response?.data
        this.redeemError = d?.error || 'Redemption failed'
        if (d?.details) this.redeemError += ': ' + Object.values(d.details).join(', ')
      } finally { this.redeemLoading = false }
    },
    formatNum(n) {
      return Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    },
  },
}
</script>
