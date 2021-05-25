<!-- test -->
<template>
  <v-row justify="center">
    <v-dialog v-model="closingDialog" max-width="900px">
      <v-card>
        <v-card-title>
          <span class="headline indigo--text">Closing POS Shift</span>
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
                    <!-- <template v-slot:item.closing_amount="props">
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
                    </template> -->
                    <template v-slot:item.closing_amount="props">
                    <template v-if="props.item.mode_of_payment === 'Cash'">{{
                      (
                        props.item.closing_amount = formtCurrency(totalAmount)
                      )
                    }}</template>
                    <template v-else-if="props.item.mode_of_payment === 'Credit Card'">
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
                   <v-expansion-panels>
                    <v-expansion-panel
                      v-for="(item,i) in 1"
                      :key="i"
                    >
                      <v-expansion-panel-header>
                        Cash Denomination Breakdown
                      </v-expansion-panel-header>
                      <v-expansion-panel-content>
                        <template>
                          <div>
                            <v-data-table
                              :headers = "denomHeaders"
                              :items = "denominations"
                              item-key = "denom"
                              class="elevation-1"
                            >
                            <template v-slot:item.qty="props">
                              <v-edit-dialog
                                :return-value.sync="props.item.qty"
                              >
                                {{ props.item.qty }}
                                <template v-slot:input>
                                  <v-text-field
                                    v-model="props.item.qty"
                                    :rules="[max25chars]"
                                    label="Edit"
                                    single-line
                                    counter
                                    type="number"
                                  ></v-text-field>
                                </template>
                              </v-edit-dialog>
                            </template>
                            <template v-slot:item.total="{ item }">{{
                              (item.total = formtCurrency(
                                item.denom * item.qty
                              ))
                            }}</template>
                            </v-data-table>
                          </div>
                        </template>
                      </v-expansion-panel-content>
                    </v-expansion-panel>
                  </v-expansion-panels>
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
    closingDialog: false,
    itemsPerPage: 20,
    dialog_data: {},
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
      denominations: [
      {
        denom: 1000,
        qty: 0,
        total: 0,
      },
      {
        denom: 500,
        qty: 0,
        total: 0,
      },
      {
        denom: 200,
        qty: 0,
        total: 0,
      },
      {
        denom: 100,
        qty: 0,
        total: 0,
      },
      {
        denom: 50,
        qty: 0,
        total: 0,
      },
      {
        denom: 20,
        qty: 0,
        total: 0,
      },
      {
        denom: 10,
        qty: 0,
        total: 0,
      },
      {
        denom: 5,
        qty: 0,
        total: 0,
      },
      {
        denom: 1,
        qty: 0,
        total: 0,
      },
      {
        denom: 0.25,
        qty: 0,
        total: 0,
      },
      {
        denom: 0.05,
        qty: 0,
        total: 0,
      },
      {
        denom: 0.01,
        qty: 0,
        total: 0,
      },
    ],
    denomHeaders: [
      {
        text: 'DENOMINATION',
        align: 'start',
        sortable: false,
        value: 'denom',
      },
      {
        text: 'QTY',
        sortable: false,
        value: 'qty',
      },
      {
        text: 'TOTAL',
        sortable: false,
        value: 'total',
      },
    ],
    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {},
  }),
  watch: {},
  methods: {
    close_dialog() {
      this.closingDialog = false;
    },

     calculate_totals() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.submit_total_closing_readings',
        args: {
          opening_shift:this.pos_closing_shift.name
        },
        async: true,
        callback: function (r) {
          //do nothing
        },
      });
    },

    submit_dialog() {
      evntBus.$emit('submit_closing_pos', this.dialog_data);
      this.closingDialog = false;
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
  },
  created: function () {
    evntBus.$on('open_ClosingDialog', (data) => {
      this.closingDialog = true;
      this.dialog_data = data;
    });
  },
  computed: {
    totalAmount: function(){

      return this.denominations.reduce(function(totalSum, item){

        return totalSum + (item.denom * item.qty);
      },0);
    },
  }
};
</script>
