const toJSON = function (leanMongooseObject) {
  const json = leanMongooseObject

  json.id = json._id
  delete json._id
  delete json.__v
  delete json.createdAt
  delete json.updatedAt

  return json
}

export default toJSON
