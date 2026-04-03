# SIGES — Sistema Integrado de Gestión Empresarial
## Documentación Técnica y Manual de Usuario

**Versión:** 1.0 (en desarrollo)  
**Fecha:** Marzo 2026  
**Tecnologías:** Python 3.x · Flask · PostgreSQL · SQLAlchemy · HTML/CSS/JS vanilla  
**Autor del proyecto:** Yamileth  
**Entorno de desarrollo:** Windows — `C:\Users\Yamileth\Metamodelador\`

---

## 1. ¿Qué es SIGES?

SIGES es un sistema de gestión empresarial basado en un **meta-modelador de bases de datos**. En lugar de tener tablas fijas para cada tipo de negocio, el sistema permite definir la estructura de datos (entidades y campos) según el rubro de la empresa, y luego genera las tablas físicas en PostgreSQL automáticamente.

Esto significa que el mismo sistema puede usarse para una cauchera, un restaurante, una ferretería o una distribuidora, sin cambiar el código.

### Flujo general del sistema

```
1. Primera vez → /setup (wizard de configuración)
      ↓
   Selecciona rubro → crea empresa → genera tablas físicas → crea usuario admin
      ↓
2. Login → /  (index.html)
      ↓
3. Dashboard → /dashboard  (gestión diaria)
```

---

## 2. Estructura del proyecto

```
Metamodelador/
├── backend/
│   ├── app.py           → Punto de entrada Flask, rutas de archivos estáticos
│   ├── database.py      → Configuración SQLAlchemy
│   ├── models.py        → Modelos ORM (Rubro, Entidad, Campo, Empresa, Usuario, etc.)
│   ├── routes.py        → Todos los endpoints de la API REST
│   ├── generator.py     → Generador de tablas físicas por empresa/rubro
│   ├── seed.py          → Script para cargar 8 rubros predefinidos
│   ├── requirements.txt → Dependencias Python
│   └── .env             → Variables de entorno (NO subir a git)
│
├── frontend/
│   ├── index.html       → Pantalla de login
│   ├── setup.html       → Wizard de configuración inicial (primera vez)
│   ├── dashboard.html   → Panel principal de gestión (en desarrollo)
│   ├── admin.html       → Panel de administración del meta-modelador
│   ├── siges.css        → Estilos globales (tema futurista oscuro)
│   └── uploads/         → Logos subidos por las empresas
│
├── docs/
│   └── documentacion.md → Este archivo
│
└── venv/                → Entorno virtual Python
```

---

## 3. Puesta en marcha (desde cero)

### 3.1 Requisitos previos

- Python 3.9 o superior
- PostgreSQL instalado y corriendo (puerto 5432)
- Una base de datos creada llamada `MetaModelador` (o el nombre que prefieras)

### 3.2 Crear entorno virtual e instalar dependencias

```bash
# Desde la carpeta raíz del proyecto
python -m venv venv

# Activar (Windows CMD)
venv\Scripts\activate

# Instalar dependencias
pip install -r backend/requirements.txt
```

### 3.3 Configurar variables de entorno

El archivo `backend/.env` ya existe con estos valores:

```env
DATABASE_URL=postgresql+pg8000://postgres:123456@localhost:5432/MetaModelador
SECRET_KEY=clave-secreta-meta-modelador-2026
FLASK_APP=app.py
FLASK_ENV=development
```

Ajusta `postgres:123456` con tu usuario y contraseña de PostgreSQL.

### 3.4 Cargar los rubros predefinidos (seed)

```bash
cd backend
python seed.py
```

Esto carga 8 rubros con sus entidades y campos:
- Cauchos
- Restaurante
- Perfumería
- Ferretería
- Tienda Retail
- Taller
- Distribuidora
- Servicios Profesionales

### 3.5 Iniciar el servidor

```bash
cd backend
python app.py
```

Deberías ver:
```
✅ Base de datos conectada y tablas creadas
📌 Conectado a: postgresql+pg8000://...
 * Running on http://127.0.0.1:5000
```

### 3.6 Primera vez — Configuración del sistema

Abre el navegador en `http://localhost:5000`

Si el sistema no está configurado, redirige automáticamente a `/setup`.

**Wizard de 3 pasos:**
1. Nombre de empresa + selección de rubro + logo (opcional)
2. Datos del administrador (nombre, email, contraseña)
3. Confirmación y finalización

Al finalizar:
- Se crea la empresa en la base de datos
- Se generan las tablas físicas (`emp_1_productos`, `emp_1_clientes`, etc.)
- Se crea el usuario administrador
- Redirige al dashboard

---

## 4. Arquitectura del meta-modelador

### 4.1 Modelos del sistema (tablas fijas)

| Tabla | Descripción |
|-------|-------------|
| `rubros` | Tipos de negocio disponibles (cauchos, restaurante, etc.) |
| `entidades` | Módulos de cada rubro (productos, clientes, proveedores) |
| `campos` | Campos de cada entidad (nombre, precio, stock, etc.) |
| `empresas` | Registro de la empresa configurada |
| `config_empresa` | Configuración global del sistema (1 solo registro) |
| `usuarios` | Usuarios del sistema con roles |
| `tareas` | Tareas pendientes con prioridad y fecha límite |
| `notificaciones` | Alertas del sistema (stock bajo, tareas vencidas) |

### 4.2 Tablas físicas generadas

Cuando se configura el sistema, el `generator.py` crea tablas con el patrón:

```
emp_{empresa_id}_{nombre_tabla}
```

Ejemplo para empresa ID=1, rubro Cauchos:
- `emp_1_productos_caucho`
- `emp_1_proveedores`

### 4.3 Tipos de campo soportados

| Tipo | Descripción | Columna SQL |
|------|-------------|-------------|
| `string` | Texto corto | VARCHAR(255) |
| `text` | Texto largo | TEXT |
| `integer` | Número entero | INTEGER |
| `float` | Número decimal | FLOAT |
| `boolean` | Verdadero/Falso | BOOLEAN |
| `date` | Fecha/hora | DATETIME |
| `email` | Correo electrónico | VARCHAR(255) |
| `currency` | Monto monetario | FLOAT |
| `select` | Lista de opciones | VARCHAR(255) |

---

## 5. API REST — Referencia de endpoints

Base URL: `http://localhost:5000/api`

### 5.1 Configuración y autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/config` | Estado del sistema (configurado o no, nombre, logo) |
| POST | `/config/setup` | Wizard inicial (multipart/form-data) |
| POST | `/config/logo` | Actualizar logo |
| POST | `/auth/login` | Login con email y password |
| POST | `/auth/logout` | Cerrar sesión |
| GET | `/auth/me` | Usuario autenticado actual |
| POST | `/auth/registro` | Registrar nuevo usuario |

**Ejemplo login:**
```json
POST /api/auth/login
{ "email": "admin@empresa.com", "password": "mipassword" }
```

### 5.2 Meta-modelador (rubros, entidades, campos)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/rubros` | Listar todos los rubros |
| GET | `/rubros/{id}` | Obtener un rubro |
| POST | `/rubros` | Crear rubro |
| PUT | `/rubros/{id}` | Editar rubro |
| DELETE | `/rubros/{id}` | Eliminar rubro |
| GET | `/rubros/{id}/entidades` | Entidades de un rubro |
| POST | `/rubros/{id}/entidades` | Crear entidad |
| GET | `/entidades/{id}` | Obtener entidad |
| PUT | `/entidades/{id}` | Editar entidad |
| DELETE | `/entidades/{id}` | Eliminar entidad |
| GET | `/entidades/{id}/campos` | Campos de una entidad |
| POST | `/entidades/{id}/campos` | Crear campo |
| PUT | `/campos/{id}` | Editar campo |
| DELETE | `/campos/{id}` | Eliminar campo |
| GET | `/tipos-campo` | Lista de tipos disponibles |

### 5.3 Operación de datos (tablas físicas)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/empresa/{eid}/entidad/{entid}/registros` | Listar registros |
| POST | `/empresa/{eid}/entidad/{entid}/registros` | Crear registro |
| GET | `/empresa/{eid}/entidad/{entid}/registros/{id}` | Obtener registro |
| PUT | `/empresa/{eid}/entidad/{entid}/registros/{id}` | Editar registro |
| DELETE | `/empresa/{eid}/entidad/{entid}/registros/{id}` | Eliminar registro |
| GET | `/empresa/{eid}/entidad/{entid}/schema` | Schema de campos (para formularios dinámicos) |

**Ejemplo crear registro:**
```json
POST /api/empresa/1/entidad/1/registros
{ "marca": "Bridgestone", "ancho": 205, "perfil": 55, "diametro": 16, "precio": 85.00, "stock": 10 }
```

### 5.4 Tareas y notificaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/tareas` | Listar tareas (ordenadas por completada, fecha) |
| POST | `/tareas` | Crear tarea |
| PUT | `/tareas/{id}` | Editar/completar tarea |
| DELETE | `/tareas/{id}` | Eliminar tarea |
| GET | `/notificaciones` | Últimas 50 notificaciones |
| PUT | `/notificaciones/{id}/leer` | Marcar como leída |
| PUT | `/notificaciones/leer-todas` | Marcar todas como leídas |

### 5.5 Alertas y DSS

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/alertas` | Alertas dinámicas (stock bajo + tareas vencidas) |
| GET | `/dss/resumen` | Resumen agregado para análisis (brecha DSS) |

**Respuesta `/api/dss/resumen`:**
```json
{
  "empresa": "Mi Empresa",
  "rubro": "Cauchos",
  "entidades": [
    { "nombre": "producto_caucho", "tabla": "emp_1_productos_caucho", "total_registros": 45 }
  ],
  "tareas_pendientes": 3,
  "notificaciones_no_leidas": 2
}
```

---

## 6. Frontend — Pantallas

### 6.1 `index.html` — Login

- Carga la configuración desde `/api/config` al iniciar
- Si el sistema no está configurado, redirige a `/setup`
- Muestra el logo y nombre de empresa dinámicamente
- Autentica con `/api/auth/login` y redirige a `/dashboard`

### 6.2 `setup.html` — Wizard de configuración inicial

- Solo se usa **una vez** al inicio
- Paso 1: Nombre empresa + rubro + logo (opcional)
- Paso 2: Datos del administrador
- Paso 3: Confirmación y envío a `/api/config/setup`
- Después de configurar, el sistema queda bloqueado para no reconfigurar

### 6.3 `admin.html` — Panel de administración del meta-modelador

- Permite ver y editar entidades y campos del rubro
- Útil para ajustar el modelo de datos después del setup
- Consume `/api/rubros/{id}/entidades` y `/api/entidades/{id}/campos`

### 6.4 `dashboard.html` — Panel principal (EN DESARROLLO)

Estado actual: el archivo existe con la estructura visual del concepto anterior (tablas fijas de inventario). Necesita ser reemplazado con la versión dinámica que consuma la API.

**Lo que debe tener el dashboard final:**
- Header con logo dinámico, nombre empresa, avatar usuario, toggle modo claro/oscuro, botón logout
- Stats cards con totales desde `/api/dss/resumen`
- Panel de alertas consumiendo `/api/alertas`
- Área principal con selector de entidad y tabla de registros dinámica
- Formulario dinámico para agregar/editar registros basado en `/api/empresa/{id}/entidad/{id}/schema`
- Panel de tareas pendientes consumiendo `/api/tareas`
- Sidebar con módulos: ERP (Inventario, Ventas, Compras, Caja) y CRM (Contactos, Agenda, Seguimiento)

---

## 7. Estilos — `siges.css`

El sistema usa un tema futurista oscuro con:

- Fondo: `#0a0a0a` (negro profundo)
- Primario: `#0066ff` (azul eléctrico)
- Acento: `#00d4ff` (cian)
- Glassmorphism: `backdrop-filter: blur(20px)` + `rgba(255,255,255,0.05)`
- Gradiente principal: `linear-gradient(135deg, #0066ff, #00d4ff)`
- Variables CSS para modo claro/oscuro (toggle pendiente en dashboard)

Clases principales:
- `.card` — tarjeta glassmorphism
- `.stat-card` — card de estadística con hover animado
- `.btn` — botón con gradiente y efecto shimmer
- `.modal` — modal con blur de fondo
- `.badge-success/warning/danger` — badges de estado
- `.dashboard-header` — header sticky del dashboard

---

## 8. Rubros predefinidos (seed)

| Rubro | Entidades incluidas |
|-------|---------------------|
| Cauchos | Productos (ancho/perfil/diámetro/marca/precio/stock), Proveedores |
| Restaurante | Productos (nombre/precio/categoría/disponible), Mesas |
| Perfumería | Productos (nombre/marca/volumen/género/precio/stock) |
| Ferretería | Productos (nombre/código/unidad/precio/stock/descripción) |
| Tienda Retail | Productos (nombre/código/categoría/precio costo-venta/stock/talla/color/marca), Clientes |
| Taller | Órdenes de trabajo (número/cliente/descripción/fechas/costo/estado), Repuestos |
| Distribuidora | Productos (precio mayor/detal/stock mínimo/proveedor), Clientes, Proveedores |
| Servicios Profesionales | Clientes, Proyectos (nombre/fechas/monto/estado), Citas |

---

## 9. Pendiente / Próximos pasos

### 9.1 Dashboard dinámico (prioridad alta)

El `dashboard.html` necesita ser reescrito para consumir la API. El problema actual es que el IDE tiene el archivo abierto y `fsWrite` falla. Solución:

1. Cerrar la pestaña de `dashboard.html` en el IDE
2. Eliminar el archivo manualmente
3. Pedir a Kiro que lo cree con `fsWrite`

O alternativamente, pegar un bloque base en el archivo y usar `strReplace` para construirlo.

**Estructura JS que necesita el dashboard:**
```javascript
// Al cargar:
const config = await fetch('/api/config').then(r => r.json())
const me = await fetch('/api/auth/me', {credentials:'include'}).then(r => r.json())
const resumen = await fetch('/api/dss/resumen').then(r => r.json())
const alertas = await fetch('/api/alertas').then(r => r.json())
const tareas = await fetch('/api/tareas').then(r => r.json())

// Al seleccionar entidad:
const schema = await fetch(`/api/empresa/${eid}/entidad/${entid}/schema`).then(r => r.json())
const registros = await fetch(`/api/empresa/${eid}/entidad/${entid}/registros`).then(r => r.json())
```

### 9.2 Toggle modo claro/oscuro

Las variables CSS ya están preparadas en `siges.css`. Solo falta agregar en el dashboard:
```javascript
document.body.classList.toggle('light-mode')
```
Y definir las variables `[data-theme="light"]` en el CSS.

### 9.3 Módulo DSS (Decision Support System)

El endpoint `/api/dss/resumen` ya existe como brecha. El módulo DSS completo incluiría:
- Gráficas de tendencias de ventas/stock
- Alertas predictivas (stock mínimo configurable)
- Exportación a Excel/PDF
- Comparativas por período

### 9.4 Módulos CRM

- Contactos: ya soportado via entidades dinámicas (clientes)
- Agenda: entidad `citas` disponible en rubro Servicios Profesionales
- Seguimiento: pendiente de implementar

### 9.5 Módulo de Ventas/Facturas

Solo informativo — sin lógica fiscal ni numeración legal. Implementar como entidad dinámica `ventas` con campos: cliente, fecha, total, estado.

---

## 10. Problemas conocidos

| Problema | Causa | Solución |
|----------|-------|----------|
| `fsWrite` falla en `dashboard.html` | El IDE tiene el archivo abierto como pestaña activa | Cerrar la pestaña antes de que Kiro intente crear el archivo |
| Las tablas físicas no se modifican al editar campos | `generator.py` solo crea, no hace `ALTER TABLE` | Trabajo futuro: agregar método `sync_empresa_tables()` en generator |
| `select` tipo campo no genera opciones | El campo `opciones` en el modelo existe pero el frontend no lo usa aún | Implementar en el formulario dinámico del dashboard |

---

## 11. Cómo continuar con Kiro

Al iniciar una nueva sesión, pega este mensaje de contexto:

```
Proyecto: SIGES — Sistema de gestión empresarial con meta-modelador.
Stack: Flask + PostgreSQL + SQLAlchemy + HTML/JS vanilla.
Ruta: C:\Users\Yamileth\Metamodelador\

Estado actual:
- Backend completo: modelos, rutas CRUD, auth, config, tareas, notificaciones, alertas, DSS brecha.
- Frontend: index.html (login), setup.html (wizard), admin.html (meta-modelador).
- dashboard.html: PENDIENTE — necesita ser reescrito con lógica dinámica.

Archivos clave:
- backend/routes.py → todos los endpoints
- backend/models.py → Rubro, Entidad, Campo, Empresa, ConfigEmpresa, Usuario, Tarea, Notificacion
- frontend/siges.css → estilos globales (tema futurista oscuro)

Para iniciar el servidor:
  cd backend && venv\Scripts\activate && python app.py

Próxima tarea: crear dashboard.html dinámico que consuma la API.
```

---

## 12. Comandos de referencia rápida

```bash
# Activar entorno e iniciar servidor
cd C:\Users\Yamileth\Metamodelador\backend
venv\Scripts\activate
python app.py

# Cargar rubros (solo primera vez o si se limpia la BD)
python seed.py

# Verificar conexión a BD
python test_db.py

# Acceder al sistema
http://localhost:5000          → Login
http://localhost:5000/setup    → Configuración inicial
http://localhost:5000/dashboard → Dashboard
```

---

## 13. Dependencias Python

```
Flask==2.3.3
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
python-dotenv==1.0.0
pg8000==1.30.5
SQLAlchemy==2.0.23
Flask-Login==0.6.3
Werkzeug==3.0.1
```
