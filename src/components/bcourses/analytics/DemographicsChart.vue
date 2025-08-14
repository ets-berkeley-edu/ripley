<template>
  <div class="grade-distribution-demographics pa-5">
    <h2 id="grade-distribution-demographics-header">Grade Average by Demographics</h2>
    <div>
      The grade average chart displays the class average grade point equivalent at the end of the current
      and prior semesters. Select a demographic to compare average grade point trends.
    </div>
    <v-row no-gutters>
      <v-col
        class="pr-4"
        cols="12"
        md="4"
        sm="6"
      >
        <select
          id="grade-distribution-demographics-select"
          v-model="selectedDemographic"
          class="grade-distribution-demographics-select justify-center w-100 mt-4"
          :disabled="!size(gradeDistribution)"
          @change="loadSecondarySeries"
        >
          <option :value="null">Select Demographic</option>
          <template v-for="(group, key) in demographicOptions" :key="key">
            <option
              :id="`grade-distribution-demographics-option-${key}`"
              :disabled="!size(group.options) || (!config.newtShowOtherGender && key === 'genders.other')"
              :value="{'group': key, 'option': get(group.options, 0)}"
            >
              {{ group.label }}
              <span v-if="!key.startsWith('divider') && !size(group.options)"> - No Data Available</span>
            </option>
          </template>
        </select>
        <select
          id="grade-distribution-statistic-select"
          v-model="selectedStatistic"
          class="grade-distribution-demographics-select justify-center w-100 mt-2 mb-4"
          :disabled="!size(gradeDistribution)"
          @change="onSelectStatistic"
        >
          <option id="grade-distribution-statistic-select-mean" value="mean" selected>Mean Grade Values</option>
          <option id="grade-distribution-statistic-select-mean-error" value="mean-error" selected>Mean Grade Values With Error Bars</option>
          <option id="grade-distribution-statistic-select-median" value="median">Median Grade Values</option>
        </select>
      </v-col>
      <v-col
        class="align-self-end d-flex justify-center px-2"
        cols="12"
        md="4"
        sm="6"
      >
        <v-btn
          id="grade-distribution-demographics-show-defs-btn"
          aria-controls="grade-distribution-demographics-definitions"
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
      <ChartDefinitions id="grade-distribution-demographics-definitions" :is-expanded="showChartDefinitions" :show-demographics="true" />
    </v-row>
    <hr aria-hidden="true" class="mb-3">
    <Chart ref="chartComponent" :options="chartOptions" />
    <v-row class="d-flex justify-center">
      <v-btn
        id="grade-distribution-demographics-show-btn"
        aria-controls="grade-distribution-demo-table-container"
        :aria-expanded="showTable"
        aria-haspopup="true"
        class="font-weight-medium text-no-wrap my-2"
        color="primary"
        :disabled="!size(gradeDistribution)"
        :prepend-icon="showTable ? mdiArrowUpCircle : mdiArrowDownCircle"
        size="large"
        variant="text"
        @click="showTable = !showTable"
      >
        {{ showTable ? 'Hide' : 'Show' }} Data Table
      </v-btn>
    </v-row>
    <v-row class="d-flex justify-center">
      <v-expand-transition>
        <v-card
          v-show="showTable"
          id="grade-distribution-demo-table-container"
          class="pb-2"
          width="700"
        >
          <table id="grade-distribution-demo-table" class="border-0 border-t">
            <caption class="font-weight-bold font-size-16 py-3">Class Grade Average by Semester</caption>
            <thead class="bg-grey-lighten-4">
              <tr>
                <th class="font-weight-bold pl-4 py-2" scope="col">Semester</th>
                <th class="grade-distribution-table-border font-weight-bold py-2" scope="col">Class Grade {{ capitalize(selectedStatistic.split('-')[0]) }}</th>
                <th class="text-right font-weight-bold py-2" scope="col">Class Grade Count</th>
                <th
                  v-if="size(chartOptions.series) > 3"
                  class="grade-distribution-table-border font-weight-bold py-2"
                  scope="col"
                >
                  {{ selectedDemographicLabel }} Grade {{ capitalize(selectedStatistic.split('-')[0]) }}
                </th>
                <th
                  v-if="size(chartOptions.series) > 3"
                  class="text-right font-weight-bold py-2"
                  scope="col"
                >
                  {{ selectedDemographicLabel }} Grade Count
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(term, index) in chartOptions.xAxis[0].categories"
                :id="`grade-distribution-demo-table-row-${index}`"
                :key="index"
              >
                <td
                  :id="`grade-distro-demo-table-row-${index}-term`"
                  class="text-no-wrap pl-4 py-1"
                  scope="row"
                >
                  {{ gradeDistribution[index].termName }}
                </td>
                <td :id="`grade-distro-demo-table-row-${index}-grade-0`" class="py-1">
                  {{ get(chartOptions, `series[0].data[${index}].y`) }}
                </td>
                <td :id="`grade-distro-demo-table-row-${index}-count-0`" class="text-right py-1">
                  {{ get(chartOptions, `series[0].data[${index}].custom.count`) }}
                </td>
                <td
                  v-if="size(chartOptions.series) > 3"
                  :id="`grade-distro-demo-table-row-${index}-grade-1`"
                  class="py-1"
                >
                  <em v-if="get(chartOptions, `series[3].data[${index}].custom.count`) === 'Small sample size'">
                    {{ get(chartOptions, `series[3].data[${index}].y`) }}
                  </em>
                  <span v-if="get(chartOptions, `series[3].data[${index}].custom.count`) !== 'Small sample size'">
                    {{ get(chartOptions, `series[3].data[${index}].y`) || 'No data' }}
                  </span>
                </td>
                <td
                  v-if="size(chartOptions.series) > 3"
                  :id="`grade-distro-demo-table-row-${index}-count-1`"
                  class="text-right py-1"
                >
                  <em v-if="get(chartOptions, `series[3].data[${index}].custom.count`) === 'Small sample size'">
                    Small sample size
                  </em>
                  <span v-if="get(chartOptions, `series[3].data[${index}].custom.count`) !== 'Small sample size'">
                    {{ get(chartOptions, `series[3].data[${index}].custom.count`) || 'No data' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </v-card>
      </v-expand-transition>
    </v-row>
  </div>
</template>

<script lang="ts" setup>
import Highcharts from 'highcharts'
import {mdiArrowDownCircle, mdiArrowUpCircle} from '@mdi/js'
import ChartDefinitions from '@/components/bcourses/analytics/ChartDefinitions.vue'
import {Chart} from 'highcharts-vue'
import {capitalize, cloneDeep, each, get, isNil, merge, round, size} from 'lodash'
import {
  CHART_COLORS,
  DEFAULT_SERIES_LINE_COLOR,
  SeriesAreaOptions,
  SeriesLineOptions,
  SeriesMarker,
  getDefaultChartOptions
} from '@/lib/highcharts'
import {computed, onMounted, ref, watch} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
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
  }
})

const chartComponent = ref()
const chartOptions = ref(merge(
  getDefaultChartOptions(),
  {
    chart: {
      type: 'line'
    },
    legend: {
      symbolHeight: 3,
      squareSymbol: false
    },
    plotOptions: {
      series: {
        lineWidth: 3
      }
    },
    title: {
      text: 'Class Grade Average by Semester'
    },
    tooltip: {
      distance: 20
    }
  }
))
const config = useContextStore().config
const demographicOptions = ref({
  divider1: {
    label: '─────',
    options: []
  },
  'genders.female': {
    label: 'Female Students',
    options: []
  },
  'genders.male': {
    label: 'Male Students',
    options: []
  },
  'genders.other': {
    label: 'Gender: Decline to State, Different Identity, or Genderqueer/Gender Non-Conform',
    options: []
  },
  divider2: {
    label: '─────',
    options: []
  },
  underrepresentedMinorityStatus: {
    label: 'Underrepresented Minority Students',
    options: []
  },
  internationalStatus: {
    label: 'International Students',
    options: []
  },
  transferStatus: {
    label: 'Transfer Students',
    options: []
  },
  athleteStatus: {
    label: 'Student Athletes',
    options: []
  }
})
const selectedDemographic = ref(null)
const selectedDemographicLabel = computed(() => {
  const group = get(selectedDemographic.value, 'group')
  const option = group && get(demographicOptions.value, group)
  return get(option, 'label')
})
const selectedStatistic = ref('mean')
const showChartDefinitions = ref(false)
const showTable = ref(false)

watch(() => props.isDemoMode, () => {
  setTooltipFormatter()
})

onMounted(() => {
  chartOptions.value.yAxis = [chartOptions.value.yAxis[0], cloneDeep(chartOptions.value.yAxis[0])]
  chartOptions.value.yAxis[0].labels.format = '{value:.1f}'
  chartOptions.value.yAxis[0].max = 4
  chartOptions.value.yAxis[0].min = 0
  chartOptions.value.yAxis[0].tickInterval = 1
  chartOptions.value.yAxis[1].min = 0
  chartOptions.value.yAxis[1].opposite = true
  collectDemographicOptions()
  setTooltipFormatter()
  loadPrimarySeries()
  if (chartComponent.value.chart.xAxis[0].width / chartOptions.value.xAxis[0].categories.length < 75) {
    chartOptions.value.xAxis[0].labels.rotation = -45
  }
})

const collectDemographicOptions = () => {
  each(props.gradeDistribution, item => {
    each(item, (values, category) => {
      let option = get(demographicOptions.value, category)
      if (get(values, 'true') && option && !size(option['options'])) {
        option['options'] = ['true']
      } else if (category === 'genders') {
        each(values, (vals, subcategory) => {
          if (!vals) return
          option = get(demographicOptions.value, `${category}.${subcategory}`)
          if (option && !size(option['options'])) {
            option['options'] = ['true']
          }
        })
      } else if (category === 'majors') {
        each(values, (vals, subcategory) => {
          if (!vals) return
          if (!demographicOptions.value['divider3']) {
            demographicOptions.value['divider3'] = {
              label: '─────',
              options: []
            }
          }
          demographicOptions.value[`majors.${subcategory}`] = {
            label: subcategory,
            options: ['true']
          }
        })
      }
    })
  })
}

const getSeriesMarker = (lineColor: string | undefined): SeriesMarker => {
  return {
    fillColor: 'white',
    lineColor: lineColor || DEFAULT_SERIES_LINE_COLOR,
    lineWidth: 3,
    radius: 5,
    symbol: 'circle'
  }
}

const loadPrimarySeries = () => {
  const displayStatistic = selectedStatistic.value.split('-')[0]
  chartOptions.value.colors = [CHART_COLORS.primary, CHART_COLORS.secondary]
  chartOptions.value.legend.enabled = !!size(props.gradeDistribution)
  const primaryGradeSeries: SeriesLineOptions = {
    color: CHART_COLORS.primary,
    data: [],
    legendSymbol: 'rectangle',
    marker: getSeriesMarker(get(chartOptions.value, 'series[0].color')),
    name: `Overall Class ${capitalize(displayStatistic)} Grade`,
    type: 'line',
    zIndex: 1
  }
  const primaryErrorSeries = {
    color: CHART_COLORS.primary,
    data: [],
    name: 'Overall Class Error',
    type: 'errorbar',
    visible: selectedStatistic.value === 'mean-error',
    yAxis: 0,
    zIndex: 1
  }
  const primaryPopulationSeries: SeriesAreaOptions = {
    data: [],
    color: CHART_COLORS.tertiary,
    name: 'Class Grade Count',
    type: 'area',
    yAxis: 1,
    zIndex: 0
  }
  const xAxisCategories: string[] = []
  let maxCount = 0
  each(props.gradeDistribution, item => {
    primaryGradeSeries.data.push({
      color: CHART_COLORS.primary,
      custom: {
        count: item.count,
        error: get(item, 'errorGradePoints'),
      },
      y: round(get(item, `${displayStatistic}GradePoints`), 1)
    })
    primaryErrorSeries.data.push([
      round(get(item, 'meanGradePoints') - get(item, 'errorGradePoints'), 1),
      round(get(item, 'meanGradePoints') + get(item, 'errorGradePoints'), 1)
    ])
    primaryPopulationSeries.data.push({
      color: CHART_COLORS.tertiary,
      y: item.count
    })
    if (item.count > maxCount) {
      maxCount = item.count
    }
    xAxisCategories.push(shortTermName(item.termName))
  })
  chartOptions.value.xAxis[0].categories = xAxisCategories
  chartOptions.value.yAxis[1].max = maxCount * 1.25
  chartOptions.value.series[0] = primaryGradeSeries
  chartOptions.value.series[1] = primaryPopulationSeries
  chartOptions.value.series[2] = primaryErrorSeries
}

const loadSecondarySeries = () => {
  if (selectedDemographic.value) {
    const displayStatistic = selectedStatistic.value.split('-')[0]
    const group = get(selectedDemographic.value, 'group')
    const option = get(selectedDemographic.value, 'option')
    const secondaryGradeSeries: SeriesLineOptions = {
      color: CHART_COLORS.secondary,
      data: [],
      legendSymbol: 'rectangle',
      marker: getSeriesMarker(CHART_COLORS.secondary),
      name: `${selectedDemographicLabel.value} ${capitalize(displayStatistic)} Grade`,
      type: 'line',
      zIndex: 3
    }
    const secondaryErrorSeries = {
      color: CHART_COLORS.secondary,
      data: [],
      name: `${selectedDemographicLabel.value} Error`,
      showInLegend: false,
      type: selectedStatistic.value === 'mean-error' ? 'errorbar' : 'line',
      visible: selectedStatistic.value === 'mean-error',
      yaxis: 0,
      zIndex: 3
    }
    const secondaryPopulationSeries: SeriesAreaOptions = {
      color: CHART_COLORS.quaternary,
      data: [],
      name: `${selectedDemographicLabel.value} Grade Count`,
      type: 'area',
      yAxis: 1,
      zIndex: 2
    }
    each(props.gradeDistribution, item => {
      const value = get(item, `${group}.${option}`) || get(item, `${group}`)
      const count = get(value, 'count', 0)
      const point: Highcharts.PointOptionsObject = {
        custom: {
          count: isNil(count) ? 'Small sample size' : count,
          error: isNil(count) ? null : get(value, 'errorGradePoints')
        },
        dataLabels: {
          enabled: false
        },
        marker: {
          lineWidth: isNil(count) ? 1 : 3,
          radius: isNil(count) ? 3 : 5
        },
        y: (value && count !== 0) ? round(get(value, `${displayStatistic}GradePoints`), 1) : null
      }
      secondaryGradeSeries.data.push(point)
      if (selectedStatistic.value === 'mean-error') {
        secondaryErrorSeries.data.push([
          round(get(value, 'meanGradePoints') - get(value, 'errorGradePoints'), 1),
          round(get(value, 'meanGradePoints') + get(value, 'errorGradePoints'), 1)
        ])
      }
      secondaryPopulationSeries.data.push({
        color: CHART_COLORS.quaternary,
        y: (value && count !== 0) ? count : null
      })
    })
    chartOptions.value.series[3] = secondaryGradeSeries
    chartOptions.value.series[4] = secondaryPopulationSeries
    chartOptions.value.series[5] = secondaryErrorSeries
  } else if (chartOptions.value.series.length > 3) {
    chartOptions.value.series = [
      chartOptions.value.series[0],
      chartOptions.value.series[1],
      chartOptions.value.series[2]
    ]
  }
}

const onSelectStatistic = () => {
  loadPrimarySeries()
  loadSecondarySeries()
}

const setTooltipFormatter = () => {
  const courseName = props.courseName
  const isDemoMode = props.isDemoMode
  chartOptions.value.tooltip.formatter = function () {
    const header = `<div id="grade-dist-demo-tooltip-term" class="font-weight-bold font-size-15">${this.x}</div>
        <div id="grade-dist-demo-tooltip-course" class="font-size-13 text-grey-darken-1 ${isDemoMode ? 'demo-mode-blur' : ''}">${courseName}</div>
        <hr aria-hidden="true" class="mt-1 grade-dist-tooltip-hr" />`
    return (this.points || []).reduce((tooltipText, point, index) => {
      if (point.series.name.includes('Grade Count') || point.series.name.includes('Error')) {
        return tooltipText
      }
      let errorNotation = ''
      if (selectedStatistic.value === 'mean-error') {
        errorNotation = `± ${get(point, 'point.custom.error')}`
      }
      return `${tooltipText}<div id="grade-dist-demo-tooltip-series-${index}" class="font-size-13 mt-1">
        <span aria-hidden="true" class="font-size-16" style="color:${point.color}">\u25AC</span>
        ${point.series.name}: <span class="font-weight-bold">${point.y}</span> ${errorNotation}
        (${get(point, 'point.custom.count') === 'Small sample size' ? 'Small sample size' : get(point, 'point.custom.count') + ' students' })
      </div>`
    }, header)
  }
}

const shortTermName = (termName: string): string => {
  const [season, year] = termName.split(' ')
  return `${season.substring(0,2).toUpperCase()}${year.substring(2,4)}`
}
</script>

<!-- eslint-disable-next-line vue-scoped-css/enforce-style-type  -->
<style lang="scss">
.grade-distribution-demographics .highcharts-legend .highcharts-point {
  y: 12;
}
</style>

<style scoped>
.grade-distribution-demographics-select {
  min-width: 180px;
}
</style>
