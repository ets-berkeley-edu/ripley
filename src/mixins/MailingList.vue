<script>
import {mapActions} from 'pinia'
import {mapState} from 'pinia'
import {useMailingListStore} from '@/stores/mailing-list'

export default {
  name: 'MailingList',
  computed: {
    ...mapState(useMailingListStore, [
      'canvasSite',
      'mailingList',
      'updateSummary'
    ]),
  },
  methods: {
    ...mapActions(useMailingListStore, [
      'init',
      'setCanvasSite',
      'setMailingList',
      'setUpdateSummary'
    ])
  }
}
</script>
