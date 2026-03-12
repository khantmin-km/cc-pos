/**
 * ConfirmModal Component
 * 
 * A reusable confirmation dialog modal.
 * Provides confirm/cancel actions with customizable text.
 */

/*
  Note: Empty CSS placeholder - styles handled elsewhere
*/

// ==========================================
// Vue Imports
// ==========================================

import {
  // Component definition
  defineComponent as defineComponentFn,
  // Rendering
  openBlock as openBlockFn,
  createElementBlock as createElementBlockFn,
  // Event handling
  withModifiers as withModifiersFn,
  // Element creation
  createElementVNode as createElementFn,
  // Text display
  toDisplayString as toDisplayStringFn,
  // Class normalization
  normalizeClass as normalizeClassFn,
  // Export helper
  _export_sfc as exportSfcFn
} from "./index-CP3Ltjo4.js"

// ==========================================
// Template Constants
// ==========================================

/**
 * CSS classes for modal content container
 */
const modalContentClasses = {
  class: "modal-content"
}

/**
 * CSS classes for modal title
 */
const modalTitleClasses = {
  class: "modal-title"
}

/**
 * CSS classes for modal message
 */
const modalMessageClasses = {
  class: "modal-message"
}

/**
 * CSS classes for modal actions container
 */
const modalActionsClasses = {
  class: "modal-actions"
}

// ==========================================
// Component Definition
// ==========================================

/**
 * Confirm Modal Component
 */
const ConfirmModalComponent = defineComponentFn({
  // Component metadata
  __name: "ConfirmModal",

  // Props
  props: {
    /**
     * Modal title text
     */
    title: {},

    /**
     * Modal message/body text
     */
    message: {},

    /**
     * Confirm button text
     */
    confirmText: {},

    /**
     * Cancel button text
     */
    cancelText: {},

    /**
     * Whether this is a danger action (red styling)
     */
    danger: {
      type: Boolean
    }
  },

  // Events emitted
  emits: [
    /**
     * Emitted when user confirms
     */
    "confirm",

    /**
     * Emitted when user cancels
     */
    "cancel"
  ],

  // Setup
  setup(props, { emit: emitFn }) {
    // Store emit function
    const emit = emitFn

    // --------------------------------
    // Event Handlers
    // --------------------------------

    /**
     * Handle confirm button click
     */
    function handleConfirm() {
      emit("confirm")
    }

    /**
     * Handle cancel button click
     */
    function handleCancel() {
      emit("cancel")
    }

    // --------------------------------
    // Render Function
    // --------------------------------

    return (renderCtx, renderCache) => {
      return (
        // Open render block
        openBlockFn(),

        // Create overlay div
        createElementBlockFn(
          "div",
          {
            class: "modal-overlay",
            // Close on overlay click (with self modifier)
            onClick: withModifiersFn(
              handleCancel,
              ["self"]
            )
          },
          [
            // Modal content container
            createElementFn("div", modalContentClasses, [
              // Modal title
              createElementFn(
                "h3",
                modalTitleClasses,
                toDisplayStringFn(props.title),
                1
              ),

              // Modal message
              createElementFn(
                "p",
                modalMessageClasses,
                toDisplayStringFn(props.message),
                1
              ),

              // Action buttons container
              createElementFn(
                "div",
                modalActionsClasses,
                [
                  // Cancel button
                  createElementFn(
                    "button",
                    {
                      type: "button",
                      class: "btn btn-cancel",
                      onClick: handleCancel
                    },
                    toDisplayStringFn(
                      props.cancelText || "Cancel"
                    ),
                    1
                  ),

                  // Confirm button
                  createElementFn(
                    "button",
                    {
                      type: "button",
                      // Dynamic class based on danger prop
                      class: normalizeClassFn([
                        "btn",
                        props.danger
                          ? "btn-danger"
                          : "btn-confirm"
                      ]),
                      onClick: handleConfirm
                    },
                    toDisplayStringFn(
                      props.confirmText || "Confirm"
                    ),
                    3
                  )
                ]
              )
            ])
          ]
        )
      )
    }
  }
})

// ==========================================
// Export with Styles
// ==========================================

/**
 * Export component with scoped styles
 */
const ConfirmModalExport = exportSfcFn(
  ConfirmModalComponent,
  [
    ["__scopeId", "data-v-07e48eea"]
  ]
)

/**
 * Named export
 */
export { ConfirmModalExport as C }

