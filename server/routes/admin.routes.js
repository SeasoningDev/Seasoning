import { Router } from 'express'
import * as AdminController from '../controllers/admin.controller.js'
const router = new Router()

router.route('/').get(AdminController.getAdmin)

export default router
