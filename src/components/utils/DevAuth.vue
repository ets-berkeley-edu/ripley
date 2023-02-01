<template>
  <div class="d-inline-flex">
    <v-form class="border-0" @submit="devAuth">
      <div class="p-1">
        <v-text-field
          id="basic-auth-uid"
          v-model="uid"
          aria-invalid="!!error"
          placeholder="UID"
          size="sm"
          required
        />
      </div>
      <div class="p-1">
        <v-text-field
          id="basic-auth-password"
          v-model="password"
          autocomplete="off"
          class="mb-2"
          :error-messages="error"
          placeholder="Password"
          required
          size="sm"
          type="password"
        />
        <div class="pt-2">
          <v-btn
            id="basic-auth-submit-button"
            class="cc-button-blue"
            size="sm"
            variant="flat"
            @click="devAuth"
          >
            Login
          </v-btn>
        </div>
      </div>
    </v-form>
  </div>
</template>

<script>
import auth from '@/auth'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {devAuthLogIn} from '@/api/auth'

export default {
  name: 'DevAuth',
  mixins: [Context, Utils],
  data: () => ({
    error: undefined,
    uid: undefined,
    password: undefined,
    showError: false
  }),
  methods: {
    devAuth() {
      let uid = this.$_.trim(this.uid)
      let password = this.$_.trim(this.password)
      if (uid && password) {
        devAuthLogIn(uid, password).then(
          data => {
            if (data.isLoggedIn) {
              auth.initSession().then(() => {
                this.alertScreenReader('You are logged in.')
                this.$router.push({path: '/'})
              })
            } else {
              const message = this.$_.get(data, 'response.data.error') || this.$_.get(data, 'response.data.message') || this.$_.get(data, 'message') || 'Authentication failed'
              this.reportError(message)
            }
          },
          error => {
            this.reportError(error)
          }
        )
      } else if (uid) {
        this.reportError('Password required')
      } else {
        this.reportError('Both UID and password are required', 'basic-auth-password')
      }
    },
    reportError(message, putFocus='basic-auth-uid') {
      this.error = message
      this.alertScreenReader(message)
      this.$putFocusNextTick(putFocus)
    }
  }
}
</script>