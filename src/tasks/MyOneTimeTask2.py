import re
import random

from qfluentwidgets import FluentIcon

from src.tasks.MyBaseTask import MyBaseTask


class MyOneTimeTask2(MyBaseTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "活动挑战赛"
        self.description = "用于活动挑战挂机"
        self.icon = FluentIcon.SYNC
        self.default_config.update({
            '活动赛的类型': "旧比赛",
            '挑战次数': 0, #0代表无限次
        })
        self.config_type["活动赛的类型"] = {'type': "drop_down",
                                      'options': ['旧比赛', '新比赛']}

    def run(self):
        self.log_info('活动开始运行!', notify=True)
        
        if self.config.get("活动赛的类型", "旧比赛") == "新比赛":
            targetTxt = "NEW" # 查找新比赛
        else:  
            targetTxt = re.compile("一次比赛") # 查找上一次比赛
        
        if self.config.get("挑战次数", 0) == 0:
            chanlenge_times = None
        else:
            chanlenge_times = self.config.get("挑战次数", 0)
        # 多次检测的中间区域
        centerBox = self.box_of_screen(0.25, 0.12, 0.75, 0.99, name="center_box", hcenter=True)

        while True:
            cur_times = 0
            challengeBox = self.box_of_screen(0.58, 0.16, 1, 1, name="challenge_box", hcenter=True)
            target = self.wait_ocr(box=challengeBox, match=targetTxt, log=True,time_out=30, settle_time = 1) 
            
            # 判空检查 (非常重要！)
            if not target:
                self.log_info("未找到上一次挑战赛", notify=True)
                return #直接结束本次流程
            # 获取目标框内随机坐标点
            x, y = self.point_with_variance(target, offsetX=250)

            # 点击目标框
            self.click(x, y)

            # 查找到开始按钮才继续，最长等10秒
            target2 = self.wait_feature('btn_start', time_out=10) #等待开始按钮出现，最长等10秒
            # 判空检查 (非常重要！)
            if not target2:
                self.log_info("未找到开始按钮", notify=True)
                return #直接结束本次流程
                
            # 获取挑战按钮框内随机坐标点
            x2, y2 = self.point_with_variance(target2)

            self.move(x2, y2) #移动到目标框内随机坐标点
            # 点击目标框，点击事件需要添加一定的延迟时间
            self.click(x2, y2)
            self.sleep(2) #等待2秒，确保界面元素加载完成
            self.detect_refresher(centerBox) #检测体力恢复

            self.move(x2, y2) #移动到目标框内随机坐标点
            # 点击目标框，点击事件需要添加一定的延迟时间
            self.click(x2, y2)

            # 等待比赛记录出现才继续，最长等120秒
            target3 = self.wait_ocr(match='比赛记录', time_out=120) #等待开始按钮出现，最长等10秒
            # 判空检查 (非常重要！)
            if not target3:
                self.log_info("未找到比赛记录", notify=True)
                return
            # 获取目标框内随机坐标点
            x3, y3 = self.point_with_variance(target3, offsetX=200)
            # 点击目标框且等待2秒
            self.click(x3, y3)
            self.sleep(1)

            while True :
                scene = self.detect_scene(centerBox) #检测目前处于哪个界面
                self.handle_scene(scene)

                if scene == "screen_gravure":
                    self.sleep(2) #因为找写真的场景没有等待，所以这边等待一下更好
                    self.detect_gravure_completed(centerBox) #检测写真完成场景
                    print("检测到写真场景，结束场景检测")
                    break # 这里才能真正跳出 while
                elif scene == "unknown_screen":
                    self.sleep(2) #等待3秒后再次检测，避免偶尔的识别错误导致过早结束活动, 感觉要多检测几次比较好
                    if self.detect_scene(centerBox) == "unknown_screen":
                        self.sleep(2) #等待3秒后再次检测，避免偶尔的识别错误导致过早结束活动, 感觉要多检测几次比较好
                        if self.detect_scene(centerBox) == "unknown_screen":
                            self.log_info("检测到未知界面，结束活动", notify=True)
                            break #重复检测一次依旧是未知界面则跳出检测
                
                self.sleep(2) #每次循环等待2秒，避免过于频繁地检测界面

            cur_times += 1
            if chanlenge_times and cur_times >= chanlenge_times:
                self.log_info(f'已完成{cur_times}次挑战，达到设定的挑战次数，结束活动', notify=True)
                break
            self.sleep(3) #每次挑战完成后等待3秒，避免过于频繁地进行挑战

        self.log_info('活动运行完成!', notify=True)


    #写真收集检测
    def detect_gravure_completed(self, searchBox):
        target = self.find_text(targetText=re.compile("稍后观看"), area=searchBox, delay=1) #在指定区域内查找稍后观看的字样，增加了判空检查
        if target:
            x, y = self.point_with_variance(target)
            self.click(x, y)
            self.sleep(1) #点击后等待1秒
            target1 = self.ocr(match="确定", box=searchBox, log=True)
            x1, y1 = self.point_with_variance(target1)
            self.click(x1, y1)
            return True
        else:
            return False
    #体力恢复检测
    def detect_refresher(self, searchBox):
        if self.find_text(targetText=re.compile("恢复饮料"), area=searchBox): #在指定区域内查找恢复饮料的字样，增加了判空检查
            # offsetLeft = 80 #体力瓶距离左箭头的距离
            # offsetRight = 130 #体力瓶距离右箭头的距离
            offsetMax = 140 #体力瓶距离最大箭头的距离
            x,y = self.find_one("bottle_all", threshold=0.9, box=searchBox).center() #在指定区域内找到体力瓶的特征
             # 判空检查 (非常重要！)
            if True: #根据配置中的条件进行设置，或则后续自动检测
                x += offsetMax
            self.click(x, y)
            self.sleep(1) #点击后等待1秒
            target = self.ocr(match="确定", box=searchBox, log=True)
            x1, y1 = self.point_with_variance(target)
            self.click(x1, y1)
            self.sleep(1) #点击后等待1秒
            return True
        else:
            return False
    #场景检测，检测目前处于哪个场景
    def detect_scene(self, searchBox):
        if self.find_text(targetText='初次达成报酬', area=searchBox):
            return "first_completion_reward"
        elif self.find_text(targetText='活动报酬', area=searchBox):
            return "event_reward"
        elif self.find_text(targetText='比赛记录', area=searchBox):
            return "screen_continue"
        elif self.find_text(targetText=re.compile("升级报酬"), area=searchBox):
            return "screen_level_up"
        elif self.find_one('box_gravure', box="bottom_left"):
            return "screen_gravure"
        else:
            self.screenshot("unknown_screen.png", show_box=True) #保存未知界面的截图以便后续分析
            self.log_info(f'6')
            return "unknown_screen"

    #场景检测后的处理逻辑
    def handle_scene(self, scene, centerBox = None):
        match scene:
            case "first_completion_reward" | "event_reward":
                target = self.ocr(match="确定", log=True, box=centerBox)
                x, y = self.point_with_variance(target)
                self.click(x, y)
            case "screen_continue":
                target = self.ocr(match="比赛记录", log=True, box="bottom")
                x, y = self.point_with_variance(target, offsetX=300)
                self.click(x, y)
            case "screen_level_up":
                target = self.ocr(match="确定", log=True, box=centerBox)
                x, y = self.point_with_variance(target)
                self.click(x, y)
            case "screen_gravure": #写真场景
                target = self.find_one('box_gravure', box = "bottom_left") #等待写真场景特征出现，最长等5秒
                x, y = self.point_with_variance(target)
                self.sleep(1) #点击前等待1秒，确保界面元素加载完成
                self.click(x, y)
            case "unknown_screen":
                return "Unknown Screen"
            
    #指查找文字
    def find_text(self, targetText: str = "", area: str = "full_screen", delay: float = 0.5):
        if area == "full_screen":
            area = None #默认全屏
        result = self.ocr(box=area, match=targetText, log=True) #指定box以提高ocr速度
        self.sleep(delay) #等待一段时间，避免过于频繁地进行ocr
        return result

    #查找图片
    def find_img():
        pass    

    #获取目标框内的随机坐标点，并按照要求进行一定程度的偏移按PX计算
    def point_with_variance(self, target, offsetX: int = 0, offsetY: int = 0):
        randomX = random.random()
        randomY = random.random()
        if isinstance(target, list):
            target = target[0]  # 如果是列表，取第一个元素
        x, y = target.relative_with_variance(randomX, randomY)  # 获取目标框内的随机坐标点
        x += offsetX
        y += offsetY
        return (x, y)
    

    def test_find_one_feature(self):
        return self.find_one('box_battle_1')

    def test_find_feature_list(self):
        return self.find_feature('box_battle_1')

    def run_for_5(self):
        self.operate(lambda: self.do_run_for_5())





