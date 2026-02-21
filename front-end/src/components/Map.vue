<template>
  <div>
    <v-stage ref="stage" :config="stageSize" id="stage">
      <v-layer ref="baseLayer">
        <v-image ref="image" :config="imageConfig" />
        <!-- US influence rectangles (blue) -->
        <v-rect
          v-for="country in countries"
          :key="country.name + 'Blue'"
          :config="countriesDataBlue(country)"
        />
        <!-- USSR influence rectangles (red) -->
        <v-rect
          v-for="country in countries"
          :key="country.name + 'Red'"
          :config="countriesDataRed(country)"
        />
        <!-- US influence numbers -->
        <v-text
          v-for="country in countries"
          :key="country.name + 'USText'"
          :config="usInfluenceText(country)"
        />
        <!-- USSR influence numbers -->
        <v-text
          v-for="country in countries"
          :key="country.name + 'USSRText'"
          :config="ussrInfluenceText(country)"
        />
        <!-- Country highlight for clickable countries -->
        <v-rect
          v-for="country in clickableCountries"
          :key="country.name + 'Highlight'"
          :config="highlightConfig(country)"
          @click="onCountryClick(country)"
          @mouseenter="onCountryHover(country)"
          @mouseleave="onCountryLeave()"
        />
      </v-layer>
    </v-stage>
    <img src="@/assets/big.jpg" alt="Twilight Map" ref="imgSrc" id="source" />
    <!-- Tooltip overlay -->
    <div
      v-if="tooltipVisible"
      class="country-tooltip"
      :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
    >
      <div class="tooltip-name">{{ tooltipCountry.replace(/_/g, ' ') }}</div>
      <div v-if="tooltipData" class="tooltip-details">
        <div>Stability: {{ tooltipData.stability }}</div>
        <div>US: {{ tooltipData.us_influence }} / USSR: {{ tooltipData.ussr_influence }}</div>
        <div v-if="tooltipData.battleground" class="tooltip-bg">Battleground</div>
        <div :class="controlClass(tooltipData.control)">
          {{ controlLabel(tooltipData.control) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import { countryData } from './countryData'

export default {
  name: 'Map',
  created() {
    window.addEventListener('resize', this.windowResize)
  },
  destroyed() {
    window.removeEventListener('resize', this.windowResize)
  },
  mounted() {
    const stage = this.$refs.stage.getNode()
    const layer = this.$refs.baseLayer.getNode()
    const image = new Image()

    // Initialising the canvas image
    image.src = this.$refs.imgSrc.src
    this.imageWidth = image.width
    this.imageHeight = image.height
    image.onload = () => {
      this.imageConfig.image = image
    }

    let initialScaleLevel = (this.currentScaleLevel = 0.5)
    stage.scale({ x: initialScaleLevel, y: initialScaleLevel })

    // Zooming functionality
    stage.on('wheel', (event) => {
      event.evt.preventDefault()
      let oldScale = stage.scaleX()
      let pointer = stage.getPointerPosition()

      let mousePointTo = {
        x: (pointer.x - stage.x()) / oldScale,
        y: (pointer.y - stage.y()) / oldScale,
      }

      let widthLimit = window.innerWidth / this.imageWidth,
        heightLimit = window.innerHeight / this.imageHeight

      let scaleBy = 0.9,
        minScaleLimit = widthLimit > heightLimit ? widthLimit : heightLimit,
        maxScaleLimit = 1.3

      let newScaleLevel =
        event.evt.deltaY > 0 ? oldScale * scaleBy : oldScale / scaleBy
      if (newScaleLevel > maxScaleLimit && event.evt.deltaY < 0) {
        return
      } else if (newScaleLevel < minScaleLimit && event.evt.deltaY > 0) {
        return
      } else {
        this.currentScaleLevel = newScaleLevel
        stage.scale({ x: this.currentScaleLevel, y: this.currentScaleLevel })
        this.setLimits()

        let newPos = {
          x: pointer.x - mousePointTo.x * this.currentScaleLevel,
          y: pointer.y - mousePointTo.y * this.currentScaleLevel,
        }
        newPos = this.setCurrentCoordinates(newPos)
        stage.position(newPos)
        stage.batchDraw()
      }
    })

    stage.on('click', (event) => {
      const pointer = { x: 0, y: 0 }
      pointer.x =
        (this.currentX - stage.getPointerPosition().x) / this.currentScaleLevel
      pointer.y =
        (this.currentY - stage.getPointerPosition().y) / this.currentScaleLevel
    })
  },
  data() {
    return {
      currentScaleLevel: 0.5,
      clientAction: '',
      state: {},
      stageSize: {
        width: window.innerWidth,
        height: window.innerHeight,
      },
      currentX: 0,
      currentY: 0,
      limits: {
        x: window.innerWidth - this.imageHeight * this.currentScaleLevel,
        y: window.innerHeight * 0.7 - this.imageWidth * this.currentScaleLevel,
      },
      imageWidth: 0,
      imageHeight: 0,
      imageConfig: {
        image: null,
        draggable: true,
        dragBoundFunc: (pos) => {
          this.setLimits()
          const oldPos = { x: pos.x, y: pos.y }
          const newPos = this.setCurrentCoordinates(oldPos)
          this.$refs.stage.getNode().absolutePosition({
            x: newPos.x,
            y: newPos.y,
          })
          return newPos
        },
      },
      rectConfig: {
        sides: 4,
        width: 99,
        height: 99,
      },
      countries: countryData,
      tooltipVisible: false,
      tooltipCountry: '',
      tooltipData: null,
      tooltipX: 0,
      tooltipY: 0,
    }
  },
  computed: {
    ...mapState({
      gameInProgress: (state) => state.locals.gameInProgress,
      replayInProgress: (state) => state.locals.replayInProgress,
      playerView: (state) => state.playerView,
      availableOptions: (state) => state.globals.availableOptions,
    }),
    mapData() {
      if (this.playerView && this.playerView.map) {
        return this.playerView.map
      }
      return {}
    },
    clickableCountries() {
      if (!this.availableOptions || typeof this.availableOptions !== 'object') {
        return []
      }
      const optionValues = Object.values(this.availableOptions)
      return this.countries.filter(c => optionValues.includes(c.name))
    },
  },
  methods: {
    getCountryInfluence(countryName, side) {
      if (!this.mapData[countryName]) return 0
      if (side === 'us') return this.mapData[countryName].us_influence || 0
      if (side === 'ussr') return this.mapData[countryName].ussr_influence || 0
      return 0
    },
    getCountryControl(countryName) {
      if (!this.mapData[countryName]) return 2 // NEUTRAL
      return this.mapData[countryName].control
    },
    countriesDataBlue(country) {
      const usInf = this.getCountryInfluence(country.name, 'us')
      const control = this.getCountryControl(country.name)
      const opacity = usInf > 0 ? Math.min(0.8, 0.3 + usInf * 0.08) : 0.15
      return {
        ...country,
        ...this.rectConfig,
        fill: control === 1 ? '#1565C0' : '#42A5F5',
        opacity: opacity,
      }
    },
    countriesDataRed(country) {
      let { name, x, y } = country
      x += 99
      const ussrInf = this.getCountryInfluence(name, 'ussr')
      const control = this.getCountryControl(name)
      const opacity = ussrInf > 0 ? Math.min(0.8, 0.3 + ussrInf * 0.08) : 0.15
      return {
        name: name,
        x: x,
        y: y,
        ...this.rectConfig,
        fill: control === 0 ? '#B71C1C' : '#EF5350',
        opacity: opacity,
      }
    },
    usInfluenceText(country) {
      const inf = this.getCountryInfluence(country.name, 'us')
      return {
        x: country.x + 25,
        y: country.y + 30,
        fontSize: 40,
        fontFamily: 'Arial',
        fontStyle: 'bold',
        fill: 'white',
        text: inf > 0 ? String(inf) : '',
        listening: false,
      }
    },
    ussrInfluenceText(country) {
      const inf = this.getCountryInfluence(country.name, 'ussr')
      return {
        x: country.x + 99 + 25,
        y: country.y + 30,
        fontSize: 40,
        fontFamily: 'Arial',
        fontStyle: 'bold',
        fill: 'white',
        text: inf > 0 ? String(inf) : '',
        listening: false,
      }
    },
    highlightConfig(country) {
      return {
        x: country.x - 4,
        y: country.y - 4,
        width: 99 * 2 + 8,
        height: 99 + 8,
        fill: 'transparent',
        stroke: '#FFD600',
        strokeWidth: 3,
        cornerRadius: 3,
        listening: true,
      }
    },
    onCountryClick(country) {
      // Send the country selection as a move
      this.$socket.client.emit('client_move', { move: 'm ' + country.name })
    },
    onCountryHover(country) {
      this.tooltipCountry = country.name
      this.tooltipData = this.mapData[country.name] || null
      this.tooltipX = 10
      this.tooltipY = 10
      this.tooltipVisible = true
    },
    onCountryLeave() {
      this.tooltipVisible = false
    },
    controlLabel(control) {
      if (control === 0) return 'USSR Control'
      if (control === 1) return 'US Control'
      return 'No Control'
    },
    controlClass(control) {
      if (control === 0) return 'tooltip-ussr'
      if (control === 1) return 'tooltip-us'
      return 'tooltip-neutral'
    },
    setLimits() {
      this.limits.x = window.innerWidth - 5100 * this.currentScaleLevel
      this.limits.y = window.innerHeight * 0.7 - 3300 * this.currentScaleLevel
    },
    setCurrentCoordinates({ x, y }) {
      if (x > 0) {
        x = 0
      } else if (x < this.limits.x) {
        x = this.limits.x
      }
      if (y > 0) {
        y = 0
      } else if (y < this.limits.y) {
        y = this.limits.y
      }
      this.currentX = x
      this.currentY = y
      return { x: x, y: y }
    },
    windowResize() {
      this.stageSize.width = window.innerWidth
      this.stageSize.height = window.innerHeight
    },
    post() {
      if (this.clientAction != '') {
        console.log(`Sending to server: ${this.clientAction}`)
        if (this.clientAction === 'restart') {
          this.restart()
        } else {
          this.$socket.client.emit('client_move', { move: this.clientAction })
        }
        this.clientAction = ''
      }
    },
  },
  sockets: {
    'server-move': (data) => {
      console.log(`Received from server: data = ${data.server_move}`)
    },
  },
}
</script>

<style>
#source {
  display: none;
}

#stage {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: black;
  user-select: none;
}

.country-tooltip {
  position: fixed;
  z-index: 1000;
  background: rgba(20, 20, 20, 0.95);
  color: #e0e0e0;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  border: 1px solid #444;
  min-width: 140px;
}

.tooltip-name {
  font-weight: bold;
  font-size: 13px;
  margin-bottom: 4px;
  color: #fff;
}

.tooltip-details {
  font-size: 11px;
  line-height: 1.5;
}

.tooltip-bg {
  color: #FFD600;
  font-weight: bold;
}

.tooltip-ussr { color: #EF5350; font-weight: bold; }
.tooltip-us { color: #42A5F5; font-weight: bold; }
.tooltip-neutral { color: #78909C; }
</style>
