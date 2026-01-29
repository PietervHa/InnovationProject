# 🚁 Innovatieproject – Autonome Drone met AI-veiligheid

Dit project is ontwikkeld als onderdeel van een innovatieopdracht en richt zich op het autonoom aansturen van een **DJI Tello drone** met Python. Naast basisbesturing zijn ook **automatische vluchtroutes**, **veiligheidsmechanismen** en **gezichtsdetectie met OpenCV** geïmplementeerd.

---

## 📦 Functionaliteiten

- Verbinding maken met DJI Tello via WiFi  
- Basisbesturing (opstijgen, landen, bewegen, draaien)  
- Vooraf geprogrammeerde vluchtroutes  
- Noodstop tijdens vlucht  
- Gezichtsdetectie via live camerabeeld  
- AI-veiligheidsreactie: drone onderbreekt route en landt bij detectie van een gezicht  

---

## 🖥️ Benodigdheden

### Hardware
- DJI Tello Drone  
- Opgeladen batterij  
- Laptop met WiFi  

### Software
- Python 3.10 of hoger  
- PyCharm (aanbevolen) of andere Python IDE  

---

## 📚 Benodigde Python modules

Installeer deze via de terminal:

```bash
py -m pip install djitellopy
py -m pip install opencv-python
py -m pip install keyboard
py -m pip install numpy
```

---

## 📁 Projectstructuur

```
src/
 └── drone_controller.py      # Hoofdklasse voor dronebesturing

tests/
 ├── Connectie_test.py  # test de connectie en geeft batterij percentage terug
 ├── basic_flight.py    # Basis opstijgen en landen
 ├── movement_test.py   # Test van losse bewegingen
 ├── route_test.py      # Automatische vluchtroute
 ├── demo_flight.py     # Demo met noodstop
 └── Demo.py # Combinatie van alle functies
```

---

## 🔌 Verbinding maken met de drone

1. Zet de drone aan  
2. Verbind je laptop met het WiFi-netwerk:  
   **TELLO-XXXXXX**  
3. Wacht 10 seconden voordat je een script start  

---

## ▶️ Scripts uitvoeren

### Basis test (eerste test altijd hiermee beginnen)
```bash
python tests/basic_flight.py
```

### Bewegingen testen
```bash
python tests/movement_test.py
```

### Automatische route
```bash
python tests/route_test.py
```

### Demo met noodstop (druk op **E**)
```bash
python tests/demo_flight.py
```

### Einddemo met AI-gezichtsdetectie
```bash
python tests/Demo.py
```

---

## 🧠 Hoe werkt de AI-uitbreiding?

Tijdens de vlucht wordt het live camerabeeld van de drone geanalyseerd met **OpenCV**.  
Wanneer een gezicht wordt gedetecteerd:

1. De huidige vluchtroute wordt onderbroken  
2. De drone beweegt achteruit voor extra afstand  
3. De drone landt automatisch  

Dit is ontworpen als **veiligheidsmechanisme**, niet als volledige autonome navigatie.

---

## 🛑 Veiligheidsrichtlijnen

- Vlieg alleen in een ruime, rustige omgeving  
- Niet boven mensen vliegen  
- Controleer de batterij vóór elke vlucht  
- Gebruik de noodstop alleen bij gevaar  
- Houd altijd visueel contact met de drone  

---

## ⚠️ Veelvoorkomende problemen

| Probleem | Oplossing |
|---------|-----------|
Drone reageert niet | Controleer WiFi verbinding met TELLO |
Takeoff geeft error | Batterij te laag (min. 15%) |
Beeld werkt niet | Controleer of `opencv-python` is geïnstalleerd |
Noodstop werkt niet | Start PyCharm als administrator |

---

## 👨‍💻 Auteur

**Pieter van Haaften**  
Innovatieproject – Autonome Dronebesturing met AI-veiligheid
