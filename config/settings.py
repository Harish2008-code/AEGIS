from pathlib import Path
import os
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY=os.environ.get('DJANGO_SECRET_KEY','development-only-change-before-deployment')
DEBUG=os.environ.get('DJANGO_DEBUG','1')=='1'
ALLOWED_HOSTS=os.environ.get('DJANGO_ALLOWED_HOSTS','*').split(',')
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','core']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','core.context.shell']}}]
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
STATIC_URL='/static/'
STATICFILES_DIRS=[BASE_DIR/'static']
MEDIA_ROOT=BASE_DIR/'private_documents'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
USE_TZ=True
TIME_ZONE='Asia/Kolkata'
LOGIN_URL='/login/'
LOGIN_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL='/login/'
X_FRAME_OPTIONS='SAMEORIGIN'
CSRF_TRUSTED_ORIGINS=['https://*.e2b.app']
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
SECURE_CONTENT_TYPE_NOSNIFF=True
DEMO_MODE=os.environ.get('DEMO_MODE','1')=='1'
OLLAMA_URL=os.environ.get('OLLAMA_URL','http://127.0.0.1:11434').rstrip('/')
OLLAMA_MODEL=os.environ.get('OLLAMA_MODEL','qwen2.5:7b')
# OCR executable may be on PATH, or set TESSERACT_CMD on Windows.
OCR_LANG=os.environ.get('OCR_LANG','eng')
OCR_MAX_PAGES=int(os.environ.get('OCR_MAX_PAGES','20'))
OCR_RENDER_SCALE=float(os.environ.get('OCR_RENDER_SCALE','2'))
OCR_MAX_PIXELS=int(os.environ.get('OCR_MAX_PIXELS','25000000'))
OCR_MAX_CHARACTERS=int(os.environ.get('OCR_MAX_CHARACTERS','120000'))
