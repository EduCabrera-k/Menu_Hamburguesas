from flask import Flask, render_template, request, jsonify
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)

# --- CONFIGURACIÓN DE MONGODB ATLAS ---

MONGO_URI = "mongodb+srv://al070801_db_user:m5Rb0Msee6KB74X6@cluster0.yozw2vu.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['rendon_burger_db']

pedidos_col = db['pedidos_activos']
historial_col = db['historial_ventas']
inventario_col = db['inventario_stock']


menu_items = [
    {"id": 1, "nombre": "Tradicional", "precio": 75, "descripcion": "Carne de la casa, jamón, queso, tocino y vegetales.", "categoria": "hamburguesas"},
    {"id": 2, "nombre": "Tradicional Doble", "precio": 120, "descripcion": "Doble carne, doble jamón, queso y tocino.", "categoria": "hamburguesas"},
    {"id": 3, "nombre": "Arrachera", "precio": 100, "descripcion": "Carne de arrachera, jamón, queso, tocino y vegetales.", "categoria": "hamburguesas"},
    {"id": 4, "nombre": "Crunchy", "precio": 95, "descripcion": "Pollo tender, jamón, queso, tocino y vegetales.", "categoria": "hamburguesas"},
    {"id": 5, "nombre": "Crunchy Doble", "precio": 140, "descripcion": "Doble pollo tender, jamón, queso y tocino.", "categoria": "hamburguesas"},
    {"id": 6, "nombre": "Crunchy BBQ", "precio": 105, "descripcion": "Pollo tender con aderezo BBQ.", "categoria": "hamburguesas"},
    {"id": 7, "nombre": "Crunchy Búfalo", "precio": 105, "descripcion": "Pollo tender con aderezo búfalo.", "categoria": "hamburguesas"},
    {"id": 8, "nombre": "Ranchera", "precio": 140, "descripcion": "Carne, jamón, queso, tocino, chorizo y champiñones.", "categoria": "hamburguesas"},
    {"id": 9, "nombre": "Suprema", "precio": 130, "descripcion": "Carne, jamón, queso, tocino, champiñones y queso fundido.", "categoria": "hamburguesas"},
    {"id": 10, "nombre": "Magnum", "precio": 160, "descripcion": "Carne, doble jamón, queso, tocino, arrachera y chorizo.", "categoria": "hamburguesas"},
    {"id": 11, "nombre": "Orden de Papas", "precio": 50, "descripcion": "Papas a la francesa con crema de ajo.", "categoria": "hamburguesas"},
    {"id": 12, "nombre": "Refresco Medio", "precio": 20, "descripcion": "Refresco en vaso.", "categoria": "bebidas"},
    {"id": 13, "nombre": "Refresco Litro", "precio": 30, "descripcion": "Refresco en botella de 1L.", "categoria": "bebidas"},
    {"id": 14, "nombre": "Jamaica", "precio": 20, "descripcion": "Agua de jamaica natural.", "categoria": "bebidas"},
    {"id": 15, "nombre": "Té Reca", "precio": 20, "descripcion": "Té helado de la casa.", "categoria": "bebidas"},
    {"id": 16, "nombre": "Horchata", "precio": 20, "descripcion": "Agua de horchata artesanal.", "categoria": "bebidas"},
    {"id": 17, "nombre": "Limonada", "precio": 20, "descripcion": "Limonada natural.", "categoria": "bebidas"},
    {"id": 18, "nombre": "Naranjada", "precio": 25, "descripcion": "Naranjada natural.", "categoria": "bebidas"},
    {"id": 19, "nombre": "Tranca de Pierna", "precio": 45, "descripcion": "Tranca de pierna estilo casero.", "categoria": "desayunos"},
    {"id": 20, "nombre": "Orden 3 Hot Cakes", "precio": 45, "descripcion": "Hot cakes con miel y mantequilla.", "categoria": "desayunos"},
    {"id": 21, "nombre": "Hot Dog", "precio": 20, "descripcion": "Hot dog clásico con aderezos.", "categoria": "desayunos"},
    {"id": 22, "nombre": "Tranca de Pollo", "precio": 45, "descripcion": "Tranca de pollo deshebrado.", "categoria": "desayunos"},
    {"id": 23, "nombre": "Trancas de Tender", "precio": 45, "descripcion": "Trancas de pollo tender crujiente.", "categoria": "desayunos"},
    {"id": 24, "nombre": "Orden de 3 Burritas", "precio": 30, "descripcion": "Burritas de guisado variado.", "categoria": "desayunos"},
    {"id": 25, "nombre": "Orden de 4 Flautas", "precio": 45, "descripcion": "Flautas doradas de pollo.", "categoria": "desayunos"},
    {"id": 26, "nombre": "Tostadas de Pollo", "precio": 20, "descripcion": "Tostada individual de pollo.", "categoria": "desayunos"}
]

@app.route('/')
def index():
    inventario = {item['item_id']: item['disponible'] for item in inventario_col.find()}
    menu_por_categoria = {}
    for item in menu_items:
        item['disponible'] = inventario.get(str(item['id']), True)
        cat = item.get('categoria', 'otros')
        if cat not in menu_por_categoria: menu_por_categoria[cat] = []
        menu_por_categoria[cat].append(item)
    return render_template('index.html', menu_por_categoria=menu_por_categoria)

@app.route('/cocina')
def vista_cocina():
    # IMPORTANTE: Aquí actualizamos el estado de disponibilidad desde MongoDB
    inventario = {item['item_id']: item['disponible'] for item in inventario_col.find()}
    for item in menu_items:
        item['disponible'] = inventario.get(str(item['id']), True)
    
    pedidos = list(pedidos_col.find().sort("hora", 1))
    for p in pedidos: p.pop('_id', None)
    return render_template('cocina.html', pedidos=pedidos, menu=menu_items)

@app.route('/api/stock')
def api_stock():
    inventario = {item['item_id']: item['disponible'] for item in inventario_col.find()}
    return jsonify(inventario)

@app.route('/ordenar', methods=['POST'])
def ordenar():
    data = request.json
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    total_hoy = pedidos_col.count_documents({"fecha": fecha_hoy}) + historial_col.count_documents({"fecha": fecha_hoy})
    nuevo_id = total_hoy + 1
    
    nuevo_pedido = {
        "id": nuevo_id,
        "cliente": data['cliente']['nombre'],
        "telefono": data['cliente']['telefono'],
        "entrega": data['cliente']['tipo'],
        "direccion": data['cliente'].get('direccion', 'N/A'),
        "items": data['carrito'],
        "hora": datetime.now().strftime("%H:%M:%S"),
        "fecha": fecha_hoy,
        "total": sum(i['precio'] * i['cantidad'] for i in data['carrito'])
    }
    pedidos_col.insert_one(nuevo_pedido)
    return jsonify({"status": "success", "id": nuevo_id})

@app.route('/estado/<int:pedido_id>')
def consultar_estado(pedido_id):
    pedido = pedidos_col.find_one({"id": pedido_id})
    if pedido:
        return jsonify({"status": "preparando", "detalle": "Tu pedido está en el asador 🔥"})
    
    pedido_f = historial_col.find_one({"id": pedido_id})
    if pedido_f:
        msg = "¡Tu orden está en camino! 🛵" if pedido_f.get('entrega') == 'Domicilio' else "¡Tu orden está lista para recoger! 🍔"
        return jsonify({"status": "listo", "detalle": msg})
    return jsonify({"status": "no_encontrado", "detalle": "Buscando..."})

@app.route('/toggle_disponibilidad', methods=['POST'])
def toggle_disponibilidad():
    item_id = str(request.json.get('id'))
    doc = inventario_col.find_one({"item_id": item_id})
    # Si no existe el documento, por defecto estaba disponible (True), así que ahora es False
    nuevo_estado = not doc['disponible'] if doc else False
    inventario_col.update_one({"item_id": item_id}, {"$set": {"disponible": nuevo_estado}}, upsert=True)
    return jsonify({"status": "success"})

@app.route('/marcar_listo', methods=['POST'])
def marcar_listo():
    pedido_id = int(request.json.get('id'))
    pedido = pedidos_col.find_one({"id": pedido_id})
    if pedido:
        pedido['fecha_finalizado'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        historial_col.insert_one(pedido)
        pedidos_col.delete_one({"id": pedido_id})
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 404

@app.route('/reporte')
def ver_reporte():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    ventas = list(historial_col.find({"fecha": fecha_hoy}))
    total_dinero = sum(v['total'] for v in ventas)
    return render_template('reporte.html', ventas=ventas, total=total_dinero)

if __name__ == '__main__':
    app.run(debug=True, port=5000)