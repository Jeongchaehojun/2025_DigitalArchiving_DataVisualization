import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import Champion, ChampionStat


class Command(BaseCommand):
    help = 'prechampions.csv 파일에서 챔피언 통계 데이터를 로드합니다.'
    
    def parse_side_preference(self, side_index_str):
        """
        Side Index 문자열에서 수치와 선호도 분류를 추출합니다.
        예: "0.67 (블루 선호)" -> (0.67, 'BLUE_PREF')
        """
        # 숫자 부분 추출
        parts = side_index_str.split(' ')
        side_value = float(parts[0])
        
        # 선호도 분류 추출
        preference_map = {
            '블루 필수': 'BLUE_MUST',
            '블루 선호': 'BLUE_PREF',
            '약한 블루': 'BLUE_WEAK',
            '균형': 'BALANCED',
            '약한 레드': 'RED_WEAK',
            '레드 선호': 'RED_PREF',
            '레드 필수': 'RED_MUST',
        }
        
        # 괄호 안의 텍스트 추출
        if '(' in side_index_str and ')' in side_index_str:
            pref_text = side_index_str.split('(')[1].rstrip(')')
            preference = preference_map.get(pref_text, 'BALANCED')
        else:
            preference = 'BALANCED'
        
        return side_value, preference
    
    def handle(self, *args, **options):
        csv_path = settings.BASE_DIR / 'prechampions.csv'
        
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f'CSV 파일을 찾을 수 없습니다: {csv_path}'))
            return
        
        created_count = 0
        updated_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                champion_name = row['챔피언']
                total_picks = int(row['총 픽 횟수 (Total)'])
                blue_first = int(row['블루 1픽 (Blue 1st)'])
                red_first = int(row['레드 1픽 (Red 1st)'])
                tier_score = float(row['Tier Score (가치 점수)'])
                side_index_str = row['Side Index (진영 선호도)']
                
                side_value, side_pref = self.parse_side_preference(side_index_str)
                
                # 챔피언 생성 또는 가져오기
                champion, champ_created = Champion.objects.get_or_create(name=champion_name)
                
                if champ_created:
                    self.stdout.write(f'  새 챔피언 생성: {champion_name}')
                
                # 챔피언 통계 생성 또는 업데이트
                stat, stat_created = ChampionStat.objects.update_or_create(
                    champion=champion,
                    defaults={
                        'total_picks': total_picks,
                        'blue_first_pick': blue_first,
                        'red_first_pick': red_first,
                        'tier_score': tier_score,
                        'side_index': side_value,
                        'side_preference': side_pref,
                    }
                )
                
                if stat_created:
                    created_count += 1
                else:
                    updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'✅ 데이터 로드 완료! 새로 생성: {created_count}개, 업데이트: {updated_count}개'
        ))



