# 🍔 Rendón Burgers - Sistema de Gestión de Pedidos Distribuidos

Este proyecto consiste en una plataforma web integral para la gestión de pedidos, control de cocina y administración de inventario de un negocio gastronómico. Fue desarrollado como parte de la evaluación práctica para la materia de **Sistemas Distribuidos** en la **Universidad Autónoma de Campeche (UACAM)**.

La aplicación implementa una arquitectura cliente-servidor con persistencia de datos distribuida en la nube y sincronización asíncrona en tiempo real.

## 🚀 Despliegue en Producción
El sistema se encuentra desplegado y totalmente operativo en la nube:
👉 **[Ver Rendón Burgers en Vivo](https://menu-hamburguesas.onrender.com)**

## 🛠️ Stack Tecnológico
* **Frontend:** HTML5, CSS3, Bootstrap 5 y JavaScript Vanilla (Lógica del DOM y alertas dinámicas con SweetAlert2).
* **Backend:** Python 3 con el micro-framework Flask.
* **Base de Datos:** MongoDB Atlas (Clúster NoSQL distribuido en la nube).
* **Servidor / Hosting:** Cloud Platform Render.com (Despliegue continuo vinculado a la rama principal).

## 📦 Características Principales
1. **Menú Híbrido Dinámico:** Renderizado automático de 26 productos categorizados. Soporta carga híbrida de imágenes (archivos locales en el servidor y enlaces externos vía URL de internet) optimizados visualmente mediante CSS (`object-fit`).
   
2. **Carrito de Compras Avanzado:** Lógica interactiva en el cliente que evita duplicados agrupando productos por ID, permite modificar cantidades sobre el flujo (+/-), elimina elementos de forma selectiva y calcula el total de la cuenta al instante.
   
3. **Rastreador en Tiempo Real (Polling):** Mecanismo que realiza consultas automáticas en segundo plano al servidor cada 5 segundos. Permite al cliente observar el avance de su pedido (Preparando / Listo) mediante una barra de progreso responsiva sin necesidad de recargar la página.
   
4. **Panel de Cocina y Stock:** Interfaz administrativa centralizada que permite al personal despachar órdenes físicas y cambiar la disponibilidad del menú (Toggle Stock ON/OFF) con impacto inmediato en todos los usuarios conectados.

## 📂 Estructura del Repositorio
```text
/Menu_Hamburguesas
├── app.py              # Servidor Flask y endpoints de la API
├── requirements.txt    # Dependencias del proyecto (Flask, pymongo, dnspython)
├── static/
│   ├── main.js         # Lógica interactiva del carrito y polling asíncrono
│   └── img/            # Banco de imágenes locales del negocio
└── templates/
    ├── index.html      # Interfaz pública del cliente
    ├── cocina.html     # Panel administrativo de preparación
    └── reporte.html    # Módulo de métricas e historial de ventas

 Instalación y Configuración Local
Si deseas clonar el proyecto y ejecutarlo en tu entorno local, ejecuta los siguientes comandos en tu terminal:

Clonar el repositorio:
git clone [https://github.com/EduCabrera-k/Menu_Hamburguesas.git](https://github.com/EduCabrera-k/Menu_Hamburguesas.git)
cd Menu_Hamburguesas

Configurar el entorno virtual e instalar librerías:
python -m venv venv
.\venv\Scripts\activate
pip install flask pymongo dnspython

Lanzar el servidor de desarrollo:
python app.py
Entra en tu navegador a: http://127.0.0.1:5000
