// version v0.0.1
// create by zhihua
// detail url: https://github.com/ruicky/jd_sign_bot

const exec = require('child_process').execSync
const fs = require('fs')
const rp = require('request-promise')
const download = require('download')

// 京东cookie
const cookie = process.env.JD_COOKIE
// 京东cookie（账号 2）
const cookie2 = process.env.JD_COOKIE2
// Server酱 SCKEY
const push_key = process.env.PUSH_KEY

// 京东脚本文件
const js_url = 'https://raw.githubusercontent.com/NobyDa/Script/master/JD-DailyBonus/JD_DailyBonus.js'
// 下载脚本路径
const js_path = './JD_DailyBonus.js'
// 脚本执行输出路径
const result_path = './result.txt'
// 错误信息输出路径
const error_path = './error.txt'

/**
 * 重写一些 console 属性
 */
console = (function (origConsole) {

  if (!origConsole) origConsole = {};

  return {
    error(...info) { origConsole && origConsole.log('\u001b[31m' + info + '\u001b[39m') },
    success(...info) { origConsole && origConsole.log('\u001b[32m' + info + '\u001b[39m') },
    warn(...info) { origConsole && origConsole.log('\u001b[33m' + info + '\u001b[39m') },
    log(...info) { origConsole && origConsole.log('\u001b[34m' + info + '\u001b[39m') },
    assert(...info) { origConsole && origConsole.log('\u001b[35m' + info + '\u001b[39m') },
    info(...info) { origConsole && origConsole.log('\u001b[36m' + info + '\u001b[39m') }
  };

}(console));

Date.prototype.Format = function (fmt) {
  let o = {
    'M+': this.getMonth() + 1,
    'd+': this.getDate(),
    'H+': this.getHours(),
    'm+': this.getMinutes(),
    's+': this.getSeconds(),
    'S+': this.getMilliseconds()
  };
  if (/(y+)/.test(fmt)) {
    fmt = fmt.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
  }
  for (let k in o) {
    if (new RegExp('(' + k + ')').test(fmt)) {
      fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (('00' + o[k]).substr(String(o[k]).length)));
    }
  }
  return fmt;
};

/**
 * 设置 cookie
 */
function setupCookie() {
  let js_content = fs.readFileSync(js_path, 'utf8')
  if (cookie) js_content = js_content.replace(/var Key = ''/, `let Key = '${cookie}'`)
  if (cookie2) js_content = js_content.replace(/var DualKey = ''/, `var DualKey = '${cookie2}'`)
  fs.writeFileSync(js_path, js_content, 'utf8')
}

/**
 * 发送通知
 * @returns 
 */
function sendNotificationIfNeed() {

  if (!push_key) {
    console.log('执行任务结束!'); return;
  }

  if (!fs.existsSync(result_path)) {
    console.error('没有执行结果，任务中断!'); return;
  }

  let text = "京东签到_" + new Date().Format('yyyy.MM.dd');
  let desp = fs.readFileSync(result_path, "utf8")

  // 去除末尾的换行
  let SCKEY = push_key.replace(/[\r\n]/g, "")

  const options = {
    uri: `https://sc.ftqq.com/${SCKEY}.send`,
    form: { text, desp },
    json: true,
    method: 'POST'
  }

  rp.post(options).then(res => {
    const code = res['errno'];
    if (code == 0) {
      console.success("通知发送成功，任务结束！")
    } else {
      console.log(res);
      console.error("通知发送失败，任务中断！")
      fs.writeFileSync(error_path, JSON.stringify(res), 'utf8')
    }
  }).catch((err) => {
    console.error("通知发送失败，任务中断！",err)
    fs.writeFileSync(error_path, err, 'utf8')
  })
}

function main() {

  if (!cookie) throw new Error('请配置京东cookie!')

  // 1、下载脚本
  download(js_url, './').then(res=>{
    // 2、替换cookie
    setupCookie()
    // 3、执行脚本
    exec(`node '${js_path}' >> '${result_path}'`);
    // 4、发送推送
    sendNotificationIfNeed() 
  }).catch((err)=>{
    console.error('脚本文件下载失败，任务中断！');
    fs.writeFileSync(error_path, err, 'utf8')
  })

}

main()