<template>
  <div class="ai-explanation" v-if="hasExplanation">
    <v-card flat class="explanation-card">
      <v-card-title class="py-1 explanation-header" @click="expanded = !expanded">
        <v-icon small class="mr-2" color="#90CAF9">mdi-robot</v-icon>
        AI Analysis
        <v-spacer />
        <v-icon small color="#90CAF9">
          {{ expanded ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
        </v-icon>
      </v-card-title>

      <v-expand-transition>
        <v-card-text v-show="expanded" class="py-2">
          <!-- Chosen Action -->
          <div class="chosen-action">
            <span class="label">Played:</span>
            <span class="action-name">{{ chosenAction }}</span>
            <span class="confidence-badge" :class="confidenceClass">
              {{ confidence }}
            </span>
          </div>

          <!-- Reasoning -->
          <div v-if="reasoning" class="reasoning">
            {{ reasoning }}
          </div>

          <!-- Alternatives -->
          <div v-if="alternatives.length" class="alternatives">
            <div class="label mb-1">Top alternatives:</div>
            <div
              v-for="(alt, idx) in alternatives"
              :key="idx"
              class="alt-row"
            >
              <span class="alt-name">{{ alt.action }}</span>
              <div class="alt-bar-container">
                <div
                  class="alt-bar"
                  :style="{ width: (alt.raw_confidence * 100) + '%' }"
                  :class="idx === 0 ? 'chosen' : ''"
                ></div>
              </div>
              <span class="alt-confidence">{{ alt.confidence }}</span>
            </div>
          </div>

          <!-- Simulation Info -->
          <div class="sim-info">
            {{ totalSimulations }} simulations across {{ numWorlds }} worlds
          </div>
        </v-card-text>
      </v-expand-transition>
    </v-card>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'AIExplanation',
  data() {
    return {
      expanded: true,
    }
  },
  computed: {
    ...mapState({
      aiExplanation: (state) => state.aiExplanation,
    }),
    hasExplanation() {
      return this.aiExplanation && this.aiExplanation.chosen_action
    },
    chosenAction() {
      return this.aiExplanation ? this.aiExplanation.chosen_action : ''
    },
    confidence() {
      return this.aiExplanation ? this.aiExplanation.confidence : '0%'
    },
    reasoning() {
      return this.aiExplanation ? this.aiExplanation.reasoning : ''
    },
    alternatives() {
      return this.aiExplanation ? (this.aiExplanation.alternatives || []) : []
    },
    totalSimulations() {
      return this.aiExplanation ? (this.aiExplanation.total_simulations || 0) : 0
    },
    numWorlds() {
      return this.aiExplanation ? (this.aiExplanation.num_worlds || 0) : 0
    },
    confidenceClass() {
      const conf = this.aiExplanation ? this.aiExplanation.raw_confidence || 0 : 0
      if (conf >= 0.7) return 'high'
      if (conf >= 0.4) return 'medium'
      return 'low'
    },
  },
}
</script>

<style scoped>
.explanation-card {
  background: rgba(30, 30, 30, 0.95) !important;
  color: #e0e0e0;
}

.explanation-header {
  font-size: 13px !important;
  color: #90CAF9;
  border-bottom: 1px solid #333;
  cursor: pointer;
  user-select: none;
}

.chosen-action {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.label {
  color: #B0BEC5;
  font-size: 11px;
  font-weight: bold;
}

.action-name {
  color: #E0E0E0;
  font-weight: bold;
  font-size: 13px;
}

.confidence-badge {
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: bold;
}

.confidence-badge.high { background: #2E7D32; color: white; }
.confidence-badge.medium { background: #F9A825; color: #333; }
.confidence-badge.low { background: #C62828; color: white; }

.reasoning {
  color: #90A4AE;
  font-size: 11px;
  font-style: italic;
  margin-bottom: 8px;
  padding: 4px 8px;
  border-left: 2px solid #455A64;
}

.alternatives {
  margin-bottom: 6px;
}

.alt-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 0;
}

.alt-name {
  min-width: 120px;
  font-size: 11px;
  color: #B0BEC5;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alt-bar-container {
  flex: 1;
  height: 8px;
  background: #333;
  border-radius: 2px;
  overflow: hidden;
}

.alt-bar {
  height: 100%;
  background: #546E7A;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.alt-bar.chosen {
  background: #42A5F5;
}

.alt-confidence {
  font-size: 11px;
  color: #78909C;
  min-width: 30px;
  text-align: right;
}

.sim-info {
  font-size: 10px;
  color: #546E7A;
  text-align: right;
  margin-top: 4px;
}
</style>
