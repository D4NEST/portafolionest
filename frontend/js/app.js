// ====================================================================
// CONFIGURACIÓN Y ESTADO GLOBAL
// ====================================================================
const API_BASE = '/api';
let appConfig = null;               // Datos de /api/config
let currentUser = null;              // Usuario autenticado
let entidadesPorModulo = {};         // Entidades agrupadas por módulo
let currentEntidadId = null;         // Entidad seleccionada actualmente
let currentSchema = null;            // Schema de la entidad actual
let currentUniversalModulo = null;   // 'contactos' | 'agenda' | null
    

const MODULOS_UNIVERSALES = ['contactos', 'agenda', 'ventas', 'compras', 'caja'];
const MODULOS_INFORMATIVOS = {
    seguimiento: { icono: 'fa-chart-line', titulo: 'Seguimiento', desc: 'Seguimiento de oportunidades y proyectos.' },
};

// Elementos del DOM (los más usados)
const elements = {
    dashboardScreen: document.getElementById('dashboardScreen'),
    empresaNombre: document.getElementById('empresaNombre'),
    userName: document.getElementById('userName'),
    userInitial: document.getElementById('userInitial'),
    logoutBtn: document.getElementById('logoutBtn'),
    refreshBtn: document.getElementById('refreshBtn'),
    addBtn: document.getElementById('addBtn'),
    entitySelect: document.getElementById('entitySelect'),
    entitySelectorCard: document.getElementById('entitySelectorCard'),
    tableBody: document.getElementById('tableBody'),
    tableHeader: document.querySelector('#dataTable thead tr'),
    statsContainer: document.getElementById('statsContainer'),
    tasksContainer: document.getElementById('tasksContainer'),
    alertsContainer: document.getElementById('alertsContainer'),
    searchInput: document.getElementById('searchInput'),
    searchBtn: document.getElementById('searchBtn'),
    // Modales
    itemModal: document.getElementById('itemModal'),
    closeModal: document.getElementById('closeModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalFieldsContainer: document.getElementById('modalFieldsContainer'),
    itemForm: document.getElementById('itemForm'),
    modalMessage: document.getElementById('modalMessage'),
    confirmModal: document.getElementById('confirmModal'),
    confirmMessage: document.getElementById('confirmMessage'),
    confirmYes: document.getElementById('confirmYes'),
    confirmNo: document.getElementById('confirmNo'),
    closeConfirmModal: document.getElementById('closeConfirmModal')
};

// ====================================================================
// FUNCIONES DE UTILIDAD
// ====================================================================
function showLoading(container) {
    if (container) container.innerHTML = '<div class="loading"></div> Cargando...';
}

function showError(container, message) {
    if (container) container.innerHTML = `<div class="alert alert-danger">${message}</div>`;
}

function showMessage(element, message, type) {
    if (!element) return;
    element.textContent = message;
    element.className = `alert alert-${type}`;
    element.style.display = 'block';
}

function hideMessage(element) {
    if (element) element.style.display = 'none';
}

// Fetch con manejo de sesión y errores
async function secureFetch(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
    if (response.status === 401) {
        // Sesión expirada, redirigir al login
        window.location.href = '/';
        throw new Error('Sesión expirada');
    }
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Error ${response.status}: ${error}`);
    }
    return response.json();
}

// ====================================================================
// INICIALIZACIÓN DEL DASHBOARD
// ====================================================================
async function initDashboard() {
    try {
        // 1. Obtener configuración global
        appConfig = await secureFetch(`${API_BASE}/config`);
        if (!appConfig.configurado) {
            window.location.href = '/setup';
            return;
        }

        // 2. Obtener usuario actual
        const meData = await secureFetch(`${API_BASE}/auth/me`);
        currentUser = meData.usuario;

        // 3. Actualizar UI con datos del usuario y empresa
        if (elements.empresaNombre) elements.empresaNombre.textContent = appConfig.nombre;
        if (elements.userName) elements.userName.textContent = currentUser.nombre;
        if (elements.userInitial) elements.userInitial.textContent = currentUser.nombre.charAt(0).toUpperCase();

        // 4. Cargar estadísticas, alertas y tareas
        await Promise.all([
            cargarStats(),
            cargarAlertas(),
            cargarTareas()
        ]);

        // 5. Cargar entidades y agrupar por módulo
        await cargarEntidadesYModulos();

    } catch (error) {
        console.error('Error en initDashboard:', error);
        alert('Error al cargar el dashboard. Intenta recargar.');
    }
}

// ====================================================================
// CLASIFICACIÓN DE ENTIDADES EN MÓDULOS (sin campo modulo en BD)
// Heurística por nombre: palabras clave CRM → crm, resto → erp
// ====================================================================
const CRM_KEYWORDS = ['cliente', 'contacto', 'cita', 'proyecto', 'agenda', 'seguimiento', 'lead', 'oportunidad'];
const ERP_MODULES  = {
    inventario: ['producto', 'repuesto', 'articulo', 'item', 'stock', 'caucho', 'perfume', 'ferreteria'],
    ventas:     ['venta', 'factura', 'pedido', 'orden_venta', 'cotizacion'],
    compras:    ['compra', 'proveedor', 'orden_compra', 'orden_trabajo'],
    caja:       ['caja', 'pago', 'cobro', 'movimiento', 'ingreso', 'egreso'],
};

function clasificarEntidad(entidad) {
    const nombre = entidad.nombre.toLowerCase();
    // ¿Es CRM?
    if (CRM_KEYWORDS.some(k => nombre.includes(k))) {
        if (nombre.includes('cita') || nombre.includes('agenda')) return 'agenda';
        if (nombre.includes('proyecto') || nombre.includes('seguimiento')) return 'seguimiento';
        return 'contactos';
    }
    // ¿Qué módulo ERP?
    for (const [mod, keywords] of Object.entries(ERP_MODULES)) {
        if (keywords.some(k => nombre.includes(k))) return mod;
    }
    return 'inventario'; // fallback
}

// ====================================================================
// CARGA DE ENTIDADES Y AGRUPACIÓN POR MÓDULO
// ====================================================================
async function cargarEntidadesYModulos() {
    try {
        const rubroId = appConfig.rubro_id;
        const entidades = await secureFetch(`${API_BASE}/rubros/${rubroId}/entidades`);

        // Agrupar usando clasificación por nombre
        entidadesPorModulo = {};
        entidades.forEach(e => {
            const mod = clasificarEntidad(e);
            if (!entidadesPorModulo[mod]) entidadesPorModulo[mod] = [];
            entidadesPorModulo[mod].push(e);
        });

        // Asignar evento a los enlaces del menú lateral
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.addEventListener('click', (evt) => {
                evt.preventDefault();
                const modulo = link.dataset.modulo;
                // Marcar activo
                document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                cargarModulo(modulo);
            });
        });

        // Activar el primer link que tenga entidades
        const primerLinkConDatos = [...document.querySelectorAll('.sidebar-link')]
            .find(l => entidadesPorModulo[l.dataset.modulo]?.length > 0);

        if (primerLinkConDatos) {
            primerLinkConDatos.classList.add('active');
            cargarModulo(primerLinkConDatos.dataset.modulo);
        } else if (entidades.length > 0) {
            // Si ningún módulo coincide, mostrar todas en inventario
            entidadesPorModulo['inventario'] = entidades;
            document.querySelector('[data-modulo="inventario"]')?.classList.add('active');
            cargarModulo('inventario');
        }
    } catch (error) {
        console.error('Error cargando entidades:', error);
    }
}

// ====================================================================
// CARGAR UN MÓDULO (ERP/CRM)
// ====================================================================
function cargarModulo(modulo) {
    const labels = {
        inventario: 'Inventario', ventas: 'Ventas', compras: 'Compras', caja: 'Caja',
        contactos: 'Contactos', agenda: 'Agenda', seguimiento: 'Seguimiento'
    };
    const iconos = {
        inventario: 'fa-cubes', ventas: 'fa-shopping-cart', compras: 'fa-truck', caja: 'fa-coins',
        contactos: 'fa-address-book', agenda: 'fa-calendar-alt', seguimiento: 'fa-chart-line'
    };
    const titulo = labels[modulo] || modulo.charAt(0).toUpperCase() + modulo.slice(1);
    const icono = iconos[modulo] || 'fa-chart-pie';
    document.querySelector('.page-title h1').innerHTML = `<i class="fas ${icono}"></i> ${titulo}`;

    // Módulos universales — tablas propias, independientes del rubro
    if (MODULOS_UNIVERSALES.includes(modulo)) {
        cargarModuloUniversal(modulo);
        return;
    }

    // Módulos informativos — sin tablas aún
    if (MODULOS_INFORMATIVOS[modulo]) {
        const info = MODULOS_INFORMATIVOS[modulo];
        ocultarSelectorEntidad();
        if (elements.addBtn) elements.addBtn.style.display = 'none';
        if (elements.tableHeader) elements.tableHeader.innerHTML = '';
        if (elements.tableBody) elements.tableBody.innerHTML = `
            <tr><td colspan="10" style="text-align:center;padding:60px;color:var(--color-text-secondary);">
                <i class="fas ${info.icono}" style="font-size:3rem;display:block;margin-bottom:16px;opacity:.3"></i>
                <strong style="font-size:1.1rem;display:block;margin-bottom:8px;">${info.titulo}</strong>
                <span style="font-size:.9rem;">${info.desc}<br>
                <em style="opacity:.6">Módulo en desarrollo — próximamente disponible.</em></span>
            </td></tr>`;
        return;
    }

    // Módulos ERP del rubro (inventario, compras con proveedor, etc.)
    const entidades = entidadesPorModulo[modulo];
    if (!entidades || entidades.length === 0) {
        ocultarSelectorEntidad();
        if (elements.addBtn) elements.addBtn.style.display = 'none';
        if (elements.tableHeader) elements.tableHeader.innerHTML = '';
        if (elements.tableBody) elements.tableBody.innerHTML = `
            <tr><td colspan="10" style="text-align:center;padding:40px;color:var(--color-text-secondary);">
                <i class="fas fa-inbox" style="font-size:2rem;display:block;margin-bottom:10px;opacity:.4"></i>
                Este módulo no tiene entidades configuradas para este rubro.
            </td></tr>`;
        return;
    }

    if (entidades.length > 1) {
        mostrarSelectorEntidad(entidades);
    } else {
        ocultarSelectorEntidad();
        cargarEntidad(entidades[0].id);
    }
}

function mostrarSelectorEntidad(entidades) {
    const card = elements.entitySelectorCard;
    if (card) card.style.display = 'block';

    const select = elements.entitySelect;
    if (!select) return;
    select.innerHTML = '<option value="">-- Selecciona entidad --</option>';
    entidades.forEach(e => {
        const option = document.createElement('option');
        option.value = e.id;
        option.textContent = e.nombre_plural || e.nombre;
        select.appendChild(option);
    });

    // Evento al cambiar
    select.onchange = (e) => {
        if (e.target.value) {
            cargarEntidad(e.target.value);
        }
    };
}

function ocultarSelectorEntidad() {
    const card = elements.entitySelectorCard;
    if (card) card.style.display = 'none';
}

// ====================================================================
// CARGAR UNA ENTIDAD (SCHEMA Y REGISTROS)
// ====================================================================
async function cargarEntidad(entidadId) {
    try {
        showLoading(elements.tableBody);
        currentEntidadId = entidadId;
        currentUniversalModulo = null;

        const empresaId = appConfig.empresa_id;
        const [schema, data] = await Promise.all([
            secureFetch(`${API_BASE}/empresa/${empresaId}/entidad/${entidadId}/schema`),
            secureFetch(`${API_BASE}/empresa/${empresaId}/entidad/${entidadId}/registros`)
        ]);

        currentSchema = schema;
        renderTablaDinamica(schema, data.registros);

        // Mostrar botón "Agregar" si la entidad tiene campos en formulario
        if (schema.campos.some(c => c.visible_en_formulario)) {
            if (elements.addBtn) {
                elements.addBtn.style.display = 'inline-block';
                elements.addBtn.onclick = () => abrirModalNuevo(schema);
            }
        } else {
            if (elements.addBtn) elements.addBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Error cargando entidad:', error);
        showError(elements.tableBody, 'Error al cargar los registros');
    }
}

// ====================================================================
// RENDERIZAR TABLA DINÁMICA CON ACCIONES
// ====================================================================
function renderTablaDinamica(schema, registros) {
    const tbody = elements.tableBody;
    const thead = elements.tableHeader;

    // Campos visibles en tabla
    const camposVisibles = schema.campos.filter(c => c.visible_en_tabla);

    // Cabeceras
    if (thead) {
        thead.innerHTML = camposVisibles.map(c => `<th>${c.etiqueta}</th>`).join('') + '<th>Acciones</th>';
    }

    if (registros.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${camposVisibles.length + 1}" style="text-align:center;">No hay registros</td></tr>`;
        return;
    }

    // Filas
    tbody.innerHTML = registros.map(reg => {
        const fila = camposVisibles.map(c => `<td>${reg[c.nombre_fisico] || ''}</td>`).join('');
        return `<tr data-id="${reg.id}">
            ${fila}
            <td>
                <div class="acciones-rapidas">
                    <button class="btn-accion btn-editar" data-id="${reg.id}" title="Editar"><i class="fas fa-edit"></i></button>
                    <button class="btn-accion btn-eliminar" data-id="${reg.id}" title="Eliminar"><i class="fas fa-trash"></i></button>
                </div>
            </td>
        </tr>`;
    }).join('');

    // Asignar eventos a los botones de acción
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            if (currentUniversalModulo) {
                const reg = registros.find(r => String(r.id) === String(id));
                abrirModalUniversal(currentUniversalModulo, reg);
            } else {
                abrirModalEditar(id);
            }
        });
    });

    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            if (currentUniversalModulo) {
                confirmarEliminarUniversal(currentUniversalModulo, id);
            } else {
                confirmarEliminar(id);
            }
        });
    });
}

// ====================================================================
// MODAL DINÁMICO PARA CREAR/EDITAR
// ====================================================================
function abrirModalNuevo(schema) {
    const modal = elements.itemModal;
    if (!modal) return;

    elements.modalTitle.innerHTML = `<i class="fas fa-plus"></i> Nuevo ${schema.entidad}`;
    elements.modalFieldsContainer.innerHTML = generarFormularioHTML(schema.campos.filter(c => c.visible_en_formulario));
    hideMessage(elements.modalMessage);

    modal.style.display = 'flex';

    // Configurar evento de submit del formulario
    elements.itemForm.onsubmit = async (e) => {
        e.preventDefault();
        await guardarRegistro(null);
    };
}

function abrirModalEditar(id) {
    // Obtener el registro actual desde la API
    secureFetch(`${API_BASE}/empresa/${appConfig.empresa_id}/entidad/${currentEntidadId}/registros/${id}`)
        .then(registro => {
            const modal = elements.itemModal;
            if (!modal) return;

            elements.modalTitle.innerHTML = `<i class="fas fa-edit"></i> Editar ${currentSchema.entidad}`;
            elements.modalFieldsContainer.innerHTML = generarFormularioHTML(
                currentSchema.campos.filter(c => c.visible_en_formulario),
                registro
            );
            hideMessage(elements.modalMessage);

            modal.style.display = 'flex';

            elements.itemForm.onsubmit = async (e) => {
                e.preventDefault();
                await guardarRegistro(id);
            };
        })
        .catch(error => {
            console.error('Error al obtener registro:', error);
            alert('No se pudo cargar el registro para editar');
        });
}

function generarFormularioHTML(campos, valores = {}) {
    return campos.map(c => {
        const valor = valores[c.nombre_fisico] || '';
        let input = '';
        switch (c.tipo) {
            case 'string':
            case 'email':
            case 'currency':
                input = `<input type="text" class="form-control" name="${c.nombre_fisico}" value="${valor}" ${c.es_requerido ? 'required' : ''}>`;
                break;
            case 'integer':
            case 'float':
                input = `<input type="number" step="${c.tipo === 'float' ? '0.01' : '1'}" class="form-control" name="${c.nombre_fisico}" value="${valor}" ${c.es_requerido ? 'required' : ''}>`;
                break;
            case 'date':
                input = `<input type="date" class="form-control" name="${c.nombre_fisico}" value="${valor}" ${c.es_requerido ? 'required' : ''}>`;
                break;
            case 'boolean':
                input = `<input type="checkbox" name="${c.nombre_fisico}" ${valor ? 'checked' : ''}>`;
                break;
            case 'select':
                let options = '';
                if (c.opciones && Array.isArray(c.opciones)) {
                    options = c.opciones.map(op => `<option value="${op}" ${valor == op ? 'selected' : ''}>${op}</option>`).join('');
                }
                input = `<select class="form-control" name="${c.nombre_fisico}" ${c.es_requerido ? 'required' : ''}>${options}</select>`;
                break;
            default:
                input = `<input type="text" class="form-control" name="${c.nombre_fisico}" value="${valor}">`;
        }
        return `
            <div class="form-group">
                <label>${c.etiqueta} ${c.es_requerido ? '<span style="color:red;">*</span>' : ''}</label>
                ${input}
                ${c.descripcion ? `<small>${c.descripcion}</small>` : ''}
            </div>
        `;
    }).join('');
}

async function guardarRegistro(id) {
    const form = elements.itemForm;
    const formData = new FormData(form);
    const rawData = {};
    formData.forEach((value, key) => { rawData[key] = value; });

    // Convertir los valores según el tipo de campo (usando currentSchema)
    const data = {};
    if (currentSchema && currentSchema.campos) {
        currentSchema.campos.forEach(campo => {
            const valorRaw = rawData[campo.nombre_fisico];
            if (valorRaw === undefined) return;

            let valorConvertido = valorRaw;
            switch (campo.tipo) {
                case 'integer':
                    valorConvertido = parseInt(valorRaw, 10) || 0;
                    break;
                case 'float':
                case 'currency':
                    // Eliminar símbolos de moneda, comas, espacios y convertir a número
                    valorConvertido = parseFloat(valorRaw.replace(/[$, ]/g, '')) || 0;
                    break;
                case 'boolean':
                    // Si es checkbox, el valor puede ser 'on' (true) o ausente (false)
                    valorConvertido = valorRaw === 'on' ? true : false;
                    break;
                default:
                    // string, text, email, etc. se dejan como están
                    valorConvertido = valorRaw;
            }
            data[campo.nombre_fisico] = valorConvertido;
        });
    } else {
        // Si no hay schema (no debería ocurrir), usamos los datos crudos
        Object.assign(data, rawData);
    }

    const url = id
        ? `${API_BASE}/empresa/${appConfig.empresa_id}/entidad/${currentEntidadId}/registros/${id}`
        : `${API_BASE}/empresa/${appConfig.empresa_id}/entidad/${currentEntidadId}/registros`;

    const method = id ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al guardar');
        }

        showMessage(elements.modalMessage, '✅ Guardado correctamente', 'success');
        setTimeout(() => {
            cerrarModal();
            cargarEntidad(currentEntidadId); // Recargar la entidad actual
        }, 1500);
    } catch (error) {
        console.error('Error guardando:', error);
        showMessage(elements.modalMessage, `❌ ${error.message}`, 'danger');
    }
}

function cerrarModal() {
    if (elements.itemModal) elements.itemModal.style.display = 'none';
}

// ====================================================================
// MÓDULOS UNIVERSALES — Contactos y Agenda
// ====================================================================
async function cargarModuloUniversal(modulo) {
    currentUniversalModulo = modulo;
    currentEntidadId = null;
    ocultarSelectorEntidad();
    showLoading(elements.tableBody);

    try {
        const [schemaRes, dataRes] = await Promise.all([
            secureFetch(`${API_BASE}/universal/schema/${modulo}`),
            secureFetch(`${API_BASE}/universal/${modulo}/registros`)
        ]);

        currentSchema = {
            entidad: modulo,
            campos: schemaRes.campos.map(c => ({
                nombre_fisico: c.nombre,
                etiqueta: c.etiqueta,
                tipo: c.tipo,
                es_requerido: c.requerido || false,
                visible_en_tabla: true,
                visible_en_formulario: true,
                opciones: null
            }))
        };

        renderTablaDinamica(currentSchema, dataRes.registros);

        if (elements.addBtn) {
            elements.addBtn.style.display = 'inline-block';
            elements.addBtn.onclick = () => abrirModalUniversal(modulo, null);
        }
    } catch (error) {
        console.error('Error cargando módulo universal:', error);
        showError(elements.tableBody, 'Error al cargar ' + modulo);
    }
}

function abrirModalUniversal(modulo, registro) {
    if (!currentSchema) return;
    const esEdicion = registro !== null && registro !== undefined;
    const label = modulo.charAt(0).toUpperCase() + modulo.slice(1);

    elements.modalTitle.innerHTML = `<i class="fas fa-${esEdicion ? 'edit' : 'plus'}"></i> ${esEdicion ? 'Editar' : 'Nuevo'} en ${label}`;
    elements.modalFieldsContainer.innerHTML = generarFormularioHTML(
        currentSchema.campos.filter(c => c.visible_en_formulario),
        registro || {}
    );
    hideMessage(elements.modalMessage);
    elements.itemModal.style.display = 'flex';

    elements.itemForm.onsubmit = async (e) => {
        e.preventDefault();
        await guardarUniversal(modulo, esEdicion ? registro.id : null);
    };
}

async function guardarUniversal(modulo, id) {
    const formData = new FormData(elements.itemForm);
    const data = {};
    formData.forEach((v, k) => { data[k] = v; });
    currentSchema.campos.forEach(c => {
        if (c.tipo === 'boolean') data[c.nombre_fisico] = formData.has(c.nombre_fisico);
    });

    const url = id
        ? `${API_BASE}/universal/${modulo}/registros/${id}`
        : `${API_BASE}/universal/${modulo}/registros`;

    try {
        const res = await fetch(url, {
            method: id ? 'PUT' : 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) { const e = await res.json(); throw new Error(e.error || 'Error'); }
        showMessage(elements.modalMessage, '✅ Guardado correctamente', 'success');
        setTimeout(() => { cerrarModal(); cargarModuloUniversal(modulo); }, 1200);
    } catch (error) {
        showMessage(elements.modalMessage, `❌ ${error.message}`, 'danger');
    }
}

function confirmarEliminarUniversal(modulo, id) {
    if (!elements.confirmModal) return;
    elements.confirmMessage.textContent = '¿Eliminar este registro? Esta acción no se puede deshacer.';
    elements.confirmModal.style.display = 'flex';
    elements.confirmYes.onclick = async () => {
        try {
            const res = await fetch(`${API_BASE}/universal/${modulo}/registros/${id}`, {
                method: 'DELETE', credentials: 'include'
            });
            if (!res.ok) { const e = await res.json(); throw new Error(e.error); }
            cerrarConfirmModal();
            cargarModuloUniversal(modulo);
        } catch (error) {
            alert(`Error: ${error.message}`);
            cerrarConfirmModal();
        }
    };
    elements.confirmNo.onclick = cerrarConfirmModal;
    if (elements.closeConfirmModal) elements.closeConfirmModal.onclick = cerrarConfirmModal;
}

// ====================================================================
// CONFIRMAR Y ELIMINAR REGISTRO
// ====================================================================
function confirmarEliminar(id) {
    const modal = elements.confirmModal;
    if (!modal) return;

    elements.confirmMessage.textContent = '¿Estás seguro de eliminar este registro? Esta acción no se puede deshacer.';
    modal.style.display = 'flex';

    const onYes = async () => {
        try {
            const response = await fetch(`${API_BASE}/empresa/${appConfig.empresa_id}/entidad/${currentEntidadId}/registros/${id}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Error al eliminar');
            }
            cerrarConfirmModal();
            cargarEntidad(currentEntidadId);
        } catch (error) {
            alert(`Error: ${error.message}`);
            cerrarConfirmModal();
        }
    };

    elements.confirmYes.onclick = onYes;
    elements.confirmNo.onclick = cerrarConfirmModal;
    if (elements.closeConfirmModal) elements.closeConfirmModal.onclick = cerrarConfirmModal;
}

function cerrarConfirmModal() {
    if (elements.confirmModal) elements.confirmModal.style.display = 'none';
}

// ====================================================================
// ESTADÍSTICAS (desde /api/dss/resumen)
// ====================================================================
async function cargarStats() {
    try {
        const resumen = await secureFetch(`${API_BASE}/dss/resumen`);
        if (!elements.statsContainer) return;

        const totalRegistros = resumen.entidades.reduce((acc, e) => acc + (e.total_registros || 0), 0);
        elements.statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-value">${resumen.entidades.length}</div>
                <div class="stat-label">Entidades</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${totalRegistros}</div>
                <div class="stat-label">Registros</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${resumen.tareas_pendientes || 0}</div>
                <div class="stat-label">Tareas Pendientes</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${resumen.notificaciones_no_leidas || 0}</div>
                <div class="stat-label">Notificaciones</div>
            </div>
        `;
    } catch (error) {
        console.error('Error cargando stats:', error);
    }
}

// ====================================================================
// ALERTAS (desde /api/alertas)
// ====================================================================
async function cargarAlertas() {
    try {
        const alertas = await secureFetch(`${API_BASE}/alertas`);
        if (!elements.alertsContainer) return;

        if (alertas.length === 0) {
            elements.alertsContainer.innerHTML = '<p style="color:var(--color-text-secondary);font-size:.9rem;">Sin alertas activas ✅</p>';
            return;
        }

        elements.alertsContainer.innerHTML = alertas.map(a => `
            <div style="display:block;padding:12px 16px;margin-bottom:8px;border-radius:8px;
                background:${a.tipo === 'stock_bajo' ? 'rgba(255,170,0,0.1)' : 'rgba(255,68,68,0.1)'};
                border:1px solid ${a.tipo === 'stock_bajo' ? 'rgba(255,170,0,0.3)' : 'rgba(255,68,68,0.3)'};
                color:${a.tipo === 'stock_bajo' ? 'var(--color-warning)' : 'var(--color-danger)'};">
                <strong>${a.titulo}</strong><br>
                <span style="font-size:.85rem;">${a.mensaje}</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error cargando alertas:', error);
    }
}

// ====================================================================
// TAREAS (desde /api/tareas) — con formulario y completar
// ====================================================================
async function cargarTareas() {
    try {
        const tareas = await secureFetch(`${API_BASE}/tareas`);
        if (!elements.tasksContainer) return;

        const pendientes = tareas.filter(t => !t.completada);
        const prioColor = { alta: 'var(--color-danger)', media: 'var(--color-warning)', baja: 'var(--color-success)' };

        const lista = pendientes.length === 0
            ? '<p style="color:var(--color-text-secondary);font-size:.9rem;padding:8px 0;">Sin tareas pendientes ✅</p>'
            : pendientes.map(t => `
                <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--color-border);">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <input type="checkbox" onchange="completarTarea(${t.id})" style="cursor:pointer;width:16px;height:16px;">
                        <div>
                            <strong style="font-size:.9rem;">${t.titulo}</strong>
                            ${t.fecha_limite ? `<br><small style="color:var(--color-text-muted);">📅 ${new Date(t.fecha_limite).toLocaleDateString('es-VE')}</small>` : ''}
                        </div>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <span style="font-size:.75rem;font-weight:700;color:${prioColor[t.prioridad] || 'var(--color-text-secondary)'};">${t.prioridad.toUpperCase()}</span>
                        <button onclick="eliminarTarea(${t.id})" style="background:none;border:none;color:var(--color-danger);cursor:pointer;font-size:.85rem;" title="Eliminar">✕</button>
                    </div>
                </div>`).join('');

        elements.tasksContainer.innerHTML = lista + `
            <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap;">
                <input type="text" id="nuevaTareaTxt" class="form-control" placeholder="Nueva tarea..." style="flex:1;min-width:160px;padding:10px 14px;font-size:.9rem;">
                <select id="nuevaTareaPrio" class="form-control" style="width:110px;padding:10px 14px;font-size:.9rem;">
                    <option value="alta">🔴 Alta</option>
                    <option value="media" selected>🟡 Media</option>
                    <option value="baja">🟢 Baja</option>
                </select>
                <input type="date" id="nuevaTareaFecha" class="form-control" style="width:150px;padding:10px 14px;font-size:.9rem;">
                <button onclick="crearTarea()" class="btn btn-sm" style="padding:10px 18px;white-space:nowrap;">+ Agregar</button>
            </div>`;
    } catch (error) {
        console.error('Error cargando tareas:', error);
    }
}

async function crearTarea() {
    const titulo = document.getElementById('nuevaTareaTxt')?.value.trim();
    if (!titulo) return;
    const prioridad = document.getElementById('nuevaTareaPrio')?.value || 'media';
    const fecha_limite = document.getElementById('nuevaTareaFecha')?.value || null;
    try {
        await secureFetch(`${API_BASE}/tareas`, {
            method: 'POST',
            body: JSON.stringify({ titulo, prioridad, fecha_limite })
        });
        cargarTareas();
        cargarStats();
    } catch (e) { alert('Error al crear tarea: ' + e.message); }
}

async function completarTarea(id) {
    try {
        await secureFetch(`${API_BASE}/tareas/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ completada: true })
        });
        cargarTareas();
        cargarStats();
        cargarAlertas();
    } catch (e) { console.error(e); }
}

async function eliminarTarea(id) {
    if (!confirm('¿Eliminar esta tarea?')) return;
    try {
        await fetch(`${API_BASE}/tareas/${id}`, { method: 'DELETE', credentials: 'include' });
        cargarTareas();
        cargarStats();
    } catch (e) { console.error(e); }
}

// ====================================================================
// LOGOUT
// ====================================================================
async function logout() {
    try {
        await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' });
        window.location.href = '/';
    } catch (error) {
        console.error('Error en logout:', error);
        window.location.href = '/';
    }
}

// ====================================================================
// EVENT LISTENERS
// ====================================================================
if (elements.logoutBtn) {
    elements.logoutBtn.addEventListener('click', logout);
}

if (elements.refreshBtn) {
    elements.refreshBtn.addEventListener('click', () => {
        if (currentEntidadId) {
            cargarEntidad(currentEntidadId);
        }
        cargarStats();
        cargarAlertas();
        cargarTareas();
    });
}

if (elements.closeModal) {
    elements.closeModal.addEventListener('click', cerrarModal);
}

// Cerrar modales al hacer clic fuera
window.addEventListener('click', (e) => {
    if (elements.itemModal && e.target === elements.itemModal) cerrarModal();
    if (elements.confirmModal && e.target === elements.confirmModal) cerrarConfirmModal();
});

// ====================================================================
// INICIALIZACIÓN
// ====================================================================
document.addEventListener('DOMContentLoaded', initDashboard);