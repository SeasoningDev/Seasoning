import mongoose from 'mongoose'

const Schema = mongoose.Schema

const ingredientSchema = new Schema({
  names: {
    type: [{
      singular: {
        type: String,
        required: true,
        minLength: 2
      },
      plural: {
        type: String,
        required: true,
        minLength: 2
      }
    }],
    validate: [val => val.length > 0, 'At least one name is required']
  },
  footprint: {
    type: Number,
    required: true,
    min: 0
  },
  units: {
    type: [{
      unit: {
        type: Schema.Types.ObjectId,
        ref: 'Unit',
        required: true
      },
      primaryToSecondaryRatio: {
        type: Number,
        required: true
      }
    }],
    validate: [val => val.length > 0, 'At least one unit is required']
  }
}, {
  timestamp: true
})

export default mongoose.model('Ingredient', ingredientSchema)
