from flask import Blueprint, request, jsonify
from database import db
from models import Rubro, Entidad, Campo, Empresa

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ========== RUBROS ==========
@api_bp.route('/rubros', methods=['GET'])
def get_rubros():
    rubros = Rubro.query.all()
    return jsonify([r.to_dict() for r in rubros])

@api_bp.route('/rubros/<int:id>', methods=['GET'])
def get_rubro(id):
    rubro = Rubro.query.get_or_404(id)
    return jsonify(rubro.to_dict())

@api_bp.route('/rubros', methods=['POST'])
def create_rubro():
    data = request.json
    rubro = Rubro(
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        configuracion_base=data.get('configuracion_base', {})
    )
    db.session.add(rubro)
    db.session.commit()
    return jsonify(rubro.to_dict()), 201

@api_bp.route('/rubros/<int:id>', methods=['PUT'])
def update_rubro(id):
    rubro = Rubro.query.get_or_404(id)
    data = request.json
    rubro.nombre = data.get('nombre', rubro.nombre)
    rubro.descripcion = data.get('descripcion', rubro.descripcion)
    rubro.configuracion_base = data.get('configuracion_base', rubro.configuracion_base)
    db.session.commit()
    return jsonify(rubro.to_dict())

@api_bp.route('/rubros/<int:id>', methods=['DELETE'])
def delete_rubro(id):
    rubro = Rubro.query.get_or_404(id)
    db.session.delete(rubro)
    db.session.commit()
    return jsonify({'mensaje': 'Rubro eliminado'})

# ========== ENTIDADES ==========
@api_bp.route('/rubros/<int:rubro_id>/entidades', methods=['GET'])
def get_entidades(rubro_id):
    entidades = Entidad.query.filter_by(rubro_id=rubro_id).order_by(Entidad.orden).all()
    return jsonify([e.to_dict() for e in entidades])

@api_bp.route('/entidades/<int:id>', methods=['GET'])
def get_entidad(id):
    entidad = Entidad.query.get_or_404(id)
    return jsonify(entidad.to_dict())

@api_bp.route('/rubros/<int:rubro_id>/entidades', methods=['POST'])
def create_entidad(rubro_id):
    data = request.json
    entidad = Entidad(
        rubro_id=rubro_id,
        nombre=data['nombre'],
        nombre_tabla=data['nombre_tabla'],
        nombre_plural=data.get('nombre_plural', data['nombre'] + 's'),
        icono=data.get('icono', '📦'),
        descripcion=data.get('descripcion', ''),
        orden=data.get('orden', 0)
    )
    db.session.add(entidad)
    db.session.commit()
    return jsonify(entidad.to_dict()), 201

@api_bp.route('/entidades/<int:id>', methods=['PUT'])
def update_entidad(id):
    entidad = Entidad.query.get_or_404(id)
    data = request.json
    entidad.nombre = data.get('nombre', entidad.nombre)
    entidad.nombre_tabla = data.get('nombre_tabla', entidad.nombre_tabla)
    entidad.nombre_plural = data.get('nombre_plural', entidad.nombre_plural)
    entidad.icono = data.get('icono', entidad.icono)
    entidad.descripcion = data.get('descripcion', entidad.descripcion)
    entidad.orden = data.get('orden', entidad.orden)
    db.session.commit()
    return jsonify(entidad.to_dict())

@api_bp.route('/entidades/<int:id>', methods=['DELETE'])
def delete_entidad(id):
    entidad = Entidad.query.get_or_404(id)
    db.session.delete(entidad)
    db.session.commit()
    return jsonify({'mensaje': 'Entidad eliminada'})

# ========== CAMPOS ==========
@api_bp.route('/entidades/<int:entidad_id>/campos', methods=['GET'])
def get_campos(entidad_id):
    campos = Campo.query.filter_by(entidad_id=entidad_id).order_by(Campo.orden).all()
    return jsonify([c.to_dict() for c in campos])

@api_bp.route('/campos/<int:id>', methods=['GET'])
def get_campo(id):
    campo = Campo.query.get_or_404(id)
    return jsonify(campo.to_dict())

@api_bp.route('/entidades/<int:entidad_id>/campos', methods=['POST'])
def create_campo(entidad_id):
    data = request.json
    campo = Campo(
        entidad_id=entidad_id,
        nombre=data['nombre'],
        nombre_fisico=data['nombre_fisico'],
        tipo=data['tipo'],
        etiqueta=data.get('etiqueta', data['nombre']),
        placeholder=data.get('placeholder', ''),
        descripcion=data.get('descripcion', ''),
        es_requerido=data.get('es_requerido', False),
        es_unico=data.get('es_unico', False),
        es_indice=data.get('es_indice', False),
        valor_por_defecto=data.get('valor_por_defecto'),
        opciones=data.get('opciones'),
        validaciones=data.get('validaciones', {}),
        orden=data.get('orden', 0),
        visible_en_tabla=data.get('visible_en_tabla', True),
        visible_en_formulario=data.get('visible_en_formulario', True)
    )
    db.session.add(campo)
    db.session.commit()
    return jsonify(campo.to_dict()), 201

@api_bp.route('/campos/<int:id>', methods=['PUT'])
def update_campo(id):
    campo = Campo.query.get_or_404(id)
    data = request.json
    for key, value in data.items():
        if hasattr(campo, key):
            setattr(campo, key, value)
    db.session.commit()
    return jsonify(campo.to_dict())

@api_bp.route('/campos/<int:id>', methods=['DELETE'])
def delete_campo(id):
    campo = Campo.query.get_or_404(id)
    db.session.delete(campo)
    db.session.commit()
    return jsonify({'mensaje': 'Campo eliminado'})

# ========== TIPOS DE CAMPO ==========
@api_bp.route('/tipos-campo', methods=['GET'])
def get_tipos_campo():
    return jsonify(Campo.TIPOS)


# ========== EMPRESAS ==========
@api_bp.route('/empresas', methods=['GET'])
def get_empresas():
    empresas = Empresa.query.all()
    return jsonify([e.to_dict() for e in empresas])


@api_bp.route('/setup-empresa', methods=['POST'])
def setup_empresa():
    import os
    import traceback
    from generator import TableGenerator

    data = request.json
    nombre = data.get('nombre_empresa') or data.get('nombre')
    rubro_id = data.get('rubro_id')

    if not nombre or not rubro_id:
        return jsonify({'error': 'nombre_empresa y rubro_id son requeridos'}), 400

    rubro = Rubro.query.get_or_404(rubro_id)

    try:
        empresa = Empresa(nombre=nombre, rubro_id=rubro_id)
        db.session.add(empresa)
        db.session.flush()

        generator = TableGenerator(os.getenv('DATABASE_URL'))
        tablas = generator.create_empresa_tables(empresa.id, rubro_id)
        empresa.tablas_creadas = tablas
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()  # imprime el error completo en la terminal Flask
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'empresa': empresa.to_dict(),
        'rubro': rubro.to_dict(),
        'tablas_creadas': tablas
    }), 201


# ========== GENERADOR ==========
@api_bp.route('/generar/<int:rubro_id>', methods=['POST'])
def generar_tablas(rubro_id):
    import os
    from generator import TableGenerator

    empresa_id = request.json.get('empresa_id', 1) if request.json else 1
    db_uri = os.getenv('DATABASE_URL')
    generator = TableGenerator(db_uri)
    tablas = generator.create_empresa_tables(empresa_id, rubro_id)
    return jsonify({'mensaje': 'Tablas creadas', 'tablas': tablas})


# ========== OPERACIÓN DE DATOS (tablas físicas) ==========
from sqlalchemy import text, inspect as sa_inspect

def _get_table_name(empresa_id, entidad_id):
    """Obtiene el nombre de la tabla física para una empresa y entidad."""
    entidad = Entidad.query.get_or_404(entidad_id)
    return f"emp_{empresa_id}_{entidad.nombre_tabla}", entidad


def _get_campos_map(entidad_id):
    """Devuelve dict {nombre_fisico: campo} para una entidad."""
    campos = Campo.query.filter_by(entidad_id=entidad_id).all()
    return {c.nombre_fisico: c for c in campos}


@api_bp.route('/empresa/<int:empresa_id>/entidad/<int:entidad_id>/registros', methods=['GET'])
def get_registros(empresa_id, entidad_id):
    """Lee todos los registros de una tabla física."""
    from database import db
    table_name, entidad = _get_table_name(empresa_id, entidad_id)

    # Verificar que la empresa existe
    Empresa.query.get_or_404(empresa_id)

    try:
        result = db.session.execute(text(f'SELECT * FROM "{table_name}"'))
        rows = [dict(row._mapping) for row in result]
        return jsonify({
            'entidad': entidad.nombre,
            'tabla': table_name,
            'total': len(rows),
            'registros': rows
        })
    except Exception as e:
        return jsonify({'error': f'Tabla no encontrada o sin datos: {str(e)}'}), 404


@api_bp.route('/empresa/<int:empresa_id>/entidad/<int:entidad_id>/registros', methods=['POST'])
def create_registro(empresa_id, entidad_id):
    """Inserta un registro en una tabla física."""
    from database import db
    table_name, entidad = _get_table_name(empresa_id, entidad_id)
    Empresa.query.get_or_404(empresa_id)

    data = request.json or {}
    campos_map = _get_campos_map(entidad_id)

    # Validar campos requeridos
    faltantes = [
        c.etiqueta or c.nombre_fisico
        for c in campos_map.values()
        if c.es_requerido and c.nombre_fisico not in data
    ]
    if faltantes:
        return jsonify({'error': f'Campos requeridos faltantes: {", ".join(faltantes)}'}), 400

    # Solo insertar columnas que existen en el meta-modelo
    columnas_validas = {k: v for k, v in data.items() if k in campos_map}
    if not columnas_validas:
        return jsonify({'error': 'No se enviaron campos válidos'}), 400

    cols = ', '.join(f'"{k}"' for k in columnas_validas)
    params = ', '.join(f':{k}' for k in columnas_validas)

    try:
        result = db.session.execute(
            text(f'INSERT INTO "{table_name}" ({cols}) VALUES ({params}) RETURNING id'),
            columnas_validas
        )
        db.session.commit()
        nuevo_id = result.fetchone()[0]
        return jsonify({'mensaje': 'Registro creado', 'id': nuevo_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/empresa/<int:empresa_id>/entidad/<int:entidad_id>/registros/<int:registro_id>', methods=['GET'])
def get_registro(empresa_id, entidad_id, registro_id):
    """Lee un registro específico por id."""
    from database import db
    table_name, _ = _get_table_name(empresa_id, entidad_id)
    Empresa.query.get_or_404(empresa_id)

    try:
        result = db.session.execute(
            text(f'SELECT * FROM "{table_name}" WHERE id = :id'),
            {'id': registro_id}
        )
        row = result.fetchone()
        if not row:
            return jsonify({'error': 'Registro no encontrado'}), 404
        return jsonify(dict(row._mapping))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/empresa/<int:empresa_id>/entidad/<int:entidad_id>/registros/<int:registro_id>', methods=['PUT'])
def update_registro(empresa_id, entidad_id, registro_id):
    """Actualiza un registro existente."""
    from database import db
    table_name, _ = _get_table_name(empresa_id, entidad_id)
    Empresa.query.get_or_404(empresa_id)

    data = request.json or {}
    campos_map = _get_campos_map(entidad_id)

    columnas_validas = {k: v for k, v in data.items() if k in campos_map}
    if not columnas_validas:
        return jsonify({'error': 'No se enviaron campos válidos'}), 400

    sets = ', '.join(f'"{k}" = :{k}' for k in columnas_validas)
    columnas_validas['_id'] = registro_id

    try:
        result = db.session.execute(
            text(f'UPDATE "{table_name}" SET {sets} WHERE id = :_id'),
            columnas_validas
        )
        db.session.commit()
        if result.rowcount == 0:
            return jsonify({'error': 'Registro no encontrado'}), 404
        return jsonify({'mensaje': 'Registro actualizado', 'id': registro_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/empresa/<int:empresa_id>/entidad/<int:entidad_id>/registros/<int:registro_id>', methods=['DELETE'])
def delete_registro(empresa_id, entidad_id, registro_id):
    """Elimina un registro por id."""
    from database import db
    table_name, _ = _get_table_name(empresa_id, entidad_id)
    Empresa.query.get_or_404(empresa_id)

    try:
        result = db.session.execute(
            text(f'DELETE FROM "{table_name}" WHERE id = :id'),
            {'id': registro_id}
        )
        db.session.commit()
        if result.rowcount == 0:
            return jsonify({'error': 'Registro no encontrado'}), 404
        return jsonify({'mensaje': 'Registro eliminado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/empresa/<int:empresa_id>/entidad/<int:entidad_id>/schema', methods=['GET'])
def get_schema(empresa_id, entidad_id):
    """Devuelve la definición de campos de una entidad (útil para construir formularios dinámicos)."""
    Empresa.query.get_or_404(empresa_id)
    entidad = Entidad.query.get_or_404(entidad_id)
    campos = Campo.query.filter_by(entidad_id=entidad_id).order_by(Campo.orden).all()
    return jsonify({
        'entidad_id': entidad_id,
        'entidad': entidad.nombre,
        'tabla': f'emp_{empresa_id}_{entidad.nombre_tabla}',
        'campos': [c.to_dict() for c in campos]
    })


# ========== AUTENTICACIÓN ==========
import os
from flask import session
from werkzeug.utils import secure_filename
from models import Usuario, ConfigEmpresa, Notificacion, Tarea

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'uploads')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api_bp.route('/auth/registro', methods=['POST'])
def registro():
    data = request.json
    if Usuario.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'El email ya está registrado'}), 400
    usuario = Usuario(
        nombre=data['nombre'],
        email=data['email'],
        rol=data.get('rol', 'admin')
    )
    usuario.set_password(data['password'])
    db.session.add(usuario)
    db.session.commit()
    session['usuario_id'] = usuario.id
    return jsonify({'usuario': usuario.to_dict()}), 201


@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    usuario = Usuario.query.filter_by(email=data.get('email')).first()
    if not usuario or not usuario.check_password(data.get('password', '')):
        return jsonify({'error': 'Credenciales incorrectas'}), 401
    if not usuario.activo:
        return jsonify({'error': 'Usuario inactivo'}), 403
    session['usuario_id'] = usuario.id
    return jsonify({'usuario': usuario.to_dict()})


@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.pop('usuario_id', None)
    return jsonify({'mensaje': 'Sesión cerrada'})


@api_bp.route('/auth/me', methods=['GET'])
def me():
    uid = session.get('usuario_id')
    if not uid:
        return jsonify({'error': 'No autenticado'}), 401
    usuario = Usuario.query.get(uid)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({'usuario': usuario.to_dict()})


# ========== CONFIGURACIÓN EMPRESA ==========
@api_bp.route('/config', methods=['GET'])
def get_config():
    config = ConfigEmpresa.query.first()
    if not config:
        return jsonify({'configurado': False})
    return jsonify(config.to_dict())


@api_bp.route('/config/setup', methods=['POST'])
def setup_sistema():
    """Wizard inicial: nombre empresa, rubro, contraseña admin, logo opcional."""
    import traceback
    from generator import TableGenerator

    nombre = request.form.get('nombre_empresa')
    rubro_id = request.form.get('rubro_id', type=int)
    admin_nombre = request.form.get('admin_nombre')
    admin_email = request.form.get('admin_email')
    admin_password = request.form.get('admin_password')

    if not all([nombre, rubro_id, admin_nombre, admin_email, admin_password]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    if ConfigEmpresa.query.filter_by(configurado=True).first():
        return jsonify({'error': 'El sistema ya está configurado'}), 400

    logo_path = None
    if 'logo' in request.files:
        file = request.files['logo']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            logo_path = f'/uploads/{filename}'

    try:
        # Crear empresa física
        empresa = Empresa(nombre=nombre, rubro_id=rubro_id)
        db.session.add(empresa)
        db.session.flush()

        generator = TableGenerator(os.getenv('DATABASE_URL'))
        tablas = generator.create_empresa_tables(empresa.id, rubro_id)
        empresa.tablas_creadas = tablas
        db.session.flush()

        # Guardar configuración
        config = ConfigEmpresa(
            nombre=nombre,
            rubro_id=rubro_id,
            empresa_id=empresa.id,
            logo_path=logo_path,
            configurado=True
        )
        db.session.add(config)

        # Crear usuario admin
        if Usuario.query.filter_by(email=admin_email).first():
            return jsonify({'error': 'El email ya está registrado'}), 400

        admin = Usuario(nombre=admin_nombre, email=admin_email, rol='admin')
        admin.set_password(admin_password)
        db.session.add(admin)

        db.session.commit()
        session['usuario_id'] = admin.id

        return jsonify({
            'mensaje': 'Sistema configurado correctamente',
            'config': config.to_dict(),
            'usuario': admin.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/config/logo', methods=['POST'])
def actualizar_logo():
    config = ConfigEmpresa.query.first()
    if not config:
        return jsonify({'error': 'Sistema no configurado'}), 400
    if 'logo' not in request.files:
        return jsonify({'error': 'No se envió archivo'}), 400
    file = request.files['logo']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        config.logo_path = f'/uploads/{filename}'
        db.session.commit()
        return jsonify({'logo_path': config.logo_path})
    return jsonify({'error': 'Formato no permitido'}), 400


# ========== NOTIFICACIONES ==========
@api_bp.route('/notificaciones', methods=['GET'])
def get_notificaciones():
    notifs = Notificacion.query.order_by(Notificacion.fecha.desc()).limit(50).all()
    return jsonify([n.to_dict() for n in notifs])


@api_bp.route('/notificaciones/<int:id>/leer', methods=['PUT'])
def marcar_leida(id):
    n = Notificacion.query.get_or_404(id)
    n.leida = True
    db.session.commit()
    return jsonify(n.to_dict())


@api_bp.route('/notificaciones/leer-todas', methods=['PUT'])
def marcar_todas_leidas():
    Notificacion.query.filter_by(leida=False).update({'leida': True})
    db.session.commit()
    return jsonify({'mensaje': 'Todas marcadas como leídas'})


# ========== TAREAS ==========
@api_bp.route('/tareas', methods=['GET'])
def get_tareas():
    tareas = Tarea.query.order_by(Tarea.completada, Tarea.fecha_limite).all()
    return jsonify([t.to_dict() for t in tareas])


@api_bp.route('/tareas', methods=['POST'])
def create_tarea():
    data = request.json
    from datetime import datetime as dt
    tarea = Tarea(
        titulo=data['titulo'],
        descripcion=data.get('descripcion', ''),
        prioridad=data.get('prioridad', 'media'),
        fecha_limite=dt.fromisoformat(data['fecha_limite']) if data.get('fecha_limite') else None
    )
    db.session.add(tarea)
    db.session.commit()
    return jsonify(tarea.to_dict()), 201


@api_bp.route('/tareas/<int:id>', methods=['PUT'])
def update_tarea(id):
    tarea = Tarea.query.get_or_404(id)
    data = request.json
    from datetime import datetime as dt
    tarea.titulo = data.get('titulo', tarea.titulo)
    tarea.descripcion = data.get('descripcion', tarea.descripcion)
    tarea.completada = data.get('completada', tarea.completada)
    tarea.prioridad = data.get('prioridad', tarea.prioridad)
    if data.get('fecha_limite'):
        tarea.fecha_limite = dt.fromisoformat(data['fecha_limite'])
    db.session.commit()
    return jsonify(tarea.to_dict())


@api_bp.route('/tareas/<int:id>', methods=['DELETE'])
def delete_tarea(id):
    tarea = Tarea.query.get_or_404(id)
    db.session.delete(tarea)
    db.session.commit()
    return jsonify({'mensaje': 'Tarea eliminada'})


# ========== MÓDULOS UNIVERSALES (Contactos, Agenda) ==========
# Disponibles para todas las empresas, independiente del rubro

_UNIVERSAL = {
    'contactos': {
        'tabla': 'contactos',
        'campos': [
            {'nombre': 'nombre',   'tipo': 'string',  'etiqueta': 'Nombre',   'requerido': True},
            {'nombre': 'telefono', 'tipo': 'string',  'etiqueta': 'Teléfono', 'requerido': False},
            {'nombre': 'email',    'tipo': 'email',   'etiqueta': 'Email',    'requerido': False},
            {'nombre': 'empresa',  'tipo': 'string',  'etiqueta': 'Empresa',  'requerido': False},
            {'nombre': 'notas',    'tipo': 'text',    'etiqueta': 'Notas',    'requerido': False},
        ]
    },
    'agenda': {
        'tabla': 'agenda',
        'campos': [
            {'nombre': 'titulo',      'tipo': 'string',  'etiqueta': 'Título',      'requerido': True},
            {'nombre': 'contacto',    'tipo': 'string',  'etiqueta': 'Contacto',    'requerido': False},
            {'nombre': 'fecha',       'tipo': 'date',    'etiqueta': 'Fecha',       'requerido': True},
            {'nombre': 'hora',        'tipo': 'string',  'etiqueta': 'Hora',        'requerido': False},
            {'nombre': 'descripcion', 'tipo': 'text',    'etiqueta': 'Descripción', 'requerido': False},
            {'nombre': 'completado',  'tipo': 'boolean', 'etiqueta': 'Completado',  'requerido': False},
        ]
    },
    'ventas': {
        'tabla': 'ventas',
        'campos': [
            {'nombre': 'cliente',     'tipo': 'string',   'etiqueta': 'Cliente',      'requerido': True},
            {'nombre': 'descripcion', 'tipo': 'text',     'etiqueta': 'Descripción',  'requerido': False},
            {'nombre': 'monto',       'tipo': 'currency', 'etiqueta': 'Monto',        'requerido': True},
            {'nombre': 'fecha',       'tipo': 'date',     'etiqueta': 'Fecha',        'requerido': True},
            {'nombre': 'estado',      'tipo': 'string',   'etiqueta': 'Estado',       'requerido': False},
            {'nombre': 'notas',       'tipo': 'text',     'etiqueta': 'Notas',        'requerido': False},
        ]
    },
    'compras': {
        'tabla': 'compras',
        'campos': [
            {'nombre': 'proveedor',   'tipo': 'string',   'etiqueta': 'Proveedor',    'requerido': True},
            {'nombre': 'descripcion', 'tipo': 'text',     'etiqueta': 'Descripción',  'requerido': False},
            {'nombre': 'monto',       'tipo': 'currency', 'etiqueta': 'Monto',        'requerido': True},
            {'nombre': 'fecha',       'tipo': 'date',     'etiqueta': 'Fecha',        'requerido': True},
            {'nombre': 'estado',      'tipo': 'string',   'etiqueta': 'Estado',       'requerido': False},
            {'nombre': 'notas',       'tipo': 'text',     'etiqueta': 'Notas',        'requerido': False},
        ]
    },
    'caja': {
        'tabla': 'caja',
        'campos': [
            {'nombre': 'tipo',        'tipo': 'string',   'etiqueta': 'Tipo (ingreso/egreso)', 'requerido': True},
            {'nombre': 'concepto',    'tipo': 'string',   'etiqueta': 'Concepto',     'requerido': True},
            {'nombre': 'monto',       'tipo': 'currency', 'etiqueta': 'Monto',        'requerido': True},
            {'nombre': 'fecha',       'tipo': 'date',     'etiqueta': 'Fecha',        'requerido': True},
            {'nombre': 'notas',       'tipo': 'text',     'etiqueta': 'Notas',        'requerido': False},
        ]
    },
}


def _univ_table(empresa_id, modulo):
    return f"univ_{empresa_id}_{_UNIVERSAL[modulo]['tabla']}"


def _ensure_univ_table(table_name, campos):
    import os
    from sqlalchemy import create_engine, Table, Column, Integer, String, Text, Boolean, DateTime, MetaData
    engine = create_engine(os.getenv('DATABASE_URL'))
    meta = MetaData()
    tipo_map = {
        'string': String(255), 'email': String(255), 'text': Text,
        'boolean': Boolean, 'date': DateTime, 'integer': Integer,
    }
    cols = [Column('id', Integer, primary_key=True)]
    for c in campos:
        cols.append(Column(c['nombre'], tipo_map.get(c['tipo'], String(255)), nullable=not c.get('requerido', False)))
    Table(table_name, meta, *cols, extend_existing=True)
    meta.create_all(engine)


@api_bp.route('/universal/schema/<string:modulo>', methods=['GET'])
def get_universal_schema(modulo):
    if modulo not in _UNIVERSAL:
        return jsonify({'error': 'Módulo no encontrado'}), 404
    config = ConfigEmpresa.query.first()
    if not config:
        return jsonify({'error': 'Sistema no configurado'}), 400
    defn = _UNIVERSAL[modulo]
    return jsonify({
        'modulo': modulo,
        'tabla': _univ_table(config.empresa_id, modulo),
        'campos': defn['campos']
    })


@api_bp.route('/universal/<string:modulo>/registros', methods=['GET'])
def get_universal_registros(modulo):
    if modulo not in _UNIVERSAL:
        return jsonify({'error': 'Módulo no encontrado'}), 404
    config = ConfigEmpresa.query.first()
    if not config:
        return jsonify({'error': 'Sistema no configurado'}), 400
    table_name = _univ_table(config.empresa_id, modulo)
    _ensure_univ_table(table_name, _UNIVERSAL[modulo]['campos'])
    try:
        result = db.session.execute(text(f'SELECT * FROM "{table_name}" ORDER BY id DESC'))
        rows = [dict(r._mapping) for r in result]
        return jsonify({'modulo': modulo, 'tabla': table_name, 'total': len(rows), 'registros': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/universal/<string:modulo>/registros', methods=['POST'])
def create_universal_registro(modulo):
    if modulo not in _UNIVERSAL:
        return jsonify({'error': 'Módulo no encontrado'}), 404
    config = ConfigEmpresa.query.first()
    if not config:
        return jsonify({'error': 'Sistema no configurado'}), 400
    table_name = _univ_table(config.empresa_id, modulo)
    _ensure_univ_table(table_name, _UNIVERSAL[modulo]['campos'])
    data = request.json or {}
    validos = {c['nombre'] for c in _UNIVERSAL[modulo]['campos']}
    cols_data = {k: v for k, v in data.items() if k in validos}
    if not cols_data:
        return jsonify({'error': 'Sin campos válidos'}), 400
    cols = ', '.join(f'"{k}"' for k in cols_data)
    params = ', '.join(f':{k}' for k in cols_data)
    try:
        result = db.session.execute(text(f'INSERT INTO "{table_name}" ({cols}) VALUES ({params}) RETURNING id'), cols_data)
        db.session.commit()
        return jsonify({'mensaje': 'Creado', 'id': result.fetchone()[0]}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/universal/<string:modulo>/registros/<int:rid>', methods=['PUT'])
def update_universal_registro(modulo, rid):
    if modulo not in _UNIVERSAL:
        return jsonify({'error': 'Módulo no encontrado'}), 404
    config = ConfigEmpresa.query.first()
    table_name = _univ_table(config.empresa_id, modulo)
    data = request.json or {}
    validos = {c['nombre'] for c in _UNIVERSAL[modulo]['campos']}
    cols_data = {k: v for k, v in data.items() if k in validos}
    if not cols_data:
        return jsonify({'error': 'Sin campos válidos'}), 400
    sets = ', '.join(f'"{k}" = :{k}' for k in cols_data)
    cols_data['_id'] = rid
    try:
        db.session.execute(text(f'UPDATE "{table_name}" SET {sets} WHERE id = :_id'), cols_data)
        db.session.commit()
        return jsonify({'mensaje': 'Actualizado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/universal/<string:modulo>/registros/<int:rid>', methods=['DELETE'])
def delete_universal_registro(modulo, rid):
    if modulo not in _UNIVERSAL:
        return jsonify({'error': 'Módulo no encontrado'}), 404
    config = ConfigEmpresa.query.first()
    table_name = _univ_table(config.empresa_id, modulo)
    try:
        db.session.execute(text(f'DELETE FROM "{table_name}" WHERE id = :id'), {'id': rid})
        db.session.commit()
        return jsonify({'mensaje': 'Eliminado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========== ALERTAS / DSS BRECHA ==========
@api_bp.route('/alertas', methods=['GET'])
def get_alertas():
    """Genera alertas dinámicas consultando tablas físicas."""
    from sqlalchemy import text
    alertas = []
    config = ConfigEmpresa.query.first()
    if not config or not config.empresa_id:
        return jsonify([])

    empresa_id = config.empresa_id
    umbral = config.stock_minimo_alerta or 5

    # Buscar entidades con campo 'stock'
    entidades = Entidad.query.filter_by(rubro_id=config.rubro_id).all()
    for entidad in entidades:
        tiene_stock = Campo.query.filter_by(
            entidad_id=entidad.id, nombre_fisico='stock'
        ).first()
        if not tiene_stock:
            continue
        table_name = f"emp_{empresa_id}_{entidad.nombre_tabla}"
        try:
            result = db.session.execute(
                text(f'SELECT id, stock FROM "{table_name}" WHERE stock <= :umbral AND stock IS NOT NULL'),
                {'umbral': umbral}
            )
            rows = result.fetchall()
            for row in rows:
                alertas.append({
                    'tipo': 'stock_bajo',
                    'titulo': f'Stock bajo en {entidad.nombre_plural or entidad.nombre}',
                    'mensaje': f'Registro #{row[0]} tiene stock de {row[1]} unidades',
                    'entidad': entidad.nombre,
                    'tabla': table_name
                })
        except Exception:
            pass

    # Tareas vencidas
    from datetime import datetime as dt
    tareas_vencidas = Tarea.query.filter(
        Tarea.completada == False,
        Tarea.fecha_limite < dt.utcnow()
    ).all()
    for t in tareas_vencidas:
        alertas.append({
            'tipo': 'tarea_vencida',
            'titulo': f'Tarea vencida: {t.titulo}',
            'mensaje': f'Venció el {t.fecha_limite.strftime("%d/%m/%Y")}',
        })

    return jsonify(alertas)


@api_bp.route('/dss/resumen', methods=['GET'])
def dss_resumen():
    """
    Brecha DSS — expone datos agregados por empresa.
    Diseñado para conectar un módulo de análisis/BI a futuro.
    """
    from sqlalchemy import text
    config = ConfigEmpresa.query.first()
    if not config:
        return jsonify({'error': 'Sistema no configurado'}), 400

    resumen = {
        'empresa': config.nombre,
        'rubro': config.rubro.nombre if config.rubro else None,
        'entidades': [],
        'tareas_pendientes': Tarea.query.filter_by(completada=False).count(),
        'notificaciones_no_leidas': Notificacion.query.filter_by(leida=False).count(),
    }

    entidades = Entidad.query.filter_by(rubro_id=config.rubro_id).all()
    for entidad in entidades:
        table_name = f"emp_{config.empresa_id}_{entidad.nombre_tabla}"
        try:
            result = db.session.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
            total = result.scalar()
            resumen['entidades'].append({
                'nombre': entidad.nombre,
                'tabla': table_name,
                'total_registros': total
            })
        except Exception:
            pass

    return jsonify(resumen)
