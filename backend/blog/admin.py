from django.contrib import admin
from .models import Post  # .은 현재패키지라는 뜻

admin.site.register(Post)
