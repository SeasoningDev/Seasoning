import { Router } from 'express'
import * as UnitController from '../controllers/unit.controller.js'
const router = new Router()

// Get all units
router.route('/units').get(
  UnitController.getUnits.validators,
  UnitController.getUnits
)

// Get one unit by cuid
router.route('/units/:id').get(
  UnitController.getUnit.validators,
  UnitController.getUnit
)

// Add a new unit
router.route('/units').post(
  UnitController.addUnit.validators,
  UnitController.addUnit
)

// Edit an unit
router.route('/units/:id').put(
  UnitController.editUnit.validators,
  UnitController.editUnit
)

// Delete a unit by cuid
router.route('/units/:id').delete(
  UnitController.deleteUnit.validators,
  UnitController.deleteUnit
)

export default router
