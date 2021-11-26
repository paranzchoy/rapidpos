<template>
  <div>
    <v-card
      style="max-height: 65vh; height: 65vh"
      class="cards my-0 py-0 grey lighten-5"
    >
      <Customer></Customer>
      <div class="my-0 py-0 overflow-y-auto" style="max-height: 55vh">
        <template @mouseover="style = 'cursor: pointer'">
          <v-data-table
            :headers="items_headers"
            :items="items"
            :single-expand="singleExpand"
            :expanded.sync="expanded"
            show-expand
            item-key="item_id"
            class="elevation-1"
            :items-per-page="itemsPerPage"
            hide-default-footer
          >
            <template v-slot:item.sub_items="{ item }">
              <v-btn
                v-if="item.is_parent_item == 1"
                small
                color="warning"
                depressed
                @click="manage_subitems_dialog(item)"
              >
                <v-icon>mdi-format-list-bulleted-square</v-icon>
              </v-btn>
            </template>
            <template v-slot:item.qty="{ item }">{{
              formtCurrency(item.qty)
            }}</template>
            <template v-slot:item.rate="{ item }">{{
              formtCurrency(item.rate)
            }}</template>
            <template v-slot:item.amount="{ item }">{{
              formtCurrency(item.qty * item.rate)
            }}</template>

            <template v-slot:expanded-item="{ headers, item }">
              <td :colspan="headers.length" class="ma-0 pa-0">
                <v-row class="ma-0 pa-0">
                  <v-col cols="1">
                    <v-btn icon color="red" @click.stop="remove_item(item)">
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </v-col>
                  <v-spacer></v-spacer>
                  <v-col cols="1">
                    <v-btn
                      icon
                      color="indigo lighten-1"
                      @click.stop="subtract_one(item)"
                    >
                      <v-icon>mdi-minus-circle-outline</v-icon>
                    </v-btn>
                  </v-col>
                  <v-col cols="1">
                    <v-btn
                      icon
                      color="indigo lighten-1"
                      @click.stop="add_one(item)"
                    >
                      <v-icon>mdi-plus-circle-outline</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
                <v-row class="ma-0 pa-0">
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Item Code"
                      background-color="white"
                      hide-details
                      v-model="item.item_code"
                      disabled
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="QTY"
                      background-color="white"
                      hide-details
                      v-model.number="item.qty"
                      type="number"
                      @change="calc_sotck_gty(item, $event)"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-select
                      dense
                      background-color="white"
                      label="UOM"
                      v-model="item.uom"
                      :items="item.item_uoms"
                      outlined
                      item-text="uom"
                      item-value="uom"
                      hide-details
                      @change="calc_uom(item, $event)"
                      :disabled="!!invoice_doc.is_return"
                    >
                    </v-select>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Rate"
                      background-color="white"
                      hide-details
                      v-model.number="item.rate"
                      type="number"
                      :prefix="invoice_doc.currency"
                      @change="calc_prices(item, $event)"
                      id="rate"
                      :disabled="
                        item.pricing_rules ||
                        !pos_profile.posa_allow_user_to_edit_rate
                          ? true
                          : false || !!invoice_doc.is_return
                      "
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Discount Percentage"
                      background-color="white"
                      hide-details
                      v-model.number="item.discount_percentage"
                      type="number"
                      @change="calc_prices(item, $event)"
                      id="discount_percentage"
                      :disabled="
                        item.pricing_rules ||
                        !pos_profile.posa_allow_user_to_edit_item_discount
                          ? true
                          : false || !!invoice_doc.is_return
                      "
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Discount Amount"
                      background-color="white"
                      hide-details
                      v-model.number="item.discount_amount"
                      type="number"
                      :prefix="invoice_doc.currency"
                      @change="calc_prices(item, $event)"
                      id="discount_amount"
                      :disabled="
                        item.pricing_rules ||
                        !pos_profile.posa_allow_user_to_edit_item_discount
                          ? true
                          : false || !!invoice_doc.is_return
                      "
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Price list Rate"
                      background-color="white"
                      hide-details
                      v-model="item.price_list_rate"
                      type="number"
                      disabled
                      :prefix="invoice_doc.currency"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Available QTY"
                      background-color="white"
                      hide-details
                      v-model="item.actual_qty"
                      type="number"
                      disabled
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Group"
                      background-color="white"
                      hide-details
                      v-model="item.item_group"
                      disabled
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Stock QTY"
                      background-color="white"
                      hide-details
                      v-model="item.stock_qty"
                      type="number"
                      disabled
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Stock UOM"
                      background-color="white"
                      hide-details
                      v-model="item.stock_uom"
                      disabled
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="4"
                    v-if="item.has_serial_no == 1 || item.serial_no"
                  >
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Serial No QTY"
                      background-color="white"
                      hide-details
                      v-model="item.serial_no_selected_count"
                      type="number"
                      disabled
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="12"
                    v-if="item.has_serial_no == 1 || item.serial_no"
                  >
                    <v-autocomplete
                      v-model="item.serial_no_selected"
                      :items="item.serial_no_data"
                      item-text="serial_no"
                      outlined
                      dense
                      chips
                      color="indigo"
                      small-chips
                      label="Serial No"
                      multiple
                      @change="set_serial_no(item)"
                    ></v-autocomplete>
                  </v-col>
                  <v-col
                    cols="4"
                    v-if="item.has_batch_no == 1 || item.batch_no"
                  >
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Batch No Available QTY"
                      background-color="white"
                      hide-details
                      v-model="item.actual_batch_qty"
                      type="number"
                      disabled
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="4"
                    v-if="item.has_batch_no == 1 || item.batch_no"
                  >
                    <v-text-field
                      dense
                      outlined
                      color="indigo"
                      label="Batch No Expiry Date"
                      background-color="white"
                      hide-details
                      v-model="item.batch_no_expiry_date"
                      disabled
                    ></v-text-field>
                  </v-col>
                  <v-col
                    cols="8"
                    v-if="item.has_batch_no == 1 || item.batch_no"
                  >
                    <v-autocomplete
                      v-model="item.batch_no"
                      :items="item.batch_no_data"
                      item-text="batch_no"
                      outlined
                      dense
                      color="indigo"
                      label="Batch No"
                      @change="set_batch_qty(item, $event)"
                    >
                      <template v-slot:item="data">
                        <template>
                          <v-list-item-content>
                            <v-list-item-title
                              v-html="data.item.batch_no"
                            ></v-list-item-title>
                            <v-list-item-subtitle
                              v-html="
                                `Available QTY  '${data.item.batch_qty}' - Expiry Date ${data.item.expiry_date}`
                              "
                            ></v-list-item-subtitle>
                          </v-list-item-content>
                        </template>
                      </template>
                    </v-autocomplete>
                  </v-col>
                </v-row>
              </td>
            </template>
          </v-data-table>
        </template>
      </div>
    </v-card>
    <v-row>
      <v-col class="pt-0 pr-0" cols="8">
          <!-- <v-card
          style="max-height: 25vh; height: 25vh"
          class="cards mb-0 mt-3 py-0 grey lighten-5"
        > -->
        <v-card
          class="cards mb-0 mt-3 py-0 grey lighten-5"
        >
          <v-row no-gutters class="pa-1 pt-2" style="height: 100%">
            <v-col cols="6" no-gutters>
              <v-row no-gutters class="ma-1 pa-0" style="height: 100%">
                <v-col cols="12">
                  <v-text-field
                    :value="formtCurrency(total_qty)"
                    label="Total Qty"
                    outlined
                    dense
                    readonly
                    hide-details
                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    :value="formtCurrency(total_items_discount_amount)"
                    label="Items Discounts"
                    outlined
                    dense
                    readonly
                    hide-details
                    :prefix="pos_profile.currency"
                  ></v-text-field>
                </v-col>
                 <v-col cols="12">
                  <v-text-field
                    v-model="discount_amount"
                    label="ِAdditional Discount"
                    ref="discount"
                    outlined
                    dense
                    hide-details
                    type="number"
                    :prefix="pos_profile.currency"
                    :disabled="
                      !pos_profile.posa_allow_user_to_edit_additional_discount
                        ? true
                        : false
                    "
                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-autocomplete
                      v-model="selectedDiscount"
                      :items="discount_types"
                      dense
                      outlined
                      label="Select Discount Type"
                      :disabled="enableDisable"
                      ref="discount"
                      item-text="discount_type"
                      @change="enableDisable = true"
                    ></v-autocomplete>
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    :value="formtCurrency(subtotal)"
                    label="Total"
                    outlined
                    dense
                    readonly
                    hide-details
                    class="text--red"
                    :prefix="pos_profile.currency"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-col>
            <v-col no-gutters cols="6">
              <v-row no-gutters class="ma-1 pa-0" style="height: 100%">
                <v-col cols="12">
                  <v-text-field
                    v-model="customer_info.email_id"
                    label="Email"
                    outlined
                    dense
                    @change="set_customer_info('email_id', $event)"
                    hide-details
                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="customer_info.mobile_no"
                    label="ِPhone Number"
                    outlined
                    dense
                    hide-details
                    @change="set_customer_info('mobile_no', $event)"
                    type="number"
                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="customer_info.loyalty_program"
                    label="Loyalty Program"
                    outlined
                    dense
                    disabled
                    hide-details
                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-text-field
                    v-model="customer_info.loyalty_points"
                    label="Loyalty Points"
                    outlined
                    dense
                    disabled
                    hide-details
                    type="number"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
      <v-col class="pt-0 pr-3" cols="4">
        <v-card
          flat
          style="max-height: 25vh; height: 25vh"
          class="cards mb-0 mt-3 py-0"
        >
          <v-row align="start" style="height: 52%">
            <v-col cols="6">
              <v-btn
                block
                class="pa-0"
                large
                color="warning"
                dark
                @click="get_draft_invoices"
                >Get Hold</v-btn
              >
            </v-col>
            <v-col cols="6">
              <v-btn
                block
                class="pa-0"
                :class="{ 'disable-events': !pos_profile.posa_allow_return }"
                large
                color="info"
                dark
                @click="open_returns"
                >Return</v-btn
              >
            </v-col>
            <v-col cols="6">
              <v-btn
                block
                class="pa-0"
                large
                color="error"
                dark
                @click="cancel_invoice"
                >Cancel</v-btn
              >
            </v-col>
            <v-col cols="6">
              <v-btn
                block
                class="pa-0"
                large
                color="success"
                dark
                @click="new_invoice"
                >New</v-btn
              >
            </v-col>
          </v-row>
          <v-row align="end" style="height: 54%">
            <v-col cols="12">
              <v-btn
                block
                class="pa-0"
                large
                color="primary"
                rounded
                @click="show_payment_method"
                dark
                >PAY</v-btn
              >
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { evntBus } from '../../bus';
import Customer from './Customer.vue';
// import Customer from '../pos/Customer.vue';
export default {
  // props: ["pos_profile"],
  data() {
    return {
      pos_profile: '',
      pos_opening_shift: '',
      stock_settings: '',
      invoice_doc: '',
      return_doc: '',
      customer: '',
      customer_info: '',
      discount_amount: 0,
      total_tax: 0,
      total: 0,
      subitems: [],
      items: [],
      itemsPerPage: 1000,
      expanded: [],
      singleExpand: true,
      enableDisable:true,
      selectedDiscount: null,
      discount_types: [],
      coupon_activated: false,
      coupon_discounts: [],
      discount_return_coupon:[],
      options: [
        { text: '0%', value: '0' },
        { text: 'SRCT', value: '5' },
        { text: 'PWD', value: '5.0' },
      ],
      items_headers: [
        {
          text: 'Name',
          align: 'start',
          sortable: true,
          value: 'item_name',
        },
        { text: 'Subitems', value: 'sub_items', align: 'center' },
        { text: 'QTY', value: 'qty', align: 'center' },
        { text: 'UOM', value: 'uom', align: 'center' },
        // { text: 'Rate', value: 'rate', align: 'center' },
        { text: 'Rate', value: 'price_list_rate', align: 'center' },
        { text: 'Discount Percentage', value: 'discount_percentage', align: 'center' },
        { text: 'Discount Amount', value: 'discount_amount', align: 'center' },
        { text: 'Amount', value: 'amount', align: 'center' },
      ],
      item_group_discounts: [],
      default_discount: 0,
    };
  },
  components: {
    Customer,
  },
  computed: {
    total_qty() {
      this.close_payments();
      let qty = 0;
      this.items.forEach((item) => {
        qty += item.qty;
      });
      return flt(qty).toFixed(2);
    },
    subtotal() {
      this.close_payments();
      let sum = 0;
      this.items.forEach((item) => {
        sum += item.qty * item.rate;
      });
      // sum -= (flt(this.discount_amount) + flt(this.calculate_discount()));
      sum -= (flt(this.calculate_discount()));
      return flt(sum).toFixed(2);
    },
    
    total_items_discount_amount() {
      let sum = 0;
      this.items.forEach((item) => {
        sum += item.qty * item.discount_amount;
      });
      return flt(sum).toFixed(2);
    },
  },
  methods: {
    enableDiscount() {		
        this.enableDisable = false;
    },
    manage_subitems_dialog(item){
      const invoice_doc = this.proces_invoice();
      let data ={}
      data.item = item;
      data.pos_profile = this.pos_profile;
      data.invoice_doc = invoice_doc;
      evntBus.$emit('open_items_selector', data);
    },
    get_discount() {
      const vm = this;
        frappe.call({
          method: "rapidposcustom.rapidposcustom.api.rapidposcustom.get_discount_types",
            callback: function (r) {
              if (r.message) {
                r.message.get_discount.forEach((element) => {
                  vm.discount_types.push(element)
                })
          }
        },
        });
    },

    get_item_group_discounts() {
      const vm = this;
      frappe.call({
        method: "rapidposcustom.rapidposcustom.api.rapidposcustom.get_item_group_discounts",
        args: { selected_discount_type: this.selectedDiscount },
        callback: function (r) {
          if (r.message) {
            if (r.message.get_item_group_discount_list) {
              r.message.get_item_group_discount_list.forEach((element) => {
                vm.item_group_discounts.push(element)
              });
            }
            else {
              vm.default_discount = r.message;
            }
          }
          else {
          }
        }
      })
    },

    calculate_discount() { //calculate coupon and item discounts
      let item_sum = 0;
      let total_amount_discount = 0;

      this.items.forEach((item) => {
        item_sum += item.qty * item.rate;
        total_amount_discount += item.discount_amount;
      });

      let discount_amount =  this.calculate_coupon_discount(item_sum) + total_amount_discount;
      this.discount_amount = discount_amount;
      return discount_amount;
    },

    calculate_coupon_discount(item_sum){
      let coupon_percentage_discount = 0;
      let coupon_amount_discount = 0;

      if(this.coupon_activated){
              this.coupon_discounts.forEach((element) => {
                if(element.discount_type == "Percentage"){
                  coupon_percentage_discount += item_sum*(element.discount_value/100);
                }
                if (element.discount_type == "Amount"){
                  coupon_amount_discount += element.discount_value;
                }
              });
      }
      return coupon_percentage_discount + coupon_amount_discount;
    },

    submit_discount_authentication() {
      this.enableDiscount();
      evntBus.$emit("show_mesage", {
            text: `Additional Discount enabled`,
            color: "success",
          });
    },
    remove_item(item) {
      const index = this.items.findIndex((el) => el === item);
      this.items.splice(index, 1);
      const idx = this.expanded.findIndex((el) => el === item);
      if (idx >= 0) {
        this.expanded.splice(idx, 1);
      }
    },
    add_one(item) {
      item.qty++;
      if (item.qty == 0) {
        this.remove_item(item);
      }
      this.calc_sotck_gty(item, item.qty);
      // this.$forceUpdate();
    },
    subtract_one(item) {
      item.qty--;
      if (item.qty == 0) {
        this.remove_item(item);
      }
      this.calc_sotck_gty(item, item.qty);
      // this.$forceUpdate();
    },
    add_item(item) {
      if (!item.uom) {
        item.uom = item.stock_uom;
      }
      const index = this.items.findIndex(
        (el) => el.item_code === item.item_code && el.uom === item.uom
      );
      if (index === -1) {
        const new_item = this.get_new_item(item);
        this.items.unshift(new_item);
        this.update_item_detail(new_item);
        if(item.is_parent_item){
            this.manage_subitems_dialog(new_item);
        }
      } else {
        const cur_item = this.items[index];
        this.update_items_details([cur_item]);
        if (!cur_item.has_batch_no) {
          cur_item.qty += item.qty;
          this.calc_sotck_gty(cur_item, cur_item.qty);
        } else {
          if (
            cur_item.stock_qty < cur_item.actual_batch_qty ||
            !cur_item.batch_no
          ) {
            cur_item.qty += item.qty;
            this.calc_sotck_gty(cur_item, cur_item.qty);
          } else {
            const new_item = this.get_new_item(cur_item);
            new_item.batch_no = '';
            new_item.batch_no_expiry_date = '';
            new_item.actual_batch_qty = '';
            new_item.qty = item.qty || 1;
            this.items.unshift(new_item);
          }
        }
      }
     
    },
    get_new_item(item) {
      const new_item = { ...item };
      if (!item.qty) {
        item.qty = 1;
      }
      if (item.rate===0){
        new_item.is_packaging_item = 1;
      }
      if (this.item_group_discounts && this.default_discount === 0) {
        this.item_group_discounts.forEach((element) => {
          if (element.item_group === item.item_group) {
            new_item.discount_percentage = element.discount_percentage;
          }
        })
      }
      else if (this.default_discount > 0 ) {
        new_item.discount_percentage = this.default_discount;
      }
      else if (!this.selectedDiscount) {
        new_item.discount_percentage = 0;
      }
      //
      new_item.subitems_reference = '';
      new_item.stock_qty = item.qty;
      new_item.discount_amount = 0;
      new_item.selectedDiscount = null;
      // new_item.discount_percentage = 0;
      new_item.discount_amount_per_item = 0;
      new_item.price_list_rate = item.rate;
      new_item.qty = item.qty;
      new_item.uom = item.uom ? item.uom : item.stock_uom;
      new_item.actual_batch_qty = '';
      new_item.conversion_factor = 1;
      new_item.item_id = Date.now();
      if (new_item.has_batch_no || new_item.has_serial_no) {
        this.expanded.push(new_item);
      }
      return new_item;
    },
    cancel_invoice() {
      const doc = this.get_invoice_doc();
      if (doc.name && this.pos_profile.posa_allow_delete) {
        frappe.call({
          method: 'posawesome.posawesome.api.posapp.delete_invoice',
          args: { invoice: doc.name },
          async: true,
          callback: function (r) {
            if (r.message) {
              evntBus.$emit('show_mesage', {
                text: r.message,
                color: 'warning',
              });
            }
          },
        });
      }
      this.items = [];
      // this.customer = this.pos_profile.customer;
      this.customer = 'WalkIn';
      this.invoice_doc = '';
      this.return_doc = '';
      this.discount_amount = 0;
      evntBus.$emit('set_customer_readonly', false);

      this.selectedDiscount = null;
      this.enableDisable = true;
    },
    new_invoice(data = {}) {
      evntBus.$emit('set_customer_readonly', false);
      this.expanded = [];
      this.return_doc = '';
      const doc = this.get_invoice_doc();
      if (doc.name) {
        this.update_invoice(doc);
      } else {
        if (doc.items.length) {
          this.save_draft_invoice(doc);
        }
      }
      if (!data.name && !data.is_return) {
        this.items = [];
        // this.customer = this.pos_profile.customer;
        this.customer = 'WalkIn';
        this.invoice_doc = '';
        this.discount_amount = 0;
      } else {
        if (data.is_return) {
          evntBus.$emit('set_customer_readonly', true);
        }
        this.invoice_doc = data;
        this.items = data.items;
        let cont = 0;
        this.items.forEach((item) => {
          cont++;
          item.item_id = Date.now() + cont;
        });
        this.update_items_details(this.items);
        this.customer = data.customer;
        this.discount_amount = data.discount_amount;
        this.items.forEach((item) => {
          if (item.serial_no) {
            item.serial_no_selected = [];
            const serial_list = item.serial_no.split('\n');
            serial_list.forEach((element) => {
              if (element.length) {
                item.serial_no_selected.push(element);
              }
            });
            item.serial_no_selected_count = item.serial_no_selected.length;
          }
        });
      }
      this.coupon_activated = false;
    },
    save_draft_invoice() {
      const vm = this;
      const doc = this.get_invoice_doc();
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.save_draft_invoice',
        args: { data: doc },
        async: false,
        callback: function (r) {
          if (r.message) {
            vm.invoice_doc = r.message;
          }
        },
      });
      return this.invoice_doc;
    },
    get_invoice_doc() {
      let doc = {};
      if (this.invoice_doc.name) {
        doc = { ...this.invoice_doc };
      }
      doc.doctype = 'Sales Invoice';
      doc.is_pos = 1;
      doc.company = doc.company || this.pos_profile.company;
      doc.pos_profile = doc.pos_profile || this.pos_profile.name;
      doc.currency = doc.currency || this.pos_profile.currency;
      doc.naming_series = doc.naming_series || this.pos_profile.naming_series;
      doc.customer = this.customer;
      doc.items = this.get_invoice_items();
      doc.total = this.subtotal;
      doc.coupon_list = this.save_coupon_to_invoice(this.discount_return_coupon);
      // doc.discount_amount = flt(this.discount_amount);
      // doc.discount_amount = flt(this.overall_discount());
      doc.discount_amount = flt(this.calculate_discount());
      doc.additional_discount_type = this.selectedDiscount;
      doc.posa_pos_opening_shift = this.pos_opening_shift.name;
      doc.payments = this.get_payments();
      doc.taxes = [];
      doc.is_return = this.invoice_doc.is_return;
      doc.return_against = this.invoice_doc.return_against;
      return doc;
    },
    //
    overall_discount() {
      let sum = 0;
      this.items.forEach((item) => {
        sum += item.qty * item.discount_amount;
      });
      sum = flt(this.calculate_discount());
      // sum = flt(sum) + flt(this.discount_amount); - original
      // sum = flt(sum) + flt(this.discount_amount) + flt(this.calculate_discount());
      return sum;
    },
    //
    get_invoice_items() {
      const items_list = [];
      this.items.forEach((item) => {
        items_list.push({
          item_code: item.item_code,
          qty: item.qty,
          rate: item.rate,
          uom: item.uom,
          is_parent_item: item.is_parent_item,
          max_subitem_quantity: item.max_subitem_quantity,
          conversion_factor: item.conversion_factor,
          serial_no: item.serial_no,
          discount_percentage: item.discount_percentage,
          discount_amount: item.discount_amount,
          batch_no: item.batch_no,
          subitems_reference: item.subitems_reference,
          is_packaging_item: item.is_packaging_item
        });
      });
      return items_list;
    },
    get_payments() {
      const payments = [];
      this.pos_profile.payments.forEach((payment) => {
        payments.push({
          amount: 0,
          mode_of_payment: payment.mode_of_payment,
          default: payment.default,
          account: '',
        });
      });
      return payments;
    },
    update_invoice(doc) {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.update_invoice',
        args: {
          data: doc,
        },
        async: false,
        callback: function (r) {
          if (r.message) {
            vm.invoice_doc = r.message;
          }
        },
      });
      return this.invoice_doc;
    },
    proces_invoice() {
      const doc = this.get_invoice_doc();
      if (doc.name) {
        return this.update_invoice(doc);
      } else {
        return this.save_draft_invoice(doc);
      }
    },
    show_payment() {
      if (!this.customer) {
        evntBus.$emit('show_mesage', {
          text: `There is no Customer !`,
          color: 'error',
        });
        return;
      }
      if (!this.items.length) {
        evntBus.$emit('show_mesage', {
          text: `There is no Items !`,
          color: 'error',
        });
        return;
      }
      if (!this.validate()) {
        return;
      }
      const invoice_doc = this.proces_invoice();
      invoice_doc.customer_info = this.customer_info;
      evntBus.$emit('send_invoice_doc_payment', invoice_doc);
      evntBus.$emit('show_payment', 'true');

      this.enableDisable = true;
    },
    /**NEW SHOW_PAYMENT() METHOD FOR ALL MODE OF PAYMENTS */
    show_payment_method(payment_method) {
      if (!this.customer) {
        evntBus.$emit('show_mesage', {
          text: `There is no Customer !`,
          color: 'error',
        });
        return;
      }
      if (!this.items.length) {
        evntBus.$emit('show_mesage', {
          text: `There is no Items !`,
          color: 'error',
        });
        return;
      }
      if (!this.validate()) {
        return;
      }
      this.close_payments();
      this.determine_payment_method(payment_method);
      const invoice_doc = this.proces_invoice();
      invoice_doc.customer_info = this.customer_info;
      // evntBus.$emit('send_invoice_doc_payment', invoice_doc);
      if(payment_method==="Cash"){
        evntBus.$emit('send_invoice_doc_cash', invoice_doc);
      }
      else if (payment_method==="Credit Card"){
        evntBus.$emit('send_invoice_doc_cc', invoice_doc);
      }
      else if (payment_method==="Debit Card"){
        evntBus.$emit('send_invoice_doc_dc', invoice_doc);
      }
      else{
       evntBus.$emit('send_invoice_doc_payment', invoice_doc);
      }
      this.enableDisable = true;
      this.selectedDiscount = null;
      this.item_group_discounts = null;
      this.default_discount = 0;
    },
    //to determine what mode_of_payment page to open
    determine_payment_method(payment_method){
      if (payment_method === "Cash") return evntBus.$emit('show_payment_cash', 'true')
      if (payment_method === "Credit Card") return evntBus.$emit('show_payment_cc', 'true')
      if (payment_method === "Debit Card") return evntBus.$emit('show_payment_dc', 'true')
      return evntBus.$emit('show_payment', 'true')
    },
    validate() {
      let value = true;
      this.items.forEach((item) => {
        if (
          this.pos_profile.update_stock &&
          this.stock_settings.allow_negative_stock != 1
        ) {
          if (item.is_stock_item && item.stock_qty > item.actual_qty) {
            evntBus.$emit('show_mesage', {
              text: `The existing quantity of item ${item.item_name} is not enough`,
              color: 'error',
            });
            value = false;
          }
        }
        if (item.has_serial_no) {
          if (
            !item.serial_no_selected ||
            item.stock_qty != item.serial_no_selected.length
          ) {
            evntBus.$emit('show_mesage', {
              text: `Selcted serial numbers of item ${item.item_name} is incorrect`,
              color: 'error',
            });
            value = false;
          }
        }
        if (item.has_batch_no) {
          if (item.stock_qty > item.actual_batch_qty) {
            evntBus.$emit('show_mesage', {
              text: `The existing batch quantity of item ${item.item_name} is not enough`,
              color: 'error',
            });
            value = false;
          }
        }
        if (this.pos_profile.posa_allow_user_to_edit_additional_discount) {
          const clac_percentage = (this.discount_amount / this.subtotal) * 100;
          if (clac_percentage > this.pos_profile.posa_max_discount_allowed) {
            evntBus.$emit('show_mesage', {
              text: `The discount should not be higher than ${this.pos_profile.posa_max_discount_allowed}%`,
              color: 'error',
            });
            value = false;
          }
        }
        if (this.invoice_doc.is_return) {
          if (this.subtotal >= 0) {
            evntBus.$emit('show_mesage', {
              text: `Return Invoice Total Not Correct`,
              color: 'error',
            });
            value = false;
            return value;
          }
          if (this.subtotal * -1 > this.return_doc.total) {
            evntBus.$emit('show_mesage', {
              text: `Return Invoice Total should not be higher than ${this.return_doc.total}`,
              color: 'error',
            });
            value = false;
            return value;
          }
          this.items.forEach((item) => {
            const return_item = this.return_doc.items.find(
              (element) => element.item_code == item.item_code
            );

            if (!return_item) {
              evntBus.$emit('show_mesage', {
                text: `The item ${item.item_name} cannot be returned because it is not in the invoice ${this.return_doc.name}`,
                color: 'error',
              });
              value = false;
              return value;
            } else if (item.qty * -1 > return_item.qty || item.qty >= 0) {
              evntBus.$emit('show_mesage', {
                text: `The QTY of the item ${item.item_name} cannot be greater than ${return_item.qty}`,
                color: 'error',
              });
              value = false;
              return value;
            }
          });
        }
      });
      return value;
    },
    get_draft_invoices() {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.get_draft_invoices',
        args: {
          pos_opening_shift: this.pos_opening_shift.name,
        },
        async: false,
        callback: function (r) {
          if (r.message) {
            evntBus.$emit('open_drafts', r.message);
          }
        },
      });
    },
    get_discount_authentication() {
      evntBus.$emit('open_discount_authentication');
    },
    open_returns() {
      evntBus.$emit('open_returns', this.pos_profile.company);
    },
    close_payments() {
      evntBus.$emit('show_payment', 'false');
      evntBus.$emit('show_payment_cash', 'false');
      evntBus.$emit('show_payment_cc', 'false');
      evntBus.$emit('show_payment_dc', 'false');
    },
    update_items_details(items) {
      if (!items.length > 0) {
        return;
      }
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.get_items_details',
        args: {
          pos_profile: vm.pos_profile,
          items_data: items,
        },
        callback: function (r) {
          if (r.message) {
            items.forEach((item) => {
              const updated_item = r.message.find(
                (element) => element.item_id == item.item_id
              );
              item.actual_qty = updated_item.actual_qty;
              item.serial_no_data = updated_item.serial_no_data;
              item.batch_no_data = updated_item.batch_no_data;
              item.item_uoms = updated_item.item_uoms;
              item.has_batch_no = updated_item.has_batch_no;
              item.has_serial_no = updated_item.has_serial_no;
            });
          }
        },
      });
    },
    update_item_detail(item) {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.get_item_detail',
        args: {
          doc: this.get_invoice_doc(),
          data: {
            item_code: item.item_code,
            customer: this.customer,
            doctype: 'Sales Invoice',
            name: 'New Sales Invoice 1',
            company: this.pos_profile.company,
            conversion_rate: 1,
            qty: item.qty,
            price_list_rate: item.price_list_rate,
            child_docname: 'New Sales Invoice Item 1',
            cost_center: this.pos_profile.cost_center,
            currency: this.pos_profile.currency,
            // plc_conversion_rate: 1,
            pos_profile: this.pos_profile.name,
            price_list: this.pos_profile.selling_price_list,
            uom: item.uom,
            tax_category: '',
            transaction_type: 'selling',
            update_stock: this.pos_profile.update_stock,
          },
        },
        callback: function (r) {
          if (r.message) {
            const data = r.message;
            if (data.has_pricing_rule) {
              item.discount_amount_on_rate = data.discount_amount_on_rate;
              item.discount_percentage = data.discount_percentage;
              item.discount_percentage_on_rate =
                data.discount_percentage_on_rate;
              item.discount_amount = data.discount_amount || 0;
            }
            if (!item.btach_price) {
              item.price_list_rate = data.price_list_rate;
            }
            item.has_pricing_rule = data.has_pricing_rule;
            item.last_purchase_rate = data.last_purchase_rate;
            item.price_or_product_discount = data.price_or_product_discount;
            item.pricing_rule_for = data.pricing_rule_for;
            item.pricing_rules = data.pricing_rules;
            item.projected_qty = data.projected_qty;
            item.reserved_qty = data.reserved_qty;
            item.conversion_factor = data.conversion_factor;
            item.stock_qty = data.stock_qty;
            item.stock_uom = data.stock_uom;
            (item.has_serial_no = data.has_serial_no),
              (item.has_batch_no = data.has_batch_no),
              vm.calc_item_price(item);
          }
        },
      });
    },
    fetch_customer_details() {
      const vm = this;
      if (this.customer) {
        return new Promise((resolve) => {
          frappe.db
            .get_value('Customer', vm.customer, [
              'email_id',
              'mobile_no',
              'image',
              'loyalty_program',
            ])
            .then(({ message }) => {
              const { loyalty_program } = message;
              if (loyalty_program) {
                frappe.call({
                  method:
                    'erpnext.accounts.doctype.loyalty_program.loyalty_program.get_loyalty_program_details_with_points',
                  args: {
                    customer: vm.customer,
                    loyalty_program,
                    silent: true,
                  },
                  callback: (r) => {
                    const { loyalty_points, conversion_factor } = r.message;
                    if (!r.exc) {
                      vm.customer_info = {
                        ...message,
                        customer: vm.customer,
                        loyalty_points,
                        conversion_factor,
                      };
                      resolve();
                    }
                  },
                });
              } else {
                vm.customer_info = { ...message, customer: vm.customer };
                resolve();
              }
            });
        });
      } else {
        return new Promise((resolve) => {
          vm.customer_info = {};
          resolve();
        });
      }
    },
    calc_prices(item, value, $event) {
      if (event.target.id === 'rate') {
        item.discount_percentage = 0;
        if (value < item.price_list_rate) {
          item.discount_amount = (
            flt(item.price_list_rate) - flt(value)
          ).toFixed(2);
        } else if (value < 0) {
          item.rate = item.price_list_rate;
          item.discount_amount = 0;
        } else if (value > item.price_list_rate) {
          item.discount_amount = 0;
        }
      } else if (event.target.id === 'discount_amount') {
        if (value < 0) {
          item.discount_amount = 0;
          item.discount_percentage = 0;
        } else {
          item.rate = flt(item.price_list_rate) - flt(value);
          item.discount_percentage = 0;
        }
      } else if (event.target.id === 'discount_percentage') {
        if (value < 0) {
          item.discount_amount = 0;
          item.discount_percentage = 0;
        } else {
          item.rate = (
            flt(item.price_list_rate) -
            (flt(item.price_list_rate) * flt(value)) / 100
          ).toFixed(2);
          item.discount_amount = (
            flt(item.price_list_rate) - flt(item.rate)
          ).toFixed(2);
        }
      }
    },
    calc_item_price(item) {
      if (!item.has_pricing_rule) {
        if (item.price_list_rate) {
          item.rate = item.price_list_rate;
        }
      }
      if (item.discount_percentage) {
        item.rate =
          flt(item.price_list_rate) -
          (flt(item.price_list_rate) * flt(item.discount_percentage)) / 100;
        item.discount_amount = (
          flt(item.price_list_rate) - flt(item.rate)
        ).toFixed(2);
      } else if (item.discount_amount) {
        item.rate = (
          flt(item.price_list_rate) - flt(item.discount_amount)
        ).toFixed(2);
      } else if (item.pricing_rule_for === 'Rate') {
        item.rate = item.price_list_rate;
      }
    },
    calc_uom(item, value) {
      const new_uom = item.item_uoms.find((element) => element.uom == value);
      item.conversion_factor = new_uom.conversion_factor;
      if (!item.has_pricing_rule) {
        item.discount_amount = 0;
        item.discount_percentage = 0;
      }
      if (item.btach_price) {
        item.price_list_rate = item.btach_price * new_uom.conversion_factor;
      }
      this.update_item_detail(item);
    },
    calc_sotck_gty(item, value) {
      item.stock_qty = item.conversion_factor * value;
    },
    set_serial_no(item) {
      item.serial_no = '';
      item.serial_no_selected.forEach((element) => {
        item.serial_no += element + '\n';
      });
      item.serial_no_selected_count = item.serial_no_selected.length;
      if (item.serial_no_selected_count != item.stock_qty) {
        evntBus.$emit('show_mesage', {
          text: `Selected Serial No QTY is ${item.serial_no_selected_count} it should be ${item.stock_qty}`,
          color: 'warning',
        });
      }
    },
    set_batch_qty(item, value) {
      const batch_no = item.batch_no_data.find(
        (element) => element.batch_no == value
      );
      item.actual_batch_qty = batch_no.batch_qty;
      item.batch_no_expiry_date = batch_no.expiry_date;
      if (batch_no.btach_price) {
        item.btach_price = batch_no.btach_price;
        item.price_list_rate = batch_no.btach_price;
        item.rate = batch_no.btach_price;
      } else {
        item.btach_price = null;
        this.update_item_detail(item);
      }
    },
    set_customer_info(field, value) {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.set_customer_info',
        args: {
          fieldname: field,
          customer: this.customer_info.customer,
          value: value,
        },
        callback: (r) => {
          if (!r.exc) {
            vm.customer_info[field] = value;
            evntBus.$emit('show_mesage', {
              text: 'Customer contact updated successfully.',
              color: 'success',
            });
            frappe.utils.play_sound('submit');
          }
        },
      });
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },
    shortOpenPayment(e) {
      if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        // this.show_payment();
        this.close_payments();
        this.show_payment_method("All");
      }
    },
    /**----->FOR PAYMENT PURPOSES<--------**/
    shortOpenCashPayment(e) {
      if (e.key === '1' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.close_payments();
        this.show_payment_method("Cash");
      }
    },
    shortOpenCCPayment(e) {
      if (e.key === '2' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.close_payments();
        this.show_payment_method("Credit Card");
      }
    },
    shortOpenDCPayment(e) {
      if (e.key === '3' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.close_payments();
        this.show_payment_method("Debit Card");
      }
    },
    shortDeleteFirstItem(e) {
      if (e.key === 'd' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.remove_item(this.items[0]);
      }
    },
    shortOpenFirstItem(e) {
      if (e.key === 'o' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.expanded = [];
        this.expanded.push(this.items[0]);
      }
    },
    shortSelectDiscount(e) {
      if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        this.$refs.discount.focus();
      }
    },
    openNewInvoice(e){
      if (e.key === "F11"){
        e.preventDefault();
        console.log({e});
        this.new_invoice();
        }
    },
    getHold(e){
      if (e.key === "F8"){
        e.preventDefault();
        console.log({e});
        this.get_draft_invoices();
        }
    },
    openReturns(e){
      if (e.key === "F9"){
        e.preventDefault();
        console.log({e});
        this.open_returns();
        }
    },
     cancelInvoice(e){
      if (e.key === "F10"){
        e.preventDefault();
        console.log({e});
        this.cancel_invoice();
        }
    },
    clearDiscount(e) {
      if (e.key === 'c' && (e.ctrlKey)) {
        this.selectedDiscount = null;
        this.enableDisable = true;
        this.discount_amount = 0;
      }
    },
    openCouponDialog(e){
      if(e.key === 'F6'){
        e.preventDefault();
        
        if (!this.items.length) {
          evntBus.$emit('show_mesage', {
            text: `There is no Items !`,
            color: 'error',
          });
          return;
        }

        if (!this.customer) {
        evntBus.$emit('show_mesage', {
          text: `There is no Customer !`,
          color: 'error',
        });
        return;
        }

        const invoice_doc = this.proces_invoice();
        evntBus.$emit("apply_coupon_code", invoice_doc);
      }
    },
    submit_coupon_codes(discount){
      this.coupon_discounts = discount;
      this.coupon_activated = true;
      evntBus.$emit("show_mesage", {
            text: `Coupon Payments added!`,
            color: "success",
          });
    },
    save_coupon_to_invoice(discount){
        let coupon_percentage_discount = 0;
        let coupon_amount_discount = 0;
        let item_sum = 0;
        let coupon_list = [];

        //for inserting purposes
        this.items.forEach((item) => {
          item_sum += item.qty * item.rate;
        });

        discount.forEach((element) => {
              if(element.discount_type == "Percentage"){
                coupon_percentage_discount += item_sum*(element.discount_value/100);
                coupon_list.push({coupon_name:element.coupon_name, qty: element.qty, discounted_amount:coupon_percentage_discount})
              }
              else if (element.discount_type == "Amount"){
                coupon_amount_discount += element.discount_value;
                coupon_list.push({coupon_name:element.coupon_name, qty: element.qty, discounted_amount:coupon_amount_discount})
              }
            });
        return coupon_list;
    },
  },
  created() {
    evntBus.$on('register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
      this.customer = data.pos_profile.customer;
      this.pos_opening_shift = data.pos_opening_shift;
      this.stock_settings = data.stock_settings;
    });
    evntBus.$on('add_item', (item) => {
      this.add_item(item);
    });
    evntBus.$on('update_customer', (customer) => {
      this.customer = customer;
    });
    evntBus.$on('new_invoice', () => {
      this.invoice_doc = '';
      this.cancel_invoice();
    });
    evntBus.$on('load_invoice', (data) => {
      this.new_invoice(data);
    });
    evntBus.$on('load_return_invoice', (data) => {
      this.new_invoice(data.invoice_doc);
      this.discount_amount = -data.return_doc.discount_amount;
      // console.log(data);
      this.return_doc = data.return_doc;
    });
    evntBus.$on("submit_discount_authentication", (data) => {
        this.submit_discount_authentication(data)
    });
    evntBus.$on("open_coupon_dialog", () => {
      this.openCouponDialog();
    });
    evntBus.$on("submit_coupon", (discount) => {
      this.submit_coupon_codes(discount);
      this.discount_return_coupon = discount;
    });
    evntBus.$on("save_subitems", (subitems, item_code) => {
       this.items.forEach((element)=>{
        if (element.item_code === item_code){
          element.subitems = subitems;
        }
      });
    });
    evntBus.$on("save_packaging_items", (data) => {
       this.items.forEach((element)=>{
        if (element.item_code === data.item_code){
          element.packaging_items = data.packaging_items;
        }
        });
    });
    evntBus.$on("submit_subitems", (data) => {
      this.items.forEach((element)=>{
        if (element.item_code === data.item_code){
          element.subitems_reference = data.subitem_reference;
        }
      });
      this.invoice_doc = data.invoice_doc;
    });

    evntBus.$on("submit_packaging_items", (invoice_doc) => {
      this.invoice_doc = invoice_doc;
    });


    this.$nextTick(function (){
      this.get_discount();
      // evntBus.$on("submit_closing_pos", (data) => {
      //   this.submit_closing_pos(data)
      // })
    });

    document.addEventListener('keydown', this.shortOpenPayment.bind(this));
    document.addEventListener('keydown', this.shortOpenCashPayment.bind(this));
    document.addEventListener('keydown', this.shortOpenCCPayment.bind(this));
    document.addEventListener('keydown', this.shortOpenDCPayment.bind(this));
    document.addEventListener('keydown', this.shortDeleteFirstItem.bind(this));
    document.addEventListener('keydown', this.shortOpenFirstItem.bind(this));
    document.addEventListener('keydown', this.shortSelectDiscount.bind(this));
    document.addEventListener('keydown', this.clearDiscount.bind(this));
    document.addEventListener('keydown', this.openCouponDialog.bind(this));
    document.addEventListener('keydown', this.openNewInvoice.bind(this));
    document.addEventListener('keydown', this.getHold.bind(this));
    document.addEventListener('keydown', this.openReturns.bind(this));
    document.addEventListener('keydown', this.cancelInvoice.bind(this));

  },
  destroyed() {
    document.removeEventListener('keydown', this.shortOpenPayment);
    document.removeEventListener('keydown', this.shortOpenCashPayment);
    document.removeEventListener('keydown', this.shortOpenCCPayment);
    document.removeEventListener('keydown', this.shortOpenDCPayment);
    document.removeEventListener('keydown', this.shortDeleteFirstItem);
    document.removeEventListener('keydown', this.shortOpenFirstItem);
    document.removeEventListener('keydown', this.shortSelectDiscount);
    document.removeEventListener('keydown', this.clearDiscount);
    document.removeEventListener('keydown', this.openCouponDialog);
    document.removeEventListener('keydown', this.openNewInvoice);
    document.removeEventListener('keydown', this.getHold);
    document.removeEventListener('keydown', this.openReturns);
    document.removeEventListener('keydown', this.cancelInvoice);

  },
  watch: {
    customer() {
      this.close_payments();
      evntBus.$emit('set_customer', this.customer);
      this.fetch_customer_details();
    },
    expanded(data_value) {
      this.update_items_details(data_value);
      if (data_value.length > 0) {
        this.update_item_detail(data_value[0]);
      }
    },
    // test
    selectedDiscount() {
      if (this.selectedDiscount) {
        this.get_item_group_discounts();
      }
    },
    // test
  },
};
</script>

<style scoped>
.border_line_bottom {
  border-bottom: 1px solid lightgray;
}
.disable-events {
  pointer-events: none;
}
</style>