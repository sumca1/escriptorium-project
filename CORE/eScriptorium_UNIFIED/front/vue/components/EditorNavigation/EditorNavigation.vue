<template>
    <nav class="escr-editor-nav">
        <div class="escr-editor-nav-meta">
            <EscrBreadcrumbs
                :items="breadcrumbs"
            />
            <h1
                class="escr-element-title"
                :title="elementHeading"
            >
                {{ elementHeading }}
            </h1>
        </div>
        <div class="escr-editor-nav-actions">
            <VDropdown
                theme="escr-tooltip-small"
                placement="bottom"
                :distance="8"
                :triggers="['hover']"
            >
                <EscrButton
                    color="text"
                    :aria-label="getPrevOrNextString('left') + ' ' + $t('page')"
                    :on-click="() => loadPart(getPrevOrNextString('left'))"
                    :disabled="disabled || !hasPrevOrNextElement('left')"
                >
                    <template #button-icon>
                        <ArrowCircleLeftIcon />
                    </template>
                </EscrButton>
                <template #popper>
                    {{ getPrevOrNextTooltip('left') }}
                </template>
            </VDropdown>
            <VDropdown
                theme="escr-tooltip-small"
                placement="bottom"
                :distance="8"
                :triggers="['hover']"
            >
                <EscrButton
                    color="text"
                    :aria-label="getPrevOrNextString('right') + ' ' + $t('page')"
                    :on-click="() => loadPart(getPrevOrNextString('right'))"
                    :disabled="disabled || !hasPrevOrNextElement('right')"
                >
                    <template #button-icon>
                        <ArrowCircleRightIcon />
                    </template>
                </EscrButton>
                <template #popper>
                    {{ getPrevOrNextTooltip('right') }}
                </template>
            </VDropdown>
            <div
                v-if="partsCount"
                class="element-switcher"
            >
                <input
                    v-if="(elementNumber || elementNumber === 0) && elementNumber !== -1"
                    type="number"
                    :min="1"
                    :max="partsCount"
                    :value="elementNumber + 1"
                    @focus="() => setBlockShortcuts(true)"
                    @blur="() => setBlockShortcuts(false)"
                    @keydown="submitNavigation"
                >
                <span v-else>-</span> / {{ partsCount }}
            </div>
            <VDropdown
                class="new-section with-separator"
                theme="escr-tooltip-small"
                placement="bottom"
                :distance="8"
                :triggers="['hover']"
            >
                <EscrButton
                    color="text"
                    :aria-label="$t('View Element Details')"
                    :disabled="disabled"
                    :on-click="() => openModal('elementDetails')"
                >
                    <template #button-icon>
                        <InfoOutlineIcon />
                    </template>
                </EscrButton>
                <template #popper>
                    {{ $t('View Element Details') }}
                </template>
            </VDropdown>
            <VDropdown
                theme="escr-tooltip-small"
                placement="bottom"
                :distance="8"
                :triggers="['hover']"
            >
                <EscrButton
                    color="text"
                    :aria-label="$t('Manage Ontology')"
                    :disabled="disabled"
                    :on-click="() => openModal('ontology')"
                >
                    <template #button-icon>
                        <OntologyIcon />
                    </template>
                </EscrButton>
                <template #popper>
                    {{ $t('Ontology') }}
                </template>
            </VDropdown>
            <VDropdown
                theme="escr-tooltip-small"
                placement="bottom"
                :distance="8"
                :triggers="['hover']"
            >
                <EscrButton
                    color="text"
                    :aria-label="$t('Manage Transcriptions')"
                    :disabled="disabled"
                    :on-click="() => openModal('transcriptions')"
                >
                    <template #button-icon>
                        <TranscribeIcon />
                    </template>
                </EscrButton>
                <template #popper>
                    {{ $t('Transcriptions') }}
                </template>
            </VDropdown>
            <VDropdown
                theme="escr-tooltip-small"
                placement="bottom"
                :distance="8"
                :triggers="['hover']"
            >
                <EscrButton
                    color="text"
                    :aria-label="$t('cer.title')"
                    :disabled="disabled"
                    :on-click="() => openModal('cerAnalysis')"
                >
                    <template #button-icon>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                            <path d="M23 8c0 1.1-.9 2-2 2-.18 0-.35-.02-.51-.07l-3.56 3.55c.05.16.07.33.07.51 0 1.1-.9 2-2 2s-2-.9-2-2c0-.18.02-.35.07-.51l-2.55-2.55c-.16.05-.33.07-.51.07s-.35-.02-.51-.07l-4.55 4.56c.05.16.07.33.07.51 0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2c.18 0 .35.02.51.07l4.56-4.55C8.02 9.35 8 9.18 8 9c0-1.1.9-2 2-2s2 .9 2 2c0 .18-.02.35-.07.51l2.55 2.55c.16-.05.33-.07.51-.07s.35.02.51.07l3.56-3.55C19.02 8.35 19 8.18 19 8c0-1.1.9-2 2-2s2 .9 2 2z"/>
                        </svg>
                    </template>
                </EscrButton>
                <template #popper>
                    {{ $t('cer.title') }}
                </template>
            </VDropdown>
            <VDropdown
                class="new-section with-separator"
                theme="escr-tooltip-small"
                placement="bottom"
                :distance="8"
                :triggers="['hover']"
            >
                <EscrButton
                    color="primary"
                    :aria-label="$t('Switch to Unified Mode')"
                    :on-click="switchToUnifiedMode"
                >
                    <template #button-icon>
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                            <path d="M3 3h8v8H3V3zm10 0h8v8h-8V3zM3 13h8v8H3v-8zm10 0h8v8h-8v-8z"/>
                        </svg>
                    </template>
                </EscrButton>
                <template #popper>
                    {{ $t('Switch to Unified Interface (ABBYY Style)') }}
                </template>
            </VDropdown>
        </div>
    </nav>
</template>
<script>
import { Dropdown as VDropdown } from "floating-vue";
import { mapActions, mapMutations, mapState } from "vuex";
import ArrowCircleLeftIcon from "../Icons/ArrowCircleLeftIcon/ArrowCircleLeftIcon.vue";
import ArrowCircleRightIcon from "../Icons/ArrowCircleRightIcon/ArrowCircleRightIcon.vue";
import EscrBreadcrumbs from "../Breadcrumbs/Breadcrumbs.vue";
import EscrButton from "../Button/Button.vue";
import InfoOutlineIcon from "../Icons/InfoOutlineIcon/InfoOutlineIcon.vue";
import OntologyIcon from "../Icons/OntologyIcon/OntologyIcon.vue";
import TranscribeIcon from "../Icons/TranscribeIcon/TranscribeIcon.vue";
import "./EditorNavigation.css";

export default {
    name: "EscrEditorNavigation",
    components: {
        ArrowCircleLeftIcon,
        ArrowCircleRightIcon,
        EscrBreadcrumbs,
        EscrButton,
        InfoOutlineIcon,
        OntologyIcon,
        TranscribeIcon,
        VDropdown,
    },
    props: {
        /**
         * True if all buttons and tools should be disabled
         */
        disabled: {
            type: Boolean,
            required: true,
        },
    },
    computed: {
        ...mapState({
            documentId: (state) => state.document.id,
            documentName: (state) => state.document.name,
            elementFilename: (state) => state.parts.filename,
            elementNumber: (state) => state.parts.order,
            elementPk: (state) => state.parts.pk,
            elementTitle: (state) => state.parts.title,
            nextPart: (state) => state.parts.next,
            partsCount: (state) => state.document.partsCount,
            prevPart: (state) => state.parts.previous,
            projectName: (state) => state.document.projectName,
            projectSlug: (state) => state.document.projectSlug,
            readDirection: (state) => state.document.readDirection,
        }),
        breadcrumbs() {
            let breadcrumbs = [{ title: this.$t("Loading...") }];
            if (this.projectName && this.projectSlug && this.documentName && this.documentId) {
                breadcrumbs = [
                    { title: this.$t("My Projects"), href: "/projects" },
                    {
                        title: this.projectName,
                        href: `/project/${this.projectSlug}`
                    },
                    {
                        title: this.documentName,
                        href: `/document/${this.documentId}`
                    },
                    {
                        title: this.$t("Images"),
                        // include select=pk to select the image being edited in the list
                        href: `/document/${this.documentId}/images${
                            this.elementPk ? "?select=" + this.elementPk : ""
                        }`,
                    },
                    {
                        title: this.elementTitle ? this.elementTitle : "Loading...",
                    },
                ];
            }
            return breadcrumbs;
        },
        elementHeading() {
            return (this.elementTitle && this.elementFilename)
                ? `${this.elementTitle} – ${this.elementFilename}`
                : "Loading...";
        },
    },
    methods: {
        ...mapActions("parts", ["loadPart", "loadPartByOrder"]),
        ...mapActions("globalTools", ["openModal"]),
        ...mapMutations("document", ["setBlockShortcuts"]),
        hasPrevOrNextElement(direction) {
            if (direction === "left") {
                // left = next in RTL, previous in LTR
                return this.readDirection === "rtl" ? this.nextPart : this.prevPart;
            }else {
                // right = previous in RTL, next in LTR
                return this.readDirection === "rtl" ? this.prevPart : this.nextPart;
            }
        },
        getPrevOrNextString(direction) {
            if (direction === "left") {
                // left = next in RTL, previous in LTR
                return this.readDirection === "rtl" ? this.$t("next") : this.$t("previous");
            } else {
                // right = previous in RTL, next in LTR
                return this.readDirection === "rtl" ? this.$t("previous") : this.$t("next");
            }
        },
        getPrevOrNextTooltip(direction) {
            if (direction === "left") {
                // left = next in RTL, previous in LTR
                return this.readDirection === "rtl"
                    ? this.$t("Next Element (PgDn)")
                    : this.$t("Previous Element (PgUp)");
            } else {
                // right = previous in RTL, next in LTR
                return this.readDirection === "rtl"
                    ? this.$t("Previous Element (PgUp)")
                    : this.$t("Next Element (PgDn)");
            }
        },
        submitNavigation(e) {
            const num = parseInt(e.target.value);
            if (e.key === "Enter" && num && num > 0 && num <= this.partsCount) {
                this.loadPartByOrder(num - 1);
            }
        },
        switchToUnifiedMode() {
            // Save preference
            userProfile.set('editor-mode', 'unified');
            // Reload page with mode parameter
            const url = new URL(window.location.href);
            url.searchParams.set('mode', 'unified');
            window.location.href = url.toString();
        }
    }
}
</script>
