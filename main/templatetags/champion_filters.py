from django import template

register = template.Library()

# 한글 챔피언 이름 → 영문 파일명 매핑
KOREAN_TO_ENGLISH_FILENAME = {
    # prechampions.csv 기반 31개 챔피언
    '라이즈': 'ryze',
    '요네': 'yone',
    '암베사': 'ambessa',
    '갈리오': 'galio',
    '카이사': 'kaisa',
    '럼블': 'rumble',
    '크산테': 'ksante',
    '오로라': 'aurora',
    '레넥톤': 'renekton',
    '오공': 'wukong',
    '사이온': 'sion',
    '자르반4세': 'jarvaniv',
    '오리아나': 'orianna',
    '노틸러스': 'nautilus',
    '아트록스': 'aatrox',
    '코르키': 'corki',
    '바이': 'vi',
    '오른': 'ornn',
    '탈리야': 'taliyah',
    '이즈리얼': 'ezreal',
    '신짜오': 'xinzhao',
    '바루스': 'varus',
    '라칸': 'rakan',
    '니코': 'neeko',
    '뽀삐': 'poppy',
    '시비르': 'sivir',
    '스카너': 'skarner',
    '아지르': 'azir',
    '애쉬': 'ashe',
    '판테온': 'pantheon',
    '알리스타': 'alistar',
    # 추가 챔피언들 (champion_pictures에 있는 것들)
    '애니비아': 'anivia',
    '바드': 'bard',
    '블리츠크랭크': 'blitzcrank',
    '케이틀린': 'caitlyn',
    '카밀': 'camille',
    '카시오페아': 'cassiopeia',
    '드레이븐': 'draven',
    '문도': 'drmundo',
    '그웬': 'gwen',
    '흐웨이': 'hwei',
    '아이번': 'ivern',
    '징크스': 'jinx',
    '칼리스타': 'kalista',
    '카르마': 'karma',
    '멜': 'mel',
    '모데카이저': 'mordekaiser',
    '니달리': 'nidalee',
    '녹턴': 'nocturne',
    '키아나': 'qiyana',
    '레나타': 'renata',
    '렉사이': 'reksai',
    '세주아니': 'sejuani',
    '스몰더': 'smolder',
    '신드라': 'syndra',
    '쓰레쉬': 'thresh',
    '트런들': 'trundle',
    '비에고': 'viego',
    '빅토르': 'viktor',
    '직스': 'ziggs',
    '조이': 'zoe',
    '아칼리': 'akali',
}

# 영문 챔피언 이름 → 파일명 매핑 (특수 케이스)
ENGLISH_FILENAME_MAP = {
    'jarvan iv': 'jarvaniv',
    'xin zhao': 'xinzhao',
    'kai\'sa': 'kaisa',
    'k\'sante': 'ksante',
    'rek\'sai': 'reksai',
    'cho\'gath': 'chogath',
    'kha\'zix': 'khazix',
    'vel\'koz': 'velkoz',
    'kog\'maw': 'kogmaw',
    'dr. mundo': 'drmundo',
    'miss fortune': 'missfortune',
    'lee sin': 'leesin',
    'twisted fate': 'twistedfate',
    'master yi': 'masteryi',
    'aurelion sol': 'aurelionsol',
    'tahm kench': 'tahmkench',
    'jarvan': 'jarvaniv',
}

@register.filter
def champion_filename(champion_name):
    """
    챔피언 이름을 파일명으로 변환합니다.
    한글 또는 영문 이름 모두 지원합니다.
    예: '라이즈' → 'ryze', 'Jarvan IV' → 'jarvaniv', 'Orianna' → 'orianna'
    """
    if not champion_name:
        return ''
    
    name = champion_name.strip()
    
    # 먼저 한글 이름 매핑 확인
    if name in KOREAN_TO_ENGLISH_FILENAME:
        return KOREAN_TO_ENGLISH_FILENAME[name]
    
    name_lower = name.lower()
    
    # 영문 특수 케이스 확인
    if name_lower in ENGLISH_FILENAME_MAP:
        return ENGLISH_FILENAME_MAP[name_lower]
    
    # 공백 및 특수문자 제거
    return name_lower.replace(' ', '').replace("'", '').replace('.', '')
