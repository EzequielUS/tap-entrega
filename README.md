# Proyecto Integrador: Control de Estado de Vehículos (API)

Este proyecto implementa un Backend (modelo API) para la gestión de turnos de inspección vehicular, cumpliendo con los requisitos de la consigna de la segunda entrega

## 🛠️ Tecnologías y Arquitectura
* **Backend:** Python 3.9 + Flask.
* **Contenedores:** Docker y Docker Compose
* **Base de Datos:** MySQL 8.0
* **Seguridad:** JSON Web Tokens (JWT) para autenticación por roles

## 🐳 Despliegue (Docker Compose)

Tener Docker y Docker Compose instalados.

1.  **Clonar el Repositorio:**
    ```bash
    git clone [LINK-DEL-REPO]
    cd tap-project-final
    ```
2.  **Levantar los Servicios:**
    ```bash
    # Esto construye la API, levanta MySQL, y ejecuta db/init/init.sql
    docker compose up --build -d
    ```

3.  **Verificación de Servicios:**
    * **API:** Disponible en `http://localhost:5001` (o el puerto mapeado en `docker-compose.yml`).
    * **Health Check:** `GET http://localhost:5001/api/health` (Debe responder 200 OK).

## 🧪 Ejecución de Pruebas

Para probar las pruebas de integración y unitarias (simulando la DB) correr los siguientes comandos:

1.  **Acceder al Contenedor de la API:**
    ```bash
    docker exec -it vehicles-api-service bash
    ```
2.  **Ejecutar Pytest:**
    ```bash
    python -m pytest
    ```

---

## 📄 Flujo de trabajo

Utilizar los siguientes *endpoints* y usuarios para probar el flujo completo con Postman.

| Paso | Rol | Método | Endpoint | Propósito Clave |
| :--- | :--- | :--- | :--- | :--- |
| 1. Login | CLIENTE | POST | /api/auth/login | Obtener el Token JWT |
| 2. Disponibilidad | CLIENTE | GET | /api/turnos/disponibilidad?fecha=... | Consulta de inventario. Requiere Token de CLIENTE. |
| 3. Reserva | CLIENTE | POST | /api/turnos/reservar | Proceso de Reserva. Actualiza el slot a RESERVADO y registra el Vehiculo. Requiere Token de CLIENTE. |
| 4. Login | INSPECTOR | POST | /api/auth/login | Obtener un Token JWT de INSPECTOR. |
| 5. Finalización | INSPECTOR | POST | /api/turnos/<id_turno>/finalizar | El sistema calcula el resultado y actualiza el turno a FINALIZADO. Requiere Token de INSPECTOR. |
| 6. Consulta | CLIENTE | GET | /api/turnos/<id_turno> | Obtener el resultado final, puntaje total y los detalles por control. Requiere Token de CLIENTE. |

---

## 🔑 Usuarios de Prueba

Utilizar estos usuarios en la ruta `POST /api/auth/login` (contraseña: `test`) para obtener tokens.

| Username | Rol | Permisos |
| :--- | :--- | :--- |
| `cliente_test` | CLIENTE | `POST /api/auth/login` |
| `inspector_test` | INSPECTOR | `POST /api/auth/login` |