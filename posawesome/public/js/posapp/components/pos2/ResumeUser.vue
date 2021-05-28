<template>
  <v-row justify="center">
    <v-dialog v-model="idleDialog" persistent max-width="400px">
      <v-card>
        <v-card-title>
          <v-row justify="center">
            <span class="headline indigo--text"><v-icon>mdi-clock</v-icon> &nbsp;&nbsp; Enter credentials to resume</span>
          </v-row>
        </v-card-title>
        <v-card-text class="pa-0">
                <template>
                <div @mouseover="resetTimerCount">
                  <v-form>
                    <v-container>
                      
                      <v-row justify="center">
                      You've been idle for {{ timerCount }} seconds.
                      </v-row>
                      <!-- <v-row justify="center">
                        <v-col
                          cols="12"
                          sm="10"
                        >
                          <v-text-field
                            label="Username"
                            v-model="inputUsername"
                            clearable
                            required
                          ></v-text-field>
                        </v-col>
                      </v-row> -->
                      <v-row justify="center">
                        <v-col
                          cols="12"
                          sm="10"
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
                        <v-btn color="primary" dark @click="submit_dialog">
                          Resume
                        </v-btn>
                        <!-- <v-btn color="warning" dark @click="resetTimerCount">
                          Reset Timer
                        </v-btn> -->
                      </v-row>
                    </v-container>
                  </v-form>
                  </div>
                </template>
        </v-card-text>
        <v-card-actions>
          <!-- <v-spacer></v-spacer> -->
          <!-- <v-btn color="error" dark @click="close_dialog">Close</v-btn> -->
          <!-- <v-row justify="center">
          <v-btn color="primary" dark @click="submit_dialog">Resume</v-btn>
          </v-row> -->
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>


<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    idleDialog: false,
    show: false,
    itemsPerPage: 20,
    dialog_data: {},
    user: frappe.session.user, 
    
    // inputUsername: null,
    inputPassword: null,
    idleDialogOpen: false,
    timerCount: 0,
  }),
  watch: {
    // timerCount: {
    //             handler(value) {

    //                 if (value < 10) {
    //                     setTimeout(() => {
    //                         this.timerCount++;
    //                     }, 1000);
    //                 }
    //                 if (value == 10) {
    //                   this.idleDialog = true;
    //                 }

    //             },
    //             immediate: true // This ensures the watcher is triggered upon creation
    //         }
  },

  beforeMount() {
    window.addEventListener("beforeunload", this.preventNav)
    this.$once("hook:beforeDestroy", () => {
      window.removeEventListener("beforeunload", this.preventNav);
    })
  },
  beforeRouteLeave(to, from, next) {
    if (this.isIdleDialogOpen) {
      if (!window.confirm("Leave without saving?")) {
        return;
      }
    }
    next(); to(); from();
  },

  methods: {
    resetTimerCount() {
    this.timerCount = 0;
    },

    close_dialog() {
      this.idleDialog = false;
    },

    submit_dialog() {
      if (!this.inputPassword) {
        evntBus.$emit("show_mesage", {
          text: `Please type in your password`,
          color: "warning",
        })
      } else {
        if (this.inputPassword) {
          frappe.call({
            method: "posawesome.posawesome.api.custom_posapp.verify_password",
            args: {
              password: this.inputPassword
            },
            callback: function(r) {
              if(!r.exc) {
                this.exc = r.exc;
              }
            }
          })
          this.idleDialog = false;
          this.isIdleDialogOpen = false;
          // this.inputUsername = null;
          this.inputPassword = null;
          this.timerCount = 0;
          }// else {
        //   evntBus.$emit("show_mesage", {
        //     text: `Username does not match. Please try again.`,
        //     color: "error",
        //   })
        // }
      }
    },
    preventNav(event) {
      if (!this.isIdleDialogOpen) return
        event.preventDefault()
        event.returnValue = ""
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
    KeyIdle(e) {
      if (e.key === 'i' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.idleDialog = true;
        this.isIdleDialogOpen = true;
      }
    },
  },
  created: function () {
    evntBus.$on('open_IdleDialog', (data) => {
      this.idleDialog = true;
      this.isIdleDialogOpen = true;
    });
    document.addEventListener('keydown', this.KeyIdle.bind(this));
  },

  destroyed(){
    document.removeEventListener('keydown', this.KeyIdle);

  }
};
</script>
