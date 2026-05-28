import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="StockAI", page_icon="📦")
st.title("📦 StockAI")
st.write("Control de inventario inteligente")

def cargar_datos(archivo):
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            return json.load(f)
    return {}

def guardar_datos(archivo, datos):
    with open(archivo, "w") as f:
        json.dump(datos, f)

if "inventario" not in st.session_state:
    st.session_state.inventario = cargar_datos("inventario.json")

if "historial" not in st.session_state:
    st.session_state.historial = cargar_datos("historial.json") if os.path.exists("historial.json") else []

st.subheader("Registrar entrada")
nombre = st.text_input("Nombre del material")
cantidad = st.number_input("Cantidad", min_value=0.0, step=1.0)
unidad = st.selectbox("Unidad", ["sacos", "toneladas", "litros", "piezas"])
peso_saco = st.number_input("Peso por saco (kg)", min_value=0.0, step=0.5)
proveedor = st.text_input("Proveedor")
remision = st.text_input("Número de remisión")
turno = st.selectbox("Turno", ["Matutino", "Vespertino", "Nocturno"])
responsable = st.text_input("Responsable")
notas = st.text_area("Notas (ej: sacos húmedos, devoluciones)")

if st.button("Registrar entrada"):
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
            "notas": notas
        })
        guardar_datos("historial.json", st.session_state.historial)
        st.success(f"Entrada registrada: {cantidad} {unidad} de {nombre}.")

st.subheader("Inventario actual")
if st.session_state.inventario:
    for material, datos in st.session_state.inventario.items():
        st.write(f"**{material}:** {datos['cantidad']} {datos['unidad']}")
else:
    st.info("No hay materiales registrados.")

st.subheader("Registrar salida")
if st.session_state.inventario:
    material_salida = st.selectbox("Material", list(st.session_state.inventario.keys()))
    cantidad_salida = st.number_input("Cantidad a descontar", min_value=0.0, step=1.0, key="salida")
    cliente = st.text_input("Nombre del cliente")
    turno_salida = st.selectbox("Turno", ["Matutino", "Vespertino", "Nocturno"], key="turno_salida")
    responsable_salida = st.text_input("Responsable", key="resp_salida")
    notas_salida = st.text_area("Notas", key="notas_salida")

    if st.button("Registrar salida"):
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
                "responsable": responsable_salida,
                "notas": notas_salida
            })
            guardar_datos("historial.json", st.session_state.historial)
            st.success(f"Salida registrada: {cantidad_salida} de {material_salida} para {cliente}.")
        else:
            st.error("No hay suficiente material en inventario.")

st.subheader("Historial de movimientos")
if st.session_state.historial:
    for mov in reversed(st.session_state.historial):
        tipo_emoji = "🟢" if mov["tipo"] == "entrada" else "🔴"
        detalle = f"{tipo_emoji} **{mov['fecha']}** — {mov['tipo'].upper()} — {mov['material']}: {mov['cantidad']}"
        if mov["tipo"] == "entrada":
            detalle += f" — Proveedor: {mov.get('proveedor', '')} — Remisión: {mov.get('remision', '')} — Turno: {mov.get('turno', '')} — {mov.get('responsable', '')}"
            if mov.get('notas'):
                detalle += f" — 📝 {mov['notas']}"
        else:
            detalle += f" — Cliente: {mov.get('cliente', '')} — Turno: {mov.get('turno', '')} — {mov.get('responsable', '')}"
            if mov.get('notas'):
                detalle += f" — 📝 {mov['notas']}"
        st.write(detalle)
else:
    st.info("Sin movimientos registrados.")
