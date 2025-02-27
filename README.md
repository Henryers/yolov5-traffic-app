<div align="center">
  <h2>基于YOLOv5的交通道路目标检测和数据分析软件</h2>
  <p>
    <a align="center" href="https://ultralytics.com/yolov5" target="_blank">
      <img width="850" src="https://raw.githubusercontent.com/ultralytics/assets/master/yolov5/v70/splash.png"></a>
  </p>

  <p>
    YOLOv5 🚀 is the world's most loved vision AI, representing <a href="https://ultralytics.com">Ultralytics</a>
    open-source research into future vision AI methods, incorporating lessons learned and best practices evolved over thousands of hours of research and development.
    <br><br>
  </p>
</div>


## <div align="center"> ⭐ 项目部署 </div>

在Pycharm中打开该项目，配置一个venv虚拟环境后，直接按下面命令安装依赖即可：
```bash
pip install -r requirements.txt
```

## <div align="center"> ⭐ 注意事项 </div>

- main.py为本项目程序入口文件，软件的所有功能都写在这个文件中，前端页面设计在 `ui` 目录下
- 本程序中连接了数据库，需要自己配置与本地的数据库进行连接，如不需要数据库的话，只需把main.py的173行位置下的以下代码注释掉并调整缩进即可：
```python
# 显示登录对话框
login_dialog = LoginDialog()
result = login_dialog.exec_()
# 检查登录对话框返回结果
if result == QDialog.Accepted:
# 下文记得向前缩进
```
- main.py的849行位置记得更改成本项目目录：
```python
base_path = "D:/MyCode/public_project/yolov5-traffic-app/"
```

