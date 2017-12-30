import express from 'express'

import ingredients from './ingredient.routes'
import units from './unit.routes'

const router = express.Router()

router.use('/v1', ingredients)
router.use('/v1', units)

export default router
