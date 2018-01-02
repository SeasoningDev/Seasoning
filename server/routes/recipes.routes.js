import { Router } from 'express'
import * as RecipeController from '../controllers/recipe.controller.js'
const router = new Router()

// Calculate a footprint
router.route('/recipes').post(
  RecipeController.calculateFootprint.validators,
  RecipeController.calculateFootprint
)

export default router
