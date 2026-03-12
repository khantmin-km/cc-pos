/**
 * StatusBadge Component
 * 
 * Displays a colored badge based on status value.
 * Maps various statuses to appropriate colors and labels.
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
  // Class/Style handling
  normalizeClass as normalizeClassFn,
  toDisplayString as toDisplayStringFn,
  // Reactivity
  computed as computedFn,
  // Export helper
  _export_sfc as exportSfcFn
} from "./index-CP3Ltjo4.js"

// ==========================================
// Component Definition
// ==========================================

/**
 * Status Badge Component
 */
const StatusBadgeComponent = defineComponentFn({
  // Component metadata
  __name: "StatusBadge",

  // Props
  props: {
    /**
     * Status value to display
     */
    status: {},

    /**
     * Badge type category
     */
    type: {}
  },

  // Setup
  setup(props) {
    // --------------------------------
    // Computed Properties
    // --------------------------------

    /**
     * Compute CSS class based on status
     */
    const statusClass = computedFn(() => {
      // Map of status values to CSS classes
      const statusClassMap = {
        // Order item statuses
        pending: "status-orange",
        kitchen_printed: "status-orange",
        served: "status-green",
        removed: "status-gray",

        // Billing statuses
        active: "status-green",
        bill_requested: "status-red",
        payment_completed: "status-green",
        closed: "status-gray",

        // Table statuses
        available: "status-green",
        reserved: "status-orange",
        occupied: "status-red",

        // Menu item statuses
        available_menu: "status-green",
        unavailable: "status-gray"
      }

      // Get class from map or default to gray
      const statusColorClass = statusClassMap[props.status]
        || "status-gray"

      // Return full class string
      return `status-badge ${statusColorClass}`
    })

    /**
     * Compute display label based on status
     */
    const statusLabel = computedFn(() => {
      // Map of status values to display labels
      const statusLabelMap = {
        // Order item statuses
        pending: "Pending",
        kitchen_printed: "Kitchen Printed",
        served: "Served",
        removed: "Removed",

        // Billing statuses
        active: "Active",
        bill_requested: "Bill Requested",
        payment_completed: "Payment Completed",
        closed: "Closed",

        // Table statuses
        available: "Available",
        reserved: "Reserved",
        occupied: "Occupied",

        // Menu item statuses
        available_menu: "Available",
        unavailable: "Unavailable"
      }

      // Get label from map or use raw status
      return statusLabelMap[props.status]
        || props.status
    })

    // --------------------------------
    // Render Function
    // --------------------------------

    return (renderCtx, renderCache) => {
      return (
        // Open render block
        openBlockFn(),

        // Create span element
        createElementBlockFn(
          "span",
          {
            // Dynamic class binding
            class: normalizeClassFn(statusClass.value)
          },
          // Text content
          toDisplayStringFn(statusLabel.value),
          // Patch flag for dynamic class
          3
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
const StatusBadgeExport = exportSfcFn(
  StatusBadgeComponent,
  [
    ["__scopeId", "data-v-8c4fac49"]
  ]
)

/**
 * Named export
 */
export { StatusBadgeExport as S }
