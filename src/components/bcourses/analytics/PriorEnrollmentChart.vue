<template>
  <div class="pa-5">
    <h2 id="grade-distribution-enrollment-header">Grade Distribution by Prior Enrollment</h2>
    <div>Lorem ipsum</div>
    <select
      id="grade-distribution-enrollment-select"
      v-model="selectedCourse"
      class="my-4"
      @change="onSelectCourse"
    >
      <option :value="null">Select Prior Enrollment</option>
      <option
        v-for="(option, index) in courses"
        :id="`grade-distribution-enrollment-option-${index}`"
        :key="index"
        :value="option"
      >
        {{ option }}
      </option>
    </select>
    <highcharts :options="chartSettings"></highcharts>
  </div>
</template>
<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'

export default {
  name: 'PriorEnrollmentChart',
  components: {
    highcharts: Chart
  },
  mixins: [Context],
  props: {
    changeSeriesColor: {
      required: true,
      type: Function
    },
    chartDefaults: {
      required: true,
      type: Object
    },
    gradeDistribution: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    chartSettings: {},
    courses: [],
    selectedCourse: null
  }),
  created() {
    this.chartSettings = this.$_.cloneDeep(this.chartDefaults)
    this.courses = this.$_.keys(this.gradeDistribution)
  },
  methods: {
    onSelectCourse() {
      if (this.selectedCourse) {
        const secondarySeries = {
          data: [],
          name: this.selectedCourse
        }
        this.$_.each(this.gradeDistribution[this.selectedCourse], item => {
          secondarySeries.data.push({
            custom: {total: this.$_.get(item, 'count', 0)},
            dataLabels: {
              enabled: false
            },
            y: this.$_.get(item, 'percentage', 0)
          })
        })
        this.chartSettings.series[1] = secondarySeries
      } else if (this.chartSettings.series.length > 1) {
        this.chartSettings.series.pop()
      }
      this.changeSeriesColor(this.chartSettings)
    }
  }
}
</script>