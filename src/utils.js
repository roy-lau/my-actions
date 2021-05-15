let fse = require('fs-extra')
let fs = require('fs')
let { resolve } = require('path')
module.exports = {
  existsGit() {
    return fs.existsSync(resolve(process.cwd(), '.git'))
  },
  ensureGayHub() {
    fse.ensureFileSync(resolve(process.cwd(), '.github-green'))
  },
  randompercentum(count) {

    let n = Math.round(Math.random() * 100)
    return n < count
  },
  writeLine(data) {
    fs.appendFileSync(resolve(process.cwd(), '.github-green'), data + '\n');
  }
}

