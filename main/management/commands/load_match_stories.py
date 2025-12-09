"""
worlds_story.docx 파일에서 경기 스토리 데이터를 로드하는 Django management command
"""
from django.core.management.base import BaseCommand
from docx import Document
from main.models import MatchStory
import re


class Command(BaseCommand):
    help = 'worlds_story.docx 파일에서 경기 스토리 데이터를 로드합니다.'

    def handle(self, *args, **options):
        self.stdout.write('경기 스토리 데이터 로드를 시작합니다...')
        
        # docx 파일 읽기
        doc = Document('worlds_story.docx')
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        
        # 기존 데이터 삭제
        MatchStory.objects.all().delete()
        
        # 데이터 파싱 및 저장
        stories = self.parse_stories(paragraphs)
        
        for story_data in stories:
            MatchStory.objects.create(**story_data)
            self.stdout.write(f"  저장: [{story_data['stage']}] {story_data['team_a']} vs {story_data['team_b']} - {story_data['set_number']}세트")
        
        self.stdout.write(self.style.SUCCESS(f'총 {len(stories)}개의 경기 스토리가 로드되었습니다.'))

    def parse_stories(self, paragraphs):
        """docx 내용을 파싱하여 스토리 데이터 리스트 반환"""
        stories = []
        
        # === 8강 (Quarter Finals) ===
        
        # 8강 1경기: Gen.G vs HLE (3:1)
        stories.extend(self.create_match_stories(
            stage='QF',
            match_number=1,
            team_a='Gen.G',
            team_b='Hanwha Life Esports',
            final_score='3:1',
            match_overview=self.find_paragraph(paragraphs, '8강 대진 추첨 결과'),
            sets=[
                {
                    'set_number': 1,
                    'winner': 'Gen.G',
                    'banpick': self.find_paragraph(paragraphs, '한화생명은 \'딜라이트\' 유환중의 서포터 판테온'),
                    'narrative': self.find_paragraph(paragraphs, '한화생명은 초반 탑과 미드에서 다이브')
                },
                {
                    'set_number': 2,
                    'winner': 'Gen.G',
                    'banpick': self.find_paragraph(paragraphs, '양 팀은 아지르-오리아나라는 0티어'),
                    'narrative': self.find_paragraph(paragraphs, '약 58분 51초')
                },
                {
                    'set_number': 3,
                    'winner': 'Hanwha Life Esports',
                    'banpick': self.find_paragraph(paragraphs, '젠지의 이해하기 힘든 밴픽이 패배의 빌미'),
                    'narrative': self.find_paragraph(paragraphs, '한화생명은 젠지의 조합적 약점을 영리하게')
                },
                {
                    'set_number': 4,
                    'winner': 'Gen.G',
                    'banpick': self.find_paragraph(paragraphs, '3세트의 실수를 만회하려는 듯'),
                    'narrative': self.find_paragraph(paragraphs, '\'기산테\'의, 기산테에 의한')
                }
            ]
        ))
        
        # 8강 2경기: KT vs CFO (3:0)
        stories.extend(self.create_match_stories(
            stage='QF',
            match_number=2,
            team_a='kt Rolster',
            team_b='CTBC Flying Oyster',
            final_score='3:0',
            match_overview=self.find_paragraph(paragraphs, '이번 월즈의 다크호스로 꼽혔던 두 팀'),
            sets=[
                {
                    'set_number': 1,
                    'winner': 'kt Rolster',
                    'banpick': self.find_paragraph(paragraphs, 'CFO는 KT의 에이스 \'비디디\''),
                    'narrative': self.find_paragraph(paragraphs, 'KT는 초반 인베이드 설계와 바위 게')
                },
                {
                    'set_number': 2,
                    'winner': 'kt Rolster',
                    'banpick': self.find_paragraph(paragraphs, 'CFO는 블루 진영의 이점을 살려 아지르'),
                    'narrative': self.find_paragraph(paragraphs, '24분 32초. KT는 2025 월즈 최단 시간')
                },
                {
                    'set_number': 3,
                    'winner': 'kt Rolster',
                    'banpick': self.find_paragraph(paragraphs, 'KT는 사이온을 선픽하며 단단한 앞라인'),
                    'narrative': self.find_paragraph(paragraphs, '초반부터 우위를 점한 KT를 상대로')
                }
            ]
        ))
        
        # 8강 3경기: G2 vs TES (1:3)
        stories.extend(self.create_match_stories(
            stage='QF',
            match_number=3,
            team_a='G2 Esports',
            team_b='Top Esports',
            final_score='1:3',
            match_overview=self.find_paragraph(paragraphs, '8강 유일의 비 LCK 팀 매치업'),
            sets=[
                {
                    'set_number': 1,
                    'winner': 'Top Esports',
                    'banpick': self.find_paragraph(paragraphs, 'G2는 레드 진영에서 오리아나를 가져오는 정석적인'),
                    'narrative': self.find_paragraph(paragraphs, 'TES가 모든 라인에서 압도적인')
                },
                {
                    'set_number': 2,
                    'winner': 'G2 Esports',
                    'banpick': self.find_paragraph(paragraphs, 'G2는 레드 진영에서 \'정글 문도\''),
                    'narrative': self.find_paragraph(paragraphs, 'G2의 승부수가 완벽하게 적중')
                },
                {
                    'set_number': 3,
                    'winner': 'Top Esports',
                    'banpick': self.find_paragraph(paragraphs, 'G2는 정글 아이번, 서포터 쓰레쉬'),
                    'narrative': self.find_paragraph(paragraphs, 'G2의 조커 픽들은 아무런 힘을 쓰지')
                },
                {
                    'set_number': 4,
                    'winner': 'Top Esports',
                    'banpick': self.find_paragraph(paragraphs, 'G2는 마지막 승부수로 블루 1픽 드레이븐'),
                    'narrative': self.find_paragraph(paragraphs, '경기 초반은 G2의 변종 라인 스왑')
                }
            ]
        ))
        
        # 8강 4경기: AL vs T1 (2:3)
        stories.extend(self.create_match_stories(
            stage='QF',
            match_number=4,
            team_a="Anyone's Legend",
            team_b='T1',
            final_score='2:3',
            match_overview=self.find_paragraph(paragraphs, '\'LPL의 사신\'이라는 별명을 가진'),
            sets=[
                {
                    'set_number': 1,
                    'winner': 'T1',
                    'banpick': self.find_paragraph(paragraphs, 'AL은 1픽으로 키아나를 선택하는 강수'),
                    'narrative': self.find_paragraph(paragraphs, '초반 상체 주도권을 내준 T1')
                },
                {
                    'set_number': 2,
                    'winner': "Anyone's Legend",
                    'banpick': self.find_paragraph(paragraphs, 'AL은 \'카엘\' 김진홍의 시그니처 픽인 뽀삐'),
                    'narrative': self.find_paragraph(paragraphs, 'AL의 정글러 \'타잔\' 이승용이 빛났습니다')
                },
                {
                    'set_number': 3,
                    'winner': "Anyone's Legend",
                    'banpick': self.find_paragraph(paragraphs, 'T1의 밴픽이 아쉬웠습니다. 상대에게 바드를'),
                    'narrative': self.find_paragraph(paragraphs, 'T1은 초반 블리츠크랭크의 그랩으로')
                },
                {
                    'set_number': 4,
                    'winner': 'T1',
                    'banpick': self.find_paragraph(paragraphs, 'T1의 영리한 밴픽이 돋보였습니다. 돌진 조합'),
                    'narrative': self.find_paragraph(paragraphs, '구마유시의 카이사가 초반 교전에서')
                },
                {
                    'set_number': 5,
                    'winner': 'T1',
                    'banpick': self.find_paragraph(paragraphs, 'AL은 징크스를 중심으로 후반 캐리'),
                    'narrative': self.find_paragraph(paragraphs, '5천 골드까지 뒤처지며 패색이 짙었던')
                }
            ]
        ))
        
        # === 4강 (Semi Finals) ===
        
        # 4강 1경기: Gen.G vs KT (1:3)
        stories.extend(self.create_match_stories(
            stage='SF',
            match_number=1,
            team_a='Gen.G',
            team_b='kt Rolster',
            final_score='1:3',
            match_overview=self.find_paragraph(paragraphs, '모두가 젠지의 압도적인 승리를 예상'),
            sets=[
                {
                    'set_number': 1,
                    'winner': 'kt Rolster',
                    'banpick': self.find_paragraph(paragraphs, '젠지는 탈리야-바이-코르키로 강력한 돌진'),
                    'narrative': self.find_paragraph(paragraphs, '중반까지 젠지가 7천 골드 차이까지')
                },
                {
                    'set_number': 2,
                    'winner': 'Gen.G',
                    'banpick': self.find_paragraph(paragraphs, '젠지는 신 짜오와 암베사-갈리오를 중심'),
                    'narrative': self.find_paragraph(paragraphs, '초반 교전에서 승리하며 기세를 올린')
                },
                {
                    'set_number': 3,
                    'winner': 'kt Rolster',
                    'banpick': self.find_paragraph(paragraphs, 'KT는 아지르-오리아나를 모두 풀어주는 과감한'),
                    'narrative': self.find_paragraph(paragraphs, '그야말로 \'순수 체급\' 차이가')
                },
                {
                    'set_number': 4,
                    'winner': 'kt Rolster',
                    'banpick': self.find_paragraph(paragraphs, '벼랑 끝에 몰린 젠지는 쵸비의 통산 첫 애니비아'),
                    'narrative': self.find_paragraph(paragraphs, '젠지의 애니비아가 힘을 발휘하기도')
                }
            ]
        ))
        
        # 4강 2경기: TES vs T1 (0:3)
        stories.extend(self.create_match_stories(
            stage='SF',
            match_number=2,
            team_a='Top Esports',
            team_b='T1',
            final_score='0:3',
            match_overview=self.find_paragraph(paragraphs, 'LPL의 마지막 희망으로 남은'),
            sets=[
                {
                    'set_number': 1,
                    'winner': 'T1',
                    'banpick': self.find_paragraph(paragraphs, 'TES는 오리아나를 풀어주고 아칼리로 카운터'),
                    'narrative': self.find_paragraph(paragraphs, '페이커의 오리아나는 \'노데스, 노플래시\'')
                },
                {
                    'set_number': 2,
                    'winner': 'T1',
                    'banpick': self.find_paragraph(paragraphs, 'T1은 니코-갈리오-카밀-자르반-카이사'),
                    'narrative': self.find_paragraph(paragraphs, 'T1의 날카로운 돌진이 TES의 핵심')
                },
                {
                    'set_number': 3,
                    'winner': 'T1',
                    'banpick': self.find_paragraph(paragraphs, '마지막 희망을 건 TES는 \'재키러브\''),
                    'narrative': self.find_paragraph(paragraphs, 'TES의 키아나가 초반 킬을 몰아먹으며')
                }
            ]
        ))
        
        # === 결승 (Finals) ===
        stories.extend(self.create_finals_story(paragraphs))
        
        return stories

    def find_paragraph(self, paragraphs, start_text):
        """특정 텍스트로 시작하는 문단 찾기"""
        for p in paragraphs:
            if start_text in p:
                return p
        return ''

    def create_match_stories(self, stage, match_number, team_a, team_b, final_score, match_overview, sets):
        """경기 스토리 데이터 리스트 생성"""
        stories = []
        for set_info in sets:
            stories.append({
                'stage': stage,
                'match_number': match_number,
                'set_number': set_info['set_number'],
                'team_a': team_a,
                'team_b': team_b,
                'winner': set_info['winner'],
                'final_score': final_score,
                'match_overview': match_overview if set_info['set_number'] == 1 else '',
                'banpick_analysis': set_info['banpick'],
                'game_narrative': set_info['narrative']
            })
        return stories

    def create_finals_story(self, paragraphs):
        """결승전 스토리 생성 (요약 형태)"""
        kt_story = self.find_paragraph(paragraphs, 'kt Rolster: LCK 정규시즌')
        t1_story = self.find_paragraph(paragraphs, 'T1: 반면 T1은')
        summary = self.find_paragraph(paragraphs, '치열한 접전 끝에 소환사의 컵은')
        conclusion = self.find_paragraph(paragraphs, '이번 우승은 선수 개개인에게도')
        
        overview = self.find_paragraph(paragraphs, '2025 월드 챔피언십 결승은 두 팀의')
        
        return [{
            'stage': 'F',
            'match_number': 1,
            'set_number': 1,
            'team_a': 'kt Rolster',
            'team_b': 'T1',
            'winner': 'T1',
            'final_score': '2:3',
            'match_overview': overview,
            'banpick_analysis': f"KT의 서사:\n{kt_story}\n\nT1의 서사:\n{t1_story}",
            'game_narrative': f"{summary}\n\n{conclusion}"
        }]

