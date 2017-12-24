import mongoose from 'mongoose'
const Schema = mongoose.Schema

const ingredientSchema = new Schema({
  names: [{ type: String, required: true }],
  footprint: { type: Number, required: true },
  units: [{
    unit: { type: Schema.Types.ObjectId, ref: 'Unit', required: true },
    primaryToSecondaryRatio: { type: Number, required: true }
  }]
}, {
  timestamp: true
})

export default mongoose.model('Ingredient', ingredientSchema)
