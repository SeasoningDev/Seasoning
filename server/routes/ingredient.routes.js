import { Router } from 'express'
import * as IngredientController from '../controllers/ingredient.controller.js'
const router = new Router()

// Get all ingredients
router.route('/ingredients').get(IngredientController.getIngredients)

// Get one ingredient by id
router.route('/ingredients/:id').get(IngredientController.getIngredient)

// Add a new ingredient
router.route('/ingredients').post(IngredientController.addIngredient)

// Edit an ingredient
router.route('/ingredients/:id').put(IngredientController.editIngredient)

// Delete a ingredient by cuid
router.route('/ingredients/:id').delete(IngredientController.deleteIngredient)

export default router
