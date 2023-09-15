<template>
  <v-btn
    id="canvas-course-settings-btn"
    class="canvas-course-settings-btn"
    density="compact"
    height="auto"
    variant="text"
    @click="goToCourseSettings"
  >
    Course Settings
  </v-btn>
</template>

<script>
import Context from '@/mixins/Context.vue'
import {iframeParentLocation} from '@/utils'

export default {
  name: 'CanvasCourseSettingsLink',
  mixins: [Context],
  methods: {
    goToCourseSettings() {
      const url = `${this.config.canvasApiUrl}/courses/${this.currentUser.canvasSiteId}/settings#tab-details`
      if (this.$isInIframe) {
        iframeParentLocation(url)
      } else {
        window.location.href = url
      }
    }
  }
}
</script>

<style scoped lang="scss">
.canvas-course-settings-btn {
  font-size: 14px;
  font-weight: normal;
  margin-bottom: 3px;
  padding: 0;
  color: $primary-color;
  text-decoration: none;
  &:hover {
    cursor: pointer;
  }
  &:hover, &:focus {
    text-decoration: underline;
  }
}
</style>
