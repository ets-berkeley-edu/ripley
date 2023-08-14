<template>
  <div class="d-flex">
    <div class="pr-1">
      <v-icon icon="mdi-chevron-left" />
    </div>
    <div>
      <a
        class="template-back-link"
        :href="`${config.canvasApiUrl}/courses/${currentUser.canvasSiteId}/grades`"
        target="_top"
      >
        Back to Gradebook
      </a>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context.vue'

export default {
  name: 'BackToGradebook',
  mixins: [Context]
}
</script>
