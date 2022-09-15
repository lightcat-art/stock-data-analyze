from django.db import models
from django.conf import settings
from django.utils import timezone


# Model을 정의함으로써 장고는 Post메소드가 데이터베이스에 저장되어야 한다고 알게됨.
class Post(models.Model):
    # 다른 모델에 대한 링크
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 글자수가 제한된 텍스트 정의 ( 글 제목같은 짧은 문자열)
    title = models.CharField(max_length=200)
    # 글자 수 에 제한이 없는 긴 텍스트를 위한 속성 ( 블로그 콘텐츠)
    text = models.TextField()
    # 날짜와 시간 정의
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title