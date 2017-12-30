import mongoose from 'mongoose'
import serverConfig from '../config'
import { readFileSync } from 'fs'
import path from 'path'

import Ingredient from '../models/ingredient'
import Unit from '../models/unit'

// MongoDB Connection
mongoose.connect(serverConfig.mongoURL, async (error) => {
  if (error) {
    console.error('Please make sure Mongodb is installed and running!') // eslint-disable-line no-console
    throw error
  }

  const units = JSON.parse(readFileSync(path.resolve(__dirname, '../fixtures/units.json'), 'utf-8'))
  const ingredients = JSON.parse(readFileSync(path.resolve(__dirname, '../fixtures/ingredients.json'), 'utf-8'))

  try {
    await Unit.find().remove()
    const newUnits = await Unit.create(units)

    const newIngredients = ingredients.reduce((acc, i) => {
      const newIng = new Ingredient(i)

      if (!i.footprint) {
        newIng.footprint = 0
        return acc
      }

      newIng.units = i.units.map(u => {
        const newUnit = newUnits.filter(nu => nu.shortName === u.unit)[0]

        return {
          unit: newUnit._id,
          primaryToSecondaryRatio: u.primaryToSecondaryRatio
        }
      })

      if (i.units.length <= 0) {
        newIng.units = {
          unit: newUnits.filter(nu => nu.shortName === 'gr')[0]._id,
          primaryToSecondaryRatio: 0.001
        }
        return acc
      }

      acc.push(newIng)
      return acc
    }, [])
    await Ingredient.find().remove()
    await Ingredient.create(newIngredients)
  } catch (err) {
    console.log(err)
  }

  mongoose.connection.close()
})
