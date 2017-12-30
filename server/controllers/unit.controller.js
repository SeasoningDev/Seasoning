import Unit from '../models/unit'
import toJSON from '../util/mongooseRestExport'
import validator from 'express-validator/check'
import filter from 'express-validator/filter'

/**
 * Get all units
 * @param req
 * @param res
 * @returns void
 */
export async function getUnits (req, res) {
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

    const units = await Unit.find()
      .sort(sort)
      .skip(skip)
      .limit(limit)
      .lean()
      .exec()

    return res
      .status(200)
      .header('X-Total-Count', units.length)
      .json(units.map(u => toJSON(u)))
  } catch (err) {
    console.log(err.stack)
    console.log(err)

    res.status(500).json({
      message: err
    })
  }
}
getUnits.validators = [
  validator.check('start').optional().isInt({ min: 0 }).toInt(),
  validator.check('end').optional().isInt({ min: 0 }).toInt(),
  validator.check('sort').optional().isIn(['id', 'footprint']),
  validator.check('order').optional().isIn(['ASC', 'DESC'])
]

/**
 * Add a new unit
 * @param req
 * @param res
 * @returns void
 */
export async function addUnit (req, res) {
  try {
    const newUnit = new Unit(req.body)

    const saved = await newUnit.save()

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
addUnit.validators = []

/**
 * Get a single unit
 * @param req
 * @param res
 * @returns void
 */
export async function getUnit (req, res) {
  try {
    const errors = validator.validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: errors.mapped()
      })
    }

    const data = filter.matchedData(req)

    const unit = await Unit.findById(data.id)
      .lean()
      .exec()

    return res.status(200).json(toJSON(unit))
  } catch (err) {
    console.log(err.stack)
    console.log(err)

    return res.status(500).json({
      message: err
    })
  }
}
getUnit.validators = [
  validator.check('id').isMongoId()
]

/**
 * Edit a unit
 * @param req
 * @param res
 * @returns void
 */
export async function editUnit (req, res) {
  try {
    const errors = validator.validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: errors.mapped()
      })
    }

    const data = filter.matchedData(req)

    const saved = await Unit.findByIdAndUpdate(data.id, req.body)
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

    return res.status(500).send(err)
  }
}
editUnit.validators = [
  validator.check('id').isMongoId()
]

/**
 * Delete a unit
 * @param req
 * @param res
 * @returns void
 */
export async function deleteUnit (req, res) {
  try {
    const errors = validator.validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: errors.mapped()
      })
    }

    const data = filter.matchedData(req)

    const unit = await Unit.findByIdAndRemove(data.id)

    if (!unit) {
      return res.status(404).json({})
    }

    return res.status(200).json({})
  } catch (err) {
    console.log(err.stack)
    console.log(err)

    return res.status(500).send(err)
  }
}
deleteUnit.validators = [
  validator.check('id').isMongoId()
]
