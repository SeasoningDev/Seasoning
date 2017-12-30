/**
 * Entry Script
 */

if (process.env.NODE_ENV === 'production') {
  // In production, serve the webpacked server file.
} else {
  require('babel-core/register')
  require('babel-polyfill')

  require('./server/server')
}
