# OpenGL Light Lab

Interaktywny edytor efektów świetlnych pozwalający eksperymentować z parametrami oświetlenia, materiałów i tekstur w czasie rzeczywistym. Aplikacja wykorzystuje OpenGL i Qt do wizualizacji sceny 3D z trzema obiektami oraz konfigurowalnym źródłem światła.

## Animacja

![animation](animation.gif)

## Funkcjonalności

### Scena 3D

- **Trzy obiekty:** cylinder (czerwony), sześcian (niebieski/teksturowany), cylinder (zielony)
- **Automatyczna rotacja** obiektów wokół różnych osi
- **Wyświetlanie osi współrzędnych** (X/Y/Z)
- **Wizualizacja źródła światła** (sfera dla punktowego, kwadrat "słońce" dla kierunkowego)

### Oświetlenie

- **Światło punktowe** z konfigurowalną pozycją i tłumieniem (constant/linear/quadratic)
- **Światło kierunkowe** z konfigurowalnym wektorem kierunku
- **Kolory światła:** diffuse, ambient, specular
- **Model oświetlenia:** local viewer, two-sided lighting

### Materiały

- Różne materiały dla każdego obiektu (czerwony, niebieski, zielony)
- Parametry: ambient, diffuse, specular, shininess

### Tekstury

- Dynamiczne ładowanie tekstur JPG z folderu `textures/`
- Możliwość wyboru tekstury dla centralnego sześcianu z GUI

### Kamera

- **Projekcja perspektywiczna** z regulowanym FOV
- **Projekcja ortogonalna** z regulowaną wysokością
- Sterowanie kamerą w układzie sferycznym (distance, theta, phi)

## Sterowanie klawiaturowe

| Klawisz | Akcja |
|---------|-------|
| `W/S` | Zmiana kąta theta kamery |
| `A/D` | Zmiana kąta phi kamery |
| `Q/E` | Zoom out/in (lub zmiana ortho half-height) |
| `U/J` | Przesunięcie światła Z +/- |
| `H/K` | Przesunięcie światła X +/- |
| `Y/I` | Przesunięcie światła Y +/- |
| `[/]` | Zmiana FOV (perspektywa) |
| `Z/X` | Zmiana odległości bocznych obiektów |
| `?` | Przełączenie nakładki pomocy |
| `Esc` | Wyjście z aplikacji |

## Wymagania

- Python 3.12+
- PySide6 (Qt 6)
- PyOpenGL
- Pillow

## Instalacja

```bash
git clone [<repo-url>](https://github.com/Nircek/opengl-light-lab.git)
cd opengl-light-lab
poetry install
```

## Uruchomienie

```bash
poetry run ui
```

## Struktura projektu

```text
opengl_light_lab/
├── __init__.py          # Eksporty modułu
├── __main__.py          # Entry point aplikacji
├── app_state.py         # Stan aplikacji (dataclass)
├── control_panel.py     # Panel kontrolny Qt (dock widget)
├── gl_widget.py         # Widget OpenGL z renderowaniem sceny
├── input_handler.py     # Obsługa klawiatury
├── main_window.py       # Główne okno aplikacji
├── materials.py         # Definicje materiałów OpenGL
├── primitives.py        # Prymitywy geometryczne (sześcian, cylinder)
└── textures.py          # Manager tekstur

textures/                # Folder z teksturami JPG
├── Bricks054_1K-JPG_Color.jpg
└── Wood026_1K-JPG_Color.jpg
```

## Panel kontrolny

Aplikacja zawiera dokowany panel kontrolny z sekcjami:

1. **Scene** - auto-rotacja, wyświetlanie osi i markera światła, włączanie oświetlenia i depth test
2. **Camera** - typ projekcji, odległość, kąty, FOV, ortho height
3. **Light Source** - typ światła, pozycja/kierunek, tłumienie
4. **Light Properties** - kolory diffuse/ambient/specular, model oświetlenia
5. **Objects** - odległość bocznych obiektów, tekstura centralnego sześcianu


## Możliwe rozszerzenia

- [ ] Zapis i odczyt konfiguracji sceny
- [ ] Wiele źródeł światła
- [ ] Materiały PBR (Physically Based Rendering)
- [ ] Shadery GLSL (modern OpenGL)
- [ ] Import modeli 3D (OBJ, GLTF)
- [ ] Normal mapping i displacement mapping
