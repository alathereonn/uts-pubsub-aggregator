BAGIAN TEORI
1. Jelaskan karakteristik utama sistem terdistribusi dan trade-off yang umum pada desain Pub-Sub log aggregator!
2. Bandingkan arsitektur client-server vs publish-subscribe untuk aggregator. Kapan memilih Pub-Sub? Berikan alasan teknis!
3. Uraikan at-least-once vs exactly-once delivery semantics. Mengapa idempotent consumer krusial di presence of retries?
4. Rancang skema penamaan untuk topic dan event_id (unik, collision-resistant). Jelaskan dampaknya terhadap dedup.
5. Bahas ordering: kapan total ordering tidak diperlukan? Usulkan pendekatan praktis (mis. event timestamp + monotonic counter) dan batasannya!
6. Identifikasi failure modes (duplikasi, out-of-order, crash). Jelaskan strategi mitigasi (retry, backoff, durable dedup store)!
7. Definisikan eventual consistency pada aggregator; jelaskan bagaimana idempotency + dedup membantu mencapai konsistensi.
8. Rumuskan metrik evaluasi sistem (throughput, latency, duplicate rate) dan kaitkan ke keputusan desain.

Jawaban:
1. Sistem terdistribusi dicirikan oleh openness, resource sharing, concurrency, scalability, transparency, dan fault tolerance (Tanenbaum & Van Steen, 2023, hlm. 18–25). Pada pola publish–subscribe berbasis message-queuing, produsen dan konsumen decoupled secara temporal: pesan disimpan persisten di queue sehingga pengirim/penerima tak perlu aktif bersamaan (Tanenbaum & Van Steen, 2023, hlm. 72–79; Tanenbaum & Van Steen, 2023, hlm. 198–205). Ini meningkatkan elastisitas, isolasi back-pressure, serta availability, tetapi ada trade-off: latensi tambahan untuk durabilitas, ketidakpastian delivery time, dan kompleksitas routing/matching saat ekspresivitas subscription meningkat (Tanenbaum & Van Steen, 2023, hlm. 206–220). Untuk log aggregator, Pub-Sub memberi fan-out efisien dan buffering saat lonjakan trafik, namun menuntut konsumen idempoten serta deduplication karena retries memicu duplikasi (Tanenbaum & Van Steen, 2023, hlm. 408–420). Selain itu, ordering global sering tidak realistis; arsitektur perlu toleran out-of-order dan memilih ordering lebih lemah (mis. FIFO/kausal) jika memadai (Tanenbaum & Van Steen, 2023, hlm. 264–280).

2. Arsitektur client–server cocok untuk request–response sinkron dengan endpoint identity yang jelas dan jalur kontrol sempit; namun ia temporally coupled—klien dan server harus aktif bersamaan (Tanenbaum & Van Steen, 2023, hlm. 72–85). Publish–subscribe memadankan subscription terhadap notification berbasis topik/atribut dan memberi decoupling in time berkat asynchronous queues (Tanenbaum & Van Steen, 2023, hlm. 198–205). Pub-Sub unggul saat fan-out besar, dynamic membership, dan kebutuhan loose coupling—tetapi menambah kompleksitas matching, kebutuhan broker/queue yang andal, serta kemungkinan delivery latency lebih tinggi (Tanenbaum & Van Steen, 2023, hlm. 206–220). Pilih Pub-Sub untuk event dissemination skala besar/log aggregation; pilih client–server untuk RPC kontrol yang sempit atau ketika endpoint identity dan low latency sangat krusial (Tanenbaum & Van Steen, 2023, hlm. 72–79; Tanenbaum & Van Steen, 2023, hlm. 206–214).

3. At-least-once menjamin eksekusi minimal sekali namun membuka peluang duplikasi saat retries; at-most-once menghindari duplikasi tetapi berisiko kehilangan pesan; exactly-once sulit dicapai secara end-to-end di hadapan crash dan ketidakpastian acknowledgement (Tanenbaum & Van Steen, 2023, hlm. 206–235). Karena itu, konsumen harus idempoten, misalnya dengan kunci (topic, event_id) dan dedup store untuk menolak replay yang sama; bila payload dapat berubah, tambahkan content hash untuk mendeteksi konflik (Tanenbaum & Van Steen, 2023, hlm. 236–250; Tanenbaum & Van Steen, 2023, hlm. 408–420). Pendekatan ini memberikan exactly-once effect di tingkat konsumen walau jaringan/messaging hanya menawarkan jaminan yang lebih lemah (Tanenbaum & Van Steen, 2023, hlm. 206–214; Tanenbaum & Van Steen, 2023, hlm. 408–412).

4. Naming memisahkan identifier dari address, mendukung location independence dan perubahan lokasi/implementasi tanpa mengubah identitas (Tanenbaum & Van Steen, 2023, hlm. 342–352). Gunakan event_id berbasis flat naming (UUID/ULID) atau self-certifying names (berbasis hash/kunci publik) guna menurunkan probabilitas tabrakan dan mendukung verifikasi (Tanenbaum & Van Steen, 2023, hlm. 360–372). topic sebaiknya structured (misalnya, logs.app.component) untuk pengelompokan dan resolution yang konsisten (Tanenbaum & Van Steen, 2023, hlm. 352–360). Kombinasi (topic, event_id) memudahkan dedup; jika terjadi tabrakan ID, content hash menjadi tie-breaker untuk membedakan duplikasi sejati dari konflik (Tanenbaum & Van Steen, 2023, hlm. 372–385).

5. Banyak aliran log tidak memerlukan total order; cukup causal/FIFO ketika tidak ada dependensi kuat antar-event (Tanenbaum & Van Steen, 2023, hlm. 264–273). Lamport clocks menjaga urutan happens-before namun tidak membuktikan kausalitas; vector clocks memungkinkan deteksi potensi kausalitas dan causally ordered delivery dengan biaya metadata lebih besar (Tanenbaum & Van Steen, 2023, hlm. 274–300). Praktik pragmatis untuk aggregator: gunakan (event_timestamp, monotonic per-producer counter) sebagai tie-breaker, izinkan late arrival dan lakukan reordering lokal sebatas window tertentu (Tanenbaum & Van Steen, 2023, hlm. 300–320). Batasan: clock skew, drift, dan overhead metadata untuk vector clocks (Tanenbaum & Van Steen, 2023, hlm. 280–320).

6. Antrian persisten memutus temporal coupling tetapi hanya menjamin enqueue, bukan delivery time—ini mendorong retry dan potensi duplikasi (Tanenbaum & Van Steen, 2023, hlm. 206–220). Out-of-order lazim pada multi-produser/partisi dan variabilitas jaringan; crash menimbulkan ketidakpastian ack (Tanenbaum & Van Steen, 2023, hlm. 220–235). Mitigasi: exponential backoff, idempotent consumer dengan durable dedup store (tahan gangguan), serta write-ahead record/insert sebelum side-effects agar dapat replay aman (Tanenbaum & Van Steen, 2023, hlm. 236–250; Tanenbaum & Van Steen, 2023, hlm. 408–420). Untuk pesan bermasalah, pisahkan ke dead-letter/poison queue guna analisis tanpa menghambat aliran utama (Tanenbaum & Van Steen, 2023, hlm. 214–220; Tanenbaum & Van Steen, 2023, hlm. 408–412).

7. Eventual consistency menyatakan bahwa—tanpa konflik tulis—semua replika akhirnya konvergen seiring propagasi update (Tanenbaum & Van Steen, 2023, hlm. 408–430). Idempotency memastikan replay tidak mengubah hasil; deduplication mencegah double-apply akibat retries/redelivery (Tanenbaum & Van Steen, 2023, hlm. 430–452). Ketika konflik tak terhindarkan, terapkan resolusi sederhana (mis. last-writer-wins berbasis jam yang disepakati) atau skema berbasis causal ordering untuk menjaga koherensi praktis (Tanenbaum & Van Steen, 2023, hlm. 452–480).

8. Metrik: 
Throughput (events/s), 
End-to-end latency, 
Duplicate rate, 
Error rate, dan 
Lag (selisih event.timestamp → commit) (Tanenbaum & Van Steen, 2023, hlm. 72–79; Tanenbaum & Van Steen, 2023, hlm. 198–205). 
Keputusan desain: 
Kunci idempoten (topic, event_id) + content hash untuk conflict detection (Tanenbaum & Van Steen, 2023, hlm. 372–385), 
Durable dedup store untuk exactly-once effect di konsumen (Tanenbaum & Van Steen, 2023, hlm. 408–420), 
Ordering praktis via timestamp + counter (tanpa global total order) (Tanenbaum & Van Steen, 2023, hlm. 264–300), dan 
Retry + backoff pada message-queuing (Tanenbaum & Van Steen, 2023, hlm. 206–220). 
Arsitektur: 
Publisher to Broker/Exchange to Queue (durable) to Idempotent Aggregator (dedup store) to Sink/Analytics; metrics endpoint untuk observabilitas (Tanenbaum & Van Steen, 2023, hlm. 72–85; Tanenbaum & Van Steen, 2023, hlm. 408–430).

Tanenbaum, A. S., & Van Steen, M. (2023). Distributed systems (Edisi ke-4). Addison-Wesley.