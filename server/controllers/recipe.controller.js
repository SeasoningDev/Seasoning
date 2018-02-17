import validator from 'express-validator/check'
import filter from 'express-validator/filter'

/**
 * Calculate the footprint of a recipe
 * @param req
 * @param res
 * @returns void
 */
export async function calculateFootprint (req, res) {
  try {
    const errors = validator.validationResult(req)
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: errors.mapped()
      })
    }

    const data = filter.matchedData(req)

    const footprint = 0

    // INSERT CODE HERE
    console.log(data)

    return res.status(200).json({
      footprint: footprint
    })
  } catch (err) {
    console.log(err.stack)
    console.log(err)

    return res.status(500).json({
      message: err
    })
  }
}
calculateFootprint.validators = [
  //validator.check('ingredients').isList()
]
