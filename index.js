#!/usr/bin/env node
const program = require('commander')
const dayjs = require('dayjs')
let GithubGreen = require('./src/github-green')


program
  .version(require('./package').version)
  // .arguments('[datastart] [dataend]')
  .option('-s ,--startDate <items>', 'startDate')
  .option('-e ,--endDate <items>', 'endDate')
  .option('-l ,--level <items>', 'level')
  .option('-m ,--multiplier <items>', 'multiplier')
  .option('-b ,--branch <items>', 'branch')
  .action(function (conf) {

    let startDate = conf['startDate']
    let endDate = conf['endDate']

    // 如果开始或结束时间格式错误
    if (!dayjs(startDate).isValid() && !dayjs(endDate).isValid()) {
      console.error('\u001b[31mWrong Date format, correct format YYYYMMDD!\u001b[39m')
      return;
    }

    // 如果开始时间不存在，设置默认为：去年今天
    if (!startDate) startDate = dayjs().subtract(1, 'year').format('YYYYMMDD')

    // 如果结束时间不存在，设置默认为：当前时间
    if (!endDate) endDate = dayjs().format('YYYYMMDD')

    let level = parseInt(conf['level']) || 4;
    if (level > 10 || level < 0) {
      console.error('\u001b[31mLevel ranges from 0 to 9 \u001b[39m')
      return;
    }
    /**
     * commit 次数，默认 3 次
     */
    let multiplier = parseInt(conf['multiplier']) || 3;
    if (multiplier < 0) multiplier = 1

    let branch = conf['branch'] || 'master'
    // console.info(startDate, endDate, level, multiplier)
     GithubGreen(startDate, endDate, level, multiplier,branch)
  })
  .parse(process.argv)
