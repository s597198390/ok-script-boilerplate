from ok import TriggerTask


class AutoChallengeCup(TriggerTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "开始活动挑战"
        self.description = "用于自动挑战活动副本"
        self.trigger_count = 0

    def run(self):
        self.trigger_count += 1
        result = self.find_some_text_on_area("top_left", "挑战赛")
        self.log_info(f'AutoChallengeCup run 成功')

    #指定区域查找文字
    def find_some_text_on_area(self, area: str = "full_screen", target: str = "" ):
        return self.ocr(box=area, match=target, log=True) #指定box以提高ocr速度

