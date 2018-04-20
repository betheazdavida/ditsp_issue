# Complaint Center

## Installation

1. Run these commands:
```
migration.sh
```
```
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata division_seed.json
python manage.py loaddata origin_seed.json
python manage.py loaddata role_seed.json
python manage.py loaddata user_seed.json
```

2. Run Server
```
python manage.py runserver <port>
```

3. Login by using this credential:
```
Username: sarpras
Password: sumiatun
```

## Production (Temporary, already built automatically)

Run these commands:
```
cd /var/lib/jenkins/workspace/Sarpras\ Complaint\ Center
sudo python manage.py runserver 167.205.35.108:8888
```