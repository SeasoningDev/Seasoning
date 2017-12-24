const gulp = require('gulp')
const mocha = require('gulp-mocha')
const del = require('del')
const standard = require('gulp-standard')

require('git-guppy')(gulp)

const paths = {
  serverFiles: ['server/**/*.js'],
  serverTestFiles: ['server/**/*.spec.js'],
  allFiles: ['./*.js', 'server/**/*.js']
}

gulp.task('clean', () => {
  return del(['build'])
})

// Rerun the task when a file changes
gulp.task('watch', () => {
  gulp.watch(paths.serverFiles, ['unitTest'])
})

gulp.task('unitTest', () => {
  return gulp.src(paths.serverTestFiles, { read: false })
    .pipe(mocha({
      bail: true
    }))
})

gulp.task('lint', () => {
  return gulp.src(paths.allFiles, { base: './' })
    .pipe(standard({
      fix: true
    }))
    .pipe(gulp.dest((file) => './'))
    .pipe(standard.reporter('default', {
      breakOnError: true,
      showRuleNames: true,
      showFIlePath: true
    }))
})

gulp.task('pre-commit', ['lint'])

gulp.task('default', ['watch'])
