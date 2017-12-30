import Ingredient from '../models/ingredient'
import sanitizeHtml from 'sanitize-html'
import toJson from '../util/mongooseRestExport'

/**
 * Get all ingredients
 * @param req
 * @param res
 * @returns void
 */
export async function getIngredients (req, res) {
  try {
    // TODO: start, end, order, sort parameters

    const ingredients = await Ingredient.find()
      .populate('units.unit')
      .sort('name')
      .lean()
      .exec()

    return res
      .status(200)
      .header('X-Total-Count', ingredients.length)
      .json(ingredients.map(i => toJson(i)))
  } catch (err) {
    res.status(500).send(err)
  }
}

/**
 * Add a new ingredient
 * @param req
 * @param res
 * @returns void
 */
export async function addIngredient (req, res) {
  try {
    if (!req.body.names || !req.body.footprint) {
      res.status(403).end()
    }

    const newIngredient = new Ingredient(req.body)

    // Let's sanitize inputs
    newIngredient.name = sanitizeHtml(newIngredient.name)
    newIngredient.footprint = parseInt(sanitizeHtml(newIngredient.footprint))

    const saved = await newIngredient.save()

    res.json(toJson(saved.toJSON()))
  } catch (err) {
    console.log(err.stack)
    console.log(err)
    return res.status(500).send(err)
  }
}

/**
 * Get a single ingredient
 * @param req
 * @param res
 * @returns void
 */
export async function getIngredient (req, res) {
  try {
    const ingredient = await Ingredient.findById(req.params.id)
      .lean()
      .exec()

    return res.status(200).json(toJson(ingredient))
  } catch (err) {
    res.status(500).send(err)
  }
}

/**
 * Get a single ingredient
 * @param req
 * @param res
 * @returns void
 */
export async function editIngredient (req, res) {
  try {
    if (!req.body.names || !req.body.footprint) {
      res.status(403).end()
    }

    const saved = await Ingredient.findByIdAndUpdate(req.params.id, req.body)

    res.json(toJson(saved.toJSON()))
  } catch (err) {
    console.log(err.stack)
    console.log(err)
    return res.status(500).send(err)
  }
}

/**
 * Delete a ingredient
 * @param req
 * @param res
 * @returns void
 */
export async function deleteIngredient (req, res) {
  try {
    const ingredient = await Ingredient.findByIdAndRemove(req.params.id)

    if (!ingredient) {
      return res.status(404).json({})
    }
    return res.status(200).json({})
  } catch (err) {
    res.status(500).send(err)
  }
}
