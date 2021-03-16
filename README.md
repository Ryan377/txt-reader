### 环境依赖
python 3.8 
pyqt5

***
### 运行方法
1.运行Server/run_server.py启动服务器 
2.运行Client/_main_.py启动客户端 
3.右击封面选择“开始阅读”打开文本阅读器 
4.ctrl+Z向前翻一页；ctrl+M向后翻一页 
5.ctrl+G弹出翻页窗口，输入页码跳页

***
### 头部协议 

客户端 
0 [filename] （下载名为filename的文件） 
1 [filename] （打开名为filename的txt文件） 
2 [num]      （翻到第num页） 
3            （关闭txt文件） 
若格式都不满足，返回 invalid request  

 

