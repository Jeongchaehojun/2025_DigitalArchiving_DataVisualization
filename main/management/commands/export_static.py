"""
정적 HTML 파일 생성 명령어
GitHub Pages 배포용 docs 폴더에 정적 HTML을 생성합니다.
"""
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from main.models import MatchStory, ChampionStat
import os

# 팀 로고 매핑
TEAM_LOGO_MAP = {
    'Gen.G': 'geng.svg', 'GEN': 'geng.svg',
    'Hanwha Life Esports': 'hle.svg', 'HLE': 'hle.svg',
    'kt Rolster': 'kt.svg', 'KT': 'kt.svg',
    'CTBC Flying Oyster': 'cfo.webp', 'CFO': 'cfo.webp',
    'G2 Esports': 'g2.svg', 'G2': 'g2.svg',
    'Top Esports': 'tes.webp', 'TES': 'tes.webp',
    "Anyone's Legend": 'al.svg', 'AL': 'al.svg',
    'T1': 't1.svg',
}

# 경기별 키워드
MATCH_KEYWORDS = {
    ('QF', 1): ['LCK내전', '사실상결승', '월즈잔혹사', '피넛라스트댄스', '1시간혈전'],
    ('QF', 2): ['다크호스대결', 'KT완승', '대만리그의도전', '4강진출'],
    ('QF', 3): ['동서대결', '서양의마지막희망', 'TES홈그라운드', '3전3패'],
    ('QF', 4): ['LPL사신', '역전의명수', 'Bo5무패징크스', '8강최고명승부'],
    ('SF', 1): ['대이변', '신데렐라런', 'DRX신화재림', '언더독의반란', 'KT의기적'],
    ('SF', 2): ['LPL마지막희망', 'LPL전12연승', 'LCK내전성사', '결승진출'],
    ('F', 1): ['월즈3연패', '쓰리핏', '왕조vsunderdog', '신데렐라스토리', '레전드'],
}

STAGE_NAMES = {
    'QF': '8강',
    'SF': '4강',
    'F': '결승'
}


class Command(BaseCommand):
    help = 'GitHub Pages용 정적 HTML 파일을 생성합니다.'

    def handle(self, *args, **options):
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'docs')
        
        self.stdout.write(f'📁 출력 폴더: {base_dir}')
        
        # 스토리 페이지 생성
        self.export_story_pages(base_dir)
        
        # 챔피언 통계 페이지 생성
        self.export_champion_stats(base_dir)
        
        self.stdout.write(self.style.SUCCESS('✅ 정적 HTML 생성 완료!'))

    def export_story_pages(self, base_dir):
        """각 경기 스토리 페이지를 정적 HTML로 생성"""
        stages = ['QF', 'SF', 'F']
        
        for stage in stages:
            stories_by_match = {}
            stories = MatchStory.objects.filter(stage=stage).order_by('match_number', 'set_number')
            
            for story in stories:
                key = story.match_number
                if key not in stories_by_match:
                    stories_by_match[key] = []
                stories_by_match[key].append(story)
            
            for match_number, match_stories in stories_by_match.items():
                first_story = match_stories[0]
                
                html_content = self.generate_story_html(
                    stage=stage,
                    match_number=match_number,
                    stories=match_stories,
                    first_story=first_story
                )
                
                # 폴더 생성
                output_dir = os.path.join(base_dir, 'stories', stage, str(match_number))
                os.makedirs(output_dir, exist_ok=True)
                
                # HTML 파일 저장
                output_path = os.path.join(output_dir, 'index.html')
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.stdout.write(f'  📄 생성: stories/{stage}/{match_number}/index.html')

    def generate_story_html(self, stage, match_number, stories, first_story):
        """스토리 상세 페이지 HTML 생성"""
        keywords = MATCH_KEYWORDS.get((stage, match_number), [])
        team_a_logo = TEAM_LOGO_MAP.get(first_story.team_a, '')
        team_b_logo = TEAM_LOGO_MAP.get(first_story.team_b, '')
        stage_name = STAGE_NAMES.get(stage, stage)
        
        # 세트별 HTML 생성
        sets_html = ""
        for story in stories:
            winner_class = "team-a" if story.winner == first_story.team_a else "team-b"
            
            # 주요 챔피언 HTML
            key_champions_html = ""
            if story.key_champions:
                champions = [c.strip() for c in story.key_champions.split(',') if c.strip()]
                if champions:
                    key_champions_html = f'''
                    <div class="key-champions">
                        <h4 class="key-champions-title"><span>🎖️</span> 주요 챔피언</h4>
                        <div class="champions-grid">
                            {"".join([f'<div class="champion-item"><div class="champion-portrait placeholder">⚔️</div><span class="champion-name">{c}</span></div>' for c in champions])}
                        </div>
                    </div>
                    '''
            
            sets_html += f'''
            <article class="set-card">
                <div class="set-header">
                    <span class="set-number">{story.set_number}세트</span>
                    <span class="set-winner {winner_class}">🏆 {story.winner} 승리</span>
                </div>
                <div class="set-body">
                    {key_champions_html}
                    <div class="analysis-section">
                        <h3 class="analysis-label"><span class="icon">🎯</span> 밴픽 전략 분석</h3>
                        <p class="analysis-content">{story.banpick_analysis}</p>
                    </div>
                    <div class="analysis-section">
                        <h3 class="analysis-label"><span class="icon">⚔️</span> 경기 흐름 및 핵심 서사</h3>
                        <p class="analysis-content">{story.game_narrative}</p>
                    </div>
                </div>
            </article>
            '''
        
        # 키워드 HTML
        keywords_html = ""
        if keywords:
            keywords_html = f'''
            <div class="keywords-container">
                {"".join([f'<span class="keyword-tag">{k}</span>' for k in keywords])}
            </div>
            '''
        
        return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{stage_name} - {first_story.team_a} vs {first_story.team_b}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
    :root {{
        --bg-dark: #0a0e13;
        --bg-card: #111827;
        --bg-hover: #1f2937;
        --gold-primary: #c89b3c;
        --gold-secondary: #f0e6d2;
        --blue-accent: #0ac8b9;
        --red-accent: #ff4655;
        --text-primary: #f0e6d2;
        --text-secondary: #a09b8c;
        --border-color: #3c3c41;
        --gradient-gold: linear-gradient(135deg, #785a28 0%, #c8aa6e 50%, #c89b3c 100%);
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Noto Sans KR', sans-serif;
        background: var(--bg-dark);
        color: var(--text-primary);
        min-height: 100vh;
        background-image: radial-gradient(ellipse at top, rgba(200, 155, 60, 0.05) 0%, transparent 50%);
    }}
    .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
    .back-link {{
        display: inline-flex; align-items: center; gap: 8px;
        color: var(--text-secondary); text-decoration: none;
        margin-bottom: 30px; font-size: 0.95rem; transition: color 0.2s;
    }}
    .back-link:hover {{ color: var(--gold-primary); }}
    .header {{
        text-align: center; margin-bottom: 40px; padding: 40px;
        background: var(--bg-card); border-radius: 16px; border: 1px solid var(--border-color);
    }}
    .stage-badge {{
        display: inline-block; font-family: 'Orbitron', sans-serif; font-size: 0.85rem;
        background: var(--gold-primary); color: var(--bg-dark);
        padding: 6px 16px; border-radius: 4px; font-weight: 700; margin-bottom: 16px;
    }}
    .match-title {{
        font-family: 'Orbitron', sans-serif; font-size: 2rem; font-weight: 900;
        color: var(--text-primary); margin-bottom: 12px; display: flex;
        align-items: center; justify-content: center; gap: 16px; flex-wrap: wrap;
    }}
    .team-logo {{ width: 48px; height: 48px; object-fit: contain; }}
    .team-with-logo {{ display: flex; align-items: center; gap: 8px; }}
    .vs-divider {{ color: var(--red-accent); margin: 0 12px; font-size: 1.2rem; }}
    .final-score {{
        font-family: 'Orbitron', sans-serif; font-size: 2.5rem; font-weight: 900;
        color: var(--gold-primary); margin-top: 12px;
    }}
    .keywords-container {{
        display: flex; flex-wrap: wrap; justify-content: center; gap: 12px;
        margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border-color);
    }}
    .keyword-tag {{
        font-family: 'Orbitron', sans-serif; font-size: 1.1rem; font-weight: 700;
        color: var(--blue-accent); background: rgba(10, 200, 185, 0.1);
        padding: 8px 16px; border-radius: 24px; border: 1px solid rgba(10, 200, 185, 0.3);
        transition: all 0.3s ease;
    }}
    .keyword-tag::before {{ content: '#'; opacity: 0.7; }}
    .keyword-tag:hover {{
        background: rgba(10, 200, 185, 0.2); transform: translateY(-2px);
    }}
    .overview-section {{
        background: var(--bg-card); border-radius: 16px; padding: 30px;
        margin-bottom: 30px; border: 1px solid var(--border-color);
    }}
    .overview-title {{
        display: flex; align-items: center; gap: 12px;
        font-family: 'Orbitron', sans-serif; font-size: 1.2rem;
        color: var(--gold-primary); margin-bottom: 16px;
    }}
    .overview-text {{ color: var(--text-secondary); line-height: 1.9; }}
    .set-card {{
        background: var(--bg-card); border-radius: 16px; border: 1px solid var(--border-color);
        margin-bottom: 24px; overflow: hidden; transition: border-color 0.3s ease;
    }}
    .set-card:hover {{ border-color: var(--gold-primary); }}
    .set-header {{
        background: linear-gradient(180deg, #1a2332 0%, #111827 100%);
        padding: 20px 24px; border-bottom: 1px solid var(--border-color);
        display: flex; justify-content: space-between; align-items: center;
    }}
    .set-number {{ font-family: 'Orbitron', sans-serif; font-size: 1.3rem; font-weight: 700; }}
    .set-winner {{
        font-size: 0.9rem; padding: 6px 16px; border-radius: 20px; font-weight: 600;
    }}
    .set-winner.team-a {{ background: rgba(10, 200, 185, 0.2); color: var(--blue-accent); border: 1px solid var(--blue-accent); }}
    .set-winner.team-b {{ background: rgba(255, 70, 85, 0.2); color: var(--red-accent); border: 1px solid var(--red-accent); }}
    .set-body {{ padding: 24px; }}
    .analysis-section {{ margin-bottom: 24px; }}
    .analysis-label {{
        display: flex; align-items: center; gap: 8px;
        font-family: 'Orbitron', sans-serif; font-size: 0.9rem;
        color: var(--gold-primary); margin-bottom: 12px;
    }}
    .analysis-content {{
        color: var(--text-secondary); line-height: 1.9; font-size: 0.95rem;
        padding-left: 28px; border-left: 2px solid var(--border-color);
    }}
    .key-champions {{ margin-bottom: 24px; }}
    .key-champions-title {{
        display: flex; align-items: center; gap: 8px;
        font-size: 0.9rem; color: var(--gold-primary); margin-bottom: 12px;
    }}
    .champions-grid {{ display: flex; flex-wrap: wrap; gap: 12px; }}
    .champion-item {{ display: flex; flex-direction: column; align-items: center; gap: 6px; }}
    .champion-portrait {{
        width: 50px; height: 50px; border-radius: 50%; border: 2px solid var(--gold-primary);
        background: var(--bg-hover); display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem; color: var(--gold-primary);
    }}
    .champion-name {{ font-size: 0.7rem; color: var(--text-secondary); text-align: center; }}
    .nav-buttons {{ display: flex; justify-content: space-between; margin-top: 40px; gap: 16px; }}
    .nav-btn {{
        flex: 1; padding: 16px 24px; background: var(--bg-card);
        border: 1px solid var(--border-color); border-radius: 8px;
        color: var(--text-secondary); text-decoration: none; text-align: center;
        font-weight: 500; transition: all 0.3s ease;
    }}
    .nav-btn:hover {{ border-color: var(--gold-primary); color: var(--gold-primary); }}
    .footer {{
        text-align: center; margin-top: 60px; padding: 30px;
        border-top: 1px solid var(--border-color); color: var(--text-secondary);
    }}
    @media (max-width: 768px) {{
        .match-title {{ font-size: 1.4rem; }}
        .final-score {{ font-size: 2rem; }}
        .nav-buttons {{ flex-direction: column; }}
    }}
</style>
</head>
<body>
    <div class="container">
        <a href="../../" class="back-link">← 스토리 목록으로 돌아가기</a>
        
        <header class="header">
            <span class="stage-badge">{stage_name}</span>
            <h1 class="match-title">
                <span class="team-with-logo">
                    <img src="../../../static/images/teams/{team_a_logo}" class="team-logo" onerror="this.style.display='none'">
                    {first_story.team_a}
                </span>
                <span class="vs-divider">VS</span>
                <span class="team-with-logo">
                    <img src="../../../static/images/teams/{team_b_logo}" class="team-logo" onerror="this.style.display='none'">
                    {first_story.team_b}
                </span>
            </h1>
            <div class="final-score">{first_story.final_score}</div>
            {keywords_html}
        </header>

        {"" if not first_story.match_overview else f'''
        <section class="overview-section">
            <h2 class="overview-title"><span>📋</span> 경기 총평</h2>
            <p class="overview-text">{first_story.match_overview}</p>
        </section>
        '''}

        {sets_html}

        <div class="nav-buttons">
            <a href="../../" class="nav-btn">📖 전체 스토리 목록</a>
            <a href="../../../" class="nav-btn">🏠 메인으로</a>
        </div>

        <footer class="footer">
            <p>2025 롤드컵 벤픽 아카이브 | Data Storytelling Project</p>
        </footer>
    </div>
</body>
</html>'''

    def export_champion_stats(self, base_dir):
        """챔피언 통계 페이지를 정적 HTML로 생성"""
        stats = list(ChampionStat.objects.select_related('champion').order_by('-tier_score'))
        
        # 통계 계산
        total_picks = sum(s.total_picks for s in stats)
        blue_picks = sum(s.blue_first_pick for s in stats)
        max_tier = stats[0].tier_score if stats else 0
        
        # 테이블 행 생성
        rows_html = ""
        for i, stat in enumerate(stats, 1):
            rank_class = f"rank-{i}" if i <= 3 else "rank-default"
            
            # 진영 선호도 뱃지 클래스
            side_class = stat.side_preference if stat.side_preference else 'BALANCED'
            
            rows_html += f'''
            <tr>
                <td><span class="rank-badge {rank_class}">{i}</span></td>
                <td><div class="champion-name"><div class="champion-icon">⚔️</div>{stat.champion.name}</div></td>
                <td>
                    <div class="tier-bar-container">
                        <div class="tier-bar"><div class="tier-bar-fill" style="width: {stat.tier_score}%; background: linear-gradient(90deg, #785a28, #c8aa6e);"></div></div>
                        <span class="tier-value">{stat.tier_score}</span>
                    </div>
                </td>
                <td>
                    <div class="pick-stats">
                        <span class="pick-stat total">{stat.total_picks}</span>
                        <span class="pick-stat blue">B{stat.blue_first_pick}</span>
                        <span class="pick-stat red">R{stat.red_first_pick}</span>
                    </div>
                </td>
                <td><span class="side-badge {side_class}"><span class="side-index">{stat.side_index}</span> {stat.get_side_preference_display()}</span></td>
            </tr>
            '''
        
        html_content = self.generate_champion_stats_html(
            stats_count=len(stats),
            max_tier=max_tier,
            total_picks=total_picks,
            blue_picks=blue_picks,
            rows_html=rows_html
        )
        
        output_path = os.path.join(base_dir, 'champions', 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.stdout.write(f'  📄 생성: champions/index.html')

    def generate_champion_stats_html(self, stats_count, max_tier, total_picks, blue_picks, rows_html):
        """챔피언 통계 페이지 HTML 생성"""
        return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>2025 롤드컵 챔피언 통계</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
    :root {{
        --bg-dark: #0a0e13; --bg-card: #111827; --bg-hover: #1f2937;
        --gold-primary: #c89b3c; --blue-accent: #0ac8b9; --red-accent: #ff4655;
        --text-primary: #f0e6d2; --text-secondary: #a09b8c; --border-color: #3c3c41;
        --gradient-gold: linear-gradient(135deg, #785a28 0%, #c8aa6e 50%, #c89b3c 100%);
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Noto Sans KR', sans-serif; background: var(--bg-dark);
        color: var(--text-primary); min-height: 100vh;
        background-image: radial-gradient(ellipse at top, rgba(200, 155, 60, 0.05) 0%, transparent 50%);
    }}
    .container {{ max-width: 1400px; margin: 0 auto; padding: 40px 20px; }}
    .header {{ text-align: center; margin-bottom: 50px; position: relative; }}
    .header::before {{
        content: ''; position: absolute; top: 50%; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, var(--gold-primary), transparent);
    }}
    .header-content {{ display: inline-block; background: var(--bg-dark); padding: 0 40px; position: relative; }}
    .title {{
        font-family: 'Orbitron', sans-serif; font-size: 2.8rem; font-weight: 900;
        background: var(--gradient-gold); -webkit-background-clip: text;
        -webkit-text-fill-color: transparent; letter-spacing: 3px; text-transform: uppercase;
    }}
    .subtitle {{ font-size: 1rem; color: var(--text-secondary); letter-spacing: 2px; }}
    .nav-bar {{ display: flex; justify-content: center; gap: 20px; margin-bottom: 40px; }}
    .nav-link {{
        color: var(--text-secondary); text-decoration: none; padding: 12px 24px;
        border: 1px solid var(--border-color); border-radius: 4px; transition: all 0.3s ease;
    }}
    .nav-link:hover, .nav-link.active {{ color: var(--gold-primary); border-color: var(--gold-primary); background: rgba(200, 155, 60, 0.1); }}
    .stats-summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }}
    .stat-card {{
        background: var(--bg-card); border: 1px solid var(--border-color);
        border-radius: 8px; padding: 24px; text-align: center; transition: all 0.3s ease;
    }}
    .stat-card:hover {{ border-color: var(--gold-primary); transform: translateY(-3px); }}
    .stat-value {{ font-family: 'Orbitron', sans-serif; font-size: 2.5rem; font-weight: 700; color: var(--gold-primary); }}
    .stat-label {{ font-size: 0.9rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }}
    .table-container {{
        background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color);
        overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }}
    .champion-table {{ width: 100%; border-collapse: collapse; }}
    .champion-table th {{
        background: linear-gradient(180deg, #1a2332 0%, #111827 100%);
        padding: 18px 16px; text-align: left; font-weight: 600; color: var(--gold-primary);
        text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px;
        border-bottom: 2px solid var(--gold-primary);
    }}
    .champion-table td {{ padding: 16px; border-bottom: 1px solid var(--border-color); }}
    .champion-table tbody tr {{ transition: all 0.2s ease; }}
    .champion-table tbody tr:hover {{ background: var(--bg-hover); }}
    .rank-badge {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; border-radius: 50%;
        font-family: 'Orbitron', sans-serif; font-weight: 700; font-size: 0.85rem;
    }}
    .rank-1 {{ background: linear-gradient(135deg, #ffd700, #b8860b); color: #000; }}
    .rank-2 {{ background: linear-gradient(135deg, #c0c0c0, #808080); color: #000; }}
    .rank-3 {{ background: linear-gradient(135deg, #cd7f32, #8b4513); color: #fff; }}
    .rank-default {{ background: var(--bg-dark); color: var(--text-secondary); border: 1px solid var(--border-color); }}
    .champion-name {{ font-weight: 600; font-size: 1.05rem; display: flex; align-items: center; gap: 12px; }}
    .champion-icon {{
        width: 40px; height: 40px; border-radius: 50%; background: var(--bg-dark);
        border: 2px solid var(--gold-primary); display: flex; align-items: center;
        justify-content: center; font-size: 1.2rem;
    }}
    .tier-bar-container {{ display: flex; align-items: center; gap: 12px; }}
    .tier-bar {{ width: 120px; height: 8px; background: var(--bg-dark); border-radius: 4px; overflow: hidden; }}
    .tier-bar-fill {{ height: 100%; border-radius: 4px; }}
    .tier-value {{ font-family: 'Orbitron', sans-serif; font-weight: 600; color: var(--gold-primary); min-width: 40px; }}
    .pick-stats {{ display: flex; gap: 8px; }}
    .pick-stat {{ padding: 4px 12px; border-radius: 4px; font-size: 0.9rem; font-weight: 500; }}
    .pick-stat.total {{ background: rgba(200, 155, 60, 0.2); color: var(--gold-primary); }}
    .pick-stat.blue {{ background: rgba(74, 144, 217, 0.2); color: #4a90d9; }}
    .pick-stat.red {{ background: rgba(217, 74, 74, 0.2); color: #d94a4a; }}
    .side-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 500;
    }}
    .side-badge.BLUE_MUST {{ background: rgba(74, 144, 217, 0.3); color: #6db3f2; border: 1px solid #4a90d9; }}
    .side-badge.BLUE_PREF {{ background: rgba(74, 144, 217, 0.2); color: #4a90d9; }}
    .side-badge.BLUE_WEAK {{ background: rgba(74, 144, 217, 0.1); color: #4a90d9; }}
    .side-badge.BALANCED {{ background: rgba(160, 155, 140, 0.2); color: var(--text-secondary); }}
    .side-badge.RED_WEAK {{ background: rgba(217, 74, 74, 0.1); color: #d94a4a; }}
    .side-badge.RED_PREF {{ background: rgba(217, 74, 74, 0.2); color: #d94a4a; }}
    .side-badge.RED_MUST {{ background: rgba(217, 74, 74, 0.3); color: #f26d6d; border: 1px solid #d94a4a; }}
    .side-index {{ font-family: 'Orbitron', sans-serif; font-weight: 600; }}
    .analysis-principles {{
        background: var(--bg-card); border: 1px solid var(--border-color);
        border-radius: 12px; padding: 30px; margin-top: 40px;
    }}
    .analysis-title {{
        font-family: 'Orbitron', sans-serif; font-size: 1.3rem; color: #28a745;
        margin-bottom: 24px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color);
        display: flex; align-items: center; gap: 10px;
    }}
    .principles-grid {{
        display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px; margin-bottom: 24px;
    }}
    .principle-card {{
        background: var(--bg-dark); border: 1px solid #28a745; border-radius: 8px; padding: 20px;
    }}
    .principle-card h4 {{
        font-family: 'Orbitron', sans-serif; font-size: 1rem; color: var(--gold-primary);
        margin-bottom: 10px; display: flex; align-items: center; gap: 8px;
    }}
    .principle-card p {{ font-size: 0.9rem; color: var(--text-secondary); line-height: 1.7; }}
    .principle-card ul {{ list-style: none; padding-left: 0; margin-top: 10px; }}
    .principle-card ul li {{ font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 5px; padding-left: 1em; }}
    .principle-card ul li::before {{ content: '•'; color: #28a745; display: inline-block; width: 1em; margin-left: -1em; }}
    .caution-box {{
        background: rgba(255, 70, 85, 0.1); border: 1px solid var(--red-accent);
        border-radius: 8px; padding: 20px; color: var(--red-accent); font-size: 0.9rem; line-height: 1.6;
    }}
    .caution-box strong {{ color: var(--gold-primary); }}
    .footer {{
        text-align: center; margin-top: 60px; padding: 30px;
        border-top: 1px solid var(--border-color); color: var(--text-secondary);
    }}
    .footer a {{ color: var(--gold-primary); text-decoration: none; }}
    @media (max-width: 768px) {{
        .title {{ font-size: 1.8rem; }}
        .stats-summary {{ grid-template-columns: repeat(2, 1fr); }}
        .champion-table {{ font-size: 0.85rem; }}
        .tier-bar {{ width: 60px; }}
    }}
</style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="header-content">
                <h1 class="title">Champion Stats</h1>
                <p class="subtitle">2025 WORLDS CHAMPIONSHIP PRE-ANALYSIS</p>
            </div>
        </header>

        <nav class="nav-bar">
            <a href="../" class="nav-link">🏠 홈</a>
            <a href="./" class="nav-link active">📊 챔피언 통계</a>
        </nav>

        <section class="stats-summary">
            <div class="stat-card">
                <div class="stat-value">{stats_count}</div>
                <div class="stat-label">총 챔피언</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{max_tier}</div>
                <div class="stat-label">최고 Tier Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_picks}</div>
                <div class="stat-label">총 픽 횟수</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{blue_picks}</div>
                <div class="stat-label">블루 1픽</div>
            </div>
        </section>

        <div class="table-container">
            <table class="champion-table">
                <thead>
                    <tr>
                        <th style="width: 60px;">#</th>
                        <th>챔피언</th>
                        <th>Tier Score</th>
                        <th>픽 횟수</th>
                        <th>진영 선호도</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>

        <section class="analysis-principles">
            <h2 class="analysis-title">📐 챔피언 통계 분석 원리</h2>
            <div class="principles-grid">
                <div class="principle-card">
                    <h4>🏆 Tier Score</h4>
                    <p>챔피언의 종합적인 경쟁력을 나타내는 점수 (0~100점). 픽률, 밴률, 승률, 그리고 프로 선수들의 선호도 등 다양한 지표에 가중치를 부여하여 산출됩니다.</p>
                </div>
                <div class="principle-card">
                    <h4>📊 픽 횟수 (Pick Count)</h4>
                    <p>해당 챔피언이 월드 챔피언십 녹아웃 스테이지에서 총 몇 번 픽되었는지, 그리고 블루 진영과 레드 진영에서 각각 몇 번의 1픽으로 선택되었는지를 나타냅니다.</p>
                </div>
                <div class="principle-card">
                    <h4>⚖️ Side Index (진영 선호도 수치)</h4>
                    <p>챔피언이 특정 진영(블루 또는 레드)에서 얼마나 더 선호되는지를 수치화한 지표 (-1.0 ~ +1.0). 0에 가까울수록 양 진영에서 균형 있게 사용됩니다.</p>
                    <ul>
                        <li>양수: 블루 진영 선호</li>
                        <li>음수: 레드 진영 선호</li>
                    </ul>
                </div>
                <div class="principle-card">
                    <h4>🎯 진영 선호도 (Side Preference)</h4>
                    <p>Side Index를 기반으로 챔피언의 진영 선호도를 7단계로 분류합니다.</p>
                    <ul>
                        <li>🔵 블루 필수: Side Index ≥ 0.8</li>
                        <li>🔵 블루 선호: 0.5 ≤ Side Index &lt; 0.8</li>
                        <li>🔵 약한 블루: 0.25 ≤ Side Index &lt; 0.5</li>
                        <li>⚪ 균형: -0.25 &lt; Side Index &lt; 0.25</li>
                        <li>🔴 약한 레드: -0.5 &lt; Side Index ≤ -0.25</li>
                        <li>🔴 레드 선호: -0.8 &lt; Side Index ≤ -0.5</li>
                        <li>🔴 레드 필수: Side Index ≤ -0.8</li>
                    </ul>
                </div>
            </div>
            <div class="caution-box">
                <strong>⚠️ 주의사항:</strong> 이 통계는 2025 월드 챔피언십 녹아웃 스테이지의 제한된 데이터만을 기반으로 합니다. 실제 게임 플레이 및 패치 상황에 따라 챔피언의 티어와 선호도는 언제든지 변동될 수 있으므로, 참고 지표로 활용하시기 바랍니다.
            </div>
        </section>

        <footer class="footer">
            <p>2025 롤드컵 벤픽 아카이브 | <a href="../">메인으로 돌아가기</a></p>
        </footer>
    </div>
</body>
</html>'''

