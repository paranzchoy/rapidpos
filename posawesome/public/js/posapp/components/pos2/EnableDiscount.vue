<template>
  <v-row justify="center">
    <v-dialog v-model="enabledDiscountDialog" persistent max-width="600px">
      <v-card>
        <v-card-title>
          <v-row justify="center">
            <span class="headline indigo--text">Enter credentials to enable discount.</span>
          </v-row>
        </v-card-title>
        <v-card-text class="pa-0">
                <template>
                  <v-form>
                    <v-container>
                      <v-row justify="center">
                        <v-col
                          cols="12"
                          sm="12"
                        >
                          <v-text-field
                            label="Username"
                            v-model="inputUsername"
                            clearable
                            required
                          ></v-text-field>
                        </v-col>
                      </v-row>
                      <v-row justify="center">
                        <v-col
                          cols="12"
                          sm="12"
                        >
                          <v-text-field
                            :append-icon="show ? 'mdi-eye' : 'mdi-eye-off'"
                            :type="show ? 'text' : 'password'"
                            name="input-10-2"
                            label="Password"
                            v-model="inputPassword"
                            value=""
                            class="input-group--focused"
                            @click:append="show = !show"
                            clearable
                            counter
                            required
                            @keyup.enter="submit_dialog"
                          ></v-text-field>
                        </v-col>
                      </v-row>
                      <v-row
                        align="center"
                        justify="space-around"
                      >
                        <v-btn color="error" dark @click="close_dialog">
                          Cancel
                        </v-btn>
                        <v-btn color="primary" dark @click="submit_dialog">
                          Authenticate
                        </v-btn>
                        <!-- <input v-model="isIdleDialogOpen" type="hidden"> -->
                      </v-row>
                    </v-container>
                  </v-form>
                </template>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    enabledDiscountDialog: false,
    show: false,
    itemsPerPage: 20,
    dialog_data: {},
    user: frappe.session.user,
    inputUsername: null,
    inputPassword: null,
  }),
  watch: {},

  methods: {
    close_dialog() {
      this.enabledDiscountDialog = false;
    },

    submit_dialog() {
        // evntBus.$emit('submit_discount_authentication', this.dialog_data);
        // this.enabledDiscountDialog = false;
        if (!this.inputUsername || !this.inputPassword) {
          evntBus.$emit("show_mesage", {
            text: `Please complete all fields`,
            color: "error",
          })
        } 
        // else if (this.inputUsername == role) {
        //   evntBus.$emit("show_mesage", {
        //     text: `You are not authorized`,
        //     color: "error",
        //   })
        // } 
        else {
          frappe.call({
            method: "posawesome.posawesome.api.custom_posapp.verify_user",
            args: {
              username: this.inputUsername,
              password: this.inputPassword
            },
            callback: function(r) {
              if(!r.exc) {
                callback();
              }
            }
          })
          evntBus.$emit('submit_discount_authentication', this.dialog_data);
          this.enabledDiscountDialog = false;
          this.inputUsername = null;
          this.inputPassword = null;
        }
    },
    KeyDiscount(e) {
      if (e.key === 'F7') {
        e.preventDefault();
        this.enabledDiscountDialog = true;
      }
      if (e.key === 'd' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.enabledDiscountDialog = true;
      }
      if (e.key === 'x' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.enabledDiscountDialog = false;
      }
    },
  },
  created: function () {
    evntBus.$on('open_discount_authentication', (data) => {
      this.enabledDiscountDialog = true;
    });
    document.addEventListener('keydown', this.KeyDiscount.bind(this));
  },
};
</script>
