from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.views import View
# 새로 추가된 모델을 import 합니다.
from .models import Match, PickBan, PBContext, ChampionStat, Champion, MatchStory 


# 1. 인덱스 페이지 뷰 (메인 화면)
def index(request):
    # 최근 5개의 경기를 가져와 메인 페이지에 표시할 수 있습니다.
    recent_matches = Match.objects.all().order_by('-match_date')[:5]
    
    # Match와 MatchStory 매핑 (stage별 match_number 계산)
    stage_match_count = {}
    all_matches = Match.objects.all().order_by('match_date')
    match_story_map = {}
    
    for match in all_matches:
        stage = match.stage
        if stage not in stage_match_count:
            stage_match_count[stage] = 0
        stage_match_count[stage] += 1
        match_story_map[match.id] = {
            'stage': stage,
            'match_number': stage_match_count[stage]
        }
    
    # recent_matches에 story 정보 및 팀 로고 추가
    matches_with_story = []
    for match in recent_matches:
        story_info = match_story_map.get(match.id, {})
        matches_with_story.append({
            'match': match,
            'story_stage': story_info.get('stage', ''),
            'story_match_number': story_info.get('match_number', 0),
            'team_a_logo': get_team_logo(match.team_a.name if match.team_a else ''),
            'team_b_logo': get_team_logo(match.team_b.name if match.team_b else ''),
        })
    
    context = {
        'title': '2025 롤드컵 벤픽 아카이브',
        'content': '데이터 스토리텔링 기반 월드 챔피언십 전략적 선택의 인터랙티브 아카이빙',
        'recent_matches': matches_with_story
    }
    return render(request, 'main/index.html', context=context)


# 2. 벤픽 시각화 페이지 뷰
def match_visualization(request, match_id):
    """
    특정 경기의 시각화 화면을 렌더링합니다.
    이 뷰는 단순히 템플릿을 제공하고, 실제 데이터는 match_data_api를 통해 비동기적으로 로드됩니다.
    """
    # match_id에 해당하는 경기가 없으면 404 에러 발생
    match = get_object_or_404(Match, pk=match_id)
    
    context = {
        'match': match,
        'title': f'[{match.get_stage_display()}] {match.team_a.name} vs {match.team_b.name} 벤픽 스토리',
    }
    # 템플릿 ('main/match_visualization.html')에서는 match_id를 사용하여 API를 호출합니다.
    return render(request, 'main/match_visualization.html', context=context)


# 3. 데이터 시각화 API 뷰 (JSON 응답) - 프로젝트의 핵심 데이터 제공
def match_data_api(request, match_id):
    """
    특정 경기의 벤픽 데이터와 PBContext(스토리텔링) 메타데이터를 JSON 형태로 제공합니다.
    """
    try:
        match = Match.objects.get(pk=match_id)
        
        # 벤/픽 데이터 조회: 
        # PickBan을 가져오면서 ForeignKey 및 OneToOneField 관계인 모델들을 미리 조인(prefetch_related/select_related)하여
        # 데이터베이스 쿼리 횟수를 최적화합니다.
        pickbans_queryset = PickBan.objects.filter(match=match).select_related(
            'champion', 
            'team', 
            'player', 
            'pbcontext' # PBContext(스토리)를 함께 가져옴
        ).order_by('order')
        
        # JSON 데이터 구조 정의
        data = {
            'match_info': {
                'id': match.id,
                'stage': match.get_stage_display(),
                'date': match.match_date.strftime('%Y-%m-%d'),
                'team_a': match.team_a.name,
                'team_b': match.team_b.name,
                'winner': match.winner.name,
            },
            'pick_bans': []
        }
        
        # 벤/픽 데이터를 순회하며 스토리텔링 정보를 결합
        for pb in pickbans_queryset:
            pb_data = {
                'order': pb.order,
                'type': pb.pb_type,
                'team': pb.team.name,
                'champion': pb.champion.name,
                'player': pb.player.name if pb.player else None,
                # 스토리텔링 메타데이터 (PBContext)
                'story_context': {
                    # get_story_label_display()는 models.py에서 정의한 Choices의 두 번째 값(읽기 쉬운 라벨)을 가져옵니다.
                    'label': pb.pbcontext.get_story_label_display() if hasattr(pb, 'pbcontext') else '분류 없음',
                    'keyword': pb.pbcontext.story_keyword if hasattr(pb, 'pbcontext') else '',
                    'comment': pb.pbcontext.expert_comment if hasattr(pb, 'pbcontext') else '',
                    'intensity': pb.pbcontext.emotional_intensity if hasattr(pb, 'pbcontext') else 0,
                }
            }
            data['pick_bans'].append(pb_data)

        return JsonResponse(data, safe=False)

    except Match.DoesNotExist:
        # 경기가 없을 경우 404 상태 코드와 에러 메시지를 반환
        return JsonResponse({'error': '해당 경기를 찾을 수 없습니다.'}, status=404)


# --- 기존 함수 유지 ---

def hello1(request):
    return HttpResponse("<h1>Hello, World!</h1><h2>Well...</h2>")

def hello2(request):
    return HttpResponse("<h1>Bye, World!</h1><h2>Well...</h2>")

def toGoogle(request):
    return redirect("https://google.com")

def not_found(request):
    raise Http404("Sorry... no page here.") #에러를 다룰 때는 raise 사용

def api_example(request):
    data = {
        "message": "Hello, this is a JSON response",
        "status": "success"
    }
    return JsonResponse(data)


# --- 챔피언 통계 관련 뷰 ---

def champion_stats(request):
    """
    챔피언 통계 페이지 뷰.
    prechampions.csv 기반의 챔피언 픽/밴 분석 데이터를 시각화합니다.
    """
    stats = ChampionStat.objects.select_related('champion').all()
    
    # 정렬 옵션 처리
    sort_by = request.GET.get('sort', 'tier_score')
    order = request.GET.get('order', 'desc')
    
    valid_sort_fields = ['tier_score', 'total_picks', 'blue_first_pick', 'red_first_pick', 'side_index']
    if sort_by not in valid_sort_fields:
        sort_by = 'tier_score'
    
    if order == 'asc':
        stats = stats.order_by(sort_by)
    else:
        stats = stats.order_by(f'-{sort_by}')
    
    # 필터 옵션 처리
    side_filter = request.GET.get('side', 'all')
    if side_filter != 'all':
        stats = stats.filter(side_preference=side_filter)
    
    context = {
        'title': '2025 롤드컵 챔피언 통계',
        'stats': stats,
        'sort_by': sort_by,
        'order': order,
        'side_filter': side_filter,
        'side_choices': ChampionStat.SIDE_PREFERENCE_CHOICES,
    }
    return render(request, 'main/champion_stats.html', context=context)


def champion_stats_api(request):
    """
    챔피언 통계 API 엔드포인트.
    JSON 형태로 모든 챔피언 통계 데이터를 반환합니다.
    """
    stats = ChampionStat.objects.select_related('champion').all()
    
    data = {
        'champions': [
            {
                'name': stat.champion.name,
                'total_picks': stat.total_picks,
                'blue_first_pick': stat.blue_first_pick,
                'red_first_pick': stat.red_first_pick,
                'tier_score': stat.tier_score,
                'side_index': stat.side_index,
                'side_preference': stat.get_side_preference_display(),
                'side_preference_code': stat.side_preference,
            }
            for stat in stats
        ],
        'total_count': stats.count(),
    }
    
    return JsonResponse(data)


# --- 경기 스토리 관련 뷰 ---

# 팀 이름 -> 로고 파일명 매핑
TEAM_LOGO_MAP = {
    'Gen.G': 'geng.svg',
    'GEN': 'geng.svg',
    'Hanwha Life Esports': 'hle.svg',
    'HLE': 'hle.svg',
    'kt Rolster': 'kt.svg',
    'KT': 'kt.svg',
    'CTBC Flying Oyster': 'cfo.webp',
    'CFO': 'cfo.webp',
    'G2 Esports': 'g2.svg',
    'G2': 'g2.svg',
    'Top Esports': 'tes.webp',
    'TES': 'tes.webp',
    "Anyone's Legend": 'al.svg',
    'AL': 'al.svg',
    'T1': 't1.svg',
}

def get_team_logo(team_name):
    """팀 이름에 해당하는 로고 파일명 반환"""
    return TEAM_LOGO_MAP.get(team_name, '')


# 경기별 대표 키워드 (해시태그)
MATCH_KEYWORDS = {
    # 8강 (Quarter Finals)
    ('QF', 1): ['LCK내전', '사실상결승', '월즈잔혹사', '피넛라스트댄스', '1시간혈전'],
    ('QF', 2): ['다크호스대결', 'KT완승', '대만리그의도전', '4강진출'],
    ('QF', 3): ['동서대결', '서양의마지막희망', 'TES홈그라운드', '3전3패'],
    ('QF', 4): ['LPL사신', '역전의명수', 'Bo5무패징크스', '8강최고명승부'],
    # 4강 (Semi Finals)
    ('SF', 1): ['대이변', '신데렐라런', 'DRX신화재림', '언더독의반란', 'KT의기적'],
    ('SF', 2): ['LPL마지막희망', 'LPL전12연승', 'LCK내전성사', '결승진출'],
    # 결승 (Finals)
    ('F', 1): ['월즈3연패', '쓰리핏', '왕조vsunderdog', '신데렐라스토리', '레전드'],
}

def get_match_keywords(stage, match_number):
    """경기에 해당하는 키워드 목록 반환"""
    return MATCH_KEYWORDS.get((stage, match_number), [])


def match_stories(request):
    """
    경기 스토리 목록 페이지.
    8강, 4강, 결승 경기별 스토리를 확인할 수 있습니다.
    """
    # 단계별로 경기 스토리 그룹화
    qf_stories = MatchStory.objects.filter(stage='QF').order_by('match_number', 'set_number')
    sf_stories = MatchStory.objects.filter(stage='SF').order_by('match_number', 'set_number')
    f_stories = MatchStory.objects.filter(stage='F').order_by('match_number', 'set_number')
    
    # 경기별로 그룹화
    def group_by_match(stories):
        matches = {}
        for story in stories:
            key = (story.match_number, story.team_a, story.team_b, story.final_score)
            if key not in matches:
                matches[key] = {
                    'match_number': story.match_number,
                    'team_a': story.team_a,
                    'team_b': story.team_b,
                    'team_a_logo': get_team_logo(story.team_a),
                    'team_b_logo': get_team_logo(story.team_b),
                    'final_score': story.final_score,
                    'match_overview': story.match_overview if story.set_number == 1 else '',
                    'sets': []
                }
            matches[key]['sets'].append(story)
        return list(matches.values())
    
    context = {
        'title': '2025 롤드컵 경기 스토리',
        'qf_matches': group_by_match(qf_stories),
        'sf_matches': group_by_match(sf_stories),
        'f_matches': group_by_match(f_stories),
    }
    return render(request, 'main/match_stories.html', context=context)


def match_story_detail(request, stage, match_number):
    """
    특정 경기의 상세 스토리 페이지.
    """
    stories = MatchStory.objects.filter(
        stage=stage, 
        match_number=match_number
    ).order_by('set_number')
    
    if not stories.exists():
        raise Http404("해당 경기 스토리를 찾을 수 없습니다.")
    
    first_story = stories.first()
    
    context = {
        'title': f'{first_story.get_stage_display()} - {first_story.team_a} vs {first_story.team_b}',
        'team_a': first_story.team_a,
        'team_b': first_story.team_b,
        'team_a_logo': get_team_logo(first_story.team_a),
        'team_b_logo': get_team_logo(first_story.team_b),
        'stage': first_story.get_stage_display(),
        'final_score': first_story.final_score,
        'match_overview': first_story.match_overview,
        'stories': stories,
        'keywords': get_match_keywords(stage, match_number),
    }
    return render(request, 'main/match_story_detail.html', context=context)


def match_stories_api(request):
    """
    경기 스토리 API 엔드포인트.
    모든 경기 스토리 데이터를 JSON 형태로 반환합니다.
    """
    stories = MatchStory.objects.all().order_by('stage', 'match_number', 'set_number')
    
    data = {
        'stories': [
            {
                'id': story.id,
                'stage': story.stage,
                'stage_display': story.get_stage_display(),
                'match_number': story.match_number,
                'set_number': story.set_number,
                'team_a': story.team_a,
                'team_b': story.team_b,
                'winner': story.winner,
                'final_score': story.final_score,
                'match_overview': story.match_overview,
                'banpick_analysis': story.banpick_analysis,
                'game_narrative': story.game_narrative,
            }
            for story in stories
        ],
        'total_count': stories.count(),
    }
    
    return JsonResponse(data)