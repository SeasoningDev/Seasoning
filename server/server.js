import Express from 'express'
import compression from 'compression'
import mongoose from 'mongoose'
import bodyParser from 'body-parser'
import path from 'path'
import mongoSanitize from 'express-mongo-sanitize'

// Import required modules
import serverConfig from './config'
import apiRoutes from './routes/api.routes'
import adminRoutes from './routes/admin.routes'

// Initialize the Express App
const app = new Express()

// Set native promises as mongoose promise
mongoose.Promise = global.Promise

// MongoDB Connection
mongoose.connect(serverConfig.mongoURL, (error) => {
  if (error) {
    console.error('Please make sure Mongodb is installed and running!') // eslint-disable-line no-console
    throw error
  }
})

// Apply body Parser and server public assets and routes
app.use(compression())
app.use(bodyParser.json({ limit: '20mb' }))
app.use(bodyParser.urlencoded({ limit: '20mb', extended: false }))
app.use(Express.static(path.resolve(__dirname, '../build/client')))
app.use('/api', apiRoutes)
app.use('/admin', adminRoutes)

app.use(mongoSanitize({
  replaceWith: '_'
}))

// start app
app.listen(serverConfig.port, (error) => {
  if (!error) {
    console.log(`Seasoning is running on port: ${serverConfig.port}!`) // eslint-disable-line no-console
  }
})

export default app
