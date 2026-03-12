/**
 * AdminCard Component
 * 
 * A reusable card component for the admin interface.
 * Displays content in a styled container with optional title.
 */

// ==========================================
// Imports from Vue core
// ==========================================

import {
  // Vue 3 Composition API
  defineComponent as defineComponentFn,
  createElementBlock as createElementBlockFn,
  toDisplayString as toDisplayStringFn,
  openBlock as openBlockFn,
  createCommentVNode as createCommentVNodeFn,
  createElementVNode as createElementVNodeFn,
  normalizeClass as normalizeClassFn,
  createCommentVNode as createSlotFn,
  unref as unrefFn,
  _export_sfc as exportSfcFn
} from "./index-CP3Ltjo4.js"

// ==========================================
// Template Render Functions
// ==========================================

/**
 * Static class object for card container
 */
const cardClasses = {
  class: "admin-card"
}

/**
 * Static class object for card title
 */
const titleClasses = {
  key: 0,
  class: "card-title"
}

// ==========================================
// Component Definition
// ==========================================

/**
 * AdminCard Component Definition
 */
const AdminCardComponent = defineComponentFn({
  // Component name for debugging
  __name: "AdminCard",
  
  // Props definition
  props: {
    /**
     * Card title text
     */
    title: {},
    
    /**
     * Whether to remove default padding
     */
    noPadding: {
      type: Boolean
    }
  },
  
  // Setup function
  setup(props) {
    return (renderCtx, renderCache) => {
      return (
        // Open block for rendering
        openBlockFn(),
        
        // Create card container div
        createElementBlockFn("div", cardClasses, [
          
          // Conditional title rendering
          props.title
            ? (
              // Render title if provided
              openBlockFn(),
              createElementBlockFn(
                "h3",
                titleClasses,
                toDisplayStringFn(props.title),
                1
              )
            )
            : (
              // Empty comment if no title
              createCommentVNodeFn("", true)
            ),
          
          // Card content container
          createElementVNodeFn(
            "div",
            {
              class: normalizeClassFn([
                "card-content",
                {
                  // Apply no-padding class if prop is true
                  "no-padding": props.noPadding
                }
              ])
            },
            [
              // Render default slot content
              createSlotFn(
                renderCtx.$slots,
                "default",
                {},
                void 0
              )
            ],
            2
          )
        ])
      )
    }
  }
})

// ==========================================
// Export with Styles
// ==========================================

/**
 * Export with scoped styles attached
 */
const AdminCardExport = exportSfcFn(
  AdminCardComponent,
  [
    ["__scopeId", "data-v-da6c7108"]
  ]
)

/**
 * Named export for AdminCard
 */
export { AdminCardExport as A }

