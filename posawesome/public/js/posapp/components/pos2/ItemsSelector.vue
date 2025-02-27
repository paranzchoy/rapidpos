<template>
  <div>
    <v-card
      class="selection mx-auto grey lighten-5"
      style="max-height: 77vh; height: 77vh"
    >
      <v-progress-linear
        :active="loading"
        :indeterminate="loading"
        absolute
        top
        color="deep-purple accent-4"
      ></v-progress-linear>
      <v-row class="items px-2 py-1">
        <!-- QTY Filter -->
        <v-col cols="3" class="pb-0 mb-2">
          <v-text-field
            dense
            clearable
            outlined
            color="indigo"
            label="Qtty (F2)"
            background-color="white"
            hide-details
            v-model="item_qtty"
            ref="quantity_field"
          ></v-text-field>
        </v-col> 
        <!-- Search Item Filter -->
        <v-col cols="9" class="pb-0 mb-2">
          <v-text-field
            dense
            clearable
            autofocus
            outlined
            color="indigo"
            label="Search Items (F3)"
            hint="Search by item code, serial number, batch no or barcode"
            background-color="white"
            hide-details
            v-model="debounce_search"
            @keydown.esc="esc_event"
            @keydown.enter="enter_event"
            ref="search_items_field"
          ></v-text-field>
        </v-col>
        
        <v-col cols="12" class="pt-0 mt-0">
          <div fluid class="items" v-if="items_view == 'card'">
            <v-row dense class="overflow-y-auto" style="max-height: 67vh">
              <v-col
                v-for="(item, idx) in filtred_items"
                :key="idx"
                xl="2"
                lg="3"
                md="6"
                sm="6"
                cols="6"
                min-height="50"
              >
                <v-card hover="hover" @click="add_item(item)">
                  <v-img
                    :src="
                      item.image ||
                      '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'
                    "
                    class="white--text align-end"
                    gradient="to bottom, rgba(0,0,0,.2), rgba(0,0,0,.7)"
                    height="100px"
                  >
                    <v-card-text
                      v-text="item.item_name"
                      class="text-subtitle-2 px-1 pb-2"
                    ></v-card-text>
                  </v-img>
                  <v-card-text class="text--primary pa-1">
                    <div class="text-caption indigo--text accent-3">
                      {{ item.rate || 0 }} {{ item.currency || '' }}
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </div>
          <div fluid class="items" v-if="items_view == 'list'">
            <div class="my-0 py-0 overflow-y-auto" style="max-height: 67vh">
              <template>
                <v-data-table
                  :headers="items_headers"
                  :items="filtred_items"
                  item-key="item_code"
                  class="elevation-1"
                  :items-per-page="itemsPerPage"
                  hide-default-footer
                  @click:row="select_item"
                >
                  <template v-slot:item.rate="{ item }">
                    {{ formtCurrency(item.rate) }}
                  </template>
                  <template v-slot:item.actual_qty="{ item }">
                    {{ formtCurrency(item.actual_qty) }}
                  </template>
                </v-data-table>
              </template>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card>
    <v-card
      style="max-height: 13vh; height: 13vh"
      class="cards mb-0 mt-3 pa-2 grey lighten-5"
    >
      <v-row no-gutters>
        <v-col cols="12">
          <v-select
            :items="items_group"
            label="Items Group"
            dense
            outlined
            hide-details
            v-model="item_group"
          ></v-select>
        </v-col>
        <v-col cols="8" class="mt-1">
          <v-btn-toggle
            v-model="items_view"
            color="primary accent-3"
            group
            dense
            rounded
          >
            <v-btn value="card">Card View</v-btn>
            <v-btn value="list">List View</v-btn>
          </v-btn-toggle>
        </v-col>
        <v-col cols="4" class="mt-1">
          <v-btn-toggle
            v-model="favourites_view"
            color="success accent-3"
            group
            dense
            rounded
          >
            <v-btn value="True">Favourites</v-btn>
          </v-btn-toggle>
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>


<script>
import { evntBus } from '../../bus';
// import debounce from 'lodash.debounce'
import _ from 'lodash';
export default {
  data: () => ({
    pos_profile: '',
    items_view: 'list',
    item_group: 'ALL',
    favourites_view: false,
    loading: false,
    items_group: ['ALL'],
    items: [],
    search: '',
    item_qtty: 1,
    first_search: '',
    itemsPerPage: 1000,
    items_headers: [
      { text: 'Name', align: 'start', sortable: true, value: 'item_name' },
      { text: 'Rate', value: 'rate', align: 'start' },
      { text: 'Currency', value: 'currency', align: 'start' },
      { text: 'Available QTY', value: 'actual_qty', align: 'start' },
      { text: 'UOM', value: 'stock_uom', align: 'start' },
    ],
  }),

  watch: {
    filtred_items(data_value) {
      this.update_items_details(data_value);
    },
  },

  methods: {
    get_items() {
      if (!this.pos_profile) {
        console.log('No POS Profile');
        return;
      }
      const vm = this;
      this.loading = true;
      if (vm.pos_profile.posa_local_storage && localStorage.items_storage) {
        vm.items = JSON.parse(localStorage.getItem('items_storage'));
        vm.loading = false;
      }
      vm.pos_profile.subitem_trigger = false;
      frappe.call({
        // method: 'posawesome.posawesome.api.posapp.get_items',
        method: 'posawesome.posawesome.api.custom_posapp.get_items',
        args: { pos_profile: vm.pos_profile },
        callback: function (r) {
          if (r.message) {
            vm.items = r.message;
            vm.loading = false;
            // console.log('loadItmes');
            if (vm.pos_profile.posa_local_storage) {
              localStorage.setItem('items_storage', '');
              localStorage.setItem('items_storage', JSON.stringify(r.message));
            }
          }
        },
      });
    },
    get_items_groups() {
      if (!this.pos_profile) {
        console.log('No POS Profile');
        return;
      }
      if (this.pos_profile.item_groups.length > 0) {
        this.pos_profile.item_groups.forEach((element) => {
          if (element.item_group !== 'All Item Groups') {
            this.items_group.push(element.item_group);
          }
        });
      } else {
        const vm = this;
        frappe.call({
          method: 'posawesome.posawesome.api.posapp.get_items_groups',
          args: {},
          callback: function (r) {
            if (r.message) {
              r.message.forEach((element) => {
                vm.items_group.push(element.name);
              });
            }
          },
        });
      }
    },
    add_item(item) {
      evntBus.$emit('add_item', item);
      this.$refs.search_items_field.focus();
    },
    select_item(item){
      if(this.item_qtty){
        let qty = this.item_qtty
        const new_item = item;
        new_item.qty = flt(qty);

        this.add_item(new_item);
        // this.item_qtty = null;
      }
      else{
       this.add_item(item)
      }
    },
    enter_event() {
      if (!this.filtred_items.length || !this.first_search) {
        return;
      }

    let qty = this.get_item_qty(this.first_search);
    if(this.item_qtty)
    {
      qty = this.item_qtty;
    }

      // const qty = this.get_item_qty(this.first_search);
      const new_item = { ...this.filtred_items[0] };
      new_item.qty = flt(qty);
      new_item.item_barcode.forEach((element) => {
        if (this.search == element.barcode) {
          new_item.uom = element.posa_uom;
        }
      });
      this.add_item(new_item);
      this.search = null;
      this.first_search = null;
      this.debounce_search = null;
      this.item_qtty = null;

    },
    get_item_qty(first_search) {
      let scal_qty = 1;
      if (first_search.startsWith(this.pos_profile.posa_scale_barcode_start)) {
        let pesokg1 = first_search.substr(7, 5);
        let pesokg;
        if (pesokg1.startsWith('0000')) {
          pesokg = '0.00' + pesokg1.substr(4);
        } else if (pesokg1.startsWith('000')) {
          pesokg = '0.0' + pesokg1.substr(3);
        } else if (pesokg1.startsWith('00')) {
          pesokg = '0.' + pesokg1.substr(2);
        } else if (pesokg1.startsWith('0')) {
          pesokg =
            pesokg1.substr(1, 1) + '.' + pesokg1.substr(2, pesokg1.length);
        } else if (!pesokg1.startsWith('0')) {
          pesokg =
            pesokg1.substr(0, 2) + '.' + pesokg1.substr(2, pesokg1.length);
        }
        scal_qty = pesokg;
      }
      return scal_qty;
    },
    get_search(first_search) {
      let search_term = '';
      if (
        first_search &&
        first_search.startsWith(this.pos_profile.posa_scale_barcode_start)
      ) {
        search_term = first_search.substr(0, 7);
      } else {
        search_term = first_search;
      }
      return search_term;
    },
    esc_event() {
      this.search = null;
      this.first_search = null;
    },
    update_items_details(items) {
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
                (element) => element.item_code == item.item_code
              );
              item.actual_qty = updated_item.actual_qty;
              item.serial_no_data = updated_item.serial_no_data;
              item.batch_no_data = updated_item.batch_no_data;
              item.item_uoms = updated_item.item_uoms;
            });
          }
        },
      });
    },
    update_cur_items_details() {
      this.update_items_details(this.filtred_items);
    },
    scan_barcoud() {
      const vm = this;
      onScan.attachTo(document, {
        suffixKeyCodes: [],
        keyCodeMapper: function (oEvent) {
          oEvent.stopImmediatePropagation();
          return onScan.decodeKeyEvent(oEvent);
        },
        onScan: function (sCode) {
          setTimeout(() => {
            vm.trigger_onscan(sCode);
          }, 300);
        },
      });
    },
    trigger_onscan(sCode) {
      if (this.filtred_items.length == 0) {
        evntBus.$emit('show_mesage', {
          text: `No Item has this barcode "${sCode}"`,
          color: 'error',
        });
        frappe.utils.play_sound('error');
      } else {
        this.enter_event();
        this.debounce_search = null;
        this.search = null;
      }
    },
    formtCurrency(value) {
      value = parseFloat(value);
      return value.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    },

    gotoQuantityField(e) {
      if (e.key === 'F2') {
        e.preventDefault();

        // console.log({ e });
        this.$refs.quantity_field.focus();
      }
    },
    gotoSearchItemsField(e) {
      if (e.key === 'F3') {
        e.preventDefault();

        // console.log({ e });
        this.$refs.search_items_field.focus();
      }
    },
  },

  computed: {
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
    debounce_search: {
      get() {
        return this.first_search;
      },
      set: _.debounce(function (newValue) {
        this.first_search = newValue;
      }, 200),
    },
  },

  created: function () {
    this.$nextTick(function () {});
    evntBus.$on('register_pos_profile', (data) => {
      this.pos_profile = data.pos_profile;
      this.get_items();
      this.get_items_groups();
    });
    evntBus.$on('update_cur_items_details', () => {
      this.update_cur_items_details();
    });
     document.addEventListener('keydown', this.gotoSearchItemsField.bind(this));
     document.addEventListener('keydown', this.gotoQuantityField.bind(this));
  },

  destroyed() {
  //document.removeEventListener('keydown', this.KeyCustomer);
  document.removeEventListener('keydown', this.gotoSearchItemsField);
  document.removeEventListener('keydown', this.gotoQuantityField);    
  },
  mounted() {
    this.scan_barcoud();
  },
};
</script>

<style scoped>
</style>