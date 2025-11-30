<template>
  <ExtraNav v-bind="$attrs" v-on="$listeners" />
</template>

<script>
import ExtraNav from '../../vue/components/ExtraNav.vue';

export default {
  name: 'ExtraNavShim',
  components: { ExtraNav },
};
</script>

<style scoped>
/* shim to satisfy build tests */
</style>
