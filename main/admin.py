from django.contrib import admin
from .models import Champion, League, Team, Player, Match, PickBan, PBContext

# admin.site.register()를 사용하여 각 모델을 관리자 페이지에 등록
admin.site.register(Champion)
admin.site.register(League)
admin.site.register(Team)
admin.site.register(Player)

# Match 모델은 인라인으로 PickBan을 함께 볼 수 있게 설정하면 편리
class PickBanInline(admin.TabularInline):
    model = PickBan
    extra = 0 # 추가 PickBan 레코드 생성 필드 수

class MatchAdmin(admin.ModelAdmin):
    list_display = ('match_date', 'stage', 'team_a', 'team_b', 'winner')
    list_filter = ('stage', 'match_date')
    inlines = [PickBanInline]

admin.site.register(Match, MatchAdmin)


# PBContext는 PickBan에 1:1로 연결되어 있으므로, PickBan에서 함께 관리할 수 있도록 설정
class PBContextInline(admin.StackedInline): # StackedInline이 더 많은 정보를 보여줌
    model = PBContext
    can_delete = False
    verbose_name_plural = 'PB Context (스토리텔링)'
    
class PickBanAdmin(admin.ModelAdmin):
    list_display = ('match', 'order', 'team', 'pb_type', 'champion', 'player')
    list_filter = ('match__stage', 'pb_type', 'team')
    inlines = [PBContextInline] # 스토리텔링 메타데이터 필드를 PickBan 등록 시 같이 입력 가능
    
admin.site.register(PickBan, PickBanAdmin)
