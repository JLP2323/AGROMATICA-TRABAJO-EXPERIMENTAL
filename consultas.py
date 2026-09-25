# =========================================================
# SISTEMA DE GESTIÓN DE CULTIVOS INTELIGENTES
# UML EN PYTHON + VISUALIZACIÓN
#
# Requiere instalar:
# pip install graphviz
#
# Además instalar Graphviz en Windows:
# https://graphviz.org/download/
# =========================================================

from graphviz import Digraph

# Crear diagrama UML
uml = Digraph("UML_Cultivos", format="png")
uml.attr(rankdir="TB")
uml.attr("node", shape="record", style="filled", fillcolor="lightyellow")


# =========================================================
# CLASES PRINCIPALES
# =========================================================

uml.node(
    "CooperativaAgricola",
    """{CooperativaAgricola|
    idCooperativa : int\l
    nombre : String\l
    direccion : String\l
    telefono : String\l|
    registrarCooperativa()\l
    actualizarDatos()\l
    eliminarCooperativa()\l
    obtenerCooperativa()\l
    }"""
)

uml.node(
    "Finca",
    """{Finca|
    idFinca : int\l
    nombre : String\l
    extensionHectareas : double\l
    tipoSuelo : String\l|
    registrarFinca()\l
    actualizarFinca()\l
    calcularExtension()\l
    obtenerFinca()\l
    }"""
)

uml.node(
    "UbicacionGPS",
    """{UbicacionGPS|
    idUbicacion : int\l
    latitud : double\l
    longitud : double\l|
    registrarUbicacion()\l
    actualizarUbicacion()\l
    obtenerUbicacion()\l
    }"""
)

uml.node(
    "LoteCultivo",
    """{LoteCultivo|
    numeroLote : int\l
    tipoCultivo : String\l
    fechaSiembra : Date\l
    fechaEstimadaCosecha : Date\l
    estadoActual : String\l|
    registrarLote()\l
    actualizarEstado()\l
    asignarCultivo()\l
    calcularEdad()\l
    obtenerLote()\l
    }"""
)

uml.node(
    "Cosecha",
    """{Cosecha|
    idCosecha : int\l
    fecha : Date\l
    cantidadKg : double\l
    calidad : String\l|
    registrarCosecha()\l
    calcularRendimiento()\l
    obtenerCosechas()\l
    }"""
)

uml.node(
    "Agricultor",
    """{Agricultor|
    cedula : String\l
    nombreCompleto : String\l
    telefono : String\l
    correoElectronico : String\l|
    registrarAgricultor()\l
    actualizarDatos()\l
    obtenerAgricultor()\l
    }"""
)

uml.node(
    "AplicacionInsumo",
    """{AplicacionInsumo|
    idAplicacion : int\l
    fechaAplicacion : Date\l
    cantidadUtilizada : double\l|
    registrarAplicacion()\l
    calcularTotalAplicado()\l
    obtenerAplicaciones()\l
    }"""
)

uml.node(
    "InsumoAgricola",
    """{InsumoAgricola|
    codigo : String\l
    nombre : String\l
    categoria : String\l
    unidadMedida : String\l
    stockDisponible : double\l|
    registrarInsumo()\l
    actualizarStock()\l
    obtenerInsumo()\l
    }"""
)


# =========================================================
# HERENCIA
# =========================================================

uml.node(
    "Semilla",
    """{Semilla|
    variedad : String\l
    poderGerminativo : double\l|
    calcularGerminacion()\l
    }"""
)

uml.node(
    "Fertilizante",
    """{Fertilizante|
    composicion : String\l
    tipoAplicacion : String\l|
    recomendarDosis()\l
    }"""
)

uml.node(
    "Pesticida",
    """{Pesticida|
    ingredienteActivo : String\l
    nivelToxicidad : String\l|
    verificarToxicidad()\l
    }"""
)

# Herencia
uml.edge("Semilla", "InsumoAgricola", arrowhead="empty")
uml.edge("Fertilizante", "InsumoAgricola", arrowhead="empty")
uml.edge("Pesticida", "InsumoAgricola", arrowhead="empty")


# =========================================================
# RELACIONES
# =========================================================

uml.edge("CooperativaAgricola", "Finca", label="administra 1..*")
uml.edge("Finca", "UbicacionGPS", label="posee 1")
uml.edge("Finca", "LoteCultivo", label="contiene 1..*")
uml.edge("LoteCultivo", "Cosecha", label="genera 0..*")
uml.edge("LoteCultivo", "AplicacionInsumo", label="registra 0..*")
uml.edge("Agricultor", "Cosecha", label="responsable de")
uml.edge("AplicacionInsumo", "InsumoAgricola", label="utiliza")


# =========================================================
# MODULO USUARIOS
# =========================================================

uml.node(
    "Usuario",
    """{Usuario|
    idUsuario : int\l
    nombreUsuario : String\l
    contrasena : String\l
    estado : String\l|
    iniciarSesion()\l
    cerrarSesion()\l
    cambiarContrasena()\l
    }"""
)

uml.node(
    "Rol",
    """{Rol|
    idRol : int\l
    nombreRol : String\l
    descripcion : String\l|
    asignarPermisos()\l
    obtenerRol()\l
    }"""
)

uml.edge("Usuario", "Rol", label="1..*")


# =========================================================
# MODULO REPORTES
# =========================================================

uml.node(
    "ReporteProduccion",
    """{ReporteProduccion|
    idReporte : int\l
    fechaInicio : Date\l
    fechaFin : Date\l
    tipoReporte : String\l|
    generarReporte()\l
    exportarPDF()\l
    exportarExcel()\l
    }"""
)

uml.node(
    "ReporteInsumos",
    """{ReporteInsumos|
    idReporte : int\l
    fechaInicio : Date\l
    fechaFin : Date\l
    tipoReporte : String\l|
    generarReporte()\l
    exportarPDF()\l
    exportarExcel()\l
    }"""
)


# =========================================================
# MODULO MONITOREO
# =========================================================

uml.node(
    "Sensor",
    """{Sensor|
    idSensor : int\l
    tipo : String\l
    ubicacion : String\l
    estado : String\l|
    registrarSensor()\l
    obtenerLecturas()\l
    }"""
)

uml.node(
    "MonitoreoClimatico",
    """{MonitoreoClimatico|
    temperatura : double\l
    humedad : double\l
    phSuelo : double\l|
    registrarDato()\l
    obtenerDatos()\l
    }"""
)

uml.node(
    "Alerta",
    """{Alerta|
    idAlerta : int\l
    tipo : String\l
    mensaje : String\l
    estado : String\l|
    generarAlerta()\l
    marcarComoLeida()\l
    }"""
)

uml.edge("Sensor", "MonitoreoClimatico")
uml.edge("MonitoreoClimatico", "Alerta")


# =========================================================
# MODULO INVENTARIO
# =========================================================

uml.node(
    "Inventario",
    """{Inventario|
    idInventario : int\l
    fecha : Date\l
    tipoMovimiento : String\l
    cantidad : double\l|
    registrarMovimiento()\l
    consultarStock()\l
    }"""
)

uml.node(
    "Proveedor",
    """{Proveedor|
    idProveedor : int\l
    nombre : String\l
    telefono : String\l
    direccion : String\l|
    registrarProveedor()\l
    obtenerProveedor()\l
    }"""
)

uml.node(
    "MovimientoInventario",
    """{MovimientoInventario|
    idMovimiento : int\l
    fecha : Date\l
    tipo : String\l
    cantidad : double\l|
    registrarMovimiento()\l
    obtenerMovimientos()\l
    }"""
)

uml.edge("Proveedor", "MovimientoInventario")
uml.edge("Inventario", "MovimientoInventario")


# =========================================================
# MODULO PRODUCCION
# =========================================================

uml.node(
    "PlanSiembra",
    """{PlanSiembra|
    idPlan : int\l
    fechaInicio : Date\l
    fechaFin : Date\l
    cultivo : String\l|
    registrarPlan()\l
    actualizarPlan()\l
    }"""
)

uml.node(
    "SeguimientoCultivo",
    """{SeguimientoCultivo|
    idSeguimiento : int\l
    fecha : Date\l
    actividad : String\l
    observacion : String\l|
    registrarSeguimiento()\l
    obtenerSeguimientos()\l
    }"""
)

uml.node(
    "RendimientoCultivo",
    """{RendimientoCultivo|
    idRendimiento : int\l
    lote : String\l
    rendimiento : double\l
    fecha : Date\l|
    calcularRendimiento()\l
    obtenerRendimiento()\l
    }"""
)

uml.edge("PlanSiembra", "SeguimientoCultivo")
uml.edge("SeguimientoCultivo", "RendimientoCultivo")


# =========================================================
# GENERAR IMAGEN
# =========================================================

uml.render("diagrama_uml_cultivos", view=True)

print("Diagrama UML generado correctamente")