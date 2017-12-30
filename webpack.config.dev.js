const webpack = require('webpack')
const path = require('path')

const BUILD_DIR = path.resolve(__dirname, 'build')
const APP_DIR = path.resolve(__dirname, 'client')

const config = {
  entry: APP_DIR + '/index.jsx',
  output: {
    path: BUILD_DIR,
    filename: 'app.js',
    publicPath: 'http://0.0.0.0:8000/'
  },
  module: {
    loaders: [{
      test: /\.html$/,
      include: APP_DIR,
      loader: 'html-loader'
    }, {
      test: /\.jsx?/,
      include: APP_DIR,
      loader: 'babel-loader',
      query: {
        presets: ['es2015', 'stage-0', 'react']
      }
    }]
  },
  plugins: [
    new webpack.ProvidePlugin({
      'React': 'react'
    })
  ]
}

module.exports = config
