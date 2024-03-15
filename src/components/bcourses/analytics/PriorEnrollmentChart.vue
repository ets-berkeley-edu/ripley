<template>
  <div class="pa-5">
    <div>
      <h2 id="grade-distribution-enrollment-header">Grade Distribution by Prior Class Enrollment</h2>
      <div>
        The grade distribution chart displays available grades at the end of the current and prior semesters.
        Search for a prerequisite course to compare side-by-side final grades of all students taking this course and
        those who have taken the prerequisite.
      </div>
      <v-row no-gutters>
        <v-col cols="12" md="4" sm="6">
          <div class="grade-dist-enroll-course-search d-flex align-center my-3">
            <v-autocomplete
              id="grade-distribution-enrollment-course-search"
              v-model="selectedCourse"
              auto-select-first
              bg-color="white"
              class="text-upper mr-2"
              density="compact"
              :disabled="isLoadingPriorEnrollments || isEmpty(get(gradeDistribution, get(selectedTerm, 'id')))"
              :error="!suppressValidation && !isEmpty(courseSearchErrors)"
              :error-messages="!suppressValidation ? courseSearchErrors : []"
              hide-details
              hide-no-data
              :items="courseSuggestions"
              label="Search Classes..."
              :loading="isSearching ? 'primary' : false"
              :menu-icon="null"
              :search="courseSearchText"
              variant="outlined"
              @blur="selectedCourse = toUpper(courseSearchText)"
              @change="suppressValidation = false"
              @update:search="text => courseSearchText = text"
            >
              <template #item="{props, item}">
                <v-list-item
                  v-bind="props"
                  class="py-0 my-0"
                  density="compact"
                  height="unset"
                  min-height="30"
                  :title="item.raw"
                  :value="item.raw"
                ></v-list-item>
              </template>
            </v-autocomplete>
            <v-btn
              id="grade-distribution-enroll-add-class-btn"
              class="font-size-13"
              color="primary"
              :disabled="!selectedCourse || isLoadingPriorEnrollments || isEmpty(get(gradeDistribution, get(selectedTerm, 'id')))"
              @click="onClickAddCourse"
            >
              Add Class
            </v-btn>
          </div>
          <div
            v-if="selectedCourse && insufficientData"
            class="grade-dist-enroll-course-search alert mb-3 px-4"
          >
            <div class="d-flex flex-no-wrap">
              <v-icon class="canvas-notice-icon mr-2" :icon="mdiAlert" />
              <span>
                No <span :class="{'demo-mode-blur': isDemoMode}">{{ courseName }}</span> {{ get(selectedTerm, 'name') }}
                students were previously enrolled in {{ selectedCourse }}.
              </span>
            </div>
          </div>
        </v-col>
        <v-col
          class="align-self-end d-flex justify-center px-2"
          cols="12"
          md="4"
          sm="6"
        >
          <v-btn
            id="grade-distribution-enrollment-show-defs-btn"
            aria-controls="grade-distribution-enrollment-definitions"
            :aria-expanded="showChartDefinitions"
            aria-haspopup="true"
            class="font-weight-medium text-no-wrap my-2"
            color="primary"
            :prepend-icon="showChartDefinitions ? mdiArrowUpCircle : mdiArrowDownCircle"
            size="large"
            variant="text"
            @click="showChartDefinitions = !showChartDefinitions"
          >
            {{ showChartDefinitions ? 'Hide' : 'Show' }} Chart Definitions
          </v-btn>
        </v-col>
      </v-row>
      <v-row class="d-flex justify-center" no-gutters>
        <ChartDefinitions id="grade-distribution-enrollment-definitions" :is-expanded="showChartDefinitions" />
      </v-row>
      <hr aria-hidden="true" class="mb-3" />
      <div class="position-relative">
        <select
          v-if="size(terms)"
          :value="get(selectedTerm, 'id')"
          class="position-absolute grade-dist-enroll-term-select"
          :disabled="isEmpty(gradeDistribution)"
          @change="onSelectTerm"
        >
          <option
            v-for="(term, index) in terms"
            :key="index"
            :value="term.id"
          >
            {{ term.name }}
          </option>
        </select>
      </div>
    </div>
    <v-overlay
      v-model="isLoadingPriorEnrollments"
      class="align-center justify-center"
      contained
      persistent
    >
      <PageLoadProgress v-if="isLoadingPriorEnrollments" color="primary" />
    </v-overlay>
    <highcharts :options="chartSettings"></highcharts>
    <v-row v-if="selectedTerm" class="d-flex justify-center">
      <v-btn
        id="grade-distribution-enrollments-show-btn"
        aria-controls="grade-distribution-enroll-table-container"
        :aria-expanded="showTable"
        aria-haspopup="true"
        class="font-weight-medium text-no-wrap my-2"
        color="primary"
        :disabled="isEmpty(get(gradeDistribution, get(selectedTerm, 'id')))"
        :prepend-icon="showTable ? mdiArrowUpCircle : mdiArrowDownCircle"
        size="large"
        variant="text"
        @click="showTable = !showTable"
      >
        {{ showTable ? 'Hide' : 'Show' }} Data Table
      </v-btn>
    </v-row>
    <v-row v-if="selectedTerm" class="d-flex justify-center">
      <v-expand-transition>
        <v-card
          v-show="showTable"
          id="grade-distribution-enroll-table-container"
          class="pb-2"
          width="700"
        >
          <table id="grade-distribution-enroll-table" class="border-0 border-t">
            <caption class="font-weight-bold font-size-16 py-3" v-html="chartSettings.title.text"></caption>
            <thead class="bg-grey-lighten-4">
              <tr>
                <th class="font-weight-bold pl-4 py-2" scope="col" rowspan="2">Grade</th>
                <template v-for="(series, index) in chartSettings.series" :key="index">
                  <th
                    class="grade-distribution-table-border font-weight-bold text-center pt-2 pb-0"
                    :class="{'demo-mode-blur': isDemoMode && index === 0}"
                    colspan="2"
                    scope="col"
                  >
                    {{ series.name }}
                  </th>
                </template>
              </tr>
              <tr>
                <template v-for="(series, index) in chartSettings.series" :key="index">
                  <th class="grade-distribution-table-border font-weight-bold pt-0" scope="col">Ratio</th>
                  <th class="text-right font-weight-bold pt-0" scope="col">Count</th>
                </template>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(grade, gradeIndex) in chartSettings.xAxis.categories"
                :id="`grade-distribution-enroll-table-row-${gradeIndex}`"
                :key="gradeIndex"
              >
                <td
                  :id="`grade-distro-enroll-table-row-${gradeIndex}-grade`"
                  class="pl-4 py-1"
                  scope="row"
                >
                  {{ grade }}
                </td>
                <template v-for="(series, index) in chartSettings.series" :key="index">
                  <td
                    :id="`grade-distro-enroll-table-row-${gradeIndex}-ratio-${index}`"
                    class="py-1"
                  >
                    {{ get(series, `data.${gradeIndex}.y`, 0) }}%
                  </td>
                  <td
                    :id="`grade-distro-enroll-table-row-${gradeIndex}-count-${index}`"
                    class="text-right py-1"
                  >
                    {{ get(series, `data.${gradeIndex}.custom.count`, 0) }}
                  </td>
                </template>
              </tr>
            </tbody>
            <tfoot>
              <tr id="grade-distribution-enroll-table-row-totals">
                <th class="pl-4 py-1" scope="row">Totals</th>
                <template v-for="(series, index) in chartSettings.series" :key="index">
                  <td
                    :id="`grade-distro-enroll-table-row-totals-ratio-${index}`"
                    class="font-weight-medium py-1"
                  >
                    {{ round(sumBy(series.data, 'y')) }}%
                  </td>
                  <td
                    :id="`grade-distro-enroll-table-row-totals-count-${index}`"
                    class="text-right font-weight-medium py-1"
                  >
                    {{ sumBy(series.data, 'custom.count') }}
                  </td>
                </template>
              </tr>
            </tfoot>
          </table>
        </v-card>
      </v-expand-transition>
    </v-row>
  </div>
</template>

<script setup>
import {mdiAlert, mdiArrowDownCircle, mdiArrowUpCircle} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import {Chart} from 'highcharts-vue'
import ChartDefinitions from '@/components/bcourses/analytics/ChartDefinitions'
import {cloneDeep, debounce, each, find, get, includes, isEmpty, round, size, sumBy, toUpper} from 'lodash'
import {getPriorEnrollmentGradeDistribution, searchCourses} from '@/api/grade-distribution'
import PageLoadProgress from '@/components/utils/PageLoadProgress.vue'

export default {
  name: 'PriorEnrollmentChart',
  components: {
    ChartDefinitions,
    highcharts: Chart,
    PageLoadProgress
  },
  mixins: [Context],
  props: {
    chartDefaults: {
      required: true,
      type: Object
    },
    colors: {
      required: true,
      type: Object
    },
    courseName: {
      required: true,
      type: String
    },
    gradeDistribution: {
      required: true,
      type: Object
    },
    isDemoMode: {
      required: false,
      type: Boolean
    },
    terms: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    chartSettings: {},
    pendingCourseSearch: undefined,
    courseSearchText: undefined,
    courseSuggestions: [],
    debouncedSearch: undefined,
    courseSearchErrors: [],
    insufficientData: false,
    isLoadingPriorEnrollments: false,
    isSearching: false,
    priorEnrollmentGradeDistribution: {},
    selectedCourse: undefined,
    selectedTerm: undefined,
    showChartDefinitions: false,
    showTable: false,
    suppressValidation: true
  }),
  computed: {
    classSize() {
      return this.selectedTerm ? get(this.gradeDistribution, `${this.selectedTerm.id}.0.classSize`) : 0
    }
  },
  watch: {
    courseSearchText(newVal, oldVal) {
      if (newVal) {
        if (newVal !== oldVal) {
          this.debouncedSearch()
        }
      }
    },
    isDemoMode() {
      this.setChartTitle()
      this.setLegendLabel()
      this.setTooltipFormatter()
    },
    selectedCourse(newVal, oldVal) {
      if (newVal !== oldVal) {
        this.insufficientData = false
      }
    }
  },
  created() {
    this.selectedTerm = get(this.terms, 0)
    this.chartSettings = cloneDeep(this.chartDefaults)
    this.chartSettings.chart.type = 'column'
    this.chartSettings.legend.enabled = this.selectedTerm && !isEmpty(get(this.gradeDistribution, this.selectedTerm.id))
    this.chartSettings.legend.useHTML = true
    this.setLegendLabel()
    this.chartSettings.legend.symbolHeight = 12
    this.chartSettings.plotOptions.series.lineWidth = 0
    this.chartSettings.plotOptions.series.states = {
      hover: {
        lineWidthPlus: 0
      }
    }
    this.chartSettings.title.widthAdjust = -200
    this.chartSettings.tooltip.distance = 12
    this.chartSettings.yAxis.labels.format = '{value}%'
    this.debouncedSearch = debounce(this.search, 300)
    this.setTooltipFormatter()
    this.loadPrimarySeries(this.colors.primary)
    this.setChartTitle()
  },
  methods: {
    get,
    getDataLabel(yVal, color) {
      if (this.chartSettings.series.length === 1) {
        const displayAboveColumn = yVal < 2
        return {
          color: displayAboveColumn ? color : 'white',
          enabled: true,
          format: '{y}%',
          style: {
            textOutline: 'none'
          },
          y: displayAboveColumn ? 2 : 22
        }
      } else {
        return {
          enabled: false
        }
      }
    },
    isEmpty,
    loadPrimarySeries(color, showLabels=true) {
      this.chartSettings.series[0] = {
        color: color,
        name: `${get(this.selectedTerm, 'name')} ${this.courseName}`,
        data: []
      }
      this.chartSettings.xAxis.categories = []
      each(this.gradeDistribution[get(this.selectedTerm, 'id')], item => {
        this.chartSettings.series[0].data.push({
          color: color,
          custom: {
            count: item.count
          },
          dataLabels: showLabels ? this.getDataLabel(item.y, color) : {enabled: false},
          y: item.percentage
        })
        this.chartSettings.xAxis.categories.push(item.grade)
      })
      this.chartSettings.plotOptions.series.dataLabels = {
        enabled: showLabels
      }
    },
    loadPriorEnrollments() {
      const gradesWithPriorEnroll = {
        color: this.colors.secondary,
        data: [],
        name: `Have taken ${this.selectedCourse}`,
        type: 'column'
      }
      each(this.priorEnrollmentGradeDistribution[get(this.selectedTerm, 'id')], item => {
        if (includes(this.chartSettings.xAxis.categories, item.grade )) {
          gradesWithPriorEnroll.data.push({
            custom: {
              count: get(item, 'priorEnrollCount', 0)
            },
            dataLabels: {enabled: false},
            y: get(item, 'priorEnrollPercentage', 0)
          })
        }
      })
      this.chartSettings.series[1] = gradesWithPriorEnroll
    },
    onClickAddCourse() {
      if (this.selectedCourse) {
        this.isLoadingPriorEnrollments = true
        getPriorEnrollmentGradeDistribution(this.currentUser.canvasSiteId, this.selectedCourse).then(response => {
          this.courseSearchText = null
          this.priorEnrollmentGradeDistribution = response
          this.isLoadingPriorEnrollments = false
          this.refresh()
        })
      }
    },
    onSelectTerm(e) {
      const termId = e.target.value
      this.selectedTerm = find(this.terms, {'id': termId})
      this.refresh()
    },
    refresh() {
      if (get(this.priorEnrollmentGradeDistribution, get(this.selectedTerm, 'id'))) {
        this.loadPrimarySeries(this.colors.primary, false)
        this.loadPriorEnrollments()
        this.insufficientData = false
      } else {
        this.chartSettings.series = []
        this.loadPrimarySeries(this.colors.primary)
        this.insufficientData = true
      }
      this.setChartTitle()
    },
    round,
    search() {
      this.isSearching = true
      if (this.pendingCourseSearch) {
        this.pendingCourseSearch.abort()
      }
      this.pendingCourseSearch = new AbortController()
      searchCourses(toUpper(this.courseSearchText), this.pendingCourseSearch).then(response => {
        this.courseSuggestions = response.results
        this.isSearching = false
      }).catch(() => {
        this.$nextTick(() => this.isSearching = false)
      })
    },
    setChartTitle() {
      if (size(this.chartSettings.series) > 1) {
        this.chartSettings.title.useHTML = true
        this.chartSettings.title.text = `Relation of <span ${this.isDemoMode ? 'class="demo-mode-blur"' : ''}>
          ${this.selectedTerm.name} ${this.courseName}
          </span> Students Who Have Taken ${this.selectedCourse} to Overall Class`
      } else {
        this.chartSettings.title.useHTML = false
        this.chartSettings.title.text = `Overall Class Grade Distribution&mdash;${this.selectedTerm.name}`
      }
    },
    setLegendLabel() {
      this.chartSettings.legend.labelFormat = `{#if (eq index 0)}<span ${this.isDemoMode ? 'class="demo-mode-blur"' : ''}>{else}<span>{/if}
          {name}
        </span> grades`
    },
    setTooltipFormatter() {
      const courseName = this.courseName
      const isDemoMode = this.isDemoMode
      this.chartSettings.tooltip.formatter = function () {
        const header = `<div id="grade-dist-enroll-tooltip-grade" class="font-weight-bold font-size-15">${this.x} Grade</div>
            <div id="grade-dist-enroll-tooltip-course" class="font-size-13 text-grey-darken-1">
              <span aria-hidden="true" class="grade-dist-enroll-tooltip-symbol" style="color:${this.color}">\u25A0</span>
              <span ${isDemoMode ? 'class="demo-mode-blur"' : ''}>${courseName}</span>
            </div>
            <div class="font-size-13 mb-2">
              Ratio of class: <span id="grade-dist-enroll-tooltip-series-0-value" class="font-weight-bold">${this.point.y}%</span>
            </div>
            <hr aria-hidden="true" class="mb-2 ${size(this.points) <= 1 ? 'd-none' : ''}" />`
        return (this.points.slice(1) || []).reduce((tooltipText, plot, index) => {
          return`${tooltipText}<div id="grade-dist-enroll-tooltip-series-${index + 1}" class="font-size-13 pb-2">
            <div class="text-grey-darken-1 text-uppercase">
              <span aria-hidden="true" class="grade-dist-enroll-tooltip-symbol" style="color:${plot.color}">\u25A0</span>
              ${plot.series.name}
            </div
            <div>
              Ratio of class: <span id="grade-dist-enroll-tooltip-series-${index + 1}-value" class="font-weight-bold">${plot.y}%</span>
            </div>
          </div>`
        }, header)
      }
    },
    size,
    sumBy,
    toUpper
  }
}
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type  -->
<style lang="scss">
.grade-dist-enroll-tooltip-symbol {
  display: inline-block;
  font-size: 20px !important;
  line-height: 1.1px;
  position: relative;
  top: 1px;
  width: 16px;
}
.v-autocomplete.text-upper input {
  text-transform: uppercase !important;
}
</style>

<style lang="scss" scoped>
.grade-dist-enroll-course-search {
  min-width: 240px;
}
.grade-dist-enroll-term-select {
  right: 0;
  top: 5px;
  z-index: 100;
}
</style>
