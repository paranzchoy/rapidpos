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
          <v-btn color="error" dark @click="close_dialog">Cancel</v-btn>
          <v-btn color="primary" @click="configure_modal">Verify</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Close POS Shift -->
    <v-dialog v-model="closingShiftDialog" max-width="900px">
      <v-card>
        <!-- Title -->
        <v-card-title>
          <span class="headline indigo--text">Closing POS Shift</span>
        </v-card-title>

        <!-- Content -->
        <v-card-text>
          <template>
            <!-- Tab titles -->
            <div class="tabs">
                <a v-on:click="activetab='1'" v-bind:class="[ activetab === '1' ? 'active' : '' ]">Details</a>
                <a v-on:click="activetab='2'" v-bind:class="[ activetab === '2' ? 'active' : '' ]">Cash</a>
                <a v-on:click="activetab='3'" v-bind:class="[ activetab === '3' ? 'active' : '' ]">Test</a>
            </div>
            <div class="content">
                <!-- TAB: Details -->
                <div v-if="activetab ==='1'" class="tabcontent">
                  <template>
                    <v-container>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Z-Counter:
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            2121
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Beginning SI No.:
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                             0000031223
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                             Ending SI No.:
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                             0000031223
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Beginning Void No.: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0000031435
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Ending Void No.: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0000031344
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Sales Count: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            324
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Void Count: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            644
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Total Transactions: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            324
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Beginning Balance: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            324, 766, 833
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Ending Balance: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            587, 874, 784
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Gross Amount: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            5,387,798,483
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Less:
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Discount: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Senior Discount:
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                             0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            PWD Discount: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Void: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Net Amount: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            5,784,763
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Cash: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            76,434,984
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Checks: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Coupons: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Gift Certificate:
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Card: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Mode of Payment Total: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            5,368,3648
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            VATable Sales: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            105.35
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            VAT Amount: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            12.36s
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            VAT Exempt Sales: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            56,374,377.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Zero-Rated Sales: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0.00
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Accumulated Grand Total:
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                             8,798,712,362.76
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Reset Counter:
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            0
                          </v-card>
                        </v-col>
                      </v-row>
                      <v-row no-gutters>
                        <v-col order="first">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            Global Transaction No.: 
                          </v-card>
                        </v-col>
                        <v-col order="last">
                          <v-card
                            class="pa-2"
                            outlined
                            tile
                          >
                            41098
                          </v-card>
                        </v-col>
                      </v-row>
                    </v-container>
                  </template>
                </div>

                <!-- TAB: Cash -->
                <div v-if="activetab ==='2'" class="tabcontent2">
                    <template>
                        <div>
                          <!-- :headers = "denomHeaders"
                            :items="pos_closing_shift_data.denominations"
                            item-key = "denom"
                            class="elevation-1"
                            :items-per-page="itemsPerPage"
                            :hide-default-footer="true"
                            v-model="pos_close" -->
                            <v-data-table
                            dense
                            :headers="denomHeaders"
                            :items="denominations"
                            :items-per-page="5"
                            class="elevation-1"
                            hide-default-footer 
                            disable-pagination
                            v-model="pos_closing_shift_data.cash_details"
                            height="373px"
                            >
                            <template v-slot:item.quantity="props">
                              <!-- <template > -->
                              <!-- <v-row justify="center">
                                <v-col
                                  
                                  sm="5"
                                  class="text-right"
                                > 
                                v-model="props.item.quantity"-->
                                <v-col
                                  sm="7"
                                >
                                <v-text-field
                                    
                                    v-model="pos_closing_shift_data.cash_details = props.item.quantity"
                                    :rules="[max25chars]"
                                    label="Edit"
                                    single-line
                                    type="number"
                                    min=0 oninput="validity.valid||(value='');"
                                    dense
                                ></v-text-field>
                                </v-col>
                                <!-- </v-col>
                              </v-row> -->
                                <!-- </template> -->
                            <!-- <v-edit-dialog
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
                            </v-edit-dialog> -->
                            </template>
                            <template v-slot:item.total="{ item }">{{
                            (item.total = 
                                item.amount * item.quantity
                            )
                            }}</template>
                            </v-data-table>
                            <!-- TESTING -->
                            <!-- <v-data-table
                              :headers="headers"
                              :items="dialog_data.payment_reconciliation"
                              item-key="mode_of_payment"
                              class="elevation-1"
                              :items-per-page="itemsPerPage"
                              hide-default-footer
                            >
                              <template v-slot:item.closing_amount="props">
                              <template v-if="props.item.mode_of_payment === 'Cash'">{{
                                (
                                  props.item.closing_amount = (totalAmount)
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
                            </v-data-table> -->
                            <!-- TESTING -->
                            <template>
                              <v-row justify="end" no-gutters class="ma-0 pa-0" height="5px">
                                <v-col
                                  cols="12"
                                  sm="9"
                                  class="text-right">
                                  Cash On Hand:
                                  <!-- <v-subheader class="text-right">Cash On Hand:</v-subheader> -->
                                </v-col>
                                <v-col
                                  cols="12"
                                  sm="3"
                                  class="text-right">
                                  {{totalAmount}}
                                <!-- <v-subheader justify="end"> {{totalAmount}} </v-subheader> -->
                                <!-- <v-text-field
                                    :value="totalAmount"
                                    outlined
                                    label="Cash On Hand"
                                    dense
                                    type="number"
                                    readonly
                                    reverse
                                ></v-text-field> -->
                                </v-col>
                                <!-- </v-row>
                                <v-row justify="end" no-gutters class="ma-0" style="height: 0%"> -->
                                  <v-col
                                  cols="12"
                                  sm="9"
                                  class="text-right">
                                  Prev. Cash Withdrawn:
                                  <!-- <v-subheader class="text-right">Prev. Cash Withdrawn:</v-subheader> -->
                                </v-col>
                                  <v-col
                                    cols="12"
                                    sm="3"
                                    class="text-right">
                                    1200
                                  <!-- <v-subheader class="text-right">1200</v-subheader> -->
                                  <!-- <v-text-field
                                      :value="1200"
                                      outlined
                                      label="Prev. Cash Withdrawn"
                                      dense
                                      type="number"
                                      readonly
                                      reverse
                                  ></v-text-field> -->
                                  </v-col>
                                <!-- </v-row>
                              <v-row justify="end" no-gutters class="ma-0" style="height: 0%"> -->
                                <v-col
                                  cols="12"
                                  sm="9"
                                  class="text-right">
                                  <!-- <v-subheader class="text-right">Total Cash:</v-subheader> -->
                                  Total Cash:
                                </v-col>
                                <v-col
                                  cols="12"
                                  sm="3"
                                  class="text-right">
                                {{totalAmount+1200}}
                                <!-- <v-subheader justify="end"> {{totalAmount+1200}} </v-subheader> -->
                                <!-- <v-text-field
                                    :value="totalAmount"
                                    label="Total Cash"
                                    outlined
                                    dense
                                    type="number"
                                    readonly
                                    reverse
                                ></v-text-field> -->
                                </v-col>
                              </v-row>
                            </template>
                        </div>
                    </template>
                </div>

                <!-- TAB: Test -->
                <div v-if="activetab ==='3'" class="tabcontent">
                  <p>Todo...</p>
                </div>
            </div>
          </template>
        </v-card-text>

        <template>
          <!-- <v-row no-gutters class="ml-5 mr-5 pa-0" style="height: 0%; margin-left: 5px;">
            <v-col cols="3">
              <v-text-field
                :value="1200"
                label="Cash"
                outlined
                dense
                readonly
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="3">
              <v-text-field
                :value="1200"
                label="Card"
                outlined
                dense
                readonly
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="3">
              <v-text-field
                :value="1200"
                label="Coupon"
                outlined
                dense
                readonly
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="3">
              <v-text-field
                :value="1200"
                label="TOTAL"
                outlined
                dense
                readonly
                hide-details
              ></v-text-field>
            </v-col>
          </v-row> -->
          <!-- TESTING -->
          <v-data-table
            :headers="headers"
            :items="dialog_data.payment_reconciliation"
            item-key="mode_of_payment"
            class="elevation-1"
            :items-per-page="itemsPerPage"
            hide-default-footer
          >
            <template v-slot:item.closing_amount="props">
            <template v-if="props.item.mode_of_payment === 'Cash'">{{
              (
                props.item.closing_amount = (totalAmount)
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
          <!-- TESTING -->
          <!-- <v-row no-gutters class="ml-5 mr-5 pa-0" style="height: 0%; margin-left: 5px;"> -->
          <v-row justify="end" no-gutters class="ma-0" style="height: 0%">
            <v-col
              cols="12"
              sm="9"
              class="text-right">
              TOTAL
            </v-col>
            <v-col
              cols="12"
              sm="3"
              class="text-right">
              1200
              <!-- <v-text-field
                :value="1200"
                label="TOTAL"
                solo
                dense
                readonly
                hide-details
                reverse
              ></v-text-field> -->
            </v-col>
          </v-row>
        </template>
        
        <!-- Buttons -->
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
    activetab: '1',
    el: '#tabs',
    closingShiftDialog: false,
    verify_user: false,
    itemsPerPage: 13,
    show: false,
    pos_closing_shift_data: {},
    cash_details: "",
    dialog_data: {},
    user: frappe.session.user,
    pos_close: '',
    pos_profile: "",
    pos_opening_shift: "",
    inputUsername: null,
    inputPassword: null,
    cash_header: [
      {
        text: 'Card Number',
        value: 'mode_of_payment',
        align: 'start',
        sortable: true,
      },
      {
        text: 'Sales Invoice #',
        align: 'center',
        sortable: true,
        value: 'opening_amount',
      },
      {
        text: 'Amount',
        value: 'closing_amount',
        align: 'end',
        sortable: true,
      },
    ],
    coupon_header: [
      {
        text: 'Coupon Number',
        value: 'mode_of_payment',
        align: 'start',
        sortable: true,
      },
      {
        text: 'Description',
        align: 'center',
        sortable: true,
        value: 'opening_amount',
      },
      {
        text: 'Amount',
        value: 'closing_amount',
        align: 'end',
        sortable: true,
      },
    ],
    denominations: [],
    cash_details_push: [],
    denomHeaders: [
      {
        text: 'DENOMINATION',
        align: 'end',
        sortable: false,
        value: 'amount',
        width: '25%',
      },
      {
        text: 'QTY',
        align: 'center',
        sortable: false,
        value: 'quantity',
        width: '50%',
      },
       {
        text: 'Total',
        align: 'end',
        sortable: false,
        value: 'total',
        width: '25%',
      },
    ],
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
    headers2: [
      {
        text: 'Mode of Payment',
        value: 'mode_of_payment',
        align: 'end',
        sortable: false,
      },
      {
        text: 'Amount',
        value: 'closing_amount',
        align: 'end',
        sortable: false,
      },
    ],
    max25chars: (v) => v.length <= 20 || 'Input too long!', // TODO : should validate as number
    pagination: {},
  }),
  watch: {},
  methods: {

    changeTab(tabIndexValue) {
      this.active_tab = tabIndexValue;
    },
    
    close_dialog() {
      this.closingShiftDialog = false;
    },

    calculate_totals() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.custom_posapp.submit_total_closing_readings',
        args: {
          opening_shift:this.pos_closing_shift.name
        },
        async: true,
        callback: function (r) {
          //do nothing
        },
      });
    },

    // GET_DENOMINATIONS METHOD: List all cash denominations
    get_denominations() {
      const vm = this;
        frappe.call({

          method: "rapidposcustom.rapidposcustom.api.rapidposcustom.get_cash_denominations_breakdown",
          // method: "posawesome.posawesome.api.custom_posapp.get_denominations",
            callback: function (r) {
          if (r.message) {
            r.message.get_denom.forEach((element) => {
              vm.denominations.push(element)
            })
          }
        },
        });
    },

    // CASH_DETAILS METHOD
    cashDetailsMethod(){
      this.denominations.forEach((element) => {
        if(element.quantity!=0){
         this.cash_details_push.push(element);
        }
      })
    },

    // calculate_totals() {
    //   const vm = this;
    //   frappe.call({
    //     method: 'posawesome.posawesome.api.posapp.submit_total_closing_readings',
    //     args: {
    //       closing_shift: this.pos_closing_shift
    //     },
    //     async: true,
    //     callback: function (r) {
    //       if (r.message) {
    //         this.pos_close = r.message;
    //       }
    //     },
    //   });
    // },

    configure_modal() {
      if (!this.inputUsername || !this.inputPassword) {
        evntBus.$emit("show_mesage", {
          text: `Please complete the required fields`,
          color: "warning",
        })
      } else {
        if (this.inputUsername === this.user && this.inputPassword) {
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

          this.closingShiftDialog = true;
          this.verify_user = false;
          this.calculate_totals();
          this.inputUsername = null;
          this.inputPassword = null;
         } else {
          evntBus.$emit("show_mesage", {
            text: `Username does not match. Please try again.`,
            color: "error",
          })
        }
      }
    },

    // SUBMIT_DIALOG METHOD: Submit POS Closing Shift data
    submit_dialog() {
      this.cashDetailsMethod();
      this.pos_closing_shift_data.cash_details = this.cash_details_push;
      const pos_closing_shift_temp = this.pos_closing_shift_data;
      console.log({pos_closing_shift_temp});
      frappe
        .call("posawesome.posawesome.doctype.pos_closing_shift.custom_pos_closing_shift.submit_closing_shift", {
          closing_shift: this.dialog_data,
          closing_cash: this.pos_closing_shift_data,
        })
        .then((r) => {
          if (r.message) {
            this.pos_closing_shift = r.message.pos_closing_shift;
            // this.load_print_page();
            evntBus.$emit("current_closing_shift", r.message);
            evntBus.$emit("show_mesage", {
              text: message,
              color: "success",
            });
            this.check_opening_entry()
          } else {
            console.log(r)
          }
        });
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
    
    OpenClosingShift(e) {
      if (e.key === 'e' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
          this.verify_user = true;
        // this.closingShiftDialog = true;
      }
    },

    check_opening_entry() {
      return frappe
        .call("posawesome.posawesome.api.posapp.check_opening_shift", {
          user: frappe.session.user,
        })
        .then((r) => {
          if (r.message) {
            this.pos_profile = r.message.pos_profile;
            this.pos_opening_shift = r.message.pos_opening_shift;
            evntBus.$emit("register_pos_profile", r.message);
            evntBus.$emit("current_opening_shift", r.message);
            evntBus.$emit("set_company", r.message.company);
            console.log("LoadPosProfile");
          } else {
            this.create_opening_voucher();
          }
        });
    },
    create_opening_voucher() {
      this.dialog = true;
    },
  },
  created: function () {
    evntBus.$on('open_ClosingDialog2', (data) => {
      this.verify_user = true;
      this.dialog_data = data;
    });

    document.addEventListener('keydown', this.OpenClosingShift.bind(this));

    this.$nextTick(function (){
      this.get_denominations();

      evntBus.$on("submit_closing_pos", (data) => {
        this.submit_closing_pos(data)
      })
    });
  },
    destroyed() {
        document.removeEventListener('keydown', this.OpenClosingShift);
    },
  computed: {
    totalAmount: function(){

      return this.denominations.reduce(function(totalSum, item){

        return totalSum + (item.amount * item.quantity);
      },0);
    },

  }
};
</script>

<style lang="scss">
/* Import Google Font */
@import url(https://fonts.googleapis.com/css?family=Nunito+Sans);

/* Style the tabs */
.tabs {
    overflow: hidden;
    margin-bottom: -2px; /* hide bottom border */
    margin-left: 24px;
}

.tabs a{
    float: left;
    cursor: pointer;
    padding: 12px 24px;
    transition: background-color 0.2s;
    border: 1px solid #ccc;
    border-right: none;
    background-color: #f1f1f1;
    border-radius: 10px 10px 0 0;
    font-weight: bold;
}
.tabs a:last-child { 
    border-right: 1px solid #ccc;
}

/* Change background color of tabs on hover */
.tabs a:hover {
    background-color: #aaa;
    color: #fff;
}

/* Styling for active tab */
.tabs a.active {
    background-color: #fff;
    color: #484848;
    border-bottom: 2px solid #fff;
    cursor: default;
}

/* Style the tab content */
.tabcontent {
    padding: 30px 50px;
    border: 1px solid #ccc;
    border-radius: 10px;
    box-shadow: 4px 4px 8px #e1e1e1
}

.tabcontent2 {
    padding: 30px 90px 10px 90px;
    border: 1px solid #ccc;
    border-radius: 10px;
    box-shadow: 4px 4px 8px #e1e1e1
}

.right-input input {
  text-align: right
}

.tabcontent td {
  padding: 0.3em 0.4em;
  color: #484848;
}
.tabcontent td.legend { 
  color: #888; 
  font-weight: bold;
  text-align: right;
}
.tabcontent .map {
  height: 173px;
  width: 220px;
  background: #D3EAFB;
  margin-left: 60px;
  border: 1px solid #ccc;
  border-radius: 10px;
}
.data { width: 120px; }
</style>