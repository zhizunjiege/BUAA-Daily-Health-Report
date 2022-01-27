# BUAA-Daily-Health-Report

An auto script for BUAA daily health report.

## 说明

1. 此脚本使用 Selenium 模拟用户与浏览器的交互，实现自动打卡功能
2. ~~白嫖~~ 利用 Github Actions 实现每天 17:00/18:00/19:00 自动运行（时间不一定准确，可能会延迟十几分钟）
3. 代码参考了这位同学的：
   [https://github.com/mottled233/buaa_daily_report](https://github.com/mottled233/buaa_daily_report)，大致思路相同，加入 Github Actions 免去服务器部署

## 使用

1. fork 本仓库
2. 通过仓库的 Settings->Secrets->New repository secret 新建 4 个 secret：
   > - `USERNAME`：统一认证的账号
   > - `PASSWORD`：统一认证的密码
   > - `LONGITUDE`：打卡位置的经度，建议保存到小数点后第 6 位
   > - `LATITUDE`：打卡位置的纬度，建议保存到小数点后第 6 位
3. 哦可啦

## 其他

1. 密码仅用于登录，不用担心泄露
2. 每天运行 3 次是为了保证打卡成功，如果想自定义打卡的时间可以修改.github/workflows/auto-report.yml 里 schedule 的 cron 表达式
3. 代码...可能不够 robust，有问题的话提 issue，二次开发的时候悠着点
