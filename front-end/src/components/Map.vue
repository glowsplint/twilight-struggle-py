<template>
  <div>
    <v-stage ref="stage" :config="stageSize" id="stage">
      <v-layer ref="baseLayer">
        <v-image ref="image" :config="imageConfig" />
        <v-rect
          v-for="country in countries"
          :key="country.name + 'Blue'"
          :config="countriesDataBlue(country)"
        />
        <v-rect
          v-for="country in countries"
          :key="country.name + 'Red'"
          :config="countriesDataRed(country)"
        />
        <v-text
          v-for="country in countries"
          :key="country.name + 'US'"
          :config="influenceConfig()"
        />
      </v-layer>
    </v-stage>
    <img src="@/assets/big.jpg" alt="Twilight Map" ref="imgSrc" id="source" />
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

      // Looks ahead to proposed scale level and rejects if past limits
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
        // console.log(this.currentScaleLevel)
        stage.position(newPos)
        stage.batchDraw()
      }
    })

    // this shows where on the IMAGE we are clicking (adjusted for zoom/pan)
    stage.on('click', (event) => {
      // const pointer = stage.getPointerPosition()
      const pointer = { x: 0, y: 0 }
      pointer.x =
        (this.currentX - stage.getPointerPosition().x) / this.currentScaleLevel
      pointer.y =
        (this.currentY - stage.getPointerPosition().y) / this.currentScaleLevel

      // console.log(`x: ${-pointer.x.toFixed(0)}, y: ${-pointer.y.toFixed(0)},`) // Prints location of click on image in original pixel units
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
          // console.log(newPos.x.toFixed(0), newPos.y.toFixed(0))
          return newPos
        },
      },
      rectConfig: {
        sides: 4,
        width: 99,
        height: 99,
      },
      countries: countryData,
    }
  },
  computed: {
    moreComputed() {
      return null
    },
    ...mapState({
      gameInProgress: (state) => state.locals.gameInProgress,
      replayInProgress: (state) => state.locals.replayInProgress,
    }),
  },
  methods: {
    countriesDataBlue(country) {
      return { ...country, ...this.rectConfig, fill: 'blue' }
    },
    countriesDataRed(country) {
      let { name, x, y, opacity } = country
      x += 99
      const redCountry = { name: name, x: x, y: y, opacity: opacity }
      return { ...redCountry, ...this.rectConfig, fill: 'red' }
    },
    influenceConfig() {
      return { fontSize: 30, fontFamily: 'Calibri', text: '' }
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
  width: 100vw;
  height: 70vh;
  overflow: hidden;
  background: black;
  user-select: none;
}
</style>
