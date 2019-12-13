# NS-Input

魔改来方便自己编写和调用脚本

脚本语句：
* `PRESS`按下按键，后面包含按键及三个参数`x y z`代表偏移1、偏移2、按下后延时。偏移仅在按键为摇杆时有用，否则无效
* `RELEASE`抬起按键，后面包含按键及一个参数代表抬起后延时
* `DELAY`延迟，格式为`DELAY DELAY [num]`表示延迟时间
* `SCRIPT`加载另一个脚本来替换该语句，后面包含引用次数和脚本路径。路径为相对该脚本的路径
* `#`注释，需要出现在开头，直接忽略。不包含任何字符的空行也会直接忽略

命令行`-script`复杂参数规则：
* 使用`:`隔开每个部分。暂不接受Windows下执行不同盘符的脚本的输入
* 每个部分有三种形式
    * 脚本路径。直接输入即可，如`scripts/connectJC.txt`
    * 一个数字。表示将前一个脚本简单重复若干次。如`scripts/connectJC.txt:2`和`scripts/connectJC.txt:scripts/connectJC.txt`等价
    * 直接输入脚本。脚本前后添加`/`作为标记。如`"/DELAY DELAY 1.5/:scripts/connectJC.txt"`在执行脚本前先延迟1.5秒