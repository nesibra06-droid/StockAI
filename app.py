import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="StockAI", page_icon="📦")

if "inventario" not in st.session_state:
    st.session_state.inventario = {}
if "historial" not in st.session_state:
    st.session_state.historial = []
if "config" not in st.session_state:
    st.session_state.config = {"empresa": "Mi Empresa", "logo": None}

def cargar_datos(archivo, default):
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            return json.load(f)
    return default

def guardar_datos(archivo, datos):
    with open(archivo, "w") as f:
        json.dump(datos, f, ensure_ascii=False)

st.session_state.inventario = cargar_datos("inventario.json", {})
st.session_state.historial = cargar_datos("historial.json", [])
st.session_state.config = cargar_datos("config.json", {"empresa": "Mi Empresa"})

st.title(f"📦 {st.session_state.config.get('empresa', 'StockAI')}")
st.write("Control de inventario inteligente")

tabs = st.tabs(["📥 Entrada", "📤 Salida", "📦 Inventario", "📋 Historial", "🚛 Logística", "⚙️ Configuración"])

with tabs[0]:
    st.subheader("Registrar entrada de material")
    nombre = st.text_input("Nombre del material")
    col1, col2 = st.columns(2)
    with col1:
        cantidad = st.number_input("Cantidad", min_value=0.0, step=1.0)
        unidad = st.selectbox("Unidad", ["sacos", "toneladas", "litros", "piezas", "bultos"])
        peso_saco = st.number_input("Peso por saco (kg)", min_value=0.0, step=0.5)
    with col2:
        proveedor = st.text_input("Proveedor")
        remision = st.text_input("Número de remisión")
        turno = st.selectbox("Turno", ["Matutino", "Vespertino", "Nocturno"])
    responsable = st.text_input("Responsable de recepción")
    
    st.write("**Campos adicionales (opcional)**")
    col3, col4 = st.columns(2)
    with col3:
        color = st.text_input("Color")
        malla = st.text_input("Malla")
    with col4:
        charola = st.text_input("Charola")
        humedad = st.text_input("Humedad (%)")
    
    notas = st.text_area("Notas (ej: sacos húmedos, devoluciones)")

    if st.button("✅ Registrar entrada"):
        if nombre and responsable:
            if nombre in st.session_state.inventario:
                st.session_state.inventario[nombre]["cantidad"] += cantidad
            else:
                st.session_state.inventario[nombre] = {"cantidad": cantidad, "unidad": unidad}
            guardar_datos("inventario.json", st.session_state.inventario)
            st.session_state.historial.append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tipo": "entrada",
                "material": nombre,
                "cantidad": cantidad,
                "unidad": unidad,
                "peso_saco": peso_saco,
                "proveedor": proveedor,
                "remision": remision,
                "turno": turno,
                "responsable": responsable,
                "color": color,
                "malla": malla,
                "charola": charola,
                "humedad": humedad,
                "notas": notas
            })
            guardar_datos("historial.json", st.session_state.historial)
            st.success(f"✅ Entrada registrada: {cantidad} {unidad} de {nombre}.")
        else:
            st.error("Completa nombre del material y responsable.")

with tabs[1]:
    st.subheader("Registrar salida de material")
    if st.session_state.inventario:
        material_salida = st.selectbox("Material", list(st.session_state.inventario.keys()))
        col1, col2 = st.columns(2)
        with col1:
            cantidad_salida = st.number_input("Cantidad", min_value=0.0, step=1.0, key="salida")
            cliente = st.text_input("Nombre del cliente")
            turno_salida = st.selectbox("Turno", ["Matutino", "Vespertino", "Nocturno"], key="turno_salida")
        with col2:
            carro = st.text_input("Número o nombre del carro")
            tipo_flete = st.selectbox("Tipo de flete", ["Propio", "Fletero"])
            hora_carga = st.text_input("Hora de carga (ej: 08:30)")
        
        quien_cargo = st.text_input("¿Quién cargó?")
        responsable_salida = st.text_input("Responsable de salida")
        
        st.write("**Verificación**")
        col5, col6 = st.columns(2)
        with col5:
            firma_chofer = st.text_input("Firma / nombre del chofer")
        with col6:
            firma_encargado = st.text_input("Firma / nombre del encargado")
        
        notas_salida = st.text_area("Notas", key="notas_salida")

        if st.button("✅ Registrar salida"):
            if cantidad_salida <= st.session_state.inventario[material_salida]["cantidad"]:
                st.session_state.inventario[material_salida]["cantidad"] -= cantidad_salida
                guardar_datos("inventario.json", st.session_state.inventario)
                st.session_state.historial.append({
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tipo": "salida",
                    "material": material_salida,
                    "cantidad": cantidad_salida,
                    "cliente": cliente,
                    "turno": turno_salida,
                    "carro": carro,
                    "tipo_flete": tipo_flete,
                    "hora_carga": hora_carga,
                    "quien_cargo": quien_cargo,
                    "responsable": responsable_salida,
                    "firma_chofer": firma_chofer,
                    "firma_encargado": firma_encargado,
                    "notas": notas_salida
                })
                guardar_datos("historial.json", st.session_state.historial)
                st.success(f"✅ Salida registrada: {cantidad_salida} de {material_salida} para {cliente}.")
            else:
                st.error("No hay suficiente material en inventario.")
    else:
        st.info("No hay materiales en inventario.")

with tabs[2]:
    st.subheader("Inventario actual")
    if st.session_state.inventario:
        for material, datos in st.session_state.inventario.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{material}**")
            with col2:
                st.write(f"{datos['cantidad']} {datos['unidad']}")
            st.divider()
    else:
        st.info("No hay materiales registrados.")

with tabs[3]:
    st.subheader("Historial de movimientos")
    if st.session_state.historial:
        for mov in reversed(st.session_state.historial):
            tipo_emoji = "🟢" if mov["tipo"] == "entrada" else "🔴"
            with st.expander(f"{tipo_emoji} {mov['fecha']} — {mov['tipo'].upper()} — {mov['material']}: {mov['cantidad']}"):
                if mov["tipo"] == "entrada":
                    st.write(f"**Proveedor:** {mov.get('proveedor', '-')}")
                    st.write(f"**Remisión:** {mov.get('remision', '-')}")
                    st.write(f"**Turno:** {mov.get('turno', '-')}")
                    st.write(f"**Responsable:** {mov.get('responsable', '-')}")
                    st.write(f"**Peso por saco:** {mov.get('peso_saco', '-')} kg")
                    if mov.get('color'): st.write(f"**Color:** {mov['color']}")
                    if mov.get('malla'): st.write(f"**Malla:** {mov['malla']}")
                    if mov.get('charola'): st.write(f"**Charola:** {mov['charola']}")
                    if mov.get('humedad'): st.write(f"**Humedad:** {mov['humedad']}%")
                    if mov.get('notas'): st.write(f"**Notas:** {mov['notas']}")
                else:
                    st.write(f"**Cliente:** {mov.get('cliente', '-')}")
                    st.write(f"**Carro:** {mov.get('carro', '-')} ({mov.get('tipo_flete', '-')})")
                    st.write(f"**Hora de carga:** {mov.get('hora_carga', '-')}")
                    st.write(f"**Quién cargó:** {mov.get('quien_cargo', '-')}")
                    st.write(f"**Turno:** {mov.get('turno', '-')}")
                    st.write(f"**Responsable:** {mov.get('responsable', '-')}")
                    st.write(f"**Firma chofer:** {mov.get('firma_chofer', '-')}")
                    st.write(f"**Firma encargado:** {mov.get('firma_encargado', '-')}")
                    if mov.get('notas'): st.write(f"**Notas:** {mov['notas']}")
    else:
        st.info("Sin movimientos registrados.")

with tabs[4]:
    st.subheader("🚛 Registro de logística y diésel")
    col1, col2 = st.columns(2)
    with col1:
        chofer = st.text_input("Chofer")
        carro_log = st.text_input("Carro")
        cliente_log = st.text_input("Cliente destino")
    with col2:
        litros = st.number_input("Litros de diésel", min_value=0.0, step=1.0)
        tiempo_viaje = st.text_input("Tiempo estimado de viaje (ej: 2 horas)")
        km = st.number_input("Kilómetros aproximados", min_value=0.0, step=1.0)
    
    notas_log = st.text_area("Notas del viaje")

    if "logistica" not in st.session_state:
        st.session_state.logistica = cargar_datos("logistica.json", [])

    if st.button("✅ Registrar viaje"):
        if chofer and carro_log:
            st.session_state.logistica.append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "chofer": chofer,
                "carro": carro_log,
                "cliente": cliente_log,
                "litros": litros,
                "tiempo_viaje": tiempo_viaje,
                "km": km,
                "notas": notas_log
            })
            guardar_datos("logistica.json", st.session_state.logistica)
            st.success("✅ Viaje registrado.")

    if st.session_state.logistica:
        st.subheader("Viajes registrados")
        for viaje in reversed(st.session_state.logistica):
            with st.expander(f"🚛 {viaje['fecha']} — {viaje['chofer']} — {viaje['cliente']}"):
                st.write(f"**Carro:** {viaje['carro']}")
                st.write(f"**Litros diésel:** {viaje['litros']}")
                st.write(f"**Tiempo estimado:** {viaje['tiempo_viaje']}")
                st.write(f"**Kilómetros:** {viaje['km']}")
                if viaje.get('notas'): st.write(f"**Notas:** {viaje['notas']}")

with tabs[5]:
    st.subheader("⚙️ Configuración de la empresa")
    empresa_nombre = st.text_input("Nombre de la empresa", value=st.session_state.config.get("empresa", ""))
    
    if st.button("💾 Guardar configuración"):
        st.session_state.config["empresa"] = empresa_nombre
        guardar_datos("config.json", st.session_state.config)
        st.success("✅ Configuración guardada. Recarga la página para ver el nombre actualizado.")
