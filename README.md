# LanBridge 🚀

> LAN üzerinden anlık mesajlaşma uygulaması

## Özellikler

- ✅ TCP socket tabanlı client-server mimarisi
- ✅ Çoklu istemci desteği (threading)
- ✅ Renkli konsol arayüzü
- ✅ Gerçek zamanlı mesajlaşma
- ✅ Kullanıcı katılma/ayrılma bildirimleri
- ✅ Online kullanıcı listesi
- ✅ Windows desteği (`msvcrt` ile klavye girdisi)
- ✅ Kolay başlatma (`baslat.bat`)

## Kurulum

```bash
git clone https://github.com/hayka8/LanBridge.git
cd LanBridge
```

## Kullanım

### Sunucu başlatma:
```bash
python server.py
```

### İstemci başlatma:
```bash
python client.py
```

### Toplu menü (Windows):
```
baslat.bat
```

## Bağlantı

Varsayılan port: **12345**

| Parametre | Açıklama |
|-----------|----------|
| `HOST` | `0.0.0.0` (tüm ağ arayüzleri) |
| `PORT` | `12345` |
| `BUFFER` | `65535` |

## Gereksinimler

- Python 3.6+
- Standart kütüphane (ek kurulum gerektirmez)

## Lisans

MIT License
