<!-- # Proyek Tengah Semester B06 - PBP Gasal 2025/2026
- [Anggota Kelompok](#kelompok-b06---sportnet)
- [Deskripsi Produk](#deskripsi-produk)
- [Moduls](#moduls)
- [Dataset](#dataset)
- [Role User](#role-user)
- [PWS](#pws)
- [Design](#design)

# SportNet
## 🧑‍💻 Kelompok B06 - SportNet 👩‍💻
1. Anya Aleena Wardhany (2406401773)
2. Azzahra Anjelika Borselano (2406419663)
3. Jessica Tandra (2406355445)
4. Muhammad Hafiz Hanan (2406437994)
5. Rayhan Derya Maheswara (2406403381)

## 🎾 Deskripsi Produk 🎾
SportNet adalah platform berbasis web yang dirancang untuk memudahkan para pecinta olahraga dalam menemukan berbagai **event olahraga terkini**, berinteraksi dengan komunitas yang memiliki minat serupa, dan ikut serta atau mendaftarkan dirinya dalam kegiatan olahraga bersama.

Melalui SportNet, pengguna dapat dengan mudah menjelajahi berbagai event olahraga yang tersedia, yaitu:
- Lari / Marathon
- Padel
- Sepak Bola / Futsal / Mini Soccer
- Yoga
- Pilates
- Bulutangkis
- Fitness
- Cycling
- Poundfit

Dengan tipe aktivitas yang berbeda, seperti:
- Fun Run/Ride
- Marathon
- Friendly Match
- Course
- Tournament
- Open Play
- Workshop


Tidak terbatas untuk menemukan event, SportNet juga menghadirkan **forum diskusi** khusus pada setiap event yang memungkinkan peserta untuk bertukar informasi, berdiskusi, serta membangun jaringan dengan sesama penggemar olahraga. Pengguna dapat mencari teman untuk berangkat bersama dan merencanakan keikutsertaan secara kolektif.

Dengan kemudahan akses dan interaksi yang ditawarkan, SportNet hadir sebagai solusi bagi siapa pun yang ingin menjalani gaya hidup aktif, memperluas relasi melalui kegiatan olahraga, dan tetap terhubung dengan komunitas olahraga di berbagai daerah. Platform ini diharapkan dapat mendorong semangat kolaborasi, mempererat hubungan antar pengguna, serta menciptakan ekosistem olahraga yang inklusif dan berkembang.

## ⌨️ Moduls ⌨️
1. **Homepage** [Rayhan Derya Maheswara]
   - Card Upcoming Event Recommendation
   - Navigation Bar (Sports Categorization/Filter, Activity Categorization/Filter)
   - Search Bar (search event)
2. **User Profile** [Jessica Tandra]
   - Menampilkan suatu model Profile mencakupi foto profil, nama, umur, city, sports interests, activity interests.
   - Menampilkan model Booked Event yang pernah diikuti user.
3. **User Registration** [Jessica Tandra]
   - Authentication user account dari Django.
   - Registrasi user profile sesuai rolenya
4. **Dashboard Event** [Anya Aleena Wardhany]
   - Menampilkan suatu model Event dengan attributes nama kegiatan, date, time, location, address, attendees, capacity, price, thumbnail, kategori activity, kategori sport.
   - Create Event baru.
   - User yang login dapat join Event, lalu jumlah attendees dari event tersebut akan bertambah.
5. **Forum Diskusi** [Muhammad Hafiz Hanan]
   - Menampilkan model Forum di setiap page detail event.
   - User yang login dapat berdiskusi terhadap event terkait.
6. **Review Event** [Muhammad Hafiz Hanan]
   - Menampilkan Review di setiap page detail event.
   - User yang login dapat memberi rating dan komentar terhadap event terkait.
7. **Bookmark / Wishlist** [Azzahra Anjelika Borselano]
   - Menampilkan model Bookmark yang ditandai user di page bookmark.
8. **Notification** [Rayhan Derya Maheswara]
   - Menampilkan reminder untuk suatu event yang diikuti (H-1, Today is the day, dll)
   - Menampilkan informasi jika event dihapus oleh penyelenggara

## 📊 Dataset 📊
Link dataset Event:
https://drive.google.com/drive/folders/1ptuFFn9E8LMG3A5_8FDTqx4pq3_cPWsA?usp=sharing

Source link website dataset (manual data scraping):
- meetup.com
- goersapp.com
- loket.com
- ayo.co.id
- baflionsrun.id
- event.rodalink.com
- ticket2u.id

## 👤 Role User 👤
1. **User yang belum login**
- Membuka homepage dan melihat semua daftar event yang tersedia.
- Menggunakan search bar untuk mencari event.
- Membuka detail suatu event.
- Melihat review suatu event.

2. **User yang sudah login (Participants)**
- Membuka homepage dan melihat semua daftar event yang tersedia.
- Menggunakan search bar untuk mencari event.
- Membuka detail suatu event.
- Melihat forum diskusi suatu event.
- Menambahkan komentar pada forum diskusi.
- Melihat profile pengguna lain.
- Melihat dan mengedit profile sendiri.
- Menambahkan review untuk suatu event.
- Join suatu event.
- Melihat history event yang pernah diikuti.
- Menambahkan suatu event ke bookmark.
- Melihat event yang sudah di-bookmark.

3. **User yang sudah login (Organizer)**
- Create event.
- Edit event milik sendiri yang sudah ada.
- Delete event milik sendiri.

## 🌐 PWS 🌐
Link PWS: https://anya-aleena-sportnet.pbp.cs.ui.ac.id/

## 🎨 Design 🎨
Designer: Azzahra Anjelika Borselano (2406419663)
https://www.figma.com/design/PSHZuSgZNQKkklskbBGPu3/SportNet-Design?node-id=1-2&p=f&t=PahYwtHFeaDuIpm0-0
 -->
