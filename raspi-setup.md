# Setup de Feedy en la Raspberry Pi

Este documento explica cómo dejar la app lista en la Raspberry Pi, desde clonar el repositorio hasta arrancar la aplicación con la cámara CSI funcionando.

## 1) Clonar el proyecto en la Raspberry

Si el repositorio todavía no existe en la Raspberry:

```bash
git clone <URL_DEL_REPO> feedy
cd feedy
```

Si ya existe:

```bash
cd feedy
git pull
```

---

## 2) Crear un entorno virtual

```bash
cd ~/feedy
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3) Instalar dependencias del proyecto

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Si falta soporte para la cámara CSI en la Raspberry, instalar también:

```bash
sudo apt update
sudo apt install -y python3-opencv python3-picamera2
```

> En Raspberry Pi OS moderno, `picamera2` es la forma recomendada para trabajar con la cámara CSI.

---

## 4) Verificar que la cámara esté detectada

Ejecutá:

```bash
rpicam-hello --list-cameras
```

Si la salida muestra una cámara tipo `ov5647`, la Raspberry la está viendo correctamente.

También podés probar la cámara con una foto fija:

```bash
rpicam-jpeg --output prueba.jpg
ls -l prueba.jpg
```

Si el archivo se crea, la cámara funciona.

---

## 5) Habilitar la cámara (si hace falta)

En la Raspberry, probar esto:

```bash
sudo raspi-config
```

Y luego entrar a:

- Interface Options
- Camera
- Enable

Si la opción no aparece, no es un problema: en muchos sistemas nuevos la cámara se maneja con `rpicam` y `picamera2`, no con la interfaz clásica.

---

## 6) Arrancar la app

Desde la carpeta del proyecto:

```bash
cd ~/feedy
source .venv/bin/activate
python run.py
```

La app quedará disponible en:

```text
http://<IP_DE_LA_RASPBERRY>:5000
```

---

## 7) Importante sobre la cámara

La cámara conectada al puerto "Camera" es la cámara CSI de la Raspberry.

No se puede abrir desde el navegador con `getUserMedia`, porque eso solo accede a la webcam del equipo que está navegando.

La Raspberry debe:

1. capturar frames con la cámara CSI
2. mandar esos frames a Flask
3. Flask expone un stream en `/video_feed`
4. la web lo muestra en el modal de cámara

Esto ya está implementado en la app.

---

## 8) Pull y actualización del repo

Cada vez que hagas cambios en tu PC y los subas a Git:

```bash
git add .
git commit -m "Actualización de la app"
git push origin main
```

Luego en la Raspberry:

```bash
cd ~/feedy
git pull
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

---

## 9) Si el puerto 5000 está ocupado

Si al arrancar la app aparece:

```bash
Address already in use
Port 5000 is in use by another program
```

Hay otra instancia corriendo. Podés revisar qué proceso es:

```bash
sudo lsof -i :5000
```

O matarlo si hace falta:

```bash
sudo kill -9 <PID>
```

Luego volver a correr:

```bash
python run.py
```

---

## 10) Recomendación final

Para evitar problemas, hace esto cada vez que hagas cambios importantes:

```bash
git status
git add .
git commit -m "Cambio funcional"
git push
ssh <raspberry>
cd ~/feedy
git pull
source .venv/bin/activate
python run.py
```

---

## 11) Estado esperado de la app

Con esto, la Raspberry debe poder:

- correr la app Flask
- detectar la cámara CSI
- servir el stream en `/video_feed`
- mostrar la cámara en la interfaz cuando el usuario aprieta "Ver camara en tiempo real"

