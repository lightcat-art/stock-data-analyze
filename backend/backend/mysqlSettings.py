DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 사용할 DB 종류
        'NAME': 'stock',        # DB 이름
        'USER': 'stock',        # DB 계정 이름
        'PASSWORD': 'stock',    # DB 계정 패스워드
        'HOST': 'localhost',    # IP
        'PORT': '3306'          # PORT
    }
}