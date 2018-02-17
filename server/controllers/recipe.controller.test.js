import { calculateFootprint } from './recipe.controller'
import sem from 'sinon-express-mock'
import sinon from 'sinon'

describe('Recipe Controller Unit Tests', () => {
  describe('calculateRecipe', () => {
    it('should calculate the footprint of the given recipe', async () => {
      const req = sem.mockReq({
        body: [{
          name: 'testIgredient',
          amount: 5,
          unit: 'testUnit',
        }]
      })
      const res = sem.mockRes()

      await calculateFootprint(req, res)

      expect(res.status).to.be.calledWith(200)
      expect(res.json).to.be.calledWith({
        footprint: 5
      })
    })
  })
})
