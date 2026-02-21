<template>
  <div class="game-info">
    <v-card flat class="info-card">
      <v-card-title class="py-1 info-header">Game Status</v-card-title>
      <v-card-text class="py-1">
        <!-- VP Track -->
        <div class="info-row">
          <span class="info-label">VP:</span>
          <div class="vp-track">
            <div class="vp-bar-container">
              <div class="vp-bar vp-ussr" :style="{ width: ussrVpWidth + '%' }"></div>
              <div class="vp-bar vp-us" :style="{ width: usVpWidth + '%' }"></div>
              <span class="vp-value">{{ vpTrack }}</span>
            </div>
          </div>
        </div>

        <!-- DEFCON -->
        <div class="info-row">
          <span class="info-label">DEFCON:</span>
          <div class="defcon-indicators">
            <span
              v-for="level in 5"
              :key="'defcon-' + level"
              class="defcon-dot"
              :class="{ active: level <= defconTrack, [`defcon-${level}`]: true }"
            >{{ level }}</span>
          </div>
        </div>

        <!-- Turn / AR -->
        <div class="info-row">
          <span class="info-label">Turn:</span>
          <span class="info-value">{{ turnTrack }} / AR {{ arTrack }}</span>
          <span class="info-side" :class="arSideClass">{{ arSideLabel }}</span>
        </div>

        <!-- Military Ops -->
        <div class="info-row">
          <span class="info-label">Mil Ops:</span>
          <span class="info-value">
            <span class="ussr-text">USSR {{ milopsUssr }}</span>
            /
            <span class="us-text">US {{ milopsUs }}</span>
          </span>
        </div>

        <!-- Space Race -->
        <div class="info-row">
          <span class="info-label">Space:</span>
          <span class="info-value">
            <span class="ussr-text">USSR {{ spaceUssr }}</span>
            /
            <span class="us-text">US {{ spaceUs }}</span>
          </span>
        </div>

        <!-- Hand Display -->
        <div v-if="hand && hand.length" class="hand-section">
          <div class="info-label mb-1">Hand ({{ hand.length }} cards):</div>
          <div class="card-list">
            <v-chip
              v-for="card in hand"
              :key="card"
              x-small
              class="ma-1 card-chip"
              :color="cardColor(card)"
              text-color="white"
            >{{ formatCardName(card) }}</v-chip>
          </div>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'GameInfo',
  computed: {
    ...mapState({
      playerView: (state) => state.playerView,
    }),
    vpTrack() {
      return this.playerView ? this.playerView.vp_track : 0
    },
    defconTrack() {
      return this.playerView ? this.playerView.defcon_track : 5
    },
    turnTrack() {
      return this.playerView ? this.playerView.turn_track : 1
    },
    arTrack() {
      return this.playerView ? this.playerView.ar_track : 0
    },
    arSideLabel() {
      if (!this.playerView) return ''
      return this.playerView.ar_side === 0 ? 'USSR' : 'US'
    },
    arSideClass() {
      if (!this.playerView) return ''
      return this.playerView.ar_side === 0 ? 'ussr-text' : 'us-text'
    },
    milopsUssr() {
      return this.playerView ? this.playerView.milops_track[0] : 0
    },
    milopsUs() {
      return this.playerView ? this.playerView.milops_track[1] : 0
    },
    spaceUssr() {
      return this.playerView ? this.playerView.space_track[0] : 0
    },
    spaceUs() {
      return this.playerView ? this.playerView.space_track[1] : 0
    },
    hand() {
      if (!this.playerView || !this.playerView.hand) return []
      return Array.from(this.playerView.hand).sort()
    },
    ussrVpWidth() {
      const vp = this.vpTrack
      return vp > 0 ? Math.min(50, (vp / 20) * 50) : 0
    },
    usVpWidth() {
      const vp = this.vpTrack
      return vp < 0 ? Math.min(50, (-vp / 20) * 50) : 0
    },
  },
  methods: {
    formatCardName(name) {
      return name.replace(/_/g, ' ')
    },
    cardColor(card) {
      // Simple color coding - could be enhanced with card data
      return '#546E7A'
    },
  },
}
</script>

<style scoped>
.game-info {
  font-size: 12px;
}

.info-card {
  background: rgba(30, 30, 30, 0.95) !important;
  color: #e0e0e0;
}

.info-header {
  font-size: 14px !important;
  color: #90CAF9;
  border-bottom: 1px solid #333;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 2px 0;
}

.info-label {
  font-weight: bold;
  color: #B0BEC5;
  min-width: 65px;
  font-size: 12px;
}

.info-value {
  color: #e0e0e0;
  font-size: 12px;
}

.info-side {
  margin-left: 8px;
  font-weight: bold;
  font-size: 11px;
}

.ussr-text { color: #EF5350; }
.us-text { color: #42A5F5; }

.vp-track {
  flex: 1;
  margin-left: 4px;
}

.vp-bar-container {
  position: relative;
  height: 16px;
  background: #333;
  border-radius: 3px;
  display: flex;
  justify-content: center;
  overflow: hidden;
}

.vp-bar {
  height: 100%;
  transition: width 0.3s ease;
}

.vp-ussr { background: #C62828; }
.vp-us { background: #1565C0; position: absolute; right: 0; }

.vp-value {
  position: absolute;
  color: white;
  font-size: 11px;
  font-weight: bold;
  line-height: 16px;
}

.defcon-indicators {
  display: flex;
  gap: 4px;
}

.defcon-dot {
  width: 20px;
  height: 20px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  background: #333;
  color: #666;
}

.defcon-dot.active { color: white; }
.defcon-1.active { background: #B71C1C; }
.defcon-2.active { background: #E65100; }
.defcon-3.active { background: #F9A825; }
.defcon-4.active { background: #558B2F; }
.defcon-5.active { background: #2E7D32; }

.hand-section {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #333;
}

.card-list {
  display: flex;
  flex-wrap: wrap;
}

.card-chip {
  font-size: 10px !important;
  height: 20px !important;
}
</style>
