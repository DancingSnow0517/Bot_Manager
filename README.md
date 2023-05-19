# Bot Manager

一个 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) 插件，需要 `2.3.0` 以上
依赖于fabric-carpet
与FZ生存数据包有（可避让的）冲突

### 命令

```
!!bot 显示本插件帮助信息
!!bot add 添加bot
（玩家执行时以玩家当前位置为bot生成位置，控制台执行时需指定坐标、维度和视角）
!!bot del 删除bot
!!bot info 查看bot详细信息
!!bot list 查看bot列表
!!bot move 移动bot的生成位置
!!bot reload 重载配置文件
!!bot rename 重命名bot，位置与命令不变
!!bot run 运行bot的命令
!!bot setcmd 编辑bot的命令
```

### 配置

```
"bots": 储存的bot列表，默认提供一个样例bot
"bot_prefix": bot的前缀，默认为无，请与fabric-carpet配置fakePlayerNamePrefix一致
"bot_suffix": bot的后缀，默认为无，请与fabric-carpet配置fakePlayerNameSuffix一致
"fz_pack_tolerate": 与FZ生存数据包冲突的避让策略，默认为false，即不避让，保持/player指令可用
```