# Chatbot Básico en Shiny for Python

Aplicación interactiva desarrollada con **Shiny for Python** que implementa un **Chatbot Básico** utilizando los componentes conversacionales nativos `ui.chat_ui()` y `ui.Chat()`, lista para ejecutarse localmente o desplegarse en **Posit Connect Cloud**.

---

## 📁 Estructura del Directorio

```text
Chatbot_Basico_Shiny/
├── app.py                            # Aplicación Shiny (UI + Server + Motor conversacional con memoria de contexto)
├── requirements.txt                  # Librerías requeridas para ejecución local y Posit Connect Cloud
├── manifest.json                     # Manifiesto de despliegue para Posit Connect Cloud
├── Reporte_Chatbot_Basico_Shiny.pdf  # Documentación con requerimientos, problemas y pasos seguidos
└── README.md                         # Guía rápida de ejecución y despliegue
```

---

## ✨ Características Principales

- **Componente Nativo `ui.Chat`**: Interfaz de mensajería moderna con burbujas para usuario y asistente, soporte de Markdown/LaTeX y desplazamiento automático.
- **Memoria de Contexto por Sesión (`reactive.value`)**:
  - **Seguimiento del Tema Activo**: Permite hacer preguntas de seguimiento sin repetir el tema (*«dame un ejemplo»*, *«muéstrame código»*, *«¿cuál es la diferencia?»*, *«¿cuál es la fórmula?»*, *«cuéntame más»*, *«explícame el primero / el segundo»* o *«volvamos al tema anterior»*).
  - **Cruce de Temas en Contexto**: Conecta el tema anterior con uno nuevo (ej. estar hablando de *Estadística* y preguntar *«¿y cómo hago eso en Python?»*).
  - **Memoria del Usuario e Historial**: Recuerda el nombre y perfil del usuario (*«Me llamo...»*, *«¿Cómo me llamo?»*) y genera resúmenes de la conversación (*«¿De qué estábamos hablando?»*).
- **Selector de Estilo de Respuesta**: Permite alternar en tiempo real entre tono **Amigable**, **Formal / Académico** y **Breve**.
- **Botones de Temas y Seguimiento Contextual**: Envía consultas de tema o preguntas de seguimiento con un solo clic desde la barra lateral.
- **Indicadores Reactivos (Value Boxes)**: Muestra el conteo de mensajes enviados, el **Contexto / Tema Activo** en tiempo real y el usuario/estilo activo.

---

## 🚀 1. Ejecución Local

1. Abre tu terminal en la carpeta del proyecto:
   ```bash
   cd "Chatbot_Basico_Shiny"
   ```
2. Ejecuta la aplicación:
   ```bash
   python app.py
   # o usando el CLI de Shiny:
   shiny run --reload --port 8000 app.py
   ```
3. Abre tu navegador en **`http://127.0.0.1:8000`**.

---

## ☁️ 2. Despliegue en Posit Connect Cloud

1. Sube la carpeta `Chatbot_Basico_Shiny` a tu repositorio de GitHub.
2. Inicia sesión en **[Posit Connect Cloud](https://connect.posit.cloud/)**.
3. Haz clic en **Publish** → **Shiny** → selecciona tu repositorio y el archivo `Chatbot_Basico_Shiny/app.py`.
4. Haz clic en **Deploy**.
