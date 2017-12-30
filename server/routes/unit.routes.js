import { Router } from 'express'
import * as UnitController from '../controllers/unit.controller.js'
const router = new Router()

// Get all units
router.route('/units').get(UnitController.getUnits)

// Get one unit by cuid
router.route('/units/:id').get(UnitController.getUnit)

// Add a new unit
router.route('/units').post(UnitController.addUnit)

// Edit an unit
router.route('/units/:id').put(UnitController.editUnit)

// Delete a unit by cuid
router.route('/units/:id').delete(UnitController.deleteUnit)

export default router
