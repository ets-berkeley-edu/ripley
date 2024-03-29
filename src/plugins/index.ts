import accessibility from 'highcharts/modules/accessibility'
import noDataToDisplay from 'highcharts/modules/no-data-to-display'
import axios from '@/plugins/axios'
import type {App} from 'vue'
import Highcharts from 'highcharts'
import vuetify from './vuetify'
import {createPinia} from 'pinia'
import {loadFonts} from './webfontloader'

export function registerPlugins (app: App) {
  accessibility(Highcharts)
  noDataToDisplay(Highcharts)
  loadFonts().then(() => {})
  app
    .use(axios, {baseUrl: import.meta.env.VITE_APP_API_BASE_URL})
    .use(createPinia())
    .use(vuetify)
}
