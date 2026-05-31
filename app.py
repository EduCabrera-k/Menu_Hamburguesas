from flask import Flask, render_template, request, jsonify
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import time
import os

load_dotenv()

app = Flask(__name__)

# --- CONFIGURACIÓN DE MONGODB ATLAS ---
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI no está definida. Agrega la variable en tu archivo .env")

client = MongoClient(MONGO_URI)
db = client['rendon_burger_db']

pedidos_col    = db['pedidos_activos']
historial_col  = db['historial_ventas']
inventario_col = db['inventario_stock']

menu_items = [
    {"id": 1, "nombre": "Tradicional", "precio": 75, "descripcion": "Carne de la casa, jamón, queso, tocino y vegetales.", "categoria": "hamburguesas" , "imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZQUZieQ9R-6Q1E-2hw1dNgQn8D-o76ferYQ&s"},
    {"id": 2, "nombre": "Tradicional Doble", "precio": 120, "descripcion": "Doble carne, doble jamón, queso y tocino.", "categoria": "hamburguesas" ,"imagen": "Tradicional Doble.jpg"},
    {"id": 3, "nombre": "Arrachera", "precio": 100, "descripcion": "Carne de arrachera, jamón, queso, tocino y vegetales.", "categoria": "hamburguesas" , "imagen": "https://foodservice.grupobachoco.com/images/productos/8240_HAMBUR-ARRACHERA_PLAT.jpg"},
    {"id": 4, "nombre": "Crunchy", "precio": 95, "descripcion": "Pollo tender, jamón, queso, tocino y vegetales.", "categoria": "hamburguesas" ,"imagen": "Crunchy.jpg"},
    {"id": 5, "nombre": "Crunchy Doble", "precio": 140, "descripcion": "Doble pollo tender, jamón, queso y tocino.", "categoria": "hamburguesas" , "imagen": "https://tofuu.getjusto.com/orioneat-local/resized2/xGK9Pho6WBXcK7pvD-2400-x.webp"},
    {"id": 6, "nombre": "Crunchy BBQ", "precio": 105, "descripcion": "Pollo tender con aderezo BBQ.", "categoria": "hamburguesas" , "imagen": "https://bichiburgers.com/wp-content/uploads/2025/03/Bichi-BBQ-Crunch.webp"},
    {"id": 7, "nombre": "Crunchy Búfalo", "precio": 105, "descripcion": "Pollo tender con aderezo búfalo.", "categoria": "hamburguesas" , "imagen": "Crunchy Búfalo.png"},
    {"id": 8, "nombre": "Ranchera", "precio": 140, "descripcion": "Carne, jamón, queso, tocino, chorizo y champiñones.", "categoria": "hamburguesas" ,"imagen": "Ranchera.jpg"},
    {"id": 9, "nombre": "Suprema", "precio": 130, "descripcion": "Carne, jamón, queso, tocino, champiñones y queso fundido.", "categoria": "hamburguesas" , "imagen": "https://bambuleburger.com/wp-content/uploads/2024/05/hamburguesa-doble-carne-1-300x300.jpg"},
    {"id": 10, "nombre": "Magnum", "precio": 160, "descripcion": "Carne, doble jamón, queso, tocino, arrachera y chorizo.", "categoria": "hamburguesas" ,"imagen": "Magnum.jpg"},
    {"id": 11, "nombre": "Orden de Papas", "precio": 50, "descripcion": "Papas a la francesa con crema de ajo.", "categoria": "hamburguesas", "imagen": "https://tofuu.getjusto.com/orioneat-local/resized2/QvQCqPgWNwSkSoSyX-2400-x.webp"},
    {"id": 12, "nombre": "Coca Cola 600ml", "precio": 20, "descripcion": "Refresco de 600ml.", "categoria": "bebidas" ,"imagen": "https://lagranbodega.vteximg.com.br/arquivos/ids/306261-600-600/75007614.jpg?v=638998835775530000"},
    {"id": 13, "nombre": "Coca Cola 1 Litro", "precio": 30, "descripcion": "Refresco en botella de 1L.", "categoria": "bebidas" ,"imagen": "https://i.pinimg.com/originals/ae/05/a7/ae05a76f345930e327f077abac734508.png"},
    {"id": 14, "nombre": "Jamaica Avia", "precio": 20, "descripcion": "Jamaica marca Avia.", "categoria": "bebidas" , "imagen": "https://images.rappi.com.mx/products/1759437953312_1759437949408_1759437946160.jpg?d=900x750&e=webp&q=30"},
    {"id": 15, "nombre": "Té Reca", "precio": 20, "descripcion": "Té marca Reca.", "categoria": "bebidas" , "imagen": "https://i5.walmartimages.com/asr/7af222a4-ab70-4c87-8d5c-ada1f83a23f9.d37d185aefd6f90ae330c6bf2ec3c49d.jpeg?odnHeight=612&odnWidth=612&odnBg=FFFFFF"},
    {"id": 16, "nombre": "Horchata Avia", "precio": 20, "descripcion": "Horchata marca Avia.", "categoria": "bebidas" , "imagen": "https://i5.walmartimages.com.mx/mg/gm/3pp/asr/1421c4ab-7fa3-4cb3-958d-05befe82ad64.bf5841758fc371cc049df0502abbd924.jpeg?odnHeight=612&odnWidth=612&odnBg=FFFFFF"},
    {"id": 17, "nombre": "Limonada Avia", "precio": 20, "descripcion": "Limonada marca Avia.", "categoria": "bebidas" , "imagen":"https://i5.walmartimages.com.mx/mg/gm/3pp/asr/9b84ce80-73fd-4c7e-b8f4-fe49e63c64f7.3ceff7683313fa9ed50974d0d01aa77a.jpeg?odnHeight=612&odnWidth=612&odnBg=FFFFFF"},
    {"id": 18, "nombre": "Naranjada Avia", "precio": 25, "descripcion": "Naranjada marca Avia.", "categoria": "bebidas" , "imagen": "https://tb-static.uber.com/prod/image-proc/processed_images/e2feeba91f43cfb75a2be6dacb04ea6f/0e5313be7a8831b8ed60f8dab3c2df10.jpeg"},
    {"id": 19, "nombre": "Tranca de Pierna", "precio": 45, "descripcion": "Tranca de pierna estilo casero.", "categoria": "desayunos" , "imagen": "https://i0.wp.com/1.bp.blogspot.com/-HEAYFb_wKs8/Vds_gT-9brI/AAAAAAAAEXc/9ArK95h0n_A/s1600/Torta-de-pierna-Viva-La-Morena.jpg"},
    {"id": 20, "nombre": "Orden 3 Hot Cakes", "precio": 45, "descripcion": "Hot cakes con miel y mantequilla.", "categoria": "desayunos" , "imagen": "https://vips.com.mx/menu/img/platos/hotcakes_trads.jpg"},
    {"id": 21, "nombre": "Hot Dog", "precio": 20, "descripcion": "Hot dog clásico con aderezos.", "categoria": "desayunos" , "imagen": "Hotdog.png"},
    {"id": 22, "nombre": "Tranca de Pollo", "precio": 45, "descripcion": "Tranca de pollo deshebrado.", "categoria": "desayunos" , "imagen": "https://http2.mlstatic.com/D_NQ_NP_921907-MLM110004907939_042026-O.webp"},
    {"id": 23, "nombre": "Trancas de Tender", "precio": 45, "descripcion": "Trancas de pollo tender crujiente.", "categoria": "desayunos" , "imagen": "TortadeTender.png"},
    {"id": 24, "nombre": "Orden de 3 Burritas", "precio": 30, "descripcion": "Burritas de guisado variado.", "categoria": "desayunos", "imagen": "https://i.pinimg.com/1200x/37/b9/a3/37b9a38fdbc790723d4ad72bf2c3109f.jpg"},
    {"id": 25, "nombre": "Orden de 4 Flautas", "precio": 45, "descripcion": "Flautas doradas de pollo.", "categoria": "desayunos" , "imagen": "https://d2j9trpqxd6hrn.cloudfront.net/uploads/recipe/main_image/138/flautas_de_pollo_2.webp"},
    {"id": 26, "nombre": "Tostadas de Pollo", "precio": 20, "descripcion": "Tostada individual de pollo.", "categoria": "desayunos" , "imagen": "https://i.pinimg.com/1200x/ac/dc/8c/acdc8c176144847a0362eb0ab605e413.jpg"}
]


# IDs válidos del menú para validar el carrito
MENU_IDS_VALIDOS = {item['id'] for item in menu_items}


def _validar_pedido(data):
    """
    Valida la estructura del payload recibido en /ordenar.
    Retorna (True, None) si es válido o (False, mensaje_error) si no lo es.
    """
    if not isinstance(data, dict):
        return False, "Payload inválido."

    cliente = data.get('cliente')
    carrito = data.get('carrito')

    # --- Validar cliente ---
    if not isinstance(cliente, dict):
        return False, "Datos de cliente inválidos."

    nombre = (cliente.get('nombre') or '').strip()
    telefono = (cliente.get('telefono') or '').strip()
    tipo = cliente.get('tipo')
    metodo_pago = cliente.get('metodo_pago')

    if not nombre:
        return False, "El nombre del cliente es obligatorio."
    if len(nombre) > 100:
        return False, "El nombre del cliente es demasiado largo."
    if not telefono:
        return False, "El teléfono del cliente es obligatorio."
    if not telefono.replace('+', '').replace(' ', '').isdigit() or not (7 <= len(telefono) <= 15):
        return False, "El teléfono no tiene un formato válido."
    if tipo not in ('Sucursal', 'Domicilio'):
        return False, "Tipo de entrega inválido."
    if metodo_pago not in ('Efectivo', 'Tarjeta'):
        return False, "Método de pago inválido."
    if tipo == 'Domicilio' and not (cliente.get('direccion') or '').strip():
        return False, "La dirección es obligatoria para pedidos a domicilio."

    # --- Validar carrito ---
    if not isinstance(carrito, list) or len(carrito) == 0:
        return False, "El carrito está vacío."
    if len(carrito) > 50:
        return False, "El carrito excede el límite de artículos permitidos."

    for i, item in enumerate(carrito):
        if not isinstance(item, dict):
            return False, f"Item #{i+1} tiene formato inválido."

        item_id  = item.get('item_id')
        cantidad = item.get('cantidad')
        precio   = item.get('precio')
        nombre_item = item.get('nombre', '')

        if not isinstance(item_id, int) or item_id not in MENU_IDS_VALIDOS:
            return False, f"El producto con ID '{item_id}' no existe en el menú."
        if not isinstance(cantidad, int) or cantidad < 1 or cantidad > 99:
            return False, f"Cantidad inválida para '{nombre_item}'."
        if not isinstance(precio, (int, float)) or precio <= 0:
            return False, f"Precio inválido para '{nombre_item}'."

    return True, None


@app.route('/')
def index():
    inventario = {item['item_id']: item['disponible'] for item in inventario_col.find()}
    menu_por_categoria = {}
    for item in menu_items:
        item['disponible'] = inventario.get(str(item['id']), True)
        cat = item['categoria']
        if cat not in menu_por_categoria:
            menu_por_categoria[cat] = []
        menu_por_categoria[cat].append(item)
    return render_template('index.html', menu_por_categoria=menu_por_categoria)


@app.route('/cocina')
def vista_cocina():
    inventario = {item['item_id']: item['disponible'] for item in inventario_col.find()}
    for item in menu_items:
        item['disponible'] = inventario.get(str(item['id']), True)
    pedidos = list(pedidos_col.find().sort("hora", 1))
    for p in pedidos:
        p.pop('_id', None)
    return render_template('cocina.html', pedidos=pedidos, menu=menu_items)


@app.route('/api/stock')
def api_stock():
    inventario = {item['item_id']: item['disponible'] for item in inventario_col.find()}
    return jsonify(inventario)


@app.route('/api/db-status')
def db_status():
    """
    Endpoint distribuido para comprobar la latencia y disponibilidad
    del clúster en la nube (Heartbeat Monitor).
    """
    try:
        inicio = time.time()
        client.admin.command('ping')
        fin = time.time()
        latencia_ms = round((fin - inicio) * 1000)
        return jsonify({
            "status": "online",
            "latencia": f"{latencia_ms} ms",
            "clase_css": "bg-success" if latencia_ms < 150 else "bg-warning"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "offline",
            "latencia": "Inalcanzable",
            "clase_css": "bg-danger",
            "error": str(e)
        }), 500


@app.route('/ordenar', methods=['POST'])
def ordenar():
    data = request.get_json(silent=True)

    # --- Validación ---
    es_valido, error_msg = _validar_pedido(data)
    if not es_valido:
        return jsonify({"status": "error", "mensaje": error_msg}), 400

    cliente = data['cliente']
    carrito = data['carrito']

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    total_hoy = (
        pedidos_col.count_documents({"fecha": fecha_hoy}) +
        historial_col.count_documents({"fecha": fecha_hoy})
    )
    nuevo_id = total_hoy + 1

    nuevo_pedido = {
        "id":          nuevo_id,
        "cliente":     cliente['nombre'].strip(),
        "telefono":    cliente['telefono'].strip(),
        "entrega":     cliente['tipo'],
        "direccion":   cliente.get('direccion', 'N/A').strip(),
        "metodo_pago": cliente.get('metodo_pago', 'Efectivo'),
        "items":       carrito,
        "hora":        datetime.now().strftime("%H:%M:%S"),
        "fecha":       fecha_hoy,
        "total":       sum(i['precio'] * i['cantidad'] for i in carrito),
    }
    pedidos_col.insert_one(nuevo_pedido)
    return jsonify({"status": "success", "id": nuevo_id})


@app.route('/estado/<int:pedido_id>')
def consultar_estado(pedido_id):
    pedido = pedidos_col.find_one({"id": pedido_id})
    if pedido:
        return jsonify({"status": "preparando", "detalle": "Preparando..."})
    pedido_f = historial_col.find_one({"id": pedido_id})
    if pedido_f:
        msg = (
            "¡Tu orden está en camino! 🛵"
            if pedido_f.get('entrega') == 'Domicilio'
            else "¡Tu orden está lista para recoger! 🍔"
        )
        return jsonify({"status": "listo", "detalle": msg})
    return jsonify({"status": "no_encontrado", "detalle": "Buscando..."})


@app.route('/reporte')
def ver_reporte():
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    ventas = list(historial_col.find({"fecha": fecha_hoy}))
    for v in ventas:
        v.pop('_id', None)
    total_dinero = sum(v['total'] for v in ventas)
    return render_template('reporte.html', ventas=ventas, total=total_dinero)


@app.route('/toggle_disponibilidad', methods=['POST'])
def toggle_disponibilidad():
    item_id = str(request.json.get('id'))
    doc = inventario_col.find_one({"item_id": item_id})
    nuevo_estado = not doc['disponible'] if doc else False
    inventario_col.update_one(
        {"item_id": item_id},
        {"$set": {"disponible": nuevo_estado}},
        upsert=True
    )
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)


   