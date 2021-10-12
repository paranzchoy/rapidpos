<template>
  <v-row class="items px-2 py-1">
    <v-col cols="12" class="pb-0 mb-2">
      <v-autocomplete
        dense
        clearable
        auto-select-first
        outlined
        color="indigo"
        label="Customer (F4)"
        hint="Search, select, or add customer. Default customer is 'Walk-in'"
        v-model="customer"
        :items="customers"
        item-text="customer_name"
        item-value="name"
        background-color="white"
        no-data-text="Customer not found"
        :filter="customFilter"
        :disabled="readonly"
        ref="customer_field"
      >
        <template v-slot:item="data">
          <template>
            <v-list-item-content>
              <v-list-item-title
                class="indigo--text subtitle-1"
                v-html="data.item.customer_name"
              ></v-list-item-title>
              <v-list-item-subtitle
                v-if="data.item.customer_name != data.item.name"
                v-html="`ID: ${data.item.name}`"
              ></v-list-item-subtitle>
              <v-list-item-subtitle
                v-if="data.item.tax_id"
                v-html="`TAX ID: ${data.item.tax_id}`"
              ></v-list-item-subtitle>
              <v-list-item-subtitle
                v-if="data.item.email_id"
                v-html="`Email: ${data.item.email_id}`"
              ></v-list-item-subtitle>
              <v-list-item-subtitle
                v-if="data.item.mobile_no"
                v-html="`Mobile No: ${data.item.mobile_no}`"
              ></v-list-item-subtitle>
            </v-list-item-content>
          </template>
        </template>
        <template v-slot:append-outer>
          <v-slide-x-reverse-transition mode="out-in">
            <v-icon @click="new_customer">mdi-plus</v-icon>
          </v-slide-x-reverse-transition>
        </template>
      </v-autocomplete>
    </v-col>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
export default {
  data: () => ({
    pos_profile: '',
    customers: [],
    customer: '',
    readonly: false,
  }),

  methods: {
    get_customer_names() {
      console.log("get_customer_names()");
      const vm = this;
      if (vm.pos_profile.posa_local_storage && localStorage.customer_storage) {
        vm.customers = JSON.parse(localStorage.getItem('customer_storage'));
      }
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.get_customer_names',
        args: {
          pos_profile: vm.pos_profile,
        },
        callback: function (r) {
          if (r.message) {
            vm.customers = r.message;
            console.log('loadCustomers');
            if (vm.pos_profile.posa_local_storage) {
              localStorage.setItem('customer_storage', '');
              localStorage.setItem(
                'customer_storage',
                JSON.stringify(r.message)
              );
            }

            ///CUSTOM
            vm.set_default_customer();
          }
        },
      });
    },
    new_customer() {
      evntBus.$emit('open_new_customer');
    },
    customFilter(item, queryText, itemText) {
      const textOne = item.customer_name
        ? item.customer_name.toLowerCase()
        : '';
      const textTwo = item.tax_id ? item.tax_id.toLowerCase() : '';
      const textThree = item.email_id ? item.email_id.toLowerCase() : '';
      const textFour = item.mobile_no ? item.mobile_no.toLowerCase() : '';
      const textFifth = item.name.toLowerCase();
      const searchText = queryText.toLowerCase();

      return (
        textOne.indexOf(searchText) > -1 ||
        textTwo.indexOf(searchText) > -1 ||
        textThree.indexOf(searchText) > -1 ||
        textFour.indexOf(searchText) > -1 ||
        textFifth.indexOf(searchText) > -1
      );
    },

    gotoCustomerField(e) {
      if (e.key === 'F4') {
        e.preventDefault();

        console.log({ e });
        this.$refs.customer_field.focus();
      }
    },
    openNewCustomer(e) {
      // if (e.key === 'c' && (e.ctrlKey || e.metaKey)) {
      if (e.key === 'F12') {
        e.preventDefault();
        console.log({ e });

        this.new_customer();
      }
    },
    set_default_customer() {
      evntBus.$emit("set_customer_default");
    }  
  },

  computed: {},

  created: function () {
    console.log("mounting Customer2.vue...");


    this.$nextTick(function () {
      evntBus.$on('register_pos_profile', (pos_profile) => {
        this.pos_profile = pos_profile;
        this.get_customer_names();
      });
      evntBus.$on('set_customer', (customer) => {
        this.customer = customer;
      });
      evntBus.$on('add_customer_to_list', (customer) => {
        this.customers.push(customer);
      });
      evntBus.$on('set_customer_readonly', (value) => {
        this.readonly = value;
      });
      evntBus.$on('set_customer_default', () => {
        const defaultCustomerName = 'WalkIn';
        // console.log(`# of Customers: ${this.customers.length}`);
        
        const defaultCustomer = this.customers.find(c => c.customer_name === defaultCustomerName);
        if(defaultCustomer)
        {
          // console.log(`Default customer: ${defaultCustomer.customer_name}`);        
          evntBus.$emit("update_customer", defaultCustomer.customer_name);
        }

      });
    });

     //document.addEventListener('keydown', this.KeyCustomer.bind(this));
      document.addEventListener('keydown', this.gotoCustomerField.bind(this));
      document.addEventListener('keydown', this.openNewCustomer.bind(this));    
  },

  destroyed() {
      //document.removeEventListener('keydown', this.KeyCustomer);
      document.removeEventListener('keydown', this.gotoCustomerField);
      document.removeEventListener('keydown', this.openNewCustomer);
    },
  watch: {
    customer() {
      evntBus.$emit('update_customer', this.customer);
    },
  },
};
</script>