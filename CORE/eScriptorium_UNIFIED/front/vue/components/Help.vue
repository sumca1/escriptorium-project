<template>
    <div v-html="helpContent"></div>
</template>

<script>
export default {
    computed: {
        helpContent() {
            return this.translate('baseline_editor_help');
        }
    },
    methods: {
        translate(key) {
            return window.EDITOR_TRANSLATIONS && window.EDITOR_TRANSLATIONS[key] ? window.EDITOR_TRANSLATIONS[key] : key;
        }
    }
}
</script>

<style scoped>
</style>
