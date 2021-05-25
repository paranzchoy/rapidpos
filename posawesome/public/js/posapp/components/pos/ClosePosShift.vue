<!-- test -->
<template>
  <v-row justify="center">
      <!-- Verify username & password -->
    <v-dialog v-model="verify_user" max-width="500px">
      <v-card>
        <!-- Title -->
        <v-card-title>
          <span>POS Closing Shift</span>
          <v-spacer></v-spacer>
        </v-card-title>

        <!-- Username -->
        <v-row justify="center">
          <h4 style="color: rgb(155, 0, 0); --darkreader-inline-color:#ff6060;" data-darkreader-inline-color="">* Head Cashier or Sales manager only   </h4>
          <v-col
            cols="12"
            sm="7"
          >
          <v-text-field
              label="Username"
              v-model="inputUsername"
              clearable
              required
            ></v-text-field>
          </v-col>  
        </v-row>

        <!-- Password -->
        <v-row justify="center">
          <v-col
            cols="12"
            sm="7"
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

        <!-- Buttons -->
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_verify_dialog">Cancel</v-btn>
          <v-btn color="primary" @click="configure_modal">Verify</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Close POS Shift -->
    <!-- <v-dialog v-model="closingDialog" max-width="900px"> -->
    <v-dialog v-model="closingShiftDialog" max-width="900px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Closing POS Shift v2</span>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-container>
            <v-row>
              <v-col cols="12" class="pa-1">
                <template>
                  <v-data-table
                    :headers="headers"
                    :items="dialog_data.payment_reconciliation"
                    item-key="mode_of_payment"
                    class="elevation-1"
                    :items-per-page="itemsPerPage"
                    hide-default-footer
                  >
                    <template v-slot:item.closing_amount="props">
                      <v-edit-dialog
                        :return-value.sync="props.item.closing_amount"
                      >
                        {{ formtCurrency(props.item.closing_amount) }}
                        <template v-slot:input>
                          <v-text-field
                            v-model="props.item.closing_amount"
                            :rules="[max25chars]"
                            label="Edit"
                            single-line
                            counter
                            type="number"
                          ></v-text-field>
                        </template>
                      </v-edit-dialog>
                    </template>
                    <template v-slot:item.difference="{ item }">{{
                      (item.difference = formtCurrency(
                        item.expected_amount - item.closing_amount
                      ))
                    }}</template>
                    <template v-slot:item.opening_amount="{ item }">{{
                      formtCurrency(item.opening_amount)
                    }}</template>
                    <template v-slot:item.expected_amount="{ item }">{{
                      formtCurrency(item.expected_amount)
                    }}</template>
                  </v-data-table>
                </template>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">Close</v-btn>
          <v-btn color="primary" dark @click="submit_dialog">Submit</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    itemsPerPage: 20,
    dialog_data: {},
    verify_user: false,
    inputUsername: null,
    inputPassword: null,
    closingShiftDialog: false,
    show: false,

    headers: [
      {
        text: 'Mode of Payment',
        value: 'mode_of_payment',
        align: 'start',
        sortable: true,
      },
      {
        text: 'Opening Amount',
        align: 'end',
        sortable: true,
        value: 'opening_amount',
      },
      {
        text: 'Closing Amount',
        value: 'closing_amount',
        align: 'end',
        sortable: true,
      },
      {
        text: 'Expected Amount',
        value: 'expected_amount',
        align: 'end',
        sortable: false,
      },
      {
        text: 'Difference',
        value: 'difference',
        align: 'end',
        sortable: false,
      },
    ],
    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {},
  }),
  watch: {},
  methods: {
    close_dialog() {
        this.closingShiftDialog = false;
    },
    close_verify_dialog() {
        this.verify_user = false;
    },
    submit_dialog() {
      evntBus.$emit('submit_closing_pos', this.dialog_data);
      this.closingDialog = false;
    },
    configure_modal() {
      if (!this.inputUsername || !this.inputPassword) {
        evntBus.$emit("show_mesage", {
          text: `Please complete the required fields`,
          color: "warning",
        })
      } else {
        // if (this.inputUsername === this.user && this.inputPassword) {
        //   frappe.call({
        //     method: "posawesome.posawesome.api.custom_posapp.verify_user",
        //     args: {
        //       username: this.inputUsername,
        //       password: this.inputPassword
        //     },
        //     callback: function(r) {
        //       if(!r.exc) {
        //         callback();
        //       }
        //     }
        //   })

          this.closingShiftDialog = true;
          this.verify_user = false;
        //   this.calculate_totals();
          this.inputUsername = null;
          this.inputPassword = null;
        //  } else {
        //   evntBus.$emit("show_mesage", {
        //     text: `Username does not match. Please try again.`,
        //     color: "error",
        //   })
        // }
      }
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
  },
  created: function () {
    evntBus.$on('open_ClosingDialog2', (data) => {
      this.verify_user = true;
      this.dialog_data = data;
    });
  },
};
</script>
