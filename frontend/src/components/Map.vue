<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { useSocket } from '@/composables/useSocket'
import { storeToRefs } from 'pinia'
import { countryData } from './countryData'
import type { CountryEntry, CountryMapData } from '@/types/game'

const store = useGameStore()
const { playerView, globals } = storeToRefs(store)
const { sendMove } = useSocket()

const stageRef = ref<InstanceType<any> | null>(null)
const imgSrc = ref<HTMLImageElement | null>(null)

const currentScaleLevel = ref(0.5)
const currentX = ref(0)
const currentY = ref(0)
const imageWidth = ref(0)
const imageHeight = ref(0)

const stageSize = ref({
  width: window.innerWidth,
  height: window.innerHeight,
})

const limits = ref({ x: 0, y: 0 })

const imageConfig = ref<{
  image: HTMLImageElement | null
  draggable: boolean
  dragBoundFunc: (pos: { x: number; y: number }) => { x: number; y: number }
}>({
  image: null,
  draggable: true,
  dragBoundFunc: (pos) => {
    setLimits()
    return setCurrentCoordinates({ x: pos.x, y: pos.y })
  },
})

const rectConfig = { sides: 4, width: 99, height: 99 }

const countries = Object.values(countryData)

// Tooltip state
const tooltipVisible = ref(false)
const tooltipCountry = ref('')
const tooltipData = ref<CountryMapData | null>(null)
const tooltipX = ref(0)
const tooltipY = ref(0)

// Computed
const mapData = computed<Record<string, CountryMapData>>(() => {
  if (playerView.value && playerView.value.map) return playerView.value.map
  return {}
})

const availableOptions = computed(() => globals.value.availableOptions)

const clickableCountries = computed(() => {
  if (!availableOptions.value || typeof availableOptions.value !== 'object') return []
  const optionValues = Object.values(availableOptions.value)
  return countries.filter((c) => optionValues.includes(c.name))
})

// Methods
function getCountryInfluence(countryName: string, side: 'us' | 'ussr'): number {
  if (!mapData.value[countryName]) return 0
  if (side === 'us') return mapData.value[countryName].us_influence || 0
  if (side === 'ussr') return mapData.value[countryName].ussr_influence || 0
  return 0
}

function getCountryControl(countryName: string): number {
  if (!mapData.value[countryName]) return 2
  return mapData.value[countryName].control
}

function countriesDataBlue(country: CountryEntry) {
  const usInf = getCountryInfluence(country.name, 'us')
  const control = getCountryControl(country.name)
  const opacity = usInf > 0 ? Math.min(0.8, 0.3 + usInf * 0.08) : 0.15
  return { ...country, ...rectConfig, fill: control === 1 ? '#1565C0' : '#42A5F5', opacity }
}

function countriesDataRed(country: CountryEntry) {
  const { name, x, y } = country
  const ussrInf = getCountryInfluence(name, 'ussr')
  const control = getCountryControl(name)
  const opacity = ussrInf > 0 ? Math.min(0.8, 0.3 + ussrInf * 0.08) : 0.15
  return { name, x: x + 99, y, ...rectConfig, fill: control === 0 ? '#B71C1C' : '#EF5350', opacity }
}

function usInfluenceText(country: CountryEntry) {
  const inf = getCountryInfluence(country.name, 'us')
  return {
    x: country.x + 25, y: country.y + 30,
    fontSize: 40, fontFamily: 'Arial', fontStyle: 'bold', fill: 'white',
    text: inf > 0 ? String(inf) : '', listening: false,
  }
}

function ussrInfluenceText(country: CountryEntry) {
  const inf = getCountryInfluence(country.name, 'ussr')
  return {
    x: country.x + 99 + 25, y: country.y + 30,
    fontSize: 40, fontFamily: 'Arial', fontStyle: 'bold', fill: 'white',
    text: inf > 0 ? String(inf) : '', listening: false,
  }
}

function highlightConfig(country: CountryEntry) {
  return {
    x: country.x - 4, y: country.y - 4,
    width: 99 * 2 + 8, height: 99 + 8,
    fill: 'transparent', stroke: '#FFD600', strokeWidth: 3, cornerRadius: 3, listening: true,
  }
}

function onCountryClick(country: CountryEntry) {
  sendMove('m ' + country.name)
}

function onCountryHover(country: CountryEntry) {
  tooltipCountry.value = country.name
  tooltipData.value = mapData.value[country.name] || null
  tooltipX.value = 10
  tooltipY.value = 10
  tooltipVisible.value = true
}

function onCountryLeave() {
  tooltipVisible.value = false
}

function controlLabel(control: number): string {
  if (control === 0) return 'USSR Control'
  if (control === 1) return 'US Control'
  return 'No Control'
}

function controlClass(control: number): string {
  if (control === 0) return 'text-ussr-light'
  if (control === 1) return 'text-us-light'
  return 'text-muted-foreground'
}

function setLimits() {
  limits.value.x = window.innerWidth - 5100 * currentScaleLevel.value
  limits.value.y = window.innerHeight * 0.7 - 3300 * currentScaleLevel.value
}

function setCurrentCoordinates({ x, y }: { x: number; y: number }) {
  if (x > 0) x = 0
  else if (x < limits.value.x) x = limits.value.x
  if (y > 0) y = 0
  else if (y < limits.value.y) y = limits.value.y
  currentX.value = x
  currentY.value = y
  return { x, y }
}

function windowResize() {
  stageSize.value.width = window.innerWidth
  stageSize.value.height = window.innerHeight
}

onMounted(() => {
  window.addEventListener('resize', windowResize)

  const stage = stageRef.value.getNode()
  const image = new Image()
  image.src = imgSrc.value!.src
  imageWidth.value = image.width
  imageHeight.value = image.height
  image.onload = () => {
    imageConfig.value.image = image
  }

  const initialScale = 0.5
  currentScaleLevel.value = initialScale
  stage.scale({ x: initialScale, y: initialScale })

  // Zoom
  stage.on('wheel', (event: any) => {
    event.evt.preventDefault()
    const oldScale = stage.scaleX()
    const pointer = stage.getPointerPosition()
    const mousePointTo = {
      x: (pointer.x - stage.x()) / oldScale,
      y: (pointer.y - stage.y()) / oldScale,
    }

    const widthLimit = window.innerWidth / imageWidth.value
    const heightLimit = window.innerHeight / imageHeight.value
    const scaleBy = 0.9
    const minScaleLimit = Math.max(widthLimit, heightLimit)
    const maxScaleLimit = 1.3

    const newScale = event.evt.deltaY > 0 ? oldScale * scaleBy : oldScale / scaleBy
    if (newScale > maxScaleLimit && event.evt.deltaY < 0) return
    if (newScale < minScaleLimit && event.evt.deltaY > 0) return

    currentScaleLevel.value = newScale
    stage.scale({ x: newScale, y: newScale })
    setLimits()

    let newPos = {
      x: pointer.x - mousePointTo.x * newScale,
      y: pointer.y - mousePointTo.y * newScale,
    }
    newPos = setCurrentCoordinates(newPos)
    stage.position(newPos)
    stage.batchDraw()
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', windowResize)
})
</script>

<template>
  <div class="relative h-full w-full">
    <v-stage ref="stageRef" :config="stageSize" class="bg-black select-none">
      <v-layer>
        <v-image :config="imageConfig" />
        <!-- US influence (blue) -->
        <v-rect
          v-for="country in countries"
          :key="country.name + 'Blue'"
          :config="countriesDataBlue(country)"
        />
        <!-- USSR influence (red) -->
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
        <!-- Clickable highlight -->
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

    <img src="@/assets/big.jpg" alt="" ref="imgSrc" class="hidden" />

    <!-- Tooltip -->
    <div
      v-if="tooltipVisible"
      class="pointer-events-none fixed z-50 min-w-[140px] rounded border border-border bg-neutral-900/95 px-3 py-2 text-xs text-neutral-200"
      :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
    >
      <div class="mb-1 text-[13px] font-bold text-white">
        {{ tooltipCountry.replace(/_/g, ' ') }}
      </div>
      <div v-if="tooltipData" class="space-y-0.5 text-[11px] leading-relaxed">
        <div>Stability: {{ tooltipData.stability }}</div>
        <div>US: {{ tooltipData.us_influence }} / USSR: {{ tooltipData.ussr_influence }}</div>
        <div v-if="tooltipData.battleground" class="font-bold text-amber-400">Battleground</div>
        <div :class="controlClass(tooltipData.control)" class="font-bold">
          {{ controlLabel(tooltipData.control) }}
        </div>
      </div>
    </div>
  </div>
</template>
