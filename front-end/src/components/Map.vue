<template>
  <div>
    <v-stage ref="stage" :config="stageSize" id="stage">
      <v-layer ref="layer">
        <v-image ref="image" :config="imageConfig" />
      </v-layer>
    </v-stage>
    <img src="@/assets/big.jpg" alt="Twilight Map" ref="imgSrc" id="source" />
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

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
    const layer = this.$refs.layer.getNode()
    const image = new Image()

    // Initialising the canvas image
    image.src = this.$refs.imgSrc.src
    this.imageWidth = image.width
    this.imageHeight = image.height
    image.onload = () => {
      this.imageConfig.image = image
    }

    let initialScaleLevel = { x: 0.5, y: 0.5 }
    stage.scale(initialScaleLevel)
    this.currentScaleLevel = 0.5

    // Zooming functionality
    let scaleBy = 0.9,
      minScaleLimit = 0.4,
      maxScaleLimit = 1.3

    stage.on('wheel', event => {
      event.evt.preventDefault()
      let oldScale = stage.scaleX()
      let pointer = stage.getPointerPosition()

      let mousePointTo = {
        x: (pointer.x - stage.x()) / oldScale,
        y: (pointer.y - stage.y()) / oldScale
      }

      if (this.currentScaleLevel > maxScaleLimit && event.evt.deltaY < 0) {
        return
      } else if (
        this.currentScaleLevel < minScaleLimit &&
        event.evt.deltaY > 0
      ) {
        return
      } else {
        let newScaleLevel =
          event.evt.deltaY > 0 ? oldScale * scaleBy : oldScale / scaleBy
        this.currentScaleLevel = newScaleLevel
        stage.scale({ x: this.currentScaleLevel, y: this.currentScaleLevel })

        this.limits.x = window.innerWidth - 5100 * this.currentScaleLevel
        this.limits.y = window.innerHeight * 0.7 - 3300 * this.currentScaleLevel

        let newPos = {
          x: pointer.x - mousePointTo.x * this.currentScaleLevel,
          y: pointer.y - mousePointTo.y * this.currentScaleLevel
        }

        if (newPos.x > 0) {
          newPos.x = 0
        } else if (newPos.x < this.limits.x) {
          newPos.x = this.limits.x
        }
        if (newPos.y > 0) {
          newPos.y = 0
        } else if (newPos.y < this.limits.y) {
          newPos.y = this.limits.y
        }

        stage.position(newPos)
        stage.batchDraw()

        console.log(
          this.currentScaleLevel.toFixed(3),
          newPos.x,
          newPos.y
          // this.limits.x.toFixed(0),
          // this.limits.y.toFixed(0)
        )
      }
    })

    layer.on('click', event => {
      console.log(
        stage.absolutePosition().x.toFixed(0),
        stage.absolutePosition().y.toFixed(0)
      )
    })
  },
  data() {
    return {
      currentScaleLevel: 1,
      clientAction: '',
      state: {},
      stageSize: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      currentX: 0,
      currentY: 0,
      limits: {
        x: window.innerWidth - 5100 * this.currentScaleLevel,
        y: window.innerHeight * 0.7 - 3300 * this.currentScaleLevel
      },
      imageWidth: 0,
      imageHeight: 0,
      imageConfig: {
        image: null,
        draggable: true,
        dragBoundFunc: pos => {
          this.limits.x = window.innerWidth - 5100 * this.currentScaleLevel
          this.limits.y =
            window.innerHeight * 0.7 - 3300 * this.currentScaleLevel
          let newX = (this.currentX =
            pos.x > 0 ? 0 : pos.x < this.limits.x ? this.limits.x : pos.x)
          let newY = (this.currentY =
            pos.y > 0 ? 0 : pos.y < this.limits.y ? this.limits.y : pos.y)
          this.$refs.stage.getNode().absolutePosition({ x: newX, y: newY })
          console.log(newX.toFixed(0), newY.toFixed(0))
          return {
            x: newX,
            y: newY
          }
        }
      }
    }
  },
  computed: {
    moreComputed() {
      return null
    },
    ...mapState({
      gameInProgress: state => state.locals.gameInProgress,
      replaceInProgress: state => state.locals.replaceInProgress
    })
  },
  methods: {
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
    }
  },
  sockets: {
    'server-move': data => {
      console.log(`Received from server: data = ${data.server_move}`)
    }
  }
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
