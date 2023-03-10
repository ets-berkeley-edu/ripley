import '@mdi/font/css/materialdesignicons.css'
import {createVuetify} from 'vuetify'
import {VDataTable, VDataTableVirtual} from 'vuetify/labs/VDataTable'

// @ts-ignore
import colors from 'vuetify/lib/util/colors'

export default createVuetify({
  components: {
    VDataTable,
    VDataTableVirtual
  },
  theme: {
    themes: {
      light: {
        colors: {
          info: '#dff0d8',
          primary: '#3b7ea1',
          red: colors.red.darken1,
          secondary: '#eee',
          success: '#dff0d8'
        },
      },
    },
  },
})
