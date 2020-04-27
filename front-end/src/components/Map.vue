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
    image.src = this.$refs.imgSrc.src
    this.imageWidth = image.width
    this.imageHeight = image.height
    image.onload = () => {
      this.imageConfig.image = image
    }
    console.log(this.imageWidth, this.imageHeight)

    let scaleBy = 0.9
    stage.on('wheel', event => {
      event.evt.preventDefault()
      let oldScale = stage.scaleX()
      let pointer = stage.getPointerPosition()

      let mousePointTo = {
        x: (pointer.x - stage.x()) / oldScale,
        y: (pointer.y - stage.y()) / oldScale
      }
      let newScaleLevel =
        event.evt.deltaY > 0 ? oldScale * scaleBy : oldScale / scaleBy

      if (this.currentScaleLevel > 1.3 && event.evt.deltaY < 0) {
        return
      } else if (this.currentScaleLevel < 0.2 && event.evt.deltaY > 0) {
        return
      } else {
        this.currentScaleLevel = newScaleLevel
        stage.scale({ x: this.currentScaleLevel, y: this.currentScaleLevel })

        let newPos = {
          x: pointer.x - mousePointTo.x * this.currentScaleLevel,
          y: pointer.y - mousePointTo.y * this.currentScaleLevel
        }
        console.log(this.currentScaleLevel)
        stage.position(newPos)
        stage.batchDraw()
      }
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
      imageWidth: 0,
      imageHeight: 0,
      imageConfig: {
        image: null,
        draggable: true,
        dragBoundFunc: pos => {
          // dragBoundFunc: function(pos) {
          // only works with the original non-es6 function
          // console.log(this.absolutePosition(), pos)
          // pos is position of mouse relative to top left of image
          // let iw = this.absolutePosition().x - window.innerWidth
          // let ih = this.absolutePosition().y - window.innerHeight
          // console.log(
          //   this.getClientRect().width.toFixed(0), / this is the current image w/h (adjusted for zoom)
          //   this.getClientRect().height.toFixed(0),
          //   pos.x.toFixed(0),
          //   pos.y.toFixed(0)
          // )
          let xLimit = window.innerWidth - 5100 * this.currentScaleLevel // 759 and 525
          let yLimit = window.innerHeight - 225 - 3300 * this.currentScaleLevel // << use canvasWidth and height instead
          // x and y keys are current coordinates
          let newX = pos.x > 0 ? 0 : pos.x < xLimit ? xLimit : pos.x
          let newY = pos.y > 0 ? 0 : pos.y < yLimit ? yLimit : pos.y
          console.log(
            pos.x.toFixed(0),
            pos.y.toFixed(0),
            newX.toFixed(0),
            newY.toFixed(0),
            xLimit.toFixed(0),
            yLimit.toFixed(0)
          )
          return {
            // x: pos.x,
            // y: pos.y
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
      console.log(this.$refs.image)
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
