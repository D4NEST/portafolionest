from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class ConfigEmpresa(db.Model):
    """Configuración global del sistema — solo existe un registro."""
    __tablename__ = 'config_empresa'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rubro_id = db.Column(db.Integer, db.ForeignKey('rubros.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=True)
    logo_path = db.Column(db.String(255), nullable=True)
    configurado = db.Column(db.Boolean, default=False)
    stock_minimo_alerta = db.Column(db.Integer, default=5)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    rubro = db.relationship('Rubro')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'rubro_id': self.rubro_id,
            'empresa_id': self.empresa_id,
            'logo_path': self.logo_path,
            'configurado': self.configurado,
            'stock_minimo_alerta': self.stock_minimo_alerta,
        }


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='admin')  # admin, usuario
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo,
        }


class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(30), nullable=False)  # stock_bajo, pago_pendiente, tarea
    titulo = db.Column(db.String(150), nullable=False)
    mensaje = db.Column(db.Text)
    leida = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'titulo': self.titulo,
            'mensaje': self.mensaje,
            'leida': self.leida,
            'fecha': self.fecha.isoformat(),
        }


class Tarea(db.Model):
    __tablename__ = 'tareas'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    completada = db.Column(db.Boolean, default=False)
    fecha_limite = db.Column(db.DateTime, nullable=True)
    prioridad = db.Column(db.String(10), default='media')  # alta, media, baja
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'completada': self.completada,
            'fecha_limite': self.fecha_limite.isoformat() if self.fecha_limite else None,
            'prioridad': self.prioridad,
            'fecha_creacion': self.fecha_creacion.isoformat(),
        }


class Empresa(db.Model):
    __tablename__ = 'empresas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rubro_id = db.Column(db.Integer, db.ForeignKey('rubros.id'), nullable=False)
    tablas_creadas = db.Column(db.JSON, default=[])
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    rubro = db.relationship('Rubro', backref='empresas')

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'rubro_id': self.rubro_id,
            'tablas_creadas': self.tablas_creadas,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

class Rubro(db.Model):
    __tablename__ = 'rubros'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    configuracion_base = db.Column(db.JSON, default={})
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    entidades = db.relationship('Entidad', backref='rubro', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'configuracion_base': self.configuracion_base,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

class Entidad(db.Model):
    __tablename__ = 'entidades'
    
    id = db.Column(db.Integer, primary_key=True)
    rubro_id = db.Column(db.Integer, db.ForeignKey('rubros.id'), nullable=False)
    
    nombre = db.Column(db.String(50), nullable=False)
    nombre_tabla = db.Column(db.String(50), nullable=False)
    nombre_plural = db.Column(db.String(50))
    icono = db.Column(db.String(20), default='??')
    descripcion = db.Column(db.String(200))
    orden = db.Column(db.Integer, default=0)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    campos = db.relationship('Campo', backref='entidad', lazy=True, cascade='all, delete-orphan', order_by='Campo.orden')
    modulo = db.Column(db.String(30), default='erp')  # erp, crm, etc.
    def to_dict(self):
        return {
            'id': self.id,
            'rubro_id': self.rubro_id,
            'nombre': self.nombre,
            'nombre_tabla': self.nombre_tabla,
            'nombre_plural': self.nombre_plural,
            'icono': self.icono,
            'descripcion': self.descripcion,
            'orden': self.orden,
            'modulo': self.modulo,
            'campos': [campo.to_dict() for campo in self.campos]
        }

class Campo(db.Model):
    __tablename__ = 'campos'
    
    TIPOS = ['string', 'text', 'integer', 'float', 'boolean', 'date', 'select', 'email', 'currency']
    
    id = db.Column(db.Integer, primary_key=True)
    entidad_id = db.Column(db.Integer, db.ForeignKey('entidades.id'), nullable=False)
    
    nombre = db.Column(db.String(50), nullable=False)
    nombre_fisico = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    etiqueta = db.Column(db.String(100))
    placeholder = db.Column(db.String(200))
    descripcion = db.Column(db.String(200))
    
    es_requerido = db.Column(db.Boolean, default=False)
    es_unico = db.Column(db.Boolean, default=False)
    es_indice = db.Column(db.Boolean, default=False)
    valor_por_defecto = db.Column(db.String(100))
    
    opciones = db.Column(db.JSON)
    validaciones = db.Column(db.JSON, default={})
    
    orden = db.Column(db.Integer, default=0)
    visible_en_tabla = db.Column(db.Boolean, default=True)
    visible_en_formulario = db.Column(db.Boolean, default=True)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('entidad_id', 'nombre', name='uq_campo_nombre'),
        db.UniqueConstraint('entidad_id', 'nombre_fisico', name='uq_campo_fisico'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'entidad_id': self.entidad_id,
            'nombre': self.nombre,
            'nombre_fisico': self.nombre_fisico,
            'tipo': self.tipo,
            'etiqueta': self.etiqueta,
            'placeholder': self.placeholder,
            'descripcion': self.descripcion,
            'es_requerido': self.es_requerido,
            'es_unico': self.es_unico,
            'es_indice': self.es_indice,
            'opciones': self.opciones,
            'validaciones': self.validaciones,
            'orden': self.orden,
            'visible_en_tabla': self.visible_en_tabla,
            'visible_en_formulario': self.visible_en_formulario
        }
