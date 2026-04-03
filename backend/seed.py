"""
Script para cargar datos semilla en el metamodelador.
Ejecutar con: python seed.py
"""
from app import create_app
from database import db
from models import Rubro, Entidad, Campo


def crear_rubro(nombre, descripcion, entidades_data):
    # Evitar duplicados
    if Rubro.query.filter_by(nombre=nombre).first():
        print(f"  ⚠️  Rubro '{nombre}' ya existe, omitiendo.")
        return

    rubro = Rubro(nombre=nombre, descripcion=descripcion)
    db.session.add(rubro)
    db.session.flush()

    for orden_e, (ent_nombre, ent_tabla, ent_plural, icono, modulo, campos) in enumerate(entidades_data):
        entidad = Entidad(
            rubro_id=rubro.id,
            nombre=ent_nombre,
            nombre_tabla=ent_tabla,
            nombre_plural=ent_plural,
            icono=icono,
            modulo=modulo,  # <-- NUEVO
            orden=orden_e
        )
        db.session.add(entidad)
        db.session.flush()

        for orden_c, (c_nombre, c_fisico, c_tipo, c_etiqueta, c_requerido) in enumerate(campos):
            campo = Campo(
                entidad_id=entidad.id,
                nombre=c_nombre,
                nombre_fisico=c_fisico,
                tipo=c_tipo,
                etiqueta=c_etiqueta,
                es_requerido=c_requerido,
                visible_en_tabla=True,
                orden=orden_c
            )
            db.session.add(campo)

    print(f"  ✅ Rubro '{nombre}' creado con {len(entidades_data)} entidad(es).")


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("🌱 Cargando datos semilla...\n")

        # ── CAUCHOS ──────────────────────────────────────────────
        crear_rubro('Cauchos', 'Venta de cauchos y llantas', [
            ('producto_caucho', 'productos_caucho', 'Productos', '🛞', 'inventario', [
                ('ancho',    'ancho',    'integer',  'Ancho (mm)',   True),
                ('perfil',   'perfil',   'integer',  'Perfil (%)',   True),
                ('diametro', 'diametro', 'integer',  'Diámetro (R)', True),
                ('marca',    'marca',    'string',   'Marca',        True),
                ('precio',   'precio',   'currency', 'Precio',       True),
                ('stock',    'stock',    'integer',  'Stock',        False),
            ]),
            ('proveedor', 'proveedores', 'Proveedores', '🏭', 'compras', [
                ('nombre',   'nombre',   'string', 'Nombre',   True),
                ('telefono', 'telefono', 'string', 'Teléfono', False),
                ('email',    'email',    'email',  'Email',    False),
            ]),
        ])

        # ── RESTAURANTE ───────────────────────────────────────────
        crear_rubro('Restaurante', 'Gestión de restaurantes y menús', [
            ('producto', 'productos', 'Productos', '🍔', 'inventario', [
                ('nombre',      'nombre',      'string',   'Nombre',      True),
                ('descripcion', 'descripcion', 'text',     'Descripción', False),
                ('precio',      'precio',      'currency', 'Precio',      True),
                ('categoria',   'categoria',   'select',   'Categoría',   False),
                ('disponible',  'disponible',  'boolean',  'Disponible',  False),
            ]),
            ('mesa', 'mesas', 'Mesas', '🪑', 'inventario', [
                ('numero',   'numero',   'integer', 'Número',   True),
                ('capacidad','capacidad','integer', 'Capacidad',True),
                ('activa',   'activa',   'boolean', 'Activa',   False),
            ]),
        ])

        # ── PERFUMERÍA ────────────────────────────────────────────
        crear_rubro('Perfumería', 'Venta de perfumes y cosméticos', [
            ('producto_perfume', 'productos_perfume', 'Productos', '🌸', 'inventario', [
                ('nombre',  'nombre',  'string',   'Nombre',  True),
                ('marca',   'marca',   'string',   'Marca',   True),
                ('volumen', 'volumen', 'integer',  'Volumen (ml)', False),
                ('genero',  'genero',  'select',   'Género',  False),
                ('precio',  'precio',  'currency', 'Precio',  True),
                ('stock',   'stock',   'integer',  'Stock',   False),
            ]),
        ])

        # ── FERRETERÍA ────────────────────────────────────────────
        crear_rubro('Ferretería', 'Venta de materiales y herramientas', [
            ('producto_ferreteria', 'productos_ferreteria', 'Productos', '🔧', 'inventario', [
                ('nombre',      'nombre',      'string',   'Nombre',      True),
                ('codigo',      'codigo',      'string',   'Código',      True),
                ('unidad',      'unidad',      'string',   'Unidad',      False),
                ('precio',      'precio',      'currency', 'Precio',      True),
                ('stock',       'stock',       'integer',  'Stock',       False),
                ('descripcion', 'descripcion', 'text',     'Descripción', False),
            ]),
        ])

        # ── TIENDA / RETAIL ───────────────────────────────────────
        crear_rubro('Tienda Retail', 'Venta al detal: boutique, kiosko, papelería, bazar', [
            ('producto', 'productos', 'Productos', '🛍️', 'inventario', [
                ('nombre',      'nombre',      'string',   'Nombre',       True),
                ('codigo',      'codigo',      'string',   'Código',       False),
                ('categoria',   'categoria',   'select',   'Categoría',    False),
                ('precio_costo','precio_costo','currency', 'Precio costo', False),
                ('precio_venta','precio_venta','currency', 'Precio venta', True),
                ('stock',       'stock',       'integer',  'Stock',        True),
                ('talla',       'talla',       'string',   'Talla',        False),
                ('color',       'color',       'string',   'Color',        False),
                ('marca',       'marca',       'string',   'Marca',        False),
            ]),
            ('cliente', 'clientes', 'Clientes', '👤', 'contactos', [
                ('nombre',    'nombre',    'string', 'Nombre',    True),
                ('telefono',  'telefono',  'string', 'Teléfono',  False),
                ('email',     'email',     'email',  'Email',     False),
                ('direccion', 'direccion', 'text',   'Dirección', False),
            ]),
        ])

        # ── TALLER / FÁBRICA ──────────────────────────────────────
        crear_rubro('Taller', 'Servicios de taller: mecánica, carpintería, cerrajería', [
            ('orden_trabajo', 'ordenes_trabajo', 'Órdenes de trabajo', '🔩', 'ventas', [
                ('numero',       'numero',       'string',   'N° Orden',      True),
                ('cliente',      'cliente',      'string',   'Cliente',       True),
                ('telefono',     'telefono',     'string',   'Teléfono',      False),
                ('descripcion',  'descripcion',  'text',     'Descripción',   True),
                ('fecha_entrada','fecha_entrada','date',     'Fecha entrada', True),
                ('fecha_salida', 'fecha_salida', 'date',     'Fecha salida',  False),
                ('costo',        'costo',        'currency', 'Costo',         False),
                ('estado',       'estado',       'select',   'Estado',        True),
            ]),
            ('repuesto', 'repuestos', 'Repuestos', '⚙️', 'inventario', [
                ('nombre',      'nombre',      'string',   'Nombre',      True),
                ('referencia',  'referencia',  'string',   'Referencia',  False),
                ('precio',      'precio',      'currency', 'Precio',      True),
                ('stock',       'stock',       'integer',  'Stock',       True),
                ('proveedor',   'proveedor',   'string',   'Proveedor',   False),
            ]),
        ])

        # ── DISTRIBUIDORA / MAYORISTA ─────────────────────────────
        crear_rubro('Distribuidora', 'Distribución y venta mayorista de productos', [
            ('producto', 'productos', 'Productos', '📦', 'inventario', [
                ('nombre',       'nombre',       'string',   'Nombre',        True),
                ('codigo',       'codigo',       'string',   'Código',        True),
                ('categoria',    'categoria',    'select',   'Categoría',     False),
                ('unidad',       'unidad',       'string',   'Unidad',        True),
                ('precio_mayor', 'precio_mayor', 'currency', 'Precio mayor',  True),
                ('precio_detal', 'precio_detal', 'currency', 'Precio detal',  False),
                ('stock',        'stock',        'integer',  'Stock',         True),
                ('stock_minimo', 'stock_minimo', 'integer',  'Stock mínimo',  False),
                ('proveedor',    'proveedor',    'string',   'Proveedor',     False),
            ]),
            ('cliente', 'clientes', 'Clientes', '🏢', 'contactos', [
                ('nombre',    'nombre',    'string',   'Nombre',      True),
                ('rif',       'rif',       'string',   'RIF',         False),
                ('telefono',  'telefono',  'string',   'Teléfono',    False),
                ('email',     'email',     'email',    'Email',       False),
                ('direccion', 'direccion', 'text',     'Dirección',   False),
                ('credito',   'credito',   'boolean',  'Tiene crédito', False),
            ]),
            ('proveedor', 'proveedores', 'Proveedores', '🏭', 'compras', [
                ('nombre',    'nombre',    'string', 'Nombre',    True),
                ('rif',       'rif',       'string', 'RIF',       False),
                ('telefono',  'telefono',  'string', 'Teléfono',  False),
                ('email',     'email',     'email',  'Email',     False),
                ('contacto',  'contacto',  'string', 'Contacto',  False),
            ]),
        ])

        # ── SERVICIOS PROFESIONALES ───────────────────────────────
        crear_rubro('Servicios Profesionales', 'Consultoras, estudios, agencias y despachos', [
            ('cliente', 'clientes', 'Clientes', '👔', 'contactos', [
                ('nombre',    'nombre',    'string',  'Nombre',     True),
                ('empresa',   'empresa',   'string',  'Empresa',    False),
                ('telefono',  'telefono',  'string',  'Teléfono',   False),
                ('email',     'email',     'email',   'Email',      True),
                ('direccion', 'direccion', 'text',    'Dirección',  False),
            ]),
            ('proyecto', 'proyectos', 'Proyectos', '📋', 'ventas', [
                ('nombre',       'nombre',       'string',   'Nombre',        True),
                ('cliente',      'cliente',      'string',   'Cliente',       True),
                ('descripcion',  'descripcion',  'text',     'Descripción',   False),
                ('fecha_inicio', 'fecha_inicio', 'date',     'Fecha inicio',  True),
                ('fecha_fin',    'fecha_fin',    'date',     'Fecha fin',     False),
                ('monto',        'monto',        'currency', 'Monto',         False),
                ('estado',       'estado',       'select',   'Estado',        True),
            ]),
            ('cita', 'citas', 'Citas', '📅', 'agenda', [
                ('cliente',   'cliente',   'string',   'Cliente',   True),
                ('fecha',     'fecha',     'date',     'Fecha',     True),
                ('hora',      'hora',      'string',   'Hora',      True),
                ('motivo',    'motivo',    'text',     'Motivo',    False),
                ('atendido',  'atendido',  'boolean',  'Atendido',  False),
            ]),
        ])

        db.session.commit()
        print("\n✅ Seed completado.")


if __name__ == '__main__':
    seed()