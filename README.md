# github actions 更新 github  历史 commit

### run github-green

```sh
yarn # npm install
yarn start # npm run start
```

### tips

```sh
git checkout --orphan latest_branch # 检出一个未跟踪的分支
```

### API

|命令|类型|默认值|备注|
|--|--|--|--|
|`-s`|Number|去年今天（20200101）|开始时间|
|`-e`|Number|当前时间（20210101）|结束时间|
|`-l`|Number（0-9）|4|级别|
|`-m`|Number（0-9）|3|commit次数|
|`-file`|String|.github-green|文件名|
|`-commit`|String|:evergreen_tree:|备注|
|`-b`|String|master|分支名|

鸣谢：https://github.com/channg/gayhub