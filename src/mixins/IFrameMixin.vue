<script>
export default {
  name: 'IFrameMixin',
  data: () => ({
    isInIframe: false,
  }),
  methods: {
    iframeParentLocation(location) {
      if (this.isInIframe) {
        const message = JSON.stringify(
          {
            subject: 'changeParent',
            parentLocation: location
          }
        )
        this.iframePostMessage(message)
      }
    },
    iframePostMessage(message) {
      if (window.parent) {
        window.parent.postMessage(message, '*')
      }
    },
    iframeScrollToTop() {
      if (this.isInIframe) {
        const message = JSON.stringify(
          {
            subject: 'changeParent',
            scrollToTop: true
          }
        )
        this.iframePostMessage(message)
      } else {
        window.scrollTo(0, 0)
      }
    }
  },
  created() {
    this.isInIframe = !!window.parent.frames.length
  }
}
</script>
