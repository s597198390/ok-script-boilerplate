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
            "挑战赛女孩1": "环",
            "挑战赛女孩2": "香迪"
        })
        self.config_type["活动赛的类型"] = {'type': "drop_down",
                                      'options': ['旧比赛', '新比赛']}
        
        girls = ['霞', '绫音', '瞳', '心', 
                '海莲娜', '玛莉', '红叶', '穗香',
                '女天狗', '海咲', '露娜', '环',
                '丽凤', '菲欧娜', '凪咲', '神无',
                '莫妮卡', '小百合', '派蒂', '筑紫',
                '萝贝莉娅', '七海', '伊莉丝', '小春',
                '蒂娜', '艾米', '香迪', '千乃', '雫', 
                '玲夏', '梅格']
        self.config_type["挑战赛女孩1"] = {'type': "drop_down",
                                      'options': girls}
        self.config_type["挑战赛女孩2"] = {'type': "drop_down",
                                      'options': girls}

    def run(self): 
        # 获取挑战赛的类型
        if self.config.get("活动赛的类型", "旧比赛") == "新比赛":
            targetTxt = "NEW" # 查找新比赛
        else:  
            targetTxt = re.compile("一次比赛") # 查找上一次比赛
        
        # 获取挑战赛的次数
        if self.config.get("挑战次数", 0) == 0:
            chanlenge_times = None
        else:
            chanlenge_times = self.config.get("挑战次数", 0)

        # 获取挑战赛女孩人选
        girl1 = self.config.get("挑战赛女孩1", "环")
        girl2 = self.config.get("挑战赛女孩2", "香迪")
        panel_girls = ['环', '香迪']# 写真已收集完成的女孩
        self.skip_detect_gravure = False #是否跳过写真完成检测的开关，默认为False，即不跳过
        if girl1 in panel_girls and girl2 in panel_girls:
            self.skip_detect_gravure = True #如果两个女孩的写真都已收集完成，则跳过写真完成检测

        # Box集合
        self.boxSet = {
            "center_box": self.box_of_screen(0.25, 0.12, 0.75, 0.99, name="center_box", hcenter=True),
            "challenge_box": self.box_of_screen(0.58, 0.16, 1, 1, name="challenge_box", hcenter=True),
            "score_Box": self.box_of_screen(0.4, 0.54, 0.54, 0.67, name="score_box", hcenter=True),
            "start_box": self.box_of_screen(0.74, 0.88, 0.94, 0.99, name="start_box", hcenter=True),
            "ok_back_box": self.box_of_screen(0.38, 0.76, 0.60, 0.91, name="ok_back_box", hcenter=True),
            "text_center_box": self.box_of_screen(0.34, 0.23, 0.67, 0.35, name="text_center_box", hcenter=True),
            "coin_box": self.box_of_screen(0.1, 0.25, 0.2, 0.3, name="coin_box", hcenter=True),
            "gravure_box": self.box_of_screen(0.02, 0.8, 0.2, 0.96, name="gravure_box", hcenter=True)
        }

        self.log_info('活动开始运行!', notify=True)
        while True:
            cur_times = 0
            # 查找目标比赛
            target = self.wait_ocr(box=self.boxSet["challenge_box"], match=targetTxt, log=True,time_out=20, settle_time = 1) 
            # 判空检查 (非常重要！)
            if not target:
                self.log_info("未找到上一次挑战赛", notify=True)
                return #直接结束本次流程
            x, y = self.point_with_variance(target, offsetX=250)
            self.click(x, y, down_time=0.5, after_sleep=1)

            # 查找到开始按钮才继续，最长等10秒
            target2 = self.wait_feature('btn_start', time_out=10, box=self.boxSet["start_box"])
            # 判空检查 (非常重要！)
            if not target2:
                self.log_info("未找到开始按钮", notify=True)
                return #直接结束本次流程
            x2, y2 = self.point_with_variance(target2)
            self.click(x2, y2, down_time=0.5, after_sleep=1)

            # 检测体力恢复
            self.detect_refresher(self.boxSet["center_box"])
            self.click(x2, y2, down_time=0.5, after_sleep=1)

            # # 等待比赛记录出现才继续，最长等60秒
            # recordBox = self.boxSet["record_box"]
            # target3 = self.wait_ocr(match='比赛记录', time_out=60, box=recordBox) #等待开始按钮出现，最长等10秒
            
            target3 = self.wait_ocr(match='最高分', time_out=60, box=self.boxSet["score_Box"], settle_time = 1) #等待开始按钮出现，最长等10秒
            # 判空检查 (非常重要！)
            if not target3:
                self.log_info("未找到得分界面", notify=True)
                return
            x3, y3 = self.point_with_variance(target3, offsetX=200)
            self.click(x3, y3, down_time=0.5, after_sleep=1)

            #开始场景检测
            while True :
                scene = self.detect_scene(self.boxSet["center_box"]) #检测目前处于哪个界面
                self.handle_scene(scene)

                if self.skip_detect_gravure and scene == "screen_exp":
                    self.detect_level_up() #检测人物升级界面
                    break
                if not self.skip_detect_gravure and scene == "screen_gravure":
                    self.sleep(2) #因为找写真的场景没有等待，所以这边等待一下更好
                    self.detect_gravure_completed(self.boxSet["center_box"]) #检测写真完成场景
                    print("检测到写真场景，结束场景检测")
                    break
                elif scene == "unknown_screen":
                    self.sleep(2) #等待3秒后再次检测，避免偶尔的识别错误导致过早结束活动, 感觉要多检测几次比较好
                    if self.detect_scene(self.boxSet["center_box"]) == "unknown_screen":
                        self.sleep(2) #等待3秒后再次检测，避免偶尔的识别错误导致过早结束活动, 感觉要多检测几次比较好
                        if self.detect_scene(self.boxSet["center_box"]) == "unknown_screen":
                            self.log_info("检测到未知界面，结束活动", notify=True)
                            break #重复检测一次依旧是未知界面则跳出检测
                
                self.sleep(1) #每次循环等待2秒，避免过于频繁地检测界面

            cur_times += 1
            if chanlenge_times and cur_times >= chanlenge_times:
                self.log_info(f'已完成{cur_times}次挑战，达到设定的挑战次数，结束活动', notify=True)
                break
            self.sleep(5) #每次挑战完成后等待5秒，避免过于频繁地进行挑战

        self.log_info('活动运行完成!', notify=True)

    #升级检测
    def detect_level_up(self):
        if self.find_text(targetText=re.compile("升级报酬"), area=self.boxSet["text_center_box"]):
            target = self.ocr(match="确定", box=self.boxSet["ok_back_box"], log=True)
            x, y = self.point_with_variance(target)
            self.click(x, y, down_time=0.5, after_sleep=1)
            return True
    #写真收集检测
    def detect_gravure_completed(self, searchBox):
        target = self.find_text(targetText=re.compile("稍后观看"), area=searchBox, delay=1) #在指定区域内查找稍后观看的字样，增加了判空检查
        if target:
            x, y = self.point_with_variance(target)
            self.click(x, y, down_time=0.5, after_sleep=1)
            target1 = self.ocr(match="确定", box=searchBox, log=True)
            x1, y1 = self.point_with_variance(target1)
            self.click(x1, y1, down_time=0.5, after_sleep=1)
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
            self.click(x, y, down_time=0.5, after_sleep=1)
            target = self.ocr(match="确定", box=self.boxSet["ok_back_box"], log=True)
            x1, y1 = self.point_with_variance(target)
            self.click(x1, y1, down_time=0.5, after_sleep=1)
            return True
        else:
            return False
    #场景检测，检测目前处于哪个场景
    def detect_scene(self, searchBox):
        if self.find_text(targetText='初次达成报酬', area=self.boxSet["text_center_box"]):
            return "first_completion_reward"
        elif self.find_text(targetText='活动报酬', area=self.boxSet["text_center_box"]):
            return "event_reward"
        elif self.find_text(targetText='获得扎克币', area=self.boxSet["coin_box"]):
            return "screen_exp"
        elif not self.skip_detect_gravure and self.find_one('box_gravure', box=self.boxSet["gravure_box"]):
            return "screen_gravure"
        else:
            self.screenshot("unknown_screen.png", show_box=True) #保存未知界面的截图以便后续分析
            self.log_info(f'6')
            return "unknown_screen"

    #场景检测后的处理逻辑
    def handle_scene(self, scene):
        match scene:
            case "first_completion_reward" | "event_reward":
                target = self.ocr(match="确定", log=True, box=self.boxSet["ok_back_box"])
                x, y = self.point_with_variance(target)
                self.click(x, y, down_time=0.5, after_sleep=1)
            case "screen_exp":
                # target = self.ocr(match="比赛记录", log=True, box=self.boxSet["record_box"])
                # x, y = self.point_with_variance(target, offsetX=300)
                self.click(862, 606, down_time=0.5, after_sleep=1)
            case "screen_gravure": #写真场景
                # target = self.find_one('box_gravure', box = "bottom_left") #等待写真场景特征出现，最长等5秒
                # x, y = self.point_with_variance(target)
                self.sleep(1) #点击前等待1秒，确保界面元素加载完成
                # self.click(x, y, down_time=0.5, after_sleep=1)
                self.click(862, 606, down_time=0.5, after_sleep=1)
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





