<template>
  <div class="template-progress-bar">
    <div v-if="percentCompleteRounded" class="template-progress-bar-container">
      <div
        class="template-progress-bar-display"
        role="progressbar"
        aria-valuemin="0"
        aria-valuemax="100"
        :aria-valuenow="percentCompleteRounded"
      >
        <div class="template-progress-bar-status">{{ percentCompleteRounded }}% Complete</div>
        <div class="template-progress-bar-value" :style="{ width: percentCompleteRounded + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    percentCompleteRounded: {
      type: Number,
      default: 0
    }
  }
}
</script>
