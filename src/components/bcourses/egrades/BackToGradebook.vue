<template>
  <div class="align-center d-flex">
    <div aria-hidden="true" class="pr-1">
      <v-icon :icon="mdiChevronLeft" />
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

<script setup>
import {mdiChevronLeft} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context.vue'

export default {
  name: 'BackToGradebook',
  mixins: [Context]
}
</script>
