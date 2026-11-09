from datetime import datetime
import random
import re
import unicodedata
from shiny import App, render, ui, reactive

# -----------------------------------------------------------------------------
# Utilidades de normalización y análisis de contexto
# -----------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    """Convierte a minúsculas y elimina tildes para coincidencias flexibles."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto.lower().strip())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


ETIQUETAS_TEMAS = {
    "ninguno": "💬 General / Inicio",
    "shiny": "✨ Shiny for Python",
    "python": "🐍 Python",
    "ciencia_datos": "📊 Ciencia de Datos",
    "estadistica": "📈 Estadística",
    "machine_learning": "🤖 Machine Learning / IA",
    "visualizacion": "🎨 Visualización de Datos",
    "sql_datos": "🗄️ SQL y Bases de Datos",
    "chiste": "😄 Humor / Chistes",
}

# -----------------------------------------------------------------------------
# Subtemas específicos (para preguntas de profundización puntual en contexto)
# -----------------------------------------------------------------------------
SUBTEMAS_ESPECIFICOS = {
    "pandas": {
        "tema": "python",
        "titulo": "Pandas (Manipulación de Datos en Python)",
        "respuesta": (
            "🐼 **Pandas** es la librería principal de **Python** para trabajar con datos tabulares:\n\n"
            "- **`Series`**: Columna unidimensional indexada.\n"
            "- **`DataFrame`**: Tabla bidimensional (filas y columnas) similar a una hoja de cálculo o tabla SQL.\n"
            "- **Operaciones clave**: `df.head()`, `df.describe()`, `df.groupby()`, `df.merge()` y `df.dropna()`.\n\n"
            "```python\n"
            "import pandas as pd\n"
            "df = pd.DataFrame({'Producto': ['A', 'B'], 'Ventas': [120, 340]})\n"
            "print(df[df['Ventas'] > 150])\n"
            "```"
        ),
    },
    "numpy": {
        "tema": "python",
        "titulo": "NumPy (Cálculo Numérico y Álgebra Lineal)",
        "respuesta": (
            "🔢 **NumPy** (*Numerical Python*) es la base del cálculo científico en **Python**:\n\n"
            "- Proporciona el objeto **`ndarray`** (arreglo multidimensional homogéneo en memoria contigua).\n"
            "- Permite operaciones **vectorizadas** y *broadcasting* a velocidad de C sin usar bucles `for`.\n\n"
            "```python\n"
            "import numpy as np\n"
            "x = np.array([10, 20, 30, 40])\n"
            "print('Media:', x.mean(), '| Doble:', x * 2)\n"
            "```"
        ),
    },
    "reactividad": {
        "tema": "shiny",
        "titulo": "Programación Reactiva en Shiny",
        "respuesta": (
            "⚡ La **Reactividad en Shiny** conecta automáticamente las entradas del usuario (`input`) con las salidas (`output`):\n\n"
            "1. **Fuente reactiva (`input.x()`)**: Cambia cuando el usuario mueve un control o envía un mensaje.\n"
            "2. **Expresión reactiva (`@reactive.calc`)**: Calcula un resultado intermedio y lo guarda en caché.\n"
            "3. **Efecto / Salida (`@reactive.effect` / `@render`)**: Actualiza la pantalla automáticamente."
        ),
    },
    "media": {
        "tema": "estadistica",
        "titulo": "Media Aritmética (Promedio)",
        "respuesta": (
            "📐 En **Estadística**, la **Media Aritmética ($\\bar{x}$)** es la suma de todos los valores dividida entre el total de observaciones ($n$):\n\n"
            "$$\\bar{x} = \\frac{1}{n} \\sum_{i=1}^{n} x_i$$\n\n"
            "- **Ventaja**: Utiliza todos los datos de la muestra.\n"
            "- **Desventaja**: Es muy sensible a valores extremos (*outliers*). En esos casos conviene usar la **mediana**."
        ),
    },
    "mediana": {
        "tema": "estadistica",
        "titulo": "Mediana (Medida Robusta de Tendencia Central)",
        "respuesta": (
            "🎯 En **Estadística**, la **Mediana ($Me$)** es el valor que ocupa la posición central cuando los datos están ordenados de menor a mayor:\n\n"
            "- Divide la distribución exactamente al **50%** (Percentil 50 o Cuartil $Q_2$).\n"
            "- **Gran ventaja**: Es una métrica **robusta**; no se altera aunque existan valores atípicos extremos.\n"
            "- **Ejemplo**: En `[10, 12, 14, 15, 500]`, la media se dispara a `110.2`, pero la **mediana** sigue siendo **`14`**."
        ),
    },
    "desviacion": {
        "tema": "estadistica",
        "titulo": "Desviación Estándar y Varianza",
        "respuesta": (
            "📏 En **Estadística**, la **Desviación Estándar ($s$)** cuantifica qué tanto se alejan en promedio los datos respecto a la media:\n\n"
            "$$s = \\sqrt{\\frac{1}{n - 1} \\sum_{i=1}^{n} (x_i - \\bar{x})^2}$$\n\n"
            "- Si $s$ es cercana a $0$, los datos están muy concentrados alrededor del promedio.\n"
            "- Su cuadrado ($s^2$) se conoce como **Varianza**."
        ),
    },
    "correlacion": {
        "tema": "estadistica",
        "titulo": "Correlación Estadística",
        "respuesta": (
            "🔗 El **Coeficiente de Correlación de Pearson ($r$)** mide la relación lineal entre dos variables numéricas ($X$ e $Y$):\n\n"
            "- $r \\approx +1$: Correlación positiva fuerte (si sube $X$, sube $Y$).\n"
            "- $r \\approx -1$: Correlación negativa fuerte (si sube $X$, baja $Y$).\n"
            "- $r \\approx 0$: Sin relación lineal.\n"
            "- ⚠️ *Regla de oro*: **Correlación no implica causalidad**."
        ),
    },
    "supervisado": {
        "tema": "machine_learning",
        "titulo": "Aprendizaje Supervisado (Machine Learning)",
        "respuesta": (
            "🎯 En **Aprendizaje Supervisado**, el algoritmo entrena con datos históricos que incluyen tanto las variables predictoras ($X$) como la respuesta correcta o etiqueta ($y$):\n\n"
            "1. **Regresión** ($y$ es continua): Predecir el precio de una casa o la temperatura de mañana (ej. *Regresión Lineal*, *XGBoost*).\n"
            "2. **Clasificación** ($y$ es categórica): Detectar si un correo es *Spam / No Spam* o si un tumor es *Benigno / Maligno* (ej. *Regresión Logística*, *Random Forest*)."
        ),
    },
    "no_supervisado": {
        "tema": "machine_learning",
        "titulo": "Aprendizaje No Supervisado (Machine Learning)",
        "respuesta": (
            "🔍 En **Aprendizaje No Supervisado**, el modelo recibe únicamente datos sin etiquetar ($X$) y descubre patrones ocultos por sí mismo:\n\n"
            "1. **Clustering (Agrupamiento)**: Agrupa observaciones similares (ej. segmentación de clientes con **K-Means** o **DBSCAN**).\n"
            "2. **Reducción de Dimensionalidad**: Comprime muchas variables conservando la varianza principal (ej. **PCA** o **t-SNE**)."
        ),
    },
    "overfitting": {
        "tema": "machine_learning",
        "titulo": "Overfitting (Sobreajuste) vs. Underfitting",
        "respuesta": (
            "⚠️ En **Machine Learning**, el **Overfitting (Sobreajuste)** ocurre cuando un modelo memoriza el ruido de los datos de entrenamiento (logrando casi 100% de acierto en *Train*), pero falla al predecir datos nuevos (*Test*).\n\n"
            "**¿Cómo evitarlo?**\n"
            "- Usar validación cruzada (*Cross-Validation*).\n"
            "- Aplicar regularización ($L_1$ Lasso / $L_2$ Ridge).\n"
            "- Recolectar más datos o podar la profundidad del modelo."
        ),
    },
    "eda": {
        "tema": "ciencia_datos",
        "titulo": "Análisis Exploratorio de Datos (EDA)",
        "respuesta": (
            "🔍 El **EDA (*Exploratory Data Analysis*)** es la fase de la **Ciencia de Datos** donde investigamos el dataset antes de modelar:\n\n"
            "- Revisar dimensiones (`df.shape`), tipos de datos (`df.dtypes`) y valores faltantes (`df.isna().sum()`).\n"
            "- Analizar distribuciones con histogramas y boxplots para detectar *outliers*.\n"
            "- Calcular matrices de correlación para elegir las mejores variables."
        ),
    },
}

# -----------------------------------------------------------------------------
# Base de conocimiento estructurada por tema y aspecto (para seguimiento contextual)
# -----------------------------------------------------------------------------
BASE_CONOCIMIENTO = {
    "shiny": {
        "nombre": "Shiny for Python",
        "definicion": (
            "**Shiny for Python** es un framework moderno desarrollado por *Posit* que permite crear "
            "aplicaciones web interactivas, dashboards y chatbots directamente en Python, sin necesidad "
            "de escribir HTML, CSS o JavaScript.\n\n"
            "- ⚡ **Programación Reactiva**: Actualiza automáticamente las salidas (`@render`) cuando cambian las entradas (`input`).\n"
            "- 💬 **Interfaces Conversacionales**: Incluye `ui.chat_ui()` y `ui.Chat()` para construir chatbots con memoria.\n"
            "- ☁️ **Despliegue Directo**: Compatible con *Posit Connect Cloud* y servidores locales.\n\n"
            "💡 *Seguimiento: Puedes pedirme «dame un ejemplo», «muéstrame código», «¿qué ventajas tiene?» o «¿cómo se instala?».*"
        ),
        "profundizacion": (
            "Profundizando en **Shiny for Python**, su arquitectura se divide en tres piezas clave:\n\n"
            "1. **Interfaz de Usuario (`app_ui`)**: Define el diseño visual con funciones como `ui.page_sidebar()`, `ui.card()`, `ui.value_box()` y controles `ui.input_*`.\n"
            "2. **Servidor Reactivo (`server`)**: Conecta entradas y salidas mediante decoradores reactivos:\n"
            "   - `@reactive.calc`: Calcula valores en caché que solo se recalculan si cambian sus dependencias.\n"
            "   - `@reactive.effect` + `@reactive.event`: Ejecuta acciones secundarias (ej. al pulsar un botón o recibir un mensaje en el chat).\n"
            "   - `reactive.value()`: Almacena estado con memoria por sesión (¡como el contexto de este chatbot!).\n"
            "3. **Objeto `App(app_ui, server)`**: Une la vista y la lógica para servir la aplicación mediante *Uvicorn / Starlette*."
        ),
        "ejemplo": (
            "Aquí tienes un **caso práctico de uso de Shiny**:\n\n"
            "- Imagina que tienes un dataset de ventas mensuales.\n"
            "- En la barra lateral colocas un `ui.input_select('region', 'Región:', ...)`.\n"
            "- En el panel principal colocas un `ui.output_plot('grafico')` y un `ui.value_box()`.\n"
            "- Cada vez que el usuario cambia la región, Shiny filtra el DataFrame reactivamente y redibuja el gráfico en milisegundos sin recargar toda la página."
        ),
        "codigo": (
            "Aquí tienes un **ejemplo en código de Shiny for Python** con estado reactivo:\n\n"
            "```python\n"
            "from shiny import App, render, ui, reactive\n\n"
            "app_ui = ui.page_fluid(\n"
            "    ui.input_slider('n', 'Número de datos:', 10, 100, 50),\n"
            "    ui.output_text_verbatim('resumen')\n"
            ")\n\n"
            "def server(input, output, session):\n"
            "    @render.text\n"
            "    def resumen():\n"
            "        return f'Seleccionaste {input.n()} observaciones en tiempo real.'\n\n"
            "app = App(app_ui, server)\n"
            "```"
        ),
        "ventajas": (
            "Las principales **ventajas de Shiny for Python** son:\n\n"
            "- 🔄 **Reactividad real (Grafo de dependencias)**: A diferencia de otros frameworks que re-ejecutan todo el script de arriba a abajo en cada clic, Shiny solo recalcula los componentes afectados.\n"
            "- 🧩 **Componentes nativos para IA**: Soporte integrado para streaming asíncrono (`async/await`) con `shinychat`.\n"
            "- 🎨 **Diseño Bootstrap 5**: Tarjetas, pestañas y cajas de valor listas para producción."
        ),
        "instalacion": (
            "Para **instalar y ejecutar Shiny for Python** en tu entorno:\n\n"
            "```bash\n"
            "pip install shiny shinychat\n"
            "shiny run --reload --port 8000 app.py\n"
            "```\n"
            "Para desplegar en **Posit Connect Cloud**, solo necesitas incluir `app.py`, `requirements.txt` y `manifest.json`."
        ),
        "comparacion": (
            "Comparativa de **Shiny for Python vs. Streamlit vs. Dash**:\n\n"
            "| Característica | ✨ Shiny for Python | 🎈 Streamlit | 📊 Dash (Plotly) |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| **Modelo de ejecución** | Reactivo granular (eficiente) | Re-ejecución completa del script | Callbacks explícitos |\n"
            "| **Estado / Memoria** | Nativo con `reactive.value()` | Requiere `st.session_state` | Requiere `dcc.Store` |\n"
            "| **Chatbots asíncronos** | Nativo con `ui.Chat` (`async`) | Básico (`st.chat_message`) | Manual con componentes externos |"
        ),
        "formula": (
            "En **Shiny**, la relación fundamental no es una ecuación algebraica sino el **Grafo Reactivo**:\n\n"
            "$$\\text{Input Reactivo } (X) \\xrightarrow{\\text{@reactive.calc}} \\text{Estado Derivado } f(X) \\xrightarrow{\\text{@render}} \\text{Output UI}$$"
        ),
    },
    "python": {
        "nombre": "Python",
        "definicion": (
            "🐍 **Python** es el lenguaje de programación líder en Ciencia de Datos, Inteligencia Artificial "
            "y desarrollo de aplicaciones analíticas gracias a su sintaxis legible y su ecosistema científico:\n\n"
            "- **Pandas / Polars**: Manipulación y limpieza de datos tabulares (*DataFrames*).\n"
            "- **NumPy**: Cálculo numérico vectorizado y álgebra lineal.\n"
            "- **Matplotlib / Seaborn / Plotly**: Visualización de datos estática e interactiva.\n"
            "- **Scikit-learn / PyTorch**: Machine Learning y Deep Learning.\n\n"
            "💡 *Seguimiento: Pregúntame «dame un ejemplo», «muéstrame código», «¿cuál es la diferencia entre sus librerías?» o «¿cómo empiezo?».*"
        ),
        "profundizacion": (
            "Profundizando en **Python para Ciencia de Datos**:\n\n"
            "- **Tipado dinámico y multiparadigma**: Permite programación funcional, orientada a objetos y scripts interactivos (Jupyter Notebooks).\n"
            "- **Vectorización con NumPy**: Aunque Python puro es interpretado, librerías como NumPy y Pandas ejecutan operaciones matriciales en C/C++ y Rust por debajo, logrando alto rendimiento.\n"
            "- **Programación Asíncrona (`asyncio`)**: Permite manejar múltiples tareas concurrentes (como este chatbot en Shiny) usando `async def` y `await`."
        ),
        "ejemplo": (
            "Un **ejemplo clásico en Python** para análisis de datos:\n\n"
            "Supongamos que tienes un archivo `ventas.csv` con miles de registros. Con **Pandas** en solo 3 pasos puedes:\n"
            "1. Leer el archivo con `df = pd.read_csv('ventas.csv')`.\n"
            "2. Filtrar valores nulos y agrupar por categoría: `df.groupby('categoria')['ingreso'].mean()`.\n"
            "3. Exportar o graficar el resultado inmediatamente."
        ),
        "codigo": (
            "Aquí tienes un **ejemplo en código de Python** usando `pandas` y `numpy`:\n\n"
            "```python\n"
            "import pandas as pd\n"
            "import numpy as np\n\n"
            "datos = pd.DataFrame({\n"
            "    'Estudiante': ['Ana', 'Luis', 'Carlos', 'Elena'],\n"
            "    'Calificacion': [92, 85, 78, 96]\n"
            "})\n\n"
            "promedio = np.mean(datos['Calificacion'])\n"
            "destacados = datos[datos['Calificacion'] >= 90]\n"
            "print(f'Promedio del grupo: {promedio:.1f}')\n"
            "```"
        ),
        "ventajas": (
            "¿Por qué elegir **Python**?\n\n"
            "- 📚 **Comunidad y Ecosistema**: Más de 500,000 paquetes en *PyPI*.\n"
            "- 🔗 **Integración Total**: Conecta bases de datos SQL, APIs REST, modelos de IA y dashboards web (como **Shiny**).\n"
            "- 🚀 **Curva de aprendizaje suave**: Su sintaxis limpia se asemeja al pseudocódigo en inglés."
        ),
        "instalacion": (
            "Para **instalar Python y su entorno de Ciencia de Datos**:\n\n"
            "1. Descarga Python 3.11+ desde `python.org` o usa *Miniconda*.\n"
            "2. Crea un entorno virtual:\n"
            "```bash\n"
            "python -m venv .venv\n"
            ".venv\\Scripts\\activate\n"
            "pip install numpy pandas matplotlib scikit-learn shiny shinychat\n"
            "```"
        ),
        "comparacion": (
            "Comparativa de las principales **librerías de datos en Python**:\n\n"
            "| Librería | Estructura Base | Uso Principal |\n"
            "| :--- | :--- | :--- |\n"
            "| **NumPy** | `ndarray` (Arreglos N-dimensionales) | Álgebra lineal, matrices y cálculo numérico rápido |\n"
            "| **Pandas** | `DataFrame` / `Series` | Limpieza, cruce (`merge`), agrupación y tablas heterogéneas |\n"
            "| **Polars** | `DataFrame` (Multihilo en Rust) | Procesamiento de grandes volúmenes de datos a alta velocidad |"
        ),
        "formula": (
            "En **Python con NumPy**, las operaciones se expresan de forma **vectorizada** sin bucles `for`:\n\n"
            "$$\\mathbf{z} = a \\cdot \\mathbf{x} + \\mathbf{y} \\quad \\Longleftrightarrow \\quad \\texttt{z = a * x + y}$$"
        ),
    },
    "ciencia_datos": {
        "nombre": "Ciencia de Datos",
        "definicion": (
            "📊 La **Ciencia de Datos (Data Science)** es una disciplina interdisciplinaria que combina "
            "**estadística**, **programación** y **conocimiento del negocio** para transformar datos crudos en decisiones estratégicas.\n\n"
            "**Flujo de vida de un proyecto (CRISP-DM):**\n"
            "1. 🧹 **Recolección e Ingeniería de Datos** (*Data Wrangling* / ETL).\n"
            "2. 🔍 **Análisis Exploratorio de Datos** (*EDA*).\n"
            "3. 🤖 **Modelado Estadístico y Machine Learning**.\n"
            "4. 📈 **Comunicación y Despliegue** (ej. aplicaciones interactivas en **Shiny**).\n\n"
            "💡 *Seguimiento: Puedes decirme «dame un ejemplo», «cuéntame más», «muéstrame código» o «¿cuál es la diferencia con analítica?».*"
        ),
        "profundizacion": (
            "Profundizando en **Ciencia de Datos**, la etapa crítica suele ser el **preprocesamiento y EDA** (que toma entre el 60% y 80% del tiempo):\n\n"
            "- **Imputación de datos faltantes (`NaN`)**: Reemplazar por media, mediana o modelos predictivos.\n"
            "- **Detección de valores atípicos (*Outliers*)**: Usando el rango intercuartílico ($IQR = Q_3 - Q_1$) o $Z$-score.\n"
            "- **Ingeniería de variables (*Feature Engineering*)**: Codificación *One-Hot*, escalamiento (*StandardScaler*) y creación de nuevas métricas."
        ),
        "ejemplo": (
            "Un **ejemplo real de Ciencia de Datos**:\n\n"
            "En una plataforma de streaming o comercio electrónico:\n"
            "1. Se recolecta el historial de clics, tiempo de visualización y compras de los usuarios.\n"
            "2. En el **EDA** se descubre que los usuarios que no usan la app en 10 días tienen un 70% de probabilidad de cancelar su suscripción (*Churn*).\n"
            "3. Se entrena un modelo predictivo y se despliega un dashboard en **Shiny** para alertar al equipo de retención."
        ),
        "codigo": (
            "Ejemplo de un **Análisis Exploratorio de Datos (EDA)** rápido en Python:\n\n"
            "```python\n"
            "import pandas as pd\n\n"
            "df = pd.read_csv('clientes.csv')\n"
            "# 1. Resumen estadístico y valores nulos\n"
            "print(df.info())\n"
            "print(df.describe())\n\n"
            "# 2. Limpieza de nulos con la mediana\n"
            "df['ingreso'] = df['ingreso'].fillna(df['ingreso'].median())\n\n"
            "# 3. Agrupación por segmento\n"
            "resumen = df.groupby('segmento')['ingreso'].agg(['count', 'mean', 'std'])\n"
            "```"
        ),
        "ventajas": (
            "Beneficios de aplicar **Ciencia de Datos**:\n\n"
            "- 🎯 **Decisiones basadas en evidencia**: Reduce la incertidumbre y los sesgos subjetivos.\n"
            "- 🔮 **Capacidad predictiva**: Permite anticipar demanda, riesgos o fallas antes de que ocurran.\n"
            "- ⚙️ **Automatización**: Optimiza procesos operativos mediante algoritmos."
        ),
        "instalacion": (
            "Para comenzar tu ruta en **Ciencia de Datos**, las herramientas esenciales que debes instalar son:\n\n"
            "- **Lenguaje**: Python 3.11+ o R.\n"
            "- **Entorno**: VS Code o JupyterLab (`pip install jupyterlab`).\n"
            "- **Stack de librerías**: `pandas`, `numpy`, `scipy`, `seaborn`, `scikit-learn` y `shiny`."
        ),
        "comparacion": (
            "Diferencias entre **roles en el ecosistema de datos**:\n\n"
            "| Rol | Enfoque Principal | Herramientas Clave |\n"
            "| :--- | :--- | :--- |\n"
            "| **Analista de Datos** | ¿Qué pasó y por qué? (Reportes, KPIs, BI) | SQL, Excel, Power BI, Shiny |\n"
            "| **Científico de Datos** | ¿Qué pasará? (Estadística avanzada, Modelos ML) | Python, R, Scikit-learn, Shiny |\n"
            "| **Ingeniero de Datos** | ¿Cómo fluyen y se almacenan los datos? (Pipelines) | SQL, Spark, Airflow, Cloud |"
        ),
        "formula": (
            "En **Ciencia de Datos**, la detección de *outliers* mediante el **Rango Intercuartílico ($IQR$)** se define como:\n\n"
            "$$IQR = Q_3 - Q_1 \\quad \\Longrightarrow \\quad \\text{Límites} = [Q_1 - 1.5 \\cdot IQR,\\; Q_3 + 1.5 \\cdot IQR]$$"
        ),
    },
    "estadistica": {
        "nombre": "Estadística",
        "definicion": (
            "📈 La **Estadística** es la base matemática de la Ciencia de Datos. Se divide en dos grandes ramas:\n\n"
            "1. **Estadística Descriptiva** (Resume los datos):\n"
            "   - **Media ($\\bar{x}$)**: Promedio aritmético de los valores.\n"
            "   - **Mediana**: Valor central que divide los datos ordenados al 50% (robusta ante valores extremos).\n"
            "   - **Desviación Estándar ($s$ / $\\sigma$)**: Mide qué tan dispersos están los datos respecto a la media.\n"
            "2. **Estadística Inferencial** (Saca conclusiones de una muestra):\n"
            "   - Intervalos de confianza, pruebas de hipótesis ($p$-valor) y correlación ($r$).\n\n"
            "💡 *Seguimiento: Pídeme «dame un ejemplo», «¿cuál es la fórmula?», «muéstrame código» o «¿cuál es la diferencia entre media y mediana?».*"
        ),
        "profundizacion": (
            "Profundizando en **Estadística Inferencial y Probabilidad**:\n\n"
            "- **Teorema del Límite Central (TLC)**: Al tomar muestras suficientemente grandes ($n \\ge 30$), la distribución de las medias muestrales se aproxima a una **Distribución Normal** sin importar la forma original de los datos.\n"
            "- **Valor $p$ ($p$-value)**: En una prueba de hipótesis, si $p < \\alpha$ (usualmente $\\alpha = 0.05$), rechazamos la hipótesis nula ($H_0$) y concluimos que el efecto observado es estadísticamente significativo.\n"
            "- **Coeficiente de Correlación de Pearson ($r \\in [-1, 1]$)**: Mide la fuerza y dirección de la asociación lineal entre dos variables cuantitativas."
        ),
        "ejemplo": (
            "Aquí tienes un **ejemplo numérico de Estadística Descriptiva**:\n\n"
            "Supongamos que los sueldos mensuales (en miles) de 5 empleados son: **`[12, 14, 15, 16, 93]`**.\n"
            "- **Media ($\\bar{x}$)**: $(12+14+15+16+93)/5 = \\mathbf{30}$ mil (¡distorsionada por el valor extremo de 93!).\n"
            "- **Mediana**: El dato central ordenado es **$15$ mil** (refleja mucho mejor al empleado típico).\n"
            "- **Conclusión**: Cuando hay asimetría o *outliers*, la **mediana** es mejor medida de tendencia central que la media."
        ),
        "codigo": (
            "Así se calculan las **métricas estadísticas en Python** con `numpy` y `scipy`:\n\n"
            "```python\n"
            "import numpy as np\n"
            "from scipy import stats\n\n"
            "datos = np.array([12, 14, 15, 16, 15, 18, 93])\n\n"
            "print('Media:', np.mean(datos))\n"
            "print('Mediana:', np.median(datos))\n"
            "print('Moda:', stats.mode(datos, keepdims=True).mode[0])\n"
            "print('Desv. Estándar muestral:', np.std(datos, ddof=1))\n"
            "```"
        ),
        "ventajas": (
            "¿Por qué es indispensable la **Estadística**?\n\n"
            "- 🛡️ **Evita conclusiones falsas**: Distingue entre correlación casual y causalidad real.\n"
            "- 📏 **Cuantifica la incertidumbre**: Permite medir márgenes de error e intervalos de confianza.\n"
            "- 🧠 **Base del Machine Learning**: Todo modelo predictivo optimiza una función de pérdida probabilística o estadística."
        ),
        "instalacion": (
            "Para trabajar con **Estadística en Python**, instala las librerías científicas:\n\n"
            "```bash\n"
            "pip install numpy scipy statsmodels pingouin\n"
            "```\n"
            "- `scipy.stats` para distribuciones y pruebas de hipótesis.\n"
            "- `statsmodels` para regresiones con tablas ANOVA y $p$-valores detallados."
        ),
        "comparacion": (
            "Comparativa de **Métricas Estadísticas Clave**:\n\n"
            "| Métrica | ¿Qué mide? | ¿Sensible a Outliers (valores extremos)? |\n"
            "| :--- | :--- | :--- |\n"
            "| **Media ($\\bar{x}$)** | Promedio aritmético | ⚠️ Sí, muy sensible |\n"
            "| **Mediana ($Me$)** | Valor central (Percentil 50) | ✅ No, es una métrica robusta |\n"
            "| **Desviación Estándar ($s$)** | Dispersión alrededor de la media | ⚠️ Sí, se infla con extremos |\n"
            "| **Rango Intercuartílico ($IQR$)** | Dispersión del 50% central de los datos | ✅ No, es robusto |"
        ),
        "formula": (
            "Las **fórmulas fundamentales de Estadística Descriptiva** son:\n\n"
            "- **Media Muestral**:\n"
            "$$\\bar{x} = \\frac{1}{n} \\sum_{i=1}^{n} x_i$$\n"
            "- **Desviación Estándar Muestral**:\n"
            "$$s = \\sqrt{\\frac{1}{n - 1} \\sum_{i=1}^{n} (x_i - \\bar{x})^2}$$\n"
            "- **Estandarización ($Z$-score)**:\n"
            "$$z_i = \\frac{x_i - \\bar{x}}{s}$$"
        ),
    },
    "machine_learning": {
        "nombre": "Machine Learning e Inteligencia Artificial",
        "definicion": (
            "🤖 El **Machine Learning (Aprendizaje Automático)** es la rama de la Inteligencia Artificial donde los "
            "algoritmos aprenden patrones a partir de datos históricos sin ser programados con reglas rígidas:\n\n"
            "- 🎯 **Aprendizaje Supervisado** (Datos con etiqueta $y$): *Regresión* (predecir números continuos) y *Clasificación* (predecir categorías).\n"
            "- 🔍 **Aprendizaje No Supervisado** (Datos sin etiqueta): *Clustering* (ej. K-Means) y *Reducción de dimensionalidad* (PCA).\n"
            "- 🧠 **Deep Learning**: Redes neuronales profundas y modelos de lenguaje (*Transformers*).\n\n"
            "💡 *Seguimiento: Pregúntame «dame un ejemplo», «muéstrame código», «¿cuál es la diferencia entre supervisado y no supervisado?» o «¿cuál es la fórmula?».*"
        ),
        "profundizacion": (
            "Profundizando en **Machine Learning**, un concepto crucial es el equilibrio entre **Sesgo y Varianza**:\n\n"
            "- 📉 **Underfitting (Subajuste)**: El modelo es demasiado simple y no captura los patrones ni siquiera en los datos de entrenamiento.\n"
            "- 📈 **Overfitting (Sobreajuste)**: El modelo memoriza el ruido de los datos de entrenamiento y falla al generalizar con datos nuevos.\n"
            "- ✅ **Solución**: Dividir los datos en *Entrenamiento (Train)* y *Prueba (Test)* (ej. 80% / 20%) y aplicar **Validación Cruzada (*K-Fold Cross-Validation*)**."
        ),
        "ejemplo": (
            "Aquí tienes **dos ejemplos prácticos de Machine Learning**:\n\n"
            "1. **Supervisado (Clasificación)**: Un banco entrena un algoritmo *Random Forest* con el historial de pagos, ingresos y edad de miles de clientes para predecir si una nueva solicitud de crédito será `Aprobada (1)` o `Riesgosa (0)`.\n"
            "2. **No Supervisado (Clustering)**: Una tienda usa **K-Means** para agrupar automáticamente a sus clientes en 4 perfiles de compra sin tener etiquetas previas."
        ),
        "codigo": (
            "Ejemplo completo de **Machine Learning en Python** con `scikit-learn`:\n\n"
            "```python\n"
            "from sklearn.model_selection import train_test_split\n"
            "from sklearn.ensemble import RandomForestClassifier\n"
            "from sklearn.metrics import accuracy_score\n\n"
            "# 1. Dividir datos en entrenamiento (80%) y prueba (20%)\n"
            "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\n"
            "# 2. Crear y entrenar el modelo\n"
            "modelo = RandomForestClassifier(n_estimators=100, random_state=42)\n"
            "modelo.fit(X_train, y_train)\n\n"
            "# 3. Evaluar predicciones\n"
            "predicciones = modelo.predict(X_test)\n"
            "print(f'Exactitud (Accuracy): {accuracy_score(y_test, predicciones):.2%}')\n"
            "```"
        ),
        "ventajas": (
            "Ventajas de implementar modelos de **Machine Learning**:\n\n"
            "- 📈 **Escalabilidad**: Procesa millones de registros y variables simultáneamente.\n"
            "- 🔄 **Mejora continua**: Se puede re-entrenar conforme llegan nuevos datos.\n"
            "- 🎯 **Personalización**: Impulsa motores de recomendación, diagnóstico médico y detección de fraude en tiempo real."
        ),
        "instalacion": (
            "Para desarrollar modelos de **Machine Learning en Python**, instala:\n\n"
            "```bash\n"
            "pip install scikit-learn xgboost matplotlib joblib\n"
            "```\n"
            "Con `joblib.dump(modelo, 'modelo.pkl')` puedes guardar tu modelo entrenado y cargarlo dentro de tu app de **Shiny**."
        ),
        "comparacion": (
            "Comparativa: **Aprendizaje Supervisado vs. No Supervisado**:\n\n"
            "| Característica | 🎯 Supervisado | 🔍 No Supervisado |\n"
            "| :--- | :--- | :--- |\n"
            "| **Datos de entrada** | Variables $X$ + Etiqueta objetivo $y$ | Solo variables $X$ (sin etiquetas) |\n"
            "| **Objetivo** | Predecir $y$ para nuevos datos | Descubrir estructura o grupos ocultos |\n"
            "| **Tareas principales** | Regresión y Clasificación | Clustering y Reducción de dimensión |\n"
            "| **Algoritmos típicos** | Regresión Lineal/Logística, Random Forest, SVM | K-Means, DBSCAN, PCA, UMAP |\n"
            "| **Métricas de evaluación** | Accuracy, F1-Score, RMSE, $R^2$ | Silhouette Score, Inercia |"
        ),
        "formula": (
            "En **Machine Learning**, el modelo base de **Regresión Lineal Múltiple** y su función de pérdida (**MSE**) son:\n\n"
            "$$\\hat{y} = \\beta_0 + \\beta_1 x_1 + \\beta_2 x_2 + \\dots + \\beta_p x_p$$\n\n"
            "$$\\text{MSE} = \\frac{1}{n} \\sum_{i=1}^{n} (y_i - \\hat{y}_i)^2$$"
        ),
    },
    "visualizacion": {
        "nombre": "Visualización de Datos",
        "definicion": (
            "🎨 La **Visualización de Datos** consiste en representar información numérica mediante gráficos claros "
            "para identificar tendencias, patrones y valores atípicos rápidamente:\n\n"
            "- 📊 **Histograma / Boxplot**: Para analizar la distribución de una variable continua.\n"
            "- 🔵 **Gráfico de Dispersión (*Scatter Plot*)**: Para ver la relación o correlación entre 2 variables.\n"
            "- 📈 **Gráfico de Líneas**: Ideal para series de tiempo.\n"
            "- 📊 **Gráfico de Barras**: Para comparar categorías.\n\n"
            "💡 *Seguimiento: Pídeme «dame un ejemplo», «muéstrame código en Python» o «¿cuál es la diferencia entre los tipos de gráficos?».*"
        ),
        "profundizacion": (
            "En **Visualización de Datos con Python y Shiny**, puedes usar tanto gráficos estáticos (`matplotlib`, `seaborn` con `ui.output_plot`) "
            "como gráficos interactivos con zoom y tooltips (`plotly` con `shinyswatch` / `shinywidgets`)."
        ),
        "ejemplo": (
            "**Ejemplo práctico**: Si quieres comparar el salario de empleados según su nivel educativo, un **Boxplot (Diagrama de Caja)** te permite ver en una sola imagen la mediana, los cuartiles ($Q_1, Q_3$) y los valores atípicos de cada grupo."
        ),
        "codigo": (
            "Ejemplo de **visualización en Python con Matplotlib**:\n\n"
            "```python\n"
            "import matplotlib.pyplot as plt\n\n"
            "fig, ax = plt.subplots(figsize=(6, 4))\n"
            "ax.hist(datos, bins=20, color='#2563eb', edgecolor='white')\n"
            "ax.set_title('Distribución de la Muestra')\n"
            "ax.set_xlabel('Valor')\n"
            "ax.set_ylabel('Frecuencia')\n"
            "plt.show()\n"
            "```"
        ),
        "ventajas": (
            "Una buena visualización comunica hallazgos complejos en segundos y permite detectar errores o sesgos que pasan desapercibidos en tablas numéricas (como demuestra el famoso *Cuarteto de Anscombe*)."
        ),
        "instalacion": "Instala las librerías gráficas con: `pip install matplotlib seaborn plotly`.",
        "comparacion": (
            "| Gráfico | Cuándo usarlo |\n"
            "| :--- | :--- |\n"
            "| **Histograma** | Ver forma y asimetría de 1 variable numérica |\n"
            "| **Boxplot** | Comparar distribuciones y detectar *outliers* entre grupos |\n"
            "| **Dispersión (Scatter)** | Evaluar correlación entre 2 variables numéricas |"
        ),
        "formula": "Regla de Sturges para sugerir el número de intervalos ($k$) en un histograma:\n$$k = 1 + 3.322 \\log_{10}(n)$$",
    },
    "sql_datos": {
        "nombre": "SQL y Bases de Datos",
        "definicion": (
            "🗄️ **SQL (Structured Query Language)** es el lenguaje estándar para consultar y administrar bases de datos relacionales.\n\n"
            "- **Comandos clave**: `SELECT`, `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `JOIN` y `ORDER BY`.\n"
            "- En **Python**, puedes ejecutar consultas SQL directamente con `sqlite3`, `SQLAlchemy`, `DuckDB` o `pandas.read_sql()`.\n\n"
            "💡 *Seguimiento: Pídeme «dame un ejemplo» o «muéstrame código SQL».*"
        ),
        "profundizacion": (
            "En proyectos de Ciencia de Datos, **SQL** se utiliza para filtrar y agregar millones de filas directamente en el motor de base de datos antes de pasar el subconjunto limpio a **Pandas** o **Shiny**."
        ),
        "ejemplo": (
            "**Ejemplo de uso de SQL**: Unir la tabla `clientes` con la tabla `compras` mediante un `INNER JOIN` para obtener el total gastado por cada cliente activo durante el último año."
        ),
        "codigo": (
            "Ejemplo de **consulta SQL analítica**:\n\n"
            "```sql\n"
            "SELECT c.region,\n"
            "       COUNT(v.id_venta) AS total_ventas,\n"
            "       AVG(v.monto) AS ticket_promedio\n"
            "FROM ventas v\n"
            "JOIN clientes c ON v.id_cliente = c.id_cliente\n"
            "WHERE v.fecha >= '2026-01-01'\n"
            "GROUP BY c.region\n"
            "ORDER BY ticket_promedio DESC;\n"
            "```"
        ),
        "ventajas": "Permite consultar grandes volúmenes de datos estructurados con integridad transaccional y alto rendimiento.",
        "instalacion": "En Python ya viene incluido `import sqlite3` en la librería estándar, o puedes instalar `pip install duckdb sqlalchemy`.",
        "comparacion": "**SQL** opera sobre bases de datos relacionales en el servidor, mientras que **Pandas** opera sobre DataFrames en la memoria RAM local.",
        "formula": "En Álgebra Relacional, una consulta `SELECT ... WHERE` equivale a una proyección ($\\pi$) combinada con una selección ($\\sigma$): $$\\pi_{\\text{columnas}}(\\sigma_{\\text{condición}}(\\text{Tabla}))$$",
    },
}

CHISTES = [
    "¿Por qué los científicos de datos prefieren el frío? ¡Porque odian el *overfitting* (sobrecalentamiento)! 😄",
    "Hay 10 tipos de personas en el mundo: las que entienden binario y las que no. 💻",
    "¿Cuál es el animal favorito de un programador de Python? ¡La serpiente con *pandas*! 🐼🐍",
    "Un SQL entra a un bar, se acerca a dos tablas y les pregunta: *«¿Puedo hacer un JOIN con ustedes?»* 😂",
    "¿Por qué la media y la mediana dejaron de ser amigas? Porque llegó un *outlier* y la media perdió el equilibrio. 📈😄",
    "Un modelo de Machine Learning entra a un bar... El cantinero le pregunta: *«¿Qué vas a tomar?»* Y el modelo responde: *«Lo mismo que el 85% de los clientes anteriores con un intervalo de confianza del 95%»*. 🤖🍺",
]

# -----------------------------------------------------------------------------
# Mensaje de bienvenida inicial del Chatbot
# -----------------------------------------------------------------------------
MENSAJE_BIENVENIDA = (
    "¡Hola! 👋 Soy tu **Chatbot Básico en Shiny for Python**.\n\n"
    "Recuerdo tu nombre, el tema del que estamos hablando "
    "y tus preguntas anteriores para que puedas hacer **preguntas de seguimiento naturales**.\n\n"
    "Puedes conversar conmigo sobre:\n"
    "- 🐍 **Python**, ✨ **Shiny** o 🗄️ **SQL**\n"
    "- 📊 **Ciencia de Datos**, 📈 **Estadística** o 🎨 **Visualización**\n"
    "- 🤖 **Machine Learning / IA**\n"
    "- 🔗 **Preguntas de seguimiento**: Después de preguntar por un tema, escribe *«dame un ejemplo»*, *«muéstrame código»*, *«¿cuál es la diferencia?»*, *«cuéntame más»* o *«¿de qué estábamos hablando?»*.\n\n"
    "¿Cómo te llamas o sobre qué tema te gustaría conversar hoy?"
)


# -----------------------------------------------------------------------------
# Funciones de extracción de entidades, tema, subtema e intención contextual
# -----------------------------------------------------------------------------
PALABRAS_NO_NOMBRE = {
    "estudiante", "ingeniero", "ingeniera", "programador", "programadora",
    "analista", "cientifico", "cientifica", "profesor", "profesora", "docente",
    "alumno", "alumna", "nuevo", "nueva", "principiante", "experto", "un", "una",
    "el", "la", "de", "del", "en", "fan", "usuario", "yo", "feliz", "bien",
}


def extraer_info_usuario(texto_original: str, contexto: dict) -> dict:
    """
    Detecta si el usuario menciona su nombre o su interés/carrera/ocupación
    y actualiza la memoria de contexto de la sesión.
    """
    hallazgos = {"nuevo_nombre": None, "nuevo_perfil": None}
    texto_limpio = texto_original.strip()

    # 1. Detectar nombre del usuario ("me llamo X", "mi nombre es X", "soy X", "llámame X")
    patrones_nombre = [
        r"(?:me llamo|mi nombre es|puedes llamarme|llamame|llámame)\s+([A-Za-zÁÉÍÓÚáéíóúñÑ]+(?:\s+[A-Za-zÁÉÍÓÚáéíóúñÑ]+)?)",
        r"(?:^|[.,;¡!¿?\s])soy\s+([A-Za-zÁÉÍÓÚáéíóúñÑ]+)",
    ]
    for idx, patron in enumerate(patrones_nombre):
        m = re.search(patron, texto_limpio, flags=re.IGNORECASE)
        if m:
            candidato = m.group(1).strip()
            candidato = re.split(
                r"\b(?:y|pero|que|de|del|estudio|trabajo|quiero|vengo|me|busco)\b",
                candidato,
                flags=re.IGNORECASE,
            )[0].strip()
            palabras_cand = [normalizar(p) for p in candidato.split() if p]
            if palabras_cand and palabras_cand[0] not in PALABRAS_NO_NOMBRE and len(palabras_cand[0]) >= 2:
                if idx == 1:
                    candidato = candidato.split()[0]
                nombre_formateado = candidato.title()
                contexto["nombre_usuario"] = nombre_formateado
                hallazgos["nuevo_nombre"] = nombre_formateado
                break

    # 2. Detectar carrera / interés / ocupación ("estudio X", "trabajo en X", "me interesa X", "aprendo X")
    patrones_perfil = [
        r"(?:estudio|estoy estudiando|soy estudiante de)\s+([^.,;!?]+)",
        r"(?:trabajo en|trabajo como|me dedico a)\s+([^.,;!?]+)",
        r"(?:estoy aprendiendo|quiero aprender)\s+([^.,;!?]+)",
    ]
    for patron in patrones_perfil:
        m = re.search(patron, texto_limpio, flags=re.IGNORECASE)
        if m:
            perfil = m.group(1).strip()
            if 2 < len(perfil) <= 60:
                contexto["perfil_usuario"] = perfil
                hallazgos["nuevo_perfil"] = perfil
                break

    return hallazgos


def detectar_subtema_especifico(texto_norm: str, tema_anterior: str) -> str | None:
    """Detecta si el usuario pregunta por un subtema específico o hace referencia ordinal ('el primero', 'el segundo')."""
    # Referencias ordinales en contexto ("explícame el primero", "¿y el segundo?")
    if any(p in texto_norm for p in ["el primero", "la primera", "primera opcion", "primer tipo"]):
        mapa_primero = {
            "machine_learning": "supervisado",
            "estadistica": "media",
            "python": "pandas",
            "ciencia_datos": "eda",
            "shiny": "reactividad",
        }
        if tema_anterior in mapa_primero:
            return mapa_primero[tema_anterior]

    if any(p in texto_norm for p in ["el segundo", "la segunda", "segunda opcion", "segundo tipo"]):
        mapa_segundo = {
            "machine_learning": "no_supervisado",
            "estadistica": "mediana",
            "python": "numpy",
        }
        if tema_anterior in mapa_segundo:
            return mapa_segundo[tema_anterior]

    # Subtemas directos (cuando no es una comparación entre dos cosas)
    if any(p in texto_norm for p in ["diferencia", "comparar", " vs ", "versus", "entre"]):
        return None

    if "no supervisado" in texto_norm or "clustering" in texto_norm or "k-means" in texto_norm:
        return "no_supervisado"
    if "supervisado" in texto_norm:
        return "supervisado"
    if any(p in texto_norm for p in ["overfitting", "sobreajuste", "underfitting", "subajuste"]):
        return "overfitting"
    if "mediana" in texto_norm:
        return "mediana"
    if any(p in texto_norm for p in ["desviacion", "varianza"]):
        return "desviacion"
    if "correlacion" in texto_norm:
        return "correlacion"
    if re.search(r"\b(?:media|promedio)\b", texto_norm):
        return "media"
    if "pandas" in texto_norm or "dataframe" in texto_norm:
        return "pandas"
    if "numpy" in texto_norm or "ndarray" in texto_norm:
        return "numpy"
    if any(p in texto_norm for p in ["reactividad", "reactivo", "reactive"]):
        return "reactividad"
    if re.search(r"\beda\b", texto_norm) or "analisis exploratorio" in texto_norm:
        return "eda"
    return None


def detectar_tema_explicito(texto_norm: str) -> str | None:
    """Identifica si el mensaje menciona explícitamente alguno de los temas del dominio."""
    if any(p in texto_norm for p in ["shiny", "shinychat", "posit", "dashboard", "reactividad", "reactive", "value_box", "page_sidebar"]):
        return "shiny"
    if any(p in texto_norm for p in ["machine learning", "aprendizaje automatico", "aprendizaje supervisado", "no supervisado", "supervisado", "inteligencia artificial", "deep learning", "red neuronal", "redes neuronales", "random forest", "regresion", "clasificacion", "clustering", "k-means", "overfitting", "underfitting", "scikit-learn", "sklearn"]) or re.search(r"\b(?:ia|ml|pca)\b", texto_norm):
        return "machine_learning"
    if any(p in texto_norm for p in ["estadistica", "estadistico", "estadisticos", "media", "mediana", "moda", "promedio", "desviacion", "varianza", "probabilidad", "hipotesis", "p-valor", "p-value", "correlacion", "cuartil", "iqr", "percentil", "distribucion normal"]):
        return "estadistica"
    if any(p in texto_norm for p in ["visualizacion", "graficar", "grafico", "graficos", "grafica", "histograma", "boxplot", "scatter", "matplotlib", "seaborn", "plotly"]):
        return "visualizacion"
    if any(p in texto_norm for p in ["sql", "base de datos", "bases de datos", "sqlite", "duckdb", "join", "select from"]):
        return "sql_datos"
    if any(p in texto_norm for p in ["ciencia de datos", "data science", "cientifico de datos", "eda", "analisis exploratorio", "wrangling", "limpieza de datos", "outliers", "dataset"]):
        return "ciencia_datos"
    if any(p in texto_norm for p in ["python", "pandas", "numpy", "polars", "dataframe", "pip install", "listas", "diccionarios"]):
        return "python"
    return None


def detectar_aspecto_contextual(texto_norm: str) -> str | None:
    """
    Detecta qué aspecto o pregunta de seguimiento hace el usuario sobre el tema activo
    (ej. 'dame un ejemplo', 'muéstrame código', 'cuál es la diferencia', 'cuéntame más').
    """
    if any(p in texto_norm for p in ["codigo", "script", "programa", "programar", "sintaxis", "implementa", "implementar", "escribe", "escribirlo"]):
        return "codigo"
    if any(p in texto_norm for p in ["ejemplo", "ejemplos", "caso practico", "caso real", "muestra", "muestrame", "ilustra", "como seria"]):
        return "ejemplo"
    if any(p in texto_norm for p in ["diferencia", "diferencias", "diferencian", "comparar", "comparacion", "compara", "comparalos", "versus", " vs ", "cual es mejor", "entre ellos", "entre los dos"]):
        return "comparacion"
    if any(p in texto_norm for p in ["formula", "formulas", "ecuacion", "matematica", "como se calcula", "calcularlo", "calculo"]):
        return "formula"
    if any(p in texto_norm for p in ["instalar", "instalo", "instalacion", "empezar", "empiezo", "comenzar", "comienzo", "requisitos", "configurar", "como lo uso", "como se usa", "aprenderlo"]):
        return "instalacion"
    if any(p in texto_norm for p in ["ventaja", "ventajas", "beneficio", "beneficios", "importancia", "importante", "por que usar", "por que es util", "para que sirve", "utilidad", "aplicaciones"]):
        return "ventajas"
    if any(p in texto_norm for p in [
        "cuentame mas", "explicame mas", "mas detalles", "mas informacion", "profundiza",
        "profundizar", "amplia", "sigue", "continua", "que mas", "y luego", "y despues",
        "explicame mejor", "no entendi", "mas a fondo", "otro detalle",
    ]):
        return "profundizacion"
    return None


def construir_respuesta_cruce_temas(tema_anterior: str, tema_nuevo: str, aspecto: str | None) -> str | None:
    """
    Cuando el usuario estaba hablando de un tema (ej. Estadística) y pregunta
    '¿y cómo hago eso en Python?' o '¿cómo lo pongo en Shiny?', conecta ambos contextos.
    """
    if tema_anterior == tema_nuevo or tema_anterior not in BASE_CONOCIMIENTO:
        return None

    # Caso 1: Estaba en Estadística / ML / Ciencia de Datos / Visualización y menciona Python
    if tema_nuevo == "python" and tema_anterior in ("estadistica", "machine_learning", "ciencia_datos", "visualizacion", "sql_datos"):
        info_ant = BASE_CONOCIMIENTO[tema_anterior]
        return (
            f"Como estábamos hablando de **{info_ant['nombre']}**, así es como lo llevamos a la práctica en **Python**:\n\n"
            f"{info_ant['codigo']}\n\n"
            f"💡 *Ahora el tema activo pasó a **Python**, recordando que veníamos de **{info_ant['nombre']}**.*"
        )

    # Caso 2: Estaba en Python / ML / Estadística / Ciencia de Datos y pregunta cómo llevarlo a Shiny
    if tema_nuevo == "shiny" and tema_anterior in ("python", "machine_learning", "estadistica", "ciencia_datos", "visualizacion"):
        info_ant = BASE_CONOCIMIENTO[tema_anterior]
        return (
            f"Para integrar tu trabajo de **{info_ant['nombre']}** dentro de una aplicación **Shiny**:\n"
            f"1. Colocas tus controles de entrada en `app_ui` (por ejemplo, `ui.input_slider` o `ui.input_select`).\n"
            f"2. Ejecutas el procesamiento de **{info_ant['nombre']}** dentro de una función `@reactive.calc` en el servidor.\n"
            f"3. Muestras los resultados en `ui.output_plot()`, `ui.output_data_frame()` o `ui.value_box()`.\n\n"
            f"{BASE_CONOCIMIENTO['shiny']['codigo']}"
        )

    return None


def generar_resumen_conversacion(contexto: dict) -> str:
    """Construye un resumen dinámico de todo lo conversado y recordado en la sesión."""
    nombre = contexto.get("nombre_usuario")
    perfil = contexto.get("perfil_usuario")
    tema_actual = contexto.get("tema_actual", "ninguno")
    temas_vistos = contexto.get("historial_temas", [])
    preguntas = contexto.get("preguntas_usuario", [])

    lineas = ["🧠 **Memoria y Contexto Actual de nuestra Conversación:**\n"]
    if nombre:
        lineas.append(f"- 👤 **Tu nombre**: **{nombre}**")
    else:
        lineas.append("- 👤 **Tu nombre**: *Aún no me lo has dicho (puedes decirme «Me llamo...»)*")

    if perfil:
        lineas.append(f"- 🎓 **Tu perfil / interés registrado**: *{perfil}*")

    lineas.append(f"- 📌 **Tema activo en este momento**: **{ETIQUETAS_TEMAS.get(tema_actual, 'General')}**")

    if temas_vistos:
        nombres_temas = [ETIQUETAS_TEMAS.get(t, t) for t in temas_vistos]
        lineas.append(f"- 🗂️ **Recorrido de temas consultados ({len(temas_vistos)})**: {' ➔ '.join(nombres_temas)}")
    else:
        lineas.append("- 🗂️ **Temas técnicos consultados**: *Ninguno todavía*")

    if preguntas:
        ultimas = preguntas[-4:]
        lista_q = "\n".join(f"  {i+1}. *«{q}»*" for i, q in enumerate(ultimas))
        lineas.append(f"- 💬 **Tus mensajes recientes ({len(preguntas)} en total)**:\n{lista_q}")

    if tema_actual in BASE_CONOCIMIENTO:
        nom_tema = BASE_CONOCIMIENTO[tema_actual]["nombre"]
        lineas.append(
            f"\n💡 *Si quieres continuar con **{nom_tema}**, solo escribe «dame un ejemplo», «muéstrame código» o «cuéntame más».*"
        )
    return "\n".join(lineas)


# -----------------------------------------------------------------------------
# Motor conversacional con entendimiento de contexto
# -----------------------------------------------------------------------------
def generar_respuesta_bot(texto_usuario: str, contexto: dict, modo: str = "amigable") -> str:
    texto_orig = texto_usuario.strip()
    texto_norm = normalizar(texto_orig)
    palabras = re.findall(r"\w+", texto_norm)

    # Extraer si el usuario mencionó su nombre o perfil en este mensaje
    hallazgos_usuario = extraer_info_usuario(texto_orig, contexto)
    nombre_usuario = contexto.get("nombre_usuario")
    saludo_personal = f", **{nombre_usuario}**" if nombre_usuario else ""

    tema_anterior = contexto.get("tema_actual", "ninguno")
    subtema_det = detectar_subtema_especifico(texto_norm, tema_anterior)
    tema_detectado = detectar_tema_explicito(texto_norm)
    aspecto_detectado = detectar_aspecto_contextual(texto_norm)

    # Si detectó un subtema (ej. "el primero" o "mediana"), asegurar que el tema padre quede registrado
    if subtema_det and not tema_detectado:
        tema_detectado = SUBTEMAS_ESPECIFICOS[subtema_det]["tema"]

    # Registrar tema detectado en el contexto si hay uno nuevo
    if tema_detectado:
        contexto["tema_actual"] = tema_detectado
        if tema_detectado not in contexto["historial_temas"]:
            contexto["historial_temas"].append(tema_detectado)

    respuesta = ""

    # -------------------------------------------------------------------------
    # A. Regresar al tema anterior ("volvamos al tema anterior", "regresa al anterior")
    # -------------------------------------------------------------------------
    if any(p in texto_norm for p in ["volvamos al tema anterior", "volver al tema anterior", "regresa al tema anterior", "tema previo"]):
        hist_t = contexto.get("historial_temas", [])
        if len(hist_t) >= 2:
            tema_prev = hist_t[-2]
            contexto["tema_actual"] = tema_prev
            info_prev = BASE_CONOCIMIENTO[tema_prev]
            respuesta = (
                f"🔄 ¡Listo{saludo_personal}! Hemos regresado al tema anterior: **{info_prev['nombre']}**.\n\n"
                f"{info_prev['definicion']}"
            )
        else:
            respuesta = "Todavía no tenemos un tema previo registrado al cual regresar. Pregúntame por cualquier tema para empezar."

    # -------------------------------------------------------------------------
    # B. Preguntas sobre la memoria del usuario ("¿cómo me llamo?", "¿quién soy?")
    # -------------------------------------------------------------------------
    elif any(p in texto_norm for p in [
        "como me llamo", "cual es mi nombre", "recuerdas mi nombre", "sabes mi nombre",
        "quien soy", "que sabes de mi", "me recuerdas",
    ]):
        if nombre_usuario:
            extra_perfil = f" También recuerdo que mencionaste: *{contexto['perfil_usuario']}*." if contexto.get("perfil_usuario") else ""
            extra_tema = (
                f" Actualmente estamos conversando sobre **{ETIQUETAS_TEMAS.get(tema_anterior, 'General')}**."
                if tema_anterior != "ninguno"
                else ""
            )
            respuesta = f"¡Por supuesto! Te llamas **{nombre_usuario}**. 😊{extra_perfil}{extra_tema}"
        else:
            respuesta = (
                "Aún no me has dicho tu nombre en esta sesión. 🤔\n\n"
                "Escríbeme por ejemplo *«Me llamo Rolando»* y lo recordaré durante toda nuestra conversación."
            )

    # -------------------------------------------------------------------------
    # C. Preguntas sobre el contexto o historial de la conversación
    # -------------------------------------------------------------------------
    elif any(p in texto_norm for p in [
        "de que estabamos hablando", "de que hablamos", "de que hemos hablado",
        "que te pregunte", "pregunta anterior", "ultimo tema", "tema anterior",
        "cual es el contexto", "resumen de la conversacion", "resumen de nuestra charla",
        "que temas hemos visto", "historial",
    ]):
        respuesta = generar_resumen_conversacion(contexto)

    # -------------------------------------------------------------------------
    # D. Hora y Fecha del sistema
    # -------------------------------------------------------------------------
    elif any(p in palabras for p in ["hora", "reloj"]) or "que hora es" in texto_norm:
        ahora = datetime.now().strftime("%H:%M:%S")
        extra_ctx = (
            f" Seguimos con nuestro tema activo: **{ETIQUETAS_TEMAS[tema_anterior]}**."
            if tema_anterior in BASE_CONOCIMIENTO
            else ""
        )
        respuesta = f"🕒 La hora actual del sistema es **{ahora}**{saludo_personal}.{extra_ctx}"

    elif any(p in palabras for p in ["fecha", "calendario"]) or any(p in texto_norm for p in ["que dia es", "fecha de hoy"]):
        hoy = datetime.now().strftime("%d/%m/%Y")
        respuesta = f"📅 La fecha de hoy es **{hoy}**{saludo_personal}."

    # -------------------------------------------------------------------------
    # E. Chistes y seguimiento de chistes ("cuéntame otro", "otro chiste")
    # -------------------------------------------------------------------------
    elif any(p in texto_norm for p in ["chiste", "broma", "reir", "divertido"]) or (
        tema_anterior == "chiste" and any(p in palabras for p in ["otro", "otra", "mas", "sigue"])
    ):
        contexto["tema_actual"] = "chiste"
        ultimo_idx = contexto.get("ultimo_chiste_idx", -1)
        indices_disp = [i for i in range(len(CHISTES)) if i != ultimo_idx]
        elegido = random.choice(indices_disp)
        contexto["ultimo_chiste_idx"] = elegido
        respuesta = (
            f"{CHISTES[elegido]}\n\n"
            "💡 *(Como sé que estamos en modo humor, puedes escribir simplemente **«otro»** y te contaré uno distinto)*."
        )

    # -------------------------------------------------------------------------
    # F. Ayuda / Menú de opciones
    # -------------------------------------------------------------------------
    elif any(p in texto_norm for p in ["ayuda", "menu", "opciones", "que puedes hacer", "como funcionas"]):
        respuesta = (
            f"¡Claro{saludo_personal}! Aquí tienes todo lo que puedo hacer con **memoria de contexto**:\n\n"
            "1. 📚 **Temas Principales**: Pregúntame sobre **Python**, **Shiny**, **Ciencia de Datos**, **Estadística**, **Machine Learning**, **Visualización** o **SQL**.\n"
            "2. 🔗 **Preguntas de Seguimiento (¡Sin repetir el tema!)**:\n"
            "   - *«Dame un ejemplo»* o *«Muéstrame código»*\n"
            "   - *«¿Cuál es la diferencia?»* o *«¿Cuál es la fórmula?»*\n"
            "   - *«¿Qué ventajas tiene?»*, *«¿Cómo se instala?»* o *«Cuéntame más»*\n"
            "   - *«Explícame el primero»* o *«¿Y el segundo?»*\n"
            "3. 🧠 **Memoria Personal y de Sesión**:\n"
            "   - Dime *«Me llamo [tu nombre]»* y luego pregúntame *«¿Cómo me llamo?»*\n"
            "   - Pregúntame *«¿De qué estábamos hablando?»* para ver el resumen de contexto."
        )

    # -------------------------------------------------------------------------
    # G. Subtema específico detectado (ej. "¿qué es la mediana?", "explícame el supervisado", "el primero")
    # -------------------------------------------------------------------------
    elif subtema_det and not aspecto_detectado:
        sub_info = SUBTEMAS_ESPECIFICOS[subtema_det]
        contexto["ultimo_aspecto"] = "profundizacion"
        respuesta = (
            f"### {sub_info['titulo']}\n\n"
            f"{sub_info['respuesta']}\n\n"
            f"💡 *Puedes seguir preguntando «dame otro ejemplo», «muéstrame código» o «¿cuál es la diferencia?».*"
        )

    # -------------------------------------------------------------------------
    # H. Tema explícito detectado (con o sin aspecto específico, o cruce de temas)
    # -------------------------------------------------------------------------
    elif tema_detectado in BASE_CONOCIMIENTO:
        info = BASE_CONOCIMIENTO[tema_detectado]
        prefijo_nombre = (
            f"¡Mucho gusto, **{hallazgos_usuario['nuevo_nombre']}**! Guardé tu nombre en memoria. 😊\n\n"
            if hallazgos_usuario["nuevo_nombre"]
            else ""
        )

        # Verificar si el usuario viene de otro tema y pide conectar ambos (ej. "¿y cómo hago eso en Python?")
        es_pregunta_cruce = any(
            p in texto_norm
            for p in ["eso en", "esto en", "aplicarlo en", "hacerlo en", "usarlo en", "ponerlo en", "integrarlo en", "calculo en", "calcularlo en"]
        )
        cruce = construir_respuesta_cruce_temas(tema_anterior, tema_detectado, aspecto_detectado) if es_pregunta_cruce else None

        if cruce:
            respuesta = prefijo_nombre + cruce
        elif aspecto_detectado and aspecto_detectado in info:
            contexto["ultimo_aspecto"] = aspecto_detectado
            respuesta = f"{prefijo_nombre}{info[aspecto_detectado]}"
        elif tema_detectado == tema_anterior and contexto.get("ultimo_aspecto") == "definicion":
            # Si ya estaba en este tema y vuelve a preguntar por él, profundizamos en vez de repetir la definición
            contexto["ultimo_aspecto"] = "profundizacion"
            respuesta = f"{prefijo_nombre}{info['profundizacion']}"
        else:
            contexto["ultimo_aspecto"] = "definicion"
            respuesta = f"{prefijo_nombre}{info['definicion']}"

    # -------------------------------------------------------------------------
    # I. Pregunta de SEGUIMIENTO CONTEXTUAL (usa el tema_actual guardado en memoria)
    # -------------------------------------------------------------------------
    elif aspecto_detectado and tema_anterior in BASE_CONOCIMIENTO:
        info = BASE_CONOCIMIENTO[tema_anterior]
        # Si pide "cuéntame más" varias veces seguidas, rotamos a otro aspecto útil para no repetir
        aspecto_a_usar = aspecto_detectado
        if aspecto_detectado == contexto.get("ultimo_aspecto") and aspecto_detectado == "profundizacion":
            orden_rotacion = ["profundizacion", "ejemplo", "codigo", "comparacion", "ventajas", "formula"]
            idx_act = orden_rotacion.index(contexto.get("aspecto_rotado", "profundizacion"))
            aspecto_a_usar = orden_rotacion[(idx_act + 1) % len(orden_rotacion)]
            contexto["aspecto_rotado"] = aspecto_a_usar

        contexto["ultimo_aspecto"] = aspecto_a_usar
        respuesta = info[aspecto_a_usar]

    # Si pide un ejemplo/código pero aún no hay ningún tema activo en la conversación
    elif aspecto_detectado and tema_anterior == "ninguno":
        respuesta = (
            f"Entiendo que quieres ver **{aspecto_detectado}**{saludo_personal}, ¡pero aún no hemos elegido un tema! 🤔\n\n"
            "Dime primero sobre cuál tema quieres hablar (**Python**, **Shiny**, **Ciencia de Datos**, **Estadística** o **Machine Learning**) "
            "y enseguida te doy el ejemplo o código."
        )

    # -------------------------------------------------------------------------
    # J. Confirmaciones cortas en contexto ("sí", "claro", "por favor", "dale", "ok")
    # -------------------------------------------------------------------------
    elif any(p in palabras for p in ["si", "claro", "dale", "ok", "bueno", "va", "porfa"]) and len(palabras) <= 4 and tema_anterior in BASE_CONOCIMIENTO:
        info = BASE_CONOCIMIENTO[tema_anterior]
        secuencia = ["definicion", "ejemplo", "codigo", "comparacion", "profundizacion"]
        ult = contexto.get("ultimo_aspecto", "definicion")
        sig_idx = (secuencia.index(ult) + 1) % len(secuencia) if ult in secuencia else 1
        sig_aspecto = secuencia[sig_idx]
        contexto["ultimo_aspecto"] = sig_aspecto
        respuesta = (
            f"¡Excelente{saludo_personal}! Continuando con **{info['nombre']}**:\n\n"
            f"{info[sig_aspecto]}"
        )

    # -------------------------------------------------------------------------
    # K. Presentación del usuario o Saludos
    # -------------------------------------------------------------------------
    elif hallazgos_usuario["nuevo_nombre"] or hallazgos_usuario["nuevo_perfil"]:
        partes_saludo = []
        if hallazgos_usuario["nuevo_nombre"]:
            partes_saludo.append(f"¡Qué gusto conocerte, **{hallazgos_usuario['nuevo_nombre']}**! 👋 He guardado tu nombre en el contexto de nuestra sesión.")
        if hallazgos_usuario["nuevo_perfil"]:
            partes_saludo.append(f"Tomé nota de tu interés/perfil en **{hallazgos_usuario['nuevo_perfil']}**.")
        if tema_anterior in BASE_CONOCIMIENTO:
            partes_saludo.append(f"Seguimos con el tema activo de **{BASE_CONOCIMIENTO[tema_anterior]['nombre']}**, ¿quieres ver un ejemplo o cambiar de tema?")
        else:
            partes_saludo.append("¿Sobre qué tema te gustaría conversar hoy? (**Python**, **Shiny**, **Ciencia de Datos**, **Estadística** o **Machine Learning**).")
        respuesta = " ".join(partes_saludo)

    elif any(p in texto_norm for p in ["hola", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos", "que tal", "como estas"]):
        if tema_anterior in BASE_CONOCIMIENTO:
            nom_t = BASE_CONOCIMIENTO[tema_anterior]["nombre"]
            respuesta = (
                f"¡Hola de nuevo{saludo_personal}! 😊 Estamos conversando en el contexto de **{nom_t}**.\n\n"
                f"Puedes pedirme *«dame un ejemplo»*, *«muéstrame código»*, *«¿cuál es la diferencia?»* o preguntarme por otro tema."
            )
        else:
            respuesta = (
                f"¡Hola{saludo_personal}! 😊 ¿Cómo estás? Pregúntame sobre **Python**, **Shiny**, **Ciencia de Datos**, "
                "**Estadística** o **Machine Learning**. También puedes decirme cómo te llamas para recordarlo."
            )

    # -------------------------------------------------------------------------
    # L. Agradecimientos y Despedidas (personalizadas con el contexto)
    # -------------------------------------------------------------------------
    elif any(p in texto_norm for p in ["gracias", "agradezco", "excelente", "genial", "super", "perfecto", "entendido"]):
        extra_tema = (
            f" Si tienes otra duda sobre **{BASE_CONOCIMIENTO[tema_anterior]['nombre']}** o quieres explorar otro tema, aquí sigo."
            if tema_anterior in BASE_CONOCIMIENTO
            else " Si tienes otra duda, aquí sigo para ayudarte."
        )
        respuesta = f"¡Con mucho gusto{saludo_personal}! 🙌{extra_tema}"

    elif any(p in texto_norm for p in ["adios", "hasta luego", "bye", "nos vemos", "chao"]):
        resumen_temas = (
            f" Hoy conversamos sobre: **{', '.join(ETIQUETAS_TEMAS[t] for t in contexto['historial_temas'])}**."
            if contexto["historial_temas"]
            else ""
        )
        respuesta = f"¡Hasta luego{saludo_personal}! 👋 Fue un gusto conversar contigo.{resumen_temas} ¡Éxito en tus proyectos con Shiny!"

    # -------------------------------------------------------------------------
    # M. Preguntas abiertas cuando YA hay un tema activo (Mantiene el contexto)
    # -------------------------------------------------------------------------
    elif tema_anterior in BASE_CONOCIMIENTO and any(
        p in texto_norm for p in ["como", "por que", "cual", "cuales", "que es", "explica", "dime", "?", "funciona", "sirve"]
    ):
        info = BASE_CONOCIMIENTO[tema_anterior]
        ult = contexto.get("ultimo_aspecto", "definicion")
        sig = "profundizacion" if ult == "definicion" else ("ejemplo" if ult == "profundizacion" else "codigo")
        contexto["ultimo_aspecto"] = sig
        respuesta = (
            f"Respecto a **{info['nombre']}** (*«{texto_orig}»*):\n\n"
            f"{info[sig]}\n\n"
            f"💡 *También puedes pedirme sobre **{info['nombre']}**: «¿cuál es la diferencia?», «¿cuál es la fórmula?» o «¿cómo se instala?».*"
        )

    # -------------------------------------------------------------------------
    # N. Respuesta por defecto guiada por el contexto actual
    # -------------------------------------------------------------------------
    else:
        ctx_msg = (
            f"Actualmente nuestro tema activo es **{ETIQUETAS_TEMAS.get(tema_anterior)}**. "
            "Sobre este tema puedes decirme *«dame un ejemplo»*, *«muéstrame código»*, *«cuéntame más»* o *«¿cuál es la diferencia?»*.\n\n"
            if tema_anterior in BASE_CONOCIMIENTO
            else ""
        )
        respuesta = (
            f"Interesante lo que comentas sobre *«{texto_orig}»*{saludo_personal}. 🤔\n\n"
            f"{ctx_msg}"
            "Puedo conversar con memoria de contexto sobre: **Python**, **Shiny**, **Ciencia de Datos**, "
            "**Estadística**, **Machine Learning**, **Visualización**, **SQL**, la **hora/fecha** o contarte un **chiste**."
        )

    # Ajustar el tono según el selector del panel lateral
    if modo == "formal":
        encabezado = f"Estimado(a) {nombre_usuario}:" if nombre_usuario else "Estimado usuario:"
        return f"{encabezado}\n\n{respuesta}"
    elif modo == "breve":
        bloques = [b.strip() for b in respuesta.split("\n\n") if b.strip()]
        resumen_breve = bloques[0]
        if len(bloques) > 1 and not bloques[1].startswith("💡"):
            resumen_breve += "\n\n" + bloques[1]
        return resumen_breve
    return respuesta


# -----------------------------------------------------------------------------
# 1. Interfaz de Usuario (UI)
# -----------------------------------------------------------------------------
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("⚙️ Panel del Chatbot", class_="fw-bold text-primary mb-1"),
        ui.p(
            "Asistente conversacional básico construido con el componente nativo ui.Chat de Shiny.",
            class_="text-muted small mb-2",
        ),
        ui.input_select(
            "modo_respuesta",
            "Estilo de Respuesta:",
            {
                "amigable": "😊 Amigable y Completo",
                "formal": "🎩 Formal / Académico",
                "breve": "⚡ Breve (Resumen rápido)",
            },
            selected="amigable",
        ),
        ui.hr(class_="my-2"),
        ui.h6("💡 1. Elegir Tema:", class_="fw-bold mb-2"),
        ui.input_action_button(
            "btn_q_shiny",
            "¿Para qué sirve Shiny?",
            class_="btn-outline-primary btn-sm w-100 mb-1",
        ),
        ui.input_action_button(
            "btn_q_cd",
            "¿Qué es Ciencia de Datos?",
            class_="btn-outline-primary btn-sm w-100 mb-1",
        ),
        ui.input_action_button(
            "btn_q_python",
            "Háblame de Python",
            class_="btn-outline-primary btn-sm w-100 mb-1",
        ),
        ui.input_action_button(
            "btn_q_ml",
            "¿Qué es Machine Learning?",
            class_="btn-outline-primary btn-sm w-100 mb-2",
        ),
        ui.h6("💡 2. Preguntas de Seguimiento:", class_="fw-bold mb-2"),
        ui.input_action_button(
            "btn_ctx_ejemplo",
            "🔎 Dame un ejemplo de esto",
            class_="btn-outline-success btn-sm w-100 mb-1",
        ),
        ui.input_action_button(
            "btn_ctx_codigo",
            "💻 Muéstrame código del tema",
            class_="btn-outline-success btn-sm w-100 mb-1",
        ),
        ui.input_action_button(
            "btn_ctx_resumen",
            "🧠 ¿De qué hemos hablado?",
            class_="btn-outline-info btn-sm w-100 mb-2",
        ),
        ui.input_action_button(
            "btn_q_chiste",
            "Cuéntame un chiste 😄",
            class_="btn-outline-secondary btn-sm w-100 mb-2",
        ),
        ui.hr(class_="my-2"),
        ui.input_action_button(
            "btn_limpiar",
            "🗑️ Reiniciar Conversación",
            class_="btn-danger btn-sm w-100",
        ),
        width=310,
    ),
    # Encabezado y KPIs superiores
    ui.h3("🤖 Chatbot Básico Interactivo con Shiny", class_="fw-bold mb-2"),
    ui.layout_columns(
        ui.value_box(
            "Mensajes del Usuario",
            ui.output_text("kpi_turnos"),
            theme="primary",
        ),
        ui.value_box(
            "Tema Activo",
            ui.output_text("kpi_contexto"),
            theme="success",
        ),
        ui.value_box(
            "Usuario / Estilo",
            ui.output_text("kpi_modo"),
            theme="info",
        ),
        col_widths=[4, 4, 4],
        fill=False,
    ),
    # Tarjeta principal que aloja el componente de Chat
    ui.card(
        ui.card_header("💬 Ventana de Conversación", class_="fw-bold"),
        ui.chat_ui(
            id="chat_principal",
            placeholder="Escribe aquí (ej. 'Me llamo Rolando', '¿Qué es Estadística?', y luego 'Dame un ejemplo' o 'Muéstrame código')...",
            greeting=MENSAJE_BIENVENIDA,
            width="100%",
            height="100%",
            fill=True,
        ),
        full_screen=True,
        fill=True,
    ),
    title="Chatbot Básico - Shiny",
    fillable=True,
)


# -----------------------------------------------------------------------------
# 2. Lógica del Servidor (Server)
# -----------------------------------------------------------------------------
def crear_contexto_inicial() -> dict:
    return {
        "tema_actual": "ninguno",
        "ultimo_aspecto": None,
        "aspecto_rotado": "profundizacion",
        "nombre_usuario": None,
        "perfil_usuario": None,
        "historial_temas": [],
        "preguntas_usuario": [],
        "ultimo_chiste_idx": -1,
    }


def server(input, output, session):
    # Estado reactivo de interacciones y memoria de contexto de la sesión
    contador_mensajes = reactive.value(0)
    memoria_contexto = reactive.value(crear_contexto_inicial())

    # Inicialización del componente Chat
    chat = ui.Chat(id="chat_principal")

    # Función auxiliar para procesar una consulta actualizando el contexto
    async def responder_consulta(pregunta: str, mostrar_pregunta_usuario: bool = False):
        if mostrar_pregunta_usuario:
            await chat.append_message({"content": pregunta, "role": "user"})

        # Copiar y actualizar el diccionario de contexto reactivo
        ctx = dict(memoria_contexto.get())
        ctx["historial_temas"] = list(ctx["historial_temas"])
        ctx["preguntas_usuario"] = list(ctx["preguntas_usuario"]) + [pregunta]

        respuesta = generar_respuesta_bot(pregunta, contexto=ctx, modo=input.modo_respuesta())

        memoria_contexto.set(ctx)
        contador_mensajes.set(contador_mensajes.get() + 1)
        await chat.append_message({"content": respuesta, "role": "assistant"})

    # Evento principal: cuando el usuario envía un mensaje desde la caja de texto
    @chat.on_user_submit
    async def procesar_envio_usuario(mensaje_usuario: str):
        await responder_consulta(mensaje_usuario, mostrar_pregunta_usuario=False)

    # Eventos de los botones de temas
    @reactive.effect
    @reactive.event(input.btn_q_shiny)
    async def _():
        await responder_consulta("¿Para qué sirve Shiny?", mostrar_pregunta_usuario=True)

    @reactive.effect
    @reactive.event(input.btn_q_cd)
    async def _():
        await responder_consulta("¿Qué es Ciencia de Datos?", mostrar_pregunta_usuario=True)

    @reactive.effect
    @reactive.event(input.btn_q_python)
    async def _():
        await responder_consulta("Háblame de Python y sus librerías", mostrar_pregunta_usuario=True)

    @reactive.effect
    @reactive.event(input.btn_q_ml)
    async def _():
        await responder_consulta("¿Qué es Machine Learning?", mostrar_pregunta_usuario=True)

    # Eventos de los botones de seguimiento contextual
    @reactive.effect
    @reactive.event(input.btn_ctx_ejemplo)
    async def _():
        await responder_consulta("¿Me das un ejemplo práctico de esto?", mostrar_pregunta_usuario=True)

    @reactive.effect
    @reactive.event(input.btn_ctx_codigo)
    async def _():
        await responder_consulta("Muéstrame un ejemplo en código", mostrar_pregunta_usuario=True)

    @reactive.effect
    @reactive.event(input.btn_ctx_resumen)
    async def _():
        await responder_consulta("¿De qué estábamos hablando en nuestra conversación?", mostrar_pregunta_usuario=True)

    @reactive.effect
    @reactive.event(input.btn_q_chiste)
    async def _():
        await responder_consulta("Cuéntame un chiste", mostrar_pregunta_usuario=True)

    # Botón para limpiar el historial del chat y reiniciar la memoria de contexto
    @reactive.effect
    @reactive.event(input.btn_limpiar)
    async def limpiar_historial():
        await chat.clear_messages()
        contador_mensajes.set(0)
        memoria_contexto.set(crear_contexto_inicial())
        await chat.append_message({"content": MENSAJE_BIENVENIDA, "role": "assistant"})

    # Salidas de indicadores (Value Boxes)
    @render.text
    def kpi_turnos():
        n = contador_mensajes.get()
        return f"{n} mensaje" if n == 1 else f"{n} mensajes"

    @render.text
    def kpi_contexto():
        ctx = memoria_contexto.get()
        tema = ctx.get("tema_actual", "ninguno")
        return ETIQUETAS_TEMAS.get(tema, "💬 General")

    @render.text
    def kpi_modo():
        ctx = memoria_contexto.get()
        nombre = ctx.get("nombre_usuario")
        modos = {
            "amigable": "Amigable 😊",
            "formal": "Formal 🎩",
            "breve": "Breve ⚡",
        }
        estilo_txt = modos.get(input.modo_respuesta(), "Amigable")
        return f"{nombre} · {estilo_txt}" if nombre else estilo_txt


# -----------------------------------------------------------------------------
# 3. Inicialización de la Aplicación
# -----------------------------------------------------------------------------
app = App(app_ui, server)

if __name__ == "__main__":
    app.run(port=8000)
