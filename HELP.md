# Guía Rápida del Proyecto

Este archivo contiene comandos y notas útiles para trabajar con el proyecto.

## 🐳 Docker

Comandos para gestionar los servicios con Docker Compose.

### Iniciar servicios
Para levantar todos los servicios (base de datos y API) en segundo plano y reconstruir la imagen de la aplicación si hay cambios:
```bash
docker compose up -d --build
```

### Detener servicios
Para detener y eliminar los contenedores, redes y volúmenes creados:
```bash
docker compose down
```

### Ver logs
Para ver los logs de la aplicación Flask en tiempo real (muy útil para debugging):
```bash
docker compose logs -f vehicles-api-service
```
Para ver los logs de la base de datos:
```bash
docker compose logs -f vehicles-db-service
```

## 🗃️ Base de Datos (MySQL)

### Conexión a la Base de Datos desde la terminal
Para abrir una consola de MySQL dentro del contenedor de la base de datos:
```bash
docker exec -it vehicles-db-service mysql -u root -p

Ejemplo de uso:
mysql -u root -ppassword_segura db_vehiculos
```
Te pedirá la contraseña, que es: `password_segura`

### Datos de Conexión
- **Host (desde tu máquina):** `127.0.0.1`
- **Host (desde el contenedor de la app):** `db`
- **Puerto:** `3306`
- **Usuario:** `root`
- **Contraseña:** `password_segura`
- **Nombre de la Base de Datos:** `db_vehiculos`

## 🚀 API Endpoints

La API se ejecuta en `http://localhost:5001`.

### Ejemplo de Login
- **Método:** `POST`
- **URL:** `http://localhost:5001/api/auth/login`
- **Body (JSON):**
  ```json
  {
      "username": "tu_usuario",
      "password": "tu_contraseña"
  }
  ```

### Health Check (si está implementado)
- **Método:** `GET`
- **URL:** `http://localhost:5001/health`