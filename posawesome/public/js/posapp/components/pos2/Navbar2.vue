<template>
  <nav>
    <v-app-bar app height="40" class="elevation-2" style="background-image: linear-gradient(to right, white, #f2ce2c);">
      <v-app-bar-nav-icon
        @click.stop="mini = !mini"
        class="grey--text"
      ></v-app-bar-nav-icon>
      <v-toolbar-title class="text-uppercase indigo--text">
        <span><img src="/assets/rapidposcustom/images/Jacobs-removebg-preview.png"  class="brand-image" style="max-width: 100px; max-height: 100px;"></span>
        <span class="font-weight-light"><img src="/assets/rapidposcustom/images/Breadnuts-removebg-preview.png"  class="brand-image" style="max-width: 200px; max-height: 100px;"></span>
        <!-- <span><img src="/assets/rapidposcustom/images/TacurongLogo.png"  class="brand-image" style="max-width: 25px; max-height: 25px;"></span>
        <span class="font-weight-bold" style="color:white;">Tacurong Doctors Hospital Pharmacy</span> -->
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <div class="text-center">
        <v-menu offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn color="grey" dark text v-bind="attrs" v-on="on">Menu</v-btn>
          </template>
          <v-card class="mx-auto" max-width="300" tile>
            <v-list dense>
              <v-list-item-group v-model="menu_item" color="primary">
                  <!-- IDLE DIALOG -->
                  <v-list-item @click="idle_dialog">
                    <v-list-item-icon>
                      <v-icon>mdi-clock</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title>Idle &nbsp;&nbsp; <span class="spacer"  style="color:gray">Ctrl+I</span></v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                  <!-- REPRINT INVOICE -->
                  <v-list-item @click="show_reprint">
                    <v-list-item-icon>
                      <v-icon>mdi-printer-check</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title>Reprint &nbsp;&nbsp; <span  style="color:gray">Ctrl+R</span></v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                  <!-- XREADING DIALOG -->
                  <v-list-item @click="xreading_print_dialog">
                    <v-list-item-icon>
                      <v-icon>mdi-printer</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title>X-Reading &nbsp;&nbsp; <span  style="color:gray">Ctrl+X</span></v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                  <!-- ZREADING DIALOG -->
                  <!-- <v-list-item @click="zreading_print_dialog">
                    <v-list-item-icon>
                      <v-icon>mdi-printer-pos</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title>Z-Reading</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item> -->
                  <!-- CASH WITHDRAWAL DIALOG -->
                  <v-list-item @click="cash_withdrawal">
                    <v-list-item-icon>
                      <v-icon>mdi-cash</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title>Cash Withdrawal &nbsp;&nbsp; <span style="color:gray">Ctrl+L</span></v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                <!-- <v-list-item
                  @click="close_shift_dialog"
                  v-if="!pos_profile.posa_hide_closing_shift"
                > -->
                <v-list-item
                  @click="close_shift_dialog"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-folder-open</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>Close Shift</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item
                  @click="close_shift_dialog2"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-folder-open</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>Close Shift v2</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-divider class="my-0"></v-divider>
                <v-list-item @click="help_modal">
                  <v-list-item-icon>
                    <v-icon>mdi-help-circle</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>Help &nbsp;&nbsp; <span  style="color:gray">F1</span></v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
                <v-divider class="my-0"></v-divider>
                  <!-- ABOUT -->
                  <v-list-item @click="go_about">
                    <v-list-item-icon>
                      <v-icon>mdi-information-outline</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title>About</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-menu>
      </div>
<!-- // TEST COMMIT1 -->
      <!-- <div class="text-center">
        <v-menu offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn color="grey" dark text v-bind="attrs" v-on="on">Pages</v-btn>
          </template>
          <v-card class="mx-auto" max-width="300" tile>
            <v-list dense>
              <v-list-item-group v-model="item" color="primary">
                <v-list-item
                  v-for="(item, index) in items"
                  :key="item.text"
                  @click="[changePage(item.text), (item = index)]"
                >
                  <v-list-item-icon>
                    <v-icon v-text="item.icon"></v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title v-text="item.text"></v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-card>
        </v-menu>
      </div> -->
      <v-btn text color="grey" @click="go_desk">
        <span right>Desk</span>
      </v-btn>
    </v-app-bar>
    <v-navigation-drawer
      v-model="drawer"
      :mini-variant.sync="mini"
      app
      class="indigo margen-top"
      style="background-image: linear-gradient(#a4de1d, #ffffff);"
    >
      <v-list dark>
        <v-list-item class="px-2">
          <v-list-item-avatar>
            <v-img :src="company_img"></v-img>
          </v-list-item-avatar>

          <v-list-item-title>{{ company }}</v-list-item-title>

          <v-btn icon @click.stop="mini = !mini">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </v-list-item>
        <!-- <MyPopup/> -->
        <v-list-item-group v-model="item" color="white">
          <v-list-item
            v-for="item in items"
            :key="item.text"
            @click="changePage(item.text)"
          >
            <v-list-item-icon>
              <v-icon v-text="item.icon"></v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title v-text="item.text"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
    <v-snackbar v-model="snack" :timeout="5000" :color="snackColor" top right>
      {{ snackText }}
      <!-- <template v-slot:action="{ attrs }"> -->
      <!-- <v-btn v-bind="attrs" text @click="snack = false">Close</v-btn> -->
      <!-- </template> -->
    </v-snackbar>
  </nav>
</template>

<script>
import { evntBus } from '../../bus';

export default {
  // components: {MyPopup},
  data() {
    return {
      drawer: true,
      mini: true,
      item: 0,
      items: [{ text: 'POS', icon: 'mdi-point-of-sale' }],
      page: '',
      fav: true,
      menu: false,
      message: false,
      hints: true,
      menu_item: 0,
      snack: false,
      snackColor: '',
      snackText: '',
      company: 'POS Awesome',
      company_img: '/assets/erpnext/images/erp-icon.svg',
      pos_profile: '',
    };
  },
  methods: {
    changePage(key) {
      this.$emit('changePage', key);
    },
    go_desk() {
      frappe.set_route('/app');
      location.reload();
    },
    go_about() {
      const win = window.open(
        'https://www.facebook.com/rapidsignalelectronics',
        '_blank'
      );
      win.focus();
    },
    close_shift_dialog() {
      evntBus.$emit('open_closing_dialog');
    },
    close_shift_dialog2() {
      evntBus.$emit('open_closing_dialog2');
    },
    show_mesage(data) {
      this.snack = true;
      this.snackColor = data.color;
      this.snackText = data.text;
    },
    // CASH WITHDRAWAL
    cash_withdrawal() {
      evntBus.$emit('open_withdrawal_2');
    },
    // CASH WITHDRAWAL Shortcut Key
    withdraw(e) {
      if (e.key === 'l' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        console.log({ e });

        this.cash_withdrawal();
      }
    },
    // XREADING
    xreading_print_dialog() {
      evntBus.$emit("open_xreading_dialog");
    },
    // XREADING Shortcut Key
    openXReading(e) {
      if (e.key === 'x' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        console.log({ e });

        this.xreading_print_dialog();
      }
    },
    // ZREADING
    openZReading(e) {
      if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        console.log({ e });
        this.xreading_print_dialog();
      }
    },
    // REPRINT INVOICE
    show_reprint(){
      evntBus.$emit("open_reprint_dialog", this.company);
    },
    // REPRINT INVOICE Shortcut Key
    openReprint(e) {
      if (e.key === 'r' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        console.log({ e });

        this.show_reprint();
      }
    },
    // IDLE
    idle_dialog() {
    evntBus.$emit("open_IdleDialog");
    },
    // HELP
    help_modal() {
      evntBus.$emit('open_help');
    },
    // HELP Shortcut Key
    openHelp(e) {
      if (e.key === 'F1') {
        e.preventDefault();
        console.log({ e });

        this.help_modal();
      }
    }, 
  },
  created: function () {
    console.log("mounting NavBar2...");

    this.$nextTick(function () {
      evntBus.$on('show_mesage', (data) => {
        this.show_mesage(data);
      });
      evntBus.$on('set_company', (data) => {
        this.company = data.name;
        this.company_img = data.company_logo
          ? data.company_logo
          : this.company_img;
      });
      evntBus.$on('register_pos_profile', (data) => {
        this.pos_profile = data.pos_profile;
        // this.pos_opening_shift = data.pos_opening_shift;
      });
    });

    document.addEventListener('keydown', this.openHelp.bind(this));    
    document.addEventListener('keydown', this.withdraw.bind(this));    
    document.addEventListener('keydown', this.openReprint.bind(this));    
    document.addEventListener('keydown', this.openXReading.bind(this));    
  },
  
  destroyed() {
    document.removeEventListener('keydown', this.openHelp);
    document.removeEventListener('keydown', this.withdraw);
    document.removeEventListener('keydown', this.openReprint);
    document.removeEventListener('keydown', this.openXReading);
  }
};
</script>

<style scoped>
.margen-top {
  margin-top: 0px;
}
</style>