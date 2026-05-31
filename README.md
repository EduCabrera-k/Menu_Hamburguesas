# 🍔 Rendón Burgers - Sistema de Gestión de Pedidos Distribuidos

Este proyecto consiste en una plataforma web integral full-stack para la gestión de pedidos, control de cocina y administración de inventario de un negocio gastronómico. Fue desarrollado como parte de la evaluación práctica para la materia de **Sistemas Distribuidos** en la **Universidad Autónoma de Campeche (UACAM)**.

La aplicación implementa una arquitectura cliente-servidor de tres capas con desacoplamiento estructural, persistencia NoSQL distribuida en la nube y mecanismos asíncronos de sincronización en tiempo real.

## 🚀 Despliegue en Producción
El sistema cuenta con un flujo de integración y despliegue continuo (CI/CD) operativo en la nube:
👉 **[Ver Rendón Burgers en Vivo](https://menu-hamburguesas.onrender.com)**

## 🛠️ Stack Tecnológico
* **Capa de Presentación (Frontend):** HTML5, CSS3, Framework Bootstrap 5 y JavaScript Vanilla (Lógica del DOM, Fetch API y alertas interactivas con SweetAlert2).
* **Capa de Lógica de Negocio (Backend):** Python 3 con el micro-framework Flask, servido en entornos de producción mediante Gunicorn WSGI.
* **Capa de Persistencia de Datos:** MongoDB Atlas (Clúster NoSQL distribuido en la nube con réplicas geográficas Shards).
* **Controladores de Red y Entorno:** PyMongo, DNSPython (resolución de URIs abstractas `mongodb+srv://`) y Python-Dotenv.

## 📦 Características Principales e Implementación Distribuida
1. **Menú Híbrido Dinámico:** Renderizado automático de 26 productos categorizados. Soporta la carga híbrida y concurrente de imágenes (recursos locales en el servidor y enlaces externos vía CDN de internet) optimizados mediante CSS (`object-fit`).
   
2. **Carrito de Compras Avanzado:** Lógica interactiva que opera mediante estructuras de datos en memoria local. Agrupa duplicados por ID único, permite modificar cantidades sobre el flujo ($+/-$), elimina elementos de forma selectiva y restringe envíos vacíos mediante SweetAlert2.
   
3. **Validación Multicapa de Pedidos:** Robustecimiento de la integridad de los datos mediante una inspección exhaustiva de los payloads JSON en el backend (`_validar_pedido()`), verificando tipos de datos, longitudes de caracteres, obligatoriedad de direcciones y rangos de precios.
   
4. **Rastreador en Tiempo Real (Short Polling):** Mecanismo de comunicación asíncrona que interroga al servidor cada 5 segundos mediante Fetch API. Actualiza el estado gráfico del ticket en el cliente (30%, 60% y 100%) sin forzar una recarga total de la página.
   
5. **Monitor de Salud de Red (Heartbeat Protocol):** Componente avanzado de observabilidad distribuida instalado en el panel de cocina. Realiza consultas periódicas cada 2 segundos ejecutando un comando de administración (`ping`) directo al clúster remoto de MongoDB Atlas, computando el **Round-Trip Time (RTT)** en milisegundos y arrojando alertas por código de color (Verde/Amarillo/Rojo).
   
6. **Control Concurrente de Inventario y Reportes:** Interruptores táctiles en cocina con persistencia atómica de tipo UPSERT. Sincroniza el menú de los clientes conectados de manera concurrente cada 10 segundos, ocultando artículos agotados. Incluye un dashboard analítico para la consulta financiera y cronológica de ventas consolidadas del día.

## 📂 Estructura del Repositorio
La arquitectura física del software refleja de manera exacta el desacoplamiento de componentes requeridos por el framework.:

```text
/MENU
├── app.py              # Servidor Flask: rutas, lógica de negocio y validación exhaustiva.
├── requirements.txt    # Dependencias declarativas de empaquetamiento del proyecto.
├── .env                # Variables de entorno locales (Credenciales de MongoDB protegidas).
├── .gitignore          # Directiva de Git para excluir el entorno virtual (venv) y el .env.
├── static/             # Nodo contenedor principal de recursos estáticos del sistema.
│   ├── main.js         # Lógica frontend estructurada: carrito, polling y monitor de red.
│   └── img/            # Banco de imágenes y recursos locales de los productos.
└── templates/          # Directorio estructural de plantillas HTML de Flask.
    ├── index.html      # Capa de presentación del cliente (menú dinámico y carrito).
    ├── cocina.html     # Capa operativa administrativa de cocina y monitor de latencia.
    └── reporte.html    # Dashboard financiero de métricas de ventas diarias.


🛠️ Instalación y Configuración Local
1. Clonar el repositorio
Abre una terminal y descarga el código fuente del proyecto.:

git clone [https://github.com/EduCabrera-k/Menu_Hamburguesas.git](https://github.com/EduCabrera-k/Menu_Hamburguesas.git)
cd Menu_Hamburguesas

2. Configurar el entorno virtual (Aislamiento de Dependencias)
En Windows (PowerShell):

python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1

En macOS / Linux:


python3 -m venv venv
source venv/bin/activate


3. Instalar librerías del ecosistema

pip install -r requirements.txt


4. Variables de Entorno y Seguridad Perimetral
Crea un archivo plano con el nombre .env en la raíz del proyecto para resguardar las credenciales lógicas de acceso.:

MONGO_URI=mongodb+srv://TU_USUARIO:TU_CONTRASENA@cluster0.xxxxx.mongodb.net/?appName=Cluster0
Asegúrate de habilitar la regla de acceso de red 0.0.0.0/0 en el panel de MongoDB Atlas para autorizar las solicitudes síncronas de datos sin bloqueos perimetrales.


5. Lanzar el servidor de desarrollo

python app.py
Accede desde tu navegador web a la dirección loopback local configurada: http://127.0.0.1:5000
