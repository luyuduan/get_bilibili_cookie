# get_bilibili_cookie

编写时间：2025-05-22
作者：lyd
[git仓库](https://github.com/luyuduan/get_bilibili_cookie)



## 功能

- 扫码登陆B站，缓存cookie，保存到文件
- 搭配[BilibiliPotPlayer项目](https://github.com/chen310/BilibiliPotPlayer)使用



## 使用方法

1. 修改参数config_file，指向PotPlayer的配置文件，也可以直接复制到配置文件路径
2. 执行脚本，扫描二维码，扫描成功后，会自动保存登陆凭证到PotPlayer的配置文件
3. 关闭PotPlayer，重新打开，即可正常使用B站登录功能



## 注意事项

1. 脚本会缓存cookies到脚本所在文件夹的cookie文件夹中，文件名为bilibili.cookies。缓存文件涉及登陆凭证，**请勿泄露**
2. 配置文件中的注释会被清除
3. 脚本仅供学习交流使用，请勿用于商业用途



## 参考

-   [【【python爬虫】获取B站cookie教程，生成cookie文件，各大网站（某乎，某音，某博等）cookie均可保存（附源码）】](https://www.bilibili.com/video/BV1Ue41197vz/?share_source=copy_web&vd_source=b22e943fdbf4809cf6c3520fdfb6ed86)



