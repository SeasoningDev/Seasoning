import Unit from '../models/unit'
import sanitizeHtml from 'sanitize-html'
import toJson from '../util/mongooseRestExport'

/**
 * Get all units
 * @param req
 * @param res
 * @returns void
 */
export async function getUnits (req, res) {
  try {
    // TODO: start, end, order, sort parameters
    const units = await Unit.find()
      .sort('name')
      .lean()
      .exec()

    return res
      .status(200)
      .header('X-Total-Count', units.length)
      .json(units.map(u => toJson(u)))
  } catch (err) {
    res.status(500).send(err)
  }
}

/**
 * Add a new unit
 * @param req
 * @param res
 * @returns void
 */
export async function addUnit (req, res) {
  try {
    if (!req.body.name || !req.body.shortName) {
      res.status(403).end()
    }

    const newUnit = new Unit(req.body)

    // Let's sanitize inputs
    newUnit.name = sanitizeHtml(newUnit.name)
    newUnit.shortName = sanitizeHtml(newUnit.shortName)

    const saved = await newUnit.save()

    res.json(toJson(saved.toJSON()))
  } catch (err) {
    console.log(err.stack)
    console.log(err)
    return res.status(500).send(err)
  }
}

/**
 * Get a single unit
 * @param req
 * @param res
 * @returns void
 */
export async function getUnit (req, res) {
  try {
    const unit = await Unit.findById(req.params.id)
      .lean()
      .exec()

    return res.status(200).json(toJson(unit))
  } catch (err) {
    res.status(500).send(err)
  }
}

/**
 * Edit a unit
 * @param req
 * @param res
 * @returns void
 */
export async function editUnit (req, res) {
  try {
    if (!req.body.name || !req.body.shortName) {
      res.status(403).end()
    }

    const saved = await Unit.findByIdAndUpdate(req.params.id, req.body)

    res.status(200).json(toJson(saved.toJSON()))
  } catch (err) {
    console.log(err.stack)
    console.log(err)
    return res.status(500).send(err)
  }
}

/**
 * Delete a unit
 * @param req
 * @param res
 * @returns void
 */
export async function deleteUnit (req, res) {
  try {
    const unit = await Unit.findByIdAndRemove(req.params.id)

    if (!unit) {
      return res.status(404).json({})
    }
    return res.status(200).json({})
  } catch (err) {
    return res.status(500).send(err)
  }
}
