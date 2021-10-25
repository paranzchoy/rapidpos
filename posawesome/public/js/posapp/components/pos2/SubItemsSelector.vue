<template>
  <v-row justify="center">
    <v-dialog v-model="dialog_state" max-width="1500px" scrollable>
      <v-card>
        <v-card-title>
           <v-col cols="4" class="headline indigo--text">Select subitems for {{item_doc.item_name}}</v-col>
           <v-spacer></v-spacer>
           <v-col cols="3">
                <v-combobox style="margin-top:8px;"
                  v-model="item_group"
                  :items="subitem_item_group"
                  label="Item Group"
                  outlined
                  dense
                ></v-combobox>
           </v-col>
           <v-spacer></v-spacer>
           <v-col cols="3">
              Max. Qty left: {{remaining_qty * item_doc.qty}}
            </v-col>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          <v-row>
              <v-col
                v-for="(item) in filtred_items"
                :value="filtred_items"
                :key="item.actual_qty"
                xl="1"
                lg="1"
                md="2"
                sm="3"
                cols="4"
                min-height="50"
              >
                <v-card hover="hover" :style="color(item)">
                      <v-col cols="12">
                        <v-img
                          :src="
                            item.image ||
                            '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'
                          "
                          @click="add_item(item)"
                          class="white--text align-end"
                          gradient="to bottom, rgba(0,0,0,.2), rgba(0,0,0,.7)"
                          height="100px"
                        >
                          <v-card-text
                            v-text="item.item_name"
                            class="text-subtitle-2 px-1 pb-2"
                          ></v-card-text>
                        </v-img>
                      </v-col>
                      <v-row style="margin-left: .5px;">
                          <v-col class="text-caption indigo--text accent-3" cols="5">
                            <!-- {{ item.rate || 0 }} {{ item.currency || '' }} -->
                            Qty
                          </v-col>
                          <v-col cols="7">
                                  <v-text-field
                                    v-model.number="item.actual_qty"
                                    dense
                                    single-line
                                    type="number"
                                    :disabled="disable_qty">
                                  </v-text-field>
                          </v-col>
                      </v-row>
                    
                </v-card>
              </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="blue-grey" dark @click="reset">Reset</v-btn>
          <v-btn color="error" dark @click="close_dialog">Cancel</v-btn>
          <v-btn
            color="primary"
            dark
            @click="submit_dialog"
            >Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>
<script>
import { evntBus } from "../../bus";
export default {
  data: () => ({
      pos_profile:'',
      invoice_doc:'',
      item_doc:'',
      dialog_state: false,
      select: '',
      total_inputted_qty:0,
      items:[],
      item_groups:[],
      item_group:'ALL',
      subitem_item_group:[],
      items_headers: [
      { text: 'Name', align: 'start', sortable: true, value: 'item_name' },
      { text: 'Rate', value: 'rate', align: 'start' },
      { text: 'Currency', value: 'currency', align: 'start' },
      { text: 'Available QTY', value: 'actual_qty', align: 'start' },
      { text: 'UOM', value: 'stock_uom', align: 'start' },
      ],
      itemsPerPage: 12,
      enableDisable: false,
      items_with_qty:[],
      counter:0
  }),
  watch: {
  },
  methods: {
     color(item){
      if(item.actual_qty!=0){
        return "background-color:#e0dfdc;";
      }
      else{
        return "background-color:#ffffff;";
      }
    },
      close_dialog(){
          this.dialog_state = false;
          //this.enableDisable = false;
          this.disable_qty = false;
      },
      add_item(item){
        if (this.total_qty>=this.item_doc.max_subitem_quantity){
            evntBus.$emit('show_mesage', {
              text: `Quantity allowed exceeded!`,
              color: 'error',
            });
            frappe.utils.play_sound('error');
        }
        else{
          // this.add_item_details(item);
          this.items.forEach((element) => {
            const index = this.items.findIndex((el) => el.item_name === element.item_name);
              if (element===item){
                element.actual_qty++;
                this.items.splice(index, 1);
                this.items.unshift(element);
              }
            });
          console.log(this.items_with_qty);
        }
      },
      // combine code to select only those items with quantity here in this method
      add_item_details(item){
        if (!item.uom) {
          item.uom = item.stock_uom;
        }
        const index = this.items_with_qty.findIndex(
          (el) => el.item_code === item.item_code && el.uom === item.uom
        );
        if (index === -1) {
          const new_item = this.get_new_item(item);
          this.items_with_qty.unshift(new_item);
          this.update_item_detail(new_item);
        }
        else {

          const cur_item = this.items_with_qty[index];
          this.update_items_details([cur_item]);
          if (!cur_item.has_batch_no) {
            cur_item.qty += item.actual_qty;
            this.calc_sotck_gty(cur_item, cur_item.qty);
          } else {
            if (
              cur_item.stock_qty < cur_item.actual_batch_qty ||
              !cur_item.batch_no
            ) {
              cur_item.qty += item.actual_qty;
              this.calc_sotck_gty(cur_item, cur_item.qty);
            } else {
              const new_item = this.get_new_item(cur_item);
              new_item.batch_no = '';
              new_item.batch_no_expiry_date = '';
              new_item.actual_batch_qty = '';
              new_item.qty = item.actual_qty || 1;
              // new_item.qty = item.actual_qty;
              this.items_with_qty.unshift(new_item);
            }
          }
        }
      },
      get_new_item(item) {
        const new_item = { ...item };
        // if (!item.qty) {
        //   item.qty = 1;
        // }
        new_item.expense_account = this.pos_profile.write_off_account;
        new_item.stock_qty = item.qty;
        new_item.discount_amount = 0;
        new_item.discount_percentage = 0;
        new_item.discount_amount_per_item = 0;
        new_item.price_list_rate = item.rate;
        new_item.qty = item.actual_qty;
        new_item.amount = item.price_list_rate * item.actual_qty;
        new_item.uom = item.uom ? item.uom : item.stock_uom;
        new_item.actual_batch_qty = '';
        new_item.conversion_factor = 1;
        new_item.item_id = Date.now();
        return new_item;
      },
      update_item_detail(item) {
      const vm = this;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.get_item_detail',
        args: {
          doc: this.invoice_doc,
          data: {
            item_code: item.item_code,
            customer: this.invoice_doc.customer,
            doctype: 'Sales Invoice',
            name: this.invoice_doc.name,
            // name: 'New Sales Invoice 1',
            company: this.pos_profile.company,
            conversion_rate: 1,
            qty: item.qty,
            price_list_rate: item.price_list_rate,
            // child_docname: 'New Sales Invoice Item 1',
            child_docname: this.item_doc.item_name,
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
              vm.items_with_qty.forEach((item) => {
                const updated_item = r.message.find(
                  (element) => element.item_id == item.item_id
                );
                // item.actual_qty = updated_item.actual_qty;
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
      calc_sotck_gty(item, value) {
        item.stock_qty = item.conversion_factor * value;
      },
      calc_item_price(item) {
          if (!item.has_pricing_rule) {
            if (item.price_list_rate) {
              item.rate = item.price_list_rate;
            }
          }
      },
      submit_dialog(){
          let data = {};
          // let selected_items = [];
          console.log("Filtred Items");
          console.log(this.filtred_items);
          this.filtred_items.forEach((item) => {
              if (item.actual_qty!=0){
                // selected_items.push({'item_name': item.item_code, 'qty': item.actual_qty, 'rate': item.rate*item.actual_qty, 'uom': item.stock_uom, 'expense_account': this.pos_profile.write_off_account});
                console.log("Before submit " + item.item_name);
                console.log(item);
                this.add_item_details(item);
              }
          });
          console.log("items with qty");
          console.log(this.items_with_qty);
          data.item_code = this.item_doc.item_code;
          data.invoice_name = this.invoice_doc.name;
          data.selected_items = this.items_with_qty;
          // data.selected_items = selected_items;
          this.send_subitems_to_invoice(data);
          this.save_subitems(data);
          this.close_dialog();
      },
      get_new_item(item) {
          const new_item = { ...item };
          // if (!item.qty) {
          //   item.qty = 1;
          // }
          new_item.subitems_reference = '';
          new_item.stock_qty = item.qty;
          new_item.discount_amount = 0;
          new_item.selectedDiscount = null;
          new_item.discount_percentage = 0;
          new_item.discount_amount_per_item = 0;
          new_item.price_list_rate = item.rate;
          new_item.qty = item.actual_qty;
          new_item.uom = item.uom ? item.uom : item.stock_uom;
          new_item.actual_batch_qty = '';
          new_item.conversion_factor = 1;
          new_item.item_id = Date.now();
          if (new_item.has_batch_no || new_item.has_serial_no) {
            this.expanded.push(new_item);
          }
          return new_item;
      },
      send_subitems_to_invoice(data){
          evntBus.$emit("save_subitems", this.items, this.item_doc.item_code);
      },
      save_subitems(data){
          const vm = this;
          frappe.call({
            method: 'posawesome.posawesome.api.custom_posapp.save_subitems',
            args: {
              data: data
            },
            callback: function (r) {
              if (r.message) {
                  vm.invoice_doc = r.message.invoice_doc;
                  evntBus.$emit("submit_subitems", r.message);
                  evntBus.$emit('show_mesage', {
                    text: `Subitems added!`,
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
      get_item_groups(){
        const vm = this;
        vm.subitem_item_group.splice(0);
        vm.subitem_item_group.push('ALL');

        frappe.call({
            method: 'posawesome.posawesome.api.custom_posapp.get_product_item_groups',
            args: { item_doc: vm.item_doc },
            callback: function (r) {
              if (r.message) {
                r.message.forEach(element => {
                  if (element.item_group !== 'All Item Groups') {
                    vm.subitem_item_group.push(element.item_group);
                    vm.item_groups.push({"item_group":element.item_group});
                  }
                });
                }
              vm.select = vm.subitem_item_group[0];
              },
            });

      },
      get_items(){
            this.get_item_groups();
            this.items.splice(0);
            this.pos_profile.subitem_item_group = this.item_groups;
            this.pos_profile.subitem_trigger = true;

            const vm = this;
            frappe.call({
            method: 'posawesome.posawesome.api.custom_posapp.get_items',
            args: { pos_profile: vm.pos_profile },
            async: true,
            callback: function (r) {
              if (r.message) {
                  vm.items = r.message;
                }
              },
            });
      },
      get_existing_subitems(subitems){
        this.get_item_groups();
        this.filtred_items=subitems;
      },
      get_search(first_search) {
        let search_term = '';
          if (first_search && first_search.startsWith(this.pos_profile.posa_scale_barcode_start)) {
            search_term = first_search.substr(0, 7);
          }
          else {
            search_term = first_search;
          }
        return search_term;
      },
      reset(){
        this.filtred_items.forEach((element) => {
            element.actual_qty = 0;
        });
        //this.enableDisable = false;
        this.disable_qty = false;
      },
      check_item_subitems(){
        if(this.item_doc.subitems){
          this.get_existing_subitems(this.item_doc.subitems);
        }
        else{
          this.get_items();
        }
      }
  },
  created: function () {
    evntBus.$on('open_items_selector', (data) => {
        this.item_doc = data.item;
        this.pos_profile = data.pos_profile;
        this.invoice_doc = data.invoice_doc;
        this.check_item_subitems();
        this.dialog_state = true;
    });
  },
  computed: {
    remaining_qty(){
      let diff_qty = (
        this.item_doc.max_subitem_quantity - this.total_qty
      )
      return diff_qty;
    },
    total_qty(){
        let total = 0;
          this.filtred_items.forEach((element) => {
              total += element.actual_qty;
          }
        )
        return total;
    },
    disable_qty(){
      if (this.total_qty === this.item_doc.max_subitem_quantity){
        return true;
      }
      else {
        return false;
      }
    },
    filtred_items() {
      this.search = this.get_search(this.first_search);
      let filtred_list = [];
      let filtred_group_list = [];

      if (this.item_group != 'ALL') {
        filtred_group_list = this.items.filter((item) =>
          item.item_group.toLowerCase().includes(this.item_group.toLowerCase())
        );
      } else {
        filtred_group_list = this.items;
      }
      if (!this.search || this.search.length < 3) {
        return (filtred_list = filtred_group_list.slice(0, 50));
      } else if (this.search) {
        filtred_list = filtred_group_list.filter((item) => {
          let found = false;
          for (let element of item.item_barcode) {
            if (element.barcode == this.search) {
              found = true;
              break;
            }
          }
          return found;
        });
        if (filtred_list.length == 0) {
          filtred_list = filtred_group_list.filter((item) =>
            item.item_name.toLowerCase().includes(this.search.toLowerCase())
          );
          if (filtred_list.length == 0) {
            filtred_list = filtred_group_list.filter((item) =>
              item.item_code.toLowerCase().includes(this.search.toLowerCase())
            );
          }
        }
      }
      return filtred_list.slice(0, 50);
  },
  }
};
</script>