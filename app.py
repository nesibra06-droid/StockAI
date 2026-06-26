SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="StockAI", page_icon="📦")

# ─── CARGAR DATOS ─────────────────────────────────────────────────────────────
def cargar_inventario():
    res = supabase.table("inventario").select("*").execute()
    return {r["material"]: {"cantidad": r["cantidad"], "unidad": r["unidad"], "id": r["id"]} for r in res.data}

def cargar_historial():
    res = supabase.table("historial").select("*").order("id", desc=True).execute()
    return res.data

def cargar_logistica():
    res = supabase.table("logistica").select("*").order("id", desc=True).execute()
    return res.data

def cargar_config():
    res = supabase.table("config").select("*").execute()
    if res.data:
        return res.data[0]
    return {"empresa": "StockAI"}

# ─── GUARDAR DATOS ────────────────────────────────────────────────────────────
def guardar_entrada_inventario(nombre, cantidad, unidad):
    inv = cargar_inventario()
    if nombre in inv:
        nueva = inv[nombre]["cantidad"] + cantidad
        supabase.table("inventario").update({"cantidad": nueva}).eq("id", inv[nombre]["id"]).execute()
    else:
        supabase.table("inventario").insert({"material": nombre, "cantidad": cantidad, "unidad": unidad}).execute()

def guardar_salida_inventario(nombre, cantidad):
    inv = cargar_inventario()
    nueva = inv[nombre]["cantidad"] - cantidad
    supabase.table("inventario").update({"cantidad": nueva}).eq("id", inv[nombre]["id"]).execute()

def guardar_historial(registro):
    supabase.table("historial").insert(registro).execute()

def guardar_logistica(registro):
    supabase.table("logistica").insert(registro).execute()

def guardar_config(empresa):
    res = supabase.table("config").select("*").execute()
    if res.data:
        supabase.table("config").update({"empresa": empresa}).eq("id", res.data[0]["id"]).execute()
    else:
        supabase.table("config").insert({"empresa": empresa}).execute()

# ─── INIT ─────────────────────────────────────────────────────────────────────
config = cargar_config()
st.title(f"📦 {config.get('empresa', 'StockAI')}")
st.write("Control de inventario inteligente")

tabs = st.tabs(["📥 Entrada", "📤 Salida", "📦 Inventario", "📋 Historial", "🚛 Logística", "⚙️ Configuración"])

# ─── TAB 0: ENTRADA ───────────────────────────────────────────────────────────
with tabs[0]:
    col_top1, col_top2 = st.columns(2)
    with col_top1:
        folio = st.text_input("Folio", key="folio_entrada")
    with col_top2:
        fecha_manual = st.date_input("Fecha", key="fecha_entrada")

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
            guardar_entrada_inventario(nombre, cantidad, unidad)
            guardar_historial({
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
                "notas": notas,
                "folio": folio,
                "fecha_manual": str(fecha_manual),
            })
            st.success(f"✅ Entrada registrada: {cantidad} {unidad} de {nombre}.")
        else:
            st.error("Completa nombre del material y responsable.")

# ─── TAB 1: SALIDA ────────────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Registrar salida de material")
    inventario = cargar_inventario()
    if inventario:
        material_salida = st.selectbox("Material", list(inventario.keys()))
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
            if cantidad_salida <= inventario[material_salida]["cantidad"]:
                guardar_salida_inventario(material_salida, cantidad_salida)
                guardar_historial({
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
                    "notas": notas_salida,
                })
                st.success(f"✅ Salida registrada: {cantidad_salida} de {material_salida} para {cliente}.")
            else:
                st.error("No hay suficiente material en inventario.")
    else:
        st.info("No hay materiales en inventario.")

# ─── TAB 2: INVENTARIO ────────────────────────────────────────────────────────
with tabs[2]:
    st.subheader("Inventario actual")
    inventario = cargar_inventario()
    if inventario:
        for material, datos in inventario.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{material}**")
            with col2:
                st.write(f"{datos['cantidad']} {datos['unidad']}")
            st.divider()
    else:
        st.info("No hay materiales registrados.")

# ─── TAB 3: HISTORIAL ─────────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("Historial de movimientos")
    historial = cargar_historial()
    if historial:
        for mov in historial:
            tipo_emoji = "🟢" if mov["tipo"] == "entrada" else "🔴"
            with st.expander(f"{tipo_emoji} {mov['fecha']} — Folio: {mov.get('folio', '-')} — {mov['tipo'].upper()} — {mov['material']}: {mov['cantidad']}"):
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

# ─── TAB 4: LOGÍSTICA ─────────────────────────────────────────────────────────
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

    if st.button("✅ Registrar viaje"):
        if chofer and carro_log:
            guardar_logistica({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "chofer": chofer,
                "carro": carro_log,
                "cliente": cliente_log,
                "litros": litros,
                "tiempo_viaje": tiempo_viaje,
                "km": km,
                "notas": notas_log,
            })
            st.success("✅ Viaje registrado.")

    logistica = cargar_logistica()
    if logistica:
        st.subheader("Viajes registrados")
        for viaje in logistica:
            with st.expander(f"🚛 {viaje['fecha']} — {viaje['chofer']} — {viaje['cliente']}"):
                st.write(f"**Carro:** {viaje['carro']}")
                st.write(f"**Litros diésel:** {viaje['litros']}")
                st.write(f"**Tiempo estimado:** {viaje['tiempo_viaje']}")
                st.write(f"**Kilómetros:** {viaje['km']}")
                if viaje.get('notas'): st.write(f"**Notas:** {viaje['notas']}")

# ─── TAB 5: CONFIGURACIÓN ─────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("⚙️ Configuración de la empresa")
    config = cargar_config()
    empresa_nombre = st.text_input("Nombre de la empresa", value=config.get("empresa", ""))

    if st.button("💾 Guardar configuración"):
        guardar_config(empresa_nombre)
        st.success("✅ Configuración guardada. Recarga la página para ver el nombre actualizado.")
