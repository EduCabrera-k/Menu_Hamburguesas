let carrito = JSON.parse(localStorage.getItem('carrito_rendon')) || [];
let intervaloRastreo;

function agregarAlCarrito(n, p) {
    const i = carrito.find(x => x.nombre === n);
    if (i) i.cantidad++; else carrito.push({ nombre: n, precio: p, cantidad: 1 });
    actualizarVista();
}
function eliminarDelCarrito(idx) { carrito[idx].cantidad--; if (carrito[idx].cantidad <= 0) carrito.splice(idx, 1); actualizarVista(); }
function incrementarCantidad(idx) { carrito[idx].cantidad++; actualizarVista(); }
function eliminarTodoProducto(idx) { carrito.splice(idx, 1); actualizarVista(); }

function actualizarVista() {
    localStorage.setItem('carrito_rendon', JSON.stringify(carrito));
    const lista = document.getElementById('lista-pedido');
    const totalTxt = document.getElementById('total-cuenta');
    lista.innerHTML = ''; let total = 0;
    if (carrito.length === 0) {
        lista.innerHTML = '<li class="text-muted text-center py-3 small">El carrito está vacío</li>';
    } else {
        carrito.forEach((item, idx) => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center px-0 bg-transparent border-0';
            li.innerHTML = `<div><span class="d-block fw-bold">${item.nombre}</span><small class="text-muted">$${item.precio} c/u</small></div>
                <div class="d-flex align-items-center gap-1">
                    <button class="btn btn-sm btn-outline-secondary py-0 px-2" onclick="eliminarDelCarrito(${idx})">-</button>
                    <span class="fw-bold text-danger mx-1">x${item.cantidad}</span>
                    <button class="btn btn-sm btn-outline-success py-0 px-2" onclick="incrementarCantidad(${idx})">+</button>
                    <button class="btn btn-sm btn-danger ms-2 py-0 px-2" onclick="eliminarTodoProducto(${idx})">&times;</button>
                </div>`;
            lista.appendChild(li); total += item.precio * item.cantidad;
        });
    }
    totalTxt.innerText = `$${total}`;
}

async function verificarStock() {
    try {
        const res = await fetch('/api/stock'); const stock = await res.json();
        document.querySelectorAll('[data-product-id]').forEach(btn => {
            const id = btn.getAttribute('data-product-id'); const disp = stock[id] !== false;
            btn.classList.replace(disp ? 'btn-secondary' : 'btn-dark', disp ? 'btn-dark' : 'btn-secondary');
            btn.innerText = disp ? '+ Agregar' : 'Agotado'; btn.disabled = !disp;
        });
    } catch(e) {}
}
setInterval(verificarStock, 5000);

async function procesarCompraFinal() {
    if (carrito.length === 0) return alert("Carrito vacío");
    const c = { nombre: document.getElementById('c-nombre').value, telefono: document.getElementById('c-tel').value, 
               tipo: document.getElementById('c-tipo').value, direccion: document.getElementById('c-dir').value || 'N/A' };
    if (!c.nombre || !c.telefono) return alert("Llena tus datos");
    const res = await fetch('/ordenar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ carrito, cliente: c }) });
    if (res.ok) {
        const data = await res.json(); bootstrap.Modal.getInstance(document.getElementById('checkoutModal')).hide();
        iniciarRastreo(data.id); carrito = []; actualizarVista();
    }
}

function iniciarRastreo(id) {
    document.getElementById('rastreador-container').classList.remove('d-none');
    document.getElementById('track-id').innerText = id;
    if (intervaloRastreo) clearInterval(intervaloRastreo);
    intervaloRastreo = setInterval(async () => {
        const r = await fetch(`/estado/${id}`); const d = await r.json();
        const b = document.getElementById('progreso-barra'); const m = document.getElementById('track-mensaje');
        if (d.status === 'preparando') { b.style.width = "50%"; m.innerText = d.detalle; }
        else if (d.status === 'listo') { b.style.width = "100%"; b.classList.replace('bg-warning', 'bg-success'); m.innerText = d.detalle; clearInterval(intervaloRastreo); }
    }, 5000);
}

function showSection(s) { document.querySelectorAll('.menu-section').forEach(sec => sec.classList.add('d-none')); document.getElementById(s + '-section').classList.remove('d-none'); }
window.onload = () => { actualizarVista(); verificarStock(); };