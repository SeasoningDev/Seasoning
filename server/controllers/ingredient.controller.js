import Ingredient from '../models/ingredient'
import toJSON from '../util/mongooseRestExport'
import validator from 'express-validator/check'
import filter from 'express-validator/filter'

/**
 * Get all ingredients
 * @param req
 * @param res
 * @returns void
 */
export async function getIngredients (req, res) {
  try {
    const errors = validator.validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: errors.mapped()
      })
    }

    const data = filter.matchedData(req)
    const skip = data.start ? data.start : 0
    const limit = data.end && data.end > data.start ? data.end - data.start : 20
    const sort = data.sort ? (data.order === 'ASC' ? '-' : '') + data.sort : 'id'

    const ingredients = await Ingredient.find()
      .populate('units.unit')
      .sort(sort)
      .skip(skip)
      .limit(limit)
      .lean()
      .exec()

    return res
      .status(200)
      .header('X-Total-Count', ingredients.length)
      .json(ingredients.map(i => toJSON(i)))
  } catch (err) {
    console.log(err.stack)
    console.log(err)

    return res.status(500).json({
      message: err
    })
  }
}
getIngredients.validators = [
  validator.check('start').optional().isInt({ min: 0 }).toInt(),
  validator.check('end').optional().isInt({ min: 0 }).toInt(),
  validator.check('sort').optional().isIn(['id', 'footprint']),
  validator.check('order').optional().isIn(['ASC', 'DESC'])
]

/**
 * Add a new ingredient
 * @param req
 * @param res
 * @returns void
 */
export async function addIngredient (req, res) {
  try {
    const newIngredient = new Ingredient(req.body)

    const saved = await newIngredient.save()

    return res.status(200).json(toJSON(saved.toJSON()))
  } catch (err) {
    if (err.name === 'ValidationError') {
      return res.status(400).json({
        message: Object.values(err.errors).join('\n')
      })
    }

    console.log(err.stack)
    console.log(err)

    return res.status(500).json({
      message: err
    })
  }
}
addIngredient.validators = []

/**
 * Get a single ingredient
 * @param req
 * @param res
 * @returns void
 */
export async function getIngredient (req, res) {
  try {
    const errors = validator.validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: errors.mapped()
      })
    }

    const data = filter.matchedData(req)

    const ingredient = await Ingredient.findById(data.id)
      .populate('units.unit')
      .lean()
      .exec()

    return res.status(200).json(toJSON(ingredient))
  } catch (err) {
    console.log(err.stack)
    console.log(err)

    return res.status(500).json({
      message: err
    })
  }
}
getIngredient.validators = [
  validator.check('id').isMongoId()
]

/**
 * Edit an ingredient
 * @param req
 * @param res
 * @returns void
 */
export async function editIngredient (req, res) {
  try {
    const errors = validator.validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: errors.mapped()
      })
    }

    const data = filter.matchedData(req)

    const saved = await Ingredient.findByIdAndUpdate(data.id, req.body)
      .populate('units.unit')
      .lean()
      .exec()

    return res.status(200).json(toJSON(saved))
  } catch (err) {
    if (err.name === 'ValidationError') {
      return res.status(400).json({
        message: Object.values(err.errors).join('\n')
      })
    }

    console.log(err.stack)
    console.log(err)

    return res.status(500).json({
      message: err
    })
  }
}
editIngredient.validators = [
  validator.check('id').isMongoId()
]

/**
 * Delete an ingredient
 * @param req
 * @param res
 * @returns void
 */
export async function deleteIngredient (req, res) {
  try {
    const errors = validator.validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: errors.mapped()
      })
    }

    const data = filter.matchedData(req)

    const ingredient = await Ingredient.findByIdAndRemove(data.id)
      .populate('units.unit')
      .lean()
      .exec()

    if (!ingredient) {
      return res.status(404).json({})
    }

    return res.status(200).json(toJSON(ingredient))
  } catch (err) {
    console.log(err.stack)
    console.log(err)

    res.status(500).json({
      message: err
    })
  }
}
deleteIngredient.validators = [
  validator.check('id').isMongoId()
]
