import mongoose from 'mongoose'
const Schema = mongoose.Schema

const unitSchema = new Schema({
  name: { type: 'String', required: true },
  shortName: { type: 'String', required: true }
}, {
  timestamps: true
})

export default mongoose.model('Unit', unitSchema)
