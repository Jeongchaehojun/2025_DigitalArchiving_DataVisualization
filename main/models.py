from django.db import models

# 1. 챔피언 (Champion) 모델: 벤픽 대상
class Champion(models.Model):
    """
    리그 오브 레전드 챔피언 정보. 171가지 챔피언 중 사용된 챔피언만 저장 가능.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='챔피언 이름')
    # 기타 필요 정보 (예: image_url, role 등)를 추가할 수 있음

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '챔피언'
        verbose_name_plural = '챔피언 목록'


# 2. 팀 (Team) 및 선수 (Player) 모델
class League(models.Model):
    """
    팀이 소속된 리그 정보 (예: LCK, LPL 등).
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='리그 이름')
    
    def __str__(self):
        return self.name

class Team(models.Model):
    """
    월드 챔피언십 참가 팀 정보.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name='팀 이름')
    league = models.ForeignKey(League, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='소속 리그')
    # 기타 필요 정보 (예: logo_url 등)를 추가할 수 있음
    
    def __str__(self):
        return self.name

class Player(models.Model):
    """
    팀 소속 선수 정보.
    """
    name = models.CharField(max_length=100, verbose_name='선수 이름')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='소속 팀')
    # position (탑, 정글, 미드, 원딜, 서포터) 등을 CharField로 추가 가능
    
    def __str__(self):
        return f"{self.name} ({self.team.name})"


# 3. 경기 (Match) 모델
class Match(models.Model):
    """
    2025 월드 챔피언십 개별 경기 (세트) 정보.
    """
    stage_choices = [ # 보고서의 경기 단계 [cite: 35]
        ('SW_R1', '스위스 스테이지 R1'),
        ('SW_R2', '스위스 스테이지 R2'),
        ('SW_R3', '스위스 스테이지 R3'),
        ('SW_R4', '스위스 스테이지 R4'),
        ('SW_R5', '스위스 스테이지 R5'),
        ('QF', '8강'), # Quarter-Finals
        ('SF', '4강'), # Semi-Finals
        ('F', '결승전'), # Finals
    ]
    
    match_date = models.DateField(verbose_name='경기 날짜')
    stage = models.CharField(max_length=10, choices=stage_choices, verbose_name='경기 단계')
    team_a = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='home_matches', verbose_name='Team A')
    team_b = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='away_matches', verbose_name='Team B')
    winner = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='won_matches', verbose_name='승리 팀')
    # match_url = models.URLField(verbose_name='경기 영상/하이라이트 URL', null=True, blank=True)
    
    def __str__(self):
        return f"[{self.stage}] {self.team_a.name} vs {self.team_b.name} ({self.match_date})"
    
    class Meta:
        verbose_name = '경기'
        verbose_name_plural = '경기 목록'


# 4. 벤/픽 (PickBan) 및 PBContext 모델: 핵심 스토리텔링 구조
class PickBan(models.Model):
    """
    개별 벤/픽 행동 기록 (총 10 Ban + 10 Pick = 20개의 레코드).
    """
    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='해당 경기')
    team = models.ForeignKey(Team, on_delete=models.PROTECT, verbose_name='수행 팀')
    champion = models.ForeignKey(Champion, on_delete=models.PROTECT, verbose_name='대상 챔피언')
    
    pb_type_choices = [ # 벤/픽 구분
        ('BAN', 'Ban'),
        ('PICK', 'Pick'),
    ]
    pb_type = models.CharField(max_length=4, choices=pb_type_choices, verbose_name='유형')
    order = models.IntegerField(verbose_name='벤/픽 순서 (1~20)') # 벤픽 순서가 중요 [cite: 21]
    
    # 픽인 경우에만 선택 선수 정보 추가
    player = models.ForeignKey(Player, on_delete=models.PROTECT, null=True, blank=True, verbose_name='선수 (픽인 경우)')
    
    class Meta:
        unique_together = ('match', 'order') # 한 경기의 순서는 유일해야 함
        ordering = ['match', 'order']
        verbose_name = '벤픽 행동'
        verbose_name_plural = '벤픽 행동 목록'

    def __str__(self):
        return f"[{self.match.stage}] {self.team.name}: {self.get_pb_type_display()} {self.champion.name} (순서 {self.order})"


class PBContext(models.Model):
    """
    각 벤/픽 행동에 연결되는 스토리텔링 메타데이터 (1:1 관계).
    프로젝트의 핵심 목표인 '벤픽의 의도와 맥락'을 정성적으로 저장.
    """
    pick_ban = models.OneToOneField(PickBan, on_delete=models.CASCADE, primary_key=True) # PickBan과 1:1 관계 [cite: 38]
    
    # 보고서의 분류 단어 기반 라벨링 [cite: 34]
    story_label_choices = [
        ('META_BAN', '메타 벤'), ('COUNTER_BAN', '카운터 벤'), ('SNIPER_BAN', '저격 벤'),
        ('META_PICK', '메타 픽'), ('COUNTER_PICK', '카운터 픽'), ('COMBO_PICK', '조합 픽'),
        ('WILD_PICK', '사파 픽'), ('ROMANCE_PICK', '낭만 픽'),
        ('NONE', '분류 없음'),
    ]
    
    story_label = models.CharField(max_length=20, choices=story_label_choices, default='NONE', verbose_name='분류 라벨')
    story_keyword = models.CharField(max_length=100, verbose_name='스토리 핵심 키워드') # 정성적 메타데이터 [cite: 37]
    expert_comment = models.TextField(verbose_name='전문가/여론 분석 (스토리)', null=True, blank=True) # 분석 데스크/나무위키 여론 활용 [cite: 33, 29]
    emotional_intensity = models.IntegerField(default=0, verbose_name='심리적 강도 (-5 ~ 5)') # 심리적 협상 과정 정량화 시도 [cite: 21]
    
    def __str__(self):
        return f"{self.pick_ban} - {self.get_story_label_display()}"
    
    class Meta:
        verbose_name = 'PB 맥락 (스토리텔링)'
        verbose_name_plural = 'PB 맥락 (스토리텔링) 목록'


# 5. 챔피언 통계 (ChampionStat) 모델: 사전 챔피언십 분석 데이터
class ChampionStat(models.Model):
    """
    2025 월드 챔피언십 사전 분석 데이터 (prechampions.csv 기반).
    챔피언별 픽 통계와 진영 선호도를 저장합니다.
    """
    SIDE_PREFERENCE_CHOICES = [
        ('BLUE_MUST', '블루 필수'),
        ('BLUE_PREF', '블루 선호'),
        ('BLUE_WEAK', '약한 블루'),
        ('BALANCED', '균형'),
        ('RED_WEAK', '약한 레드'),
        ('RED_PREF', '레드 선호'),
        ('RED_MUST', '레드 필수'),
    ]
    
    champion = models.OneToOneField(
        Champion, 
        on_delete=models.CASCADE, 
        related_name='stat',
        verbose_name='챔피언'
    )
    total_picks = models.IntegerField(default=0, verbose_name='총 픽 횟수')
    blue_first_pick = models.IntegerField(default=0, verbose_name='블루 1픽')
    red_first_pick = models.IntegerField(default=0, verbose_name='레드 1픽')
    tier_score = models.FloatField(default=0.0, verbose_name='Tier Score (가치 점수)')
    side_index = models.FloatField(default=0.0, verbose_name='Side Index (진영 선호도 수치)')
    side_preference = models.CharField(
        max_length=10, 
        choices=SIDE_PREFERENCE_CHOICES, 
        default='BALANCED',
        verbose_name='진영 선호도'
    )
    
    def __str__(self):
        return f"{self.champion.name} - Tier: {self.tier_score}, Side: {self.get_side_preference_display()}"
    
    class Meta:
        ordering = ['-tier_score']
        verbose_name = '챔피언 통계'
        verbose_name_plural = '챔피언 통계 목록'


# 6. 경기 스토리 (MatchStory) 모델: 세트별 밴픽 전략 및 스토리
class MatchStory(models.Model):
    """
    각 경기 세트에 대한 밴픽 전략 분석과 스토리.
    worlds_story.docx 파일의 내용을 저장합니다.
    """
    STAGE_CHOICES = [
        ('QF', '8강'),
        ('SF', '4강'),
        ('F', '결승'),
    ]
    
    stage = models.CharField(max_length=5, choices=STAGE_CHOICES, verbose_name='경기 단계')
    match_number = models.IntegerField(verbose_name='경기 번호')  # 해당 단계에서 몇 번째 경기인지
    set_number = models.IntegerField(verbose_name='세트 번호')  # 세트 번호 (1~5)
    
    team_a = models.CharField(max_length=100, verbose_name='Team A')
    team_b = models.CharField(max_length=100, verbose_name='Team B')
    winner = models.CharField(max_length=100, verbose_name='세트 승리팀')
    final_score = models.CharField(max_length=10, verbose_name='최종 스코어', blank=True)  # e.g., "3:1"
    
    # 경기 총평 (경기 전체에 대한 설명, 세트 1에만 저장)
    match_overview = models.TextField(verbose_name='경기 총평', blank=True)
    
    # 세트별 분석
    banpick_analysis = models.TextField(verbose_name='밴픽 전략 분석')
    game_narrative = models.TextField(verbose_name='경기 흐름 및 핵심 서사')
    
    # 주요 챔피언 (쉼표로 구분된 챔피언 이름들, 예: "라이즈,니코,오공")
    key_champions = models.CharField(max_length=500, verbose_name='주요 챔피언', blank=True, 
                                     help_text='쉼표로 구분된 챔피언 영문명 (예: Ryze,Neeko,Wukong)')
    
    def get_key_champions_list(self):
        """주요 챔피언 목록을 리스트로 반환"""
        if self.key_champions:
            return [champ.strip() for champ in self.key_champions.split(',') if champ.strip()]
        return []
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['stage', 'match_number', 'set_number']
        unique_together = ('stage', 'match_number', 'set_number')
        verbose_name = '경기 스토리'
        verbose_name_plural = '경기 스토리 목록'
    
    def __str__(self):
        return f"[{self.get_stage_display()}] {self.team_a} vs {self.team_b} - {self.set_number}세트"
    
    def get_stage_order(self):
        """정렬을 위한 단계 순서 반환"""
        order = {'QF': 1, 'SF': 2, 'F': 3}
        return order.get(self.stage, 0)