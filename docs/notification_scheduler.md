# H-1 Event Notification Scheduler

## Crontab Entry (Linux/Mac)
```bash
# Run every hour to check and send H-1 notifications
0 * * * * cd /path/to/sportnet && python manage.py send_h_minus_1
```

## Windows Task Scheduler
1. Open Task Scheduler
2. Click "Create Basic Task"
3. Name: "SportNet H-1 Event Notifications"
4. Trigger: Daily
5. Start time: Set to current time
6. Action: Start a program
7. Program/script: 
   ```
   C:\Path\To\Python\python.exe
   ```
8. Add arguments:
   ```
   manage.py send_h_minus_1
   ```
9. Start in:
   ```
   C:\Path\To\sportnet
   ```

## Penggunaan Manual
Untuk menjalankan pengecekan dan pengiriman notifikasi H-1 secara manual:
```bash
python manage.py send_h_minus_1
```

## Catatan
- Task akan mengecek semua event yang akan berlangsung dalam 24 jam ke depan
- Notifikasi hanya akan dikirim sekali untuk setiap event
- Pastikan Django settings.TIME_ZONE sudah sesuai dengan zona waktu lokal