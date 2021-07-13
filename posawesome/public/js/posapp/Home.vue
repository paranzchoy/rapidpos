<template>
  <v-app class="container1">
    <v-main>
      <Navbar @changePage="setPage($event)"></Navbar>
      <keep-alive>
        <component v-bind:is="page" class="mx-4 md-4"></component>
      </keep-alive>
    </v-main>
  </v-app>
</template>

<script>
import Navbar from "./components/pos2/Navbar2.vue";
import POS from "./components/pos2/Pos2.vue";

export default {
  data: function () {
    return {
      page: "POS",
    };
  },
  components: {
    Navbar,
    POS,
  },
  methods: {
    setPage(page) {
      this.page = page;
    },
    remove_frappe_nav() {
      this.$nextTick(function () {
        $(".page-head").remove();
        $(".navbar.navbar-default.navbar-fixed-top").remove();
      });
    },
  },
  mounted() {
    this.remove_frappe_nav();
  },
  updated() {},
  created: function () {
    setTimeout(() => {
      this.remove_frappe_nav();
    }, 1000);
  },
};
</script>

<style scoped>
.container1 {
  margin-top: 0px;
}
</style>