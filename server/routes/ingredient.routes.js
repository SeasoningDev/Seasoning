import { Router } from 'express'
import * as IngredientController from '../controllers/ingredient.controller.js'
const router = new Router()

// Get all ingredients
router.route('/ingredients').get(
  IngredientController.getIngredients.validators,
  IngredientController.getIngredients
)

// Get one ingredient by id
router.route('/ingredients/:id').get(
  IngredientController.getIngredient.validators,
  IngredientController.getIngredient
)

// Add a new ingredient
router.route('/ingredients').post(
  IngredientController.addIngredient.validators,
  IngredientController.addIngredient
)

// Edit an ingredient
router.route('/ingredients/:id').put(
  IngredientController.editIngredient.validators,
  IngredientController.editIngredient
)

// Delete a ingredient by cuid
router.route('/ingredients/:id').delete(
  IngredientController.deleteIngredient.validators,
  IngredientController.deleteIngredient
)

export default router
