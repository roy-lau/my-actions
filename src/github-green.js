const dayjs = require('dayjs')
let utils = require('./utils')
const spawn = require('cross-spawn')
const crypto = require('crypto')


/**
 * 
 * @param {Number|Date} startDate 开始时间，默认：去年今天
 * @param {Number|Date} endDate 结束时间，默认：当前时间
 * @param {Number} level 生成随机数级别
 * @param {Number} multiplier  commit 次数
 * @param {string} branchName 分支名
 * 
 * @returns 
 */
function GithubGreen(startDate, endDate, level = 4, multiplier = 3,branch) {
  if (!utils.existsGit()) {
    console.log('\u001b[31mYou need to go to a git project root directory!\u001b[39m')
    return;
  }
  if (startDate && !endDate) {
    // only startDate
    git_commit(0, startDate)
  } else {
    init(startDate, endDate, level, multiplier)
  }
  // git_push(branch)
}


const init = (startDate, endDate, level, multiplier) => {
  utils.ensureGayHub()
  let commitDate = startDate
  // 如果在结束时间之前
  while (dayjs(commitDate, 'YYYYMMDD').isBefore(dayjs(endDate, 'YYYYMMDD'))) {
    commitDate = dayjs(commitDate, 'YYYYMMDD').add(1, 'day').format('YYYYMMDD')
    if (multiplier === 1) {
      git_commit(level, commitDate)
    } else {
      for (let i = multiplier; i > 0; i--) {
        git_commit(level, commitDate)
      }
    }
  }
}
/**
 * git commit
 * @param {Number} level commit 级别
 * @param {Number} commitDate commit 日期
 * @param {String} file commit 文件名
 */
const git_commit = (level, commitDate, file = '.github-green') => {
  if (utils.randompercentum(100 - level * 10)) {
    let bas = crypto.createHash('md5').update(commitDate).digest('hex');
    utils.writeLine(bas)
    spawn.sync('git', ['add', file], { stdio: 'inherit' })
    console.log('\u001b[32mcommit ' + bas + '\u001b[39m')
    spawn.sync('git', ['commit', '-m', ':evergreen_tree:', '--date="' + dayjs(commitDate, 'YYYYMMDD').format('ddd, DD MMM YYYY HH:mm:ss ZZ') + '"'], { stdio: 'ignore' })
  }
}

/**
 * git push
 * @param {string} branchName 分支名
 */
const git_push = (branchName = 'master') => {
  spawn.sync('git', ['push', '-u', 'origin', branchName], { stdio: 'inherit' })
  console.log('\n\u001b[32mCongratulations!!\u001b[39m')
}

// module.exports = new GithubGreen(startDate, endDate, level, multiplier)
module.exports = GithubGreen
