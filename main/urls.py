from django.urls import path
from . import views 

urlpatterns = [ 
    # 1. 기본 인덱스 페이지 (전체 프로젝트 소개 및 경기 목록)
    path('', views.index, name='index'),
    
    # 2. 벤픽 인터랙티브 시각화 페이지 (match_id에 해당하는 경기의 시각화 화면)
    path('match/<int:match_id>/visualize/', views.match_visualization, name='match_visualization'),
    
    # 3. 데이터 API 엔드포인트 (시각화 라이브러리(D3.js 등)가 사용할 JSON 데이터)
    path('api/match/<int:match_id>/data/', views.match_data_api, name='match_data_api'),
    
    # 4. 챔피언 통계 페이지 및 API
    path('champions/', views.champion_stats, name='champion_stats'),
    path('api/champions/', views.champion_stats_api, name='champion_stats_api'),
    
    # 5. 경기 스토리 페이지 및 API
    path('stories/', views.match_stories, name='match_stories'),
    path('stories/<str:stage>/<int:match_number>/', views.match_story_detail, name='match_story_detail'),
    path('api/stories/', views.match_stories_api, name='match_stories_api'),
    
    # 6. 기타 예시/디버깅용 경로 (기존 유지)
    path('hello', views.hello1, name='hello'),
    path('hello/', views.hello2),
    path('redirect-google', views.toGoogle, name='to_google'), # toGoogle 함수 경로 추가
    path('404-test', views.not_found, name='not_found'), # not_found 함수 경로 추가
    path('json-test', views.api_example, name='json_test'), # api_example 함수 경로 추가
]