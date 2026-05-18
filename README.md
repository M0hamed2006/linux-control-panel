# Linux Remote Control Panel

منصة احترافية لمراقبة والتحكم في نظام Linux عبر واجهة ويب.

## المميزات
- مراقبة النظام في الوقت الفعلي
- مراقبة الشبكات
- تحليل الأنشطة المشبوهة
- واجهة ويب احترافية

## المتطلبات
- Python 3.8+
- Kali Linux أو أي توزيعة Linux

## التثبيت والتشغيل

### 1. إنشاء البيئة الوهمية
python3 -m venv venv
source venv/bin/activate

### 2. تثبيت المكتبات
pip install -r backend/requirements.txt

### 3. تشغيل السيرفر
cd backend
python app.py

ثم افتح المتصفح على: http://localhost:5000

## هيكل المشروع
- backend/ - كود Python والـ APIs
- frontend/ - HTML, CSS, JavaScript

## المراحل
- [ ] المرحلة 1 - Core Dashboard
- [ ] المرحلة 2 - Realtime System
- [ ] المرحلة 3 - Linux Monitoring
- [ ] المرحلة 4 - Security Monitoring
- [ ] المرحلة 5 - Network Tools
- [ ] المرحلة 6 - Advanced Features

## المطور
محمد
