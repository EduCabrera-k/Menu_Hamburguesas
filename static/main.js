let carrito = [];
let total = 0;

function showSection(id) {
    document.querySelectorAll('.menu-section').forEach(s => s.classList.add('d-none'));
    const section = document.getElementById(id + '-section');
    if (section) section.classList.remove('d-none');
}

// Lógica de Monitor de Red para la vista de cocina
function verificarSaludNodoDatos() {
    const badge = document.getElementById('db-status-badge');
    const latencySpan = document.getElementById('db-latency');
    
    if (!badge || !latencySpan) return; 

    fetch('/api/db-status')
        .then(res => {
            if (!res.ok) throw new Error("Error de respuesta");
            return res.json();
        })
        .then(data => {
            badge.className = `badge ${data.clase_css} px-3 py-2 fs-6 fw-normal`;
            if (data.status === 'online') {
                badge.innerHTML = `● CLÚSTER ONLINE`;
                latencySpan.innerHTML = `Latencia: ${data.latencia}`;
            } else {
                badge.innerHTML = `● CLÚSTER OFFLINE`;
                latencySpan.innerHTML = `Desconectado`;
            }
        })
        .catch(() => {
            if(badge && latencySpan) {
                badge.className = "badge bg-danger px-3 py-2 fs-6 fw-normal";
                badge.innerHTML = `● ERROR DE ENLACE`;
                latencySpan.innerHTML = `Inalcanzable`;
            }
        });
}

// Lógica de Carrito Interactiva
function agregarAlCarrito(nombre, precio, id) {
    const index = carrito.findIndex(i => i.item_id === id);
    if (index > -1) {
        carrito[index].cantidad++;
    } else {
        carrito.push({ nombre, precio, cantidad: 1, item_id: id });
    }
    actualizarCarritoUI();
    Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'Agregado', showConfirmButton: false, timer: 1000 });
}

function cambiarCantidad(index, delta) {
    carrito[index].cantidad += delta;
    if (carrito[index].cantidad <= 0) {
        eliminarDelCarrito(index);
    } else {
        actualizarCarritoUI();
    }
}

function eliminarDelCarrito(index) {
    carrito.splice(index, 1);
    actualizarCarritoUI();
}

function actualizarCarritoUI() {
    const lista = document.getElementById('lista-pedido');
    lista.innerHTML = '';
    total = 0;
    carrito.forEach((item, index) => {
        total += item.precio * item.cantidad;
        lista.innerHTML += `
            <div class="mb-3 p-2 border-bottom">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="fw-bold">${item.nombre}</span>
                    <div class="d-flex align-items-center gap-1">
                        <button class="btn-qty" onclick="cambiarCantidad(${index}, -1)">-</button>
                        <span class="mx-1 fw-bold text-danger">x${item.cantidad}</span>
                        <button class="btn-qty" onclick="cambiarCantidad(${index}, 1)">+</button>
                        <button class="btn-del ms-2" onclick="eliminarDelCarrito(${index})">×</button>
                    </div>
                </div>
                <div class="small text-muted">$${item.precio} c/u</div>
            </div>`;
    });
    document.getElementById('total-cuenta').innerText = `$${total}`;
}

// Rastreo y Sincronización
function rastrearPedido(id) {
    const intervalo = setInterval(() => {
        fetch(`/estado/${id}`).then(res => res.json()).then(data => {
            const barra = document.getElementById('progreso-barra');
            const mensaje = document.getElementById('track-mensaje');
            if (data.status === 'preparando') {
                barra.style.width = '60%';
                mensaje.innerText = data.detalle;
            } else if (data.status === 'listo') {
                barra.style.width = '100%';
                barra.classList.replace('bg-warning', 'bg-success');
                mensaje.innerText = data.detalle;
                clearInterval(intervalo);
            }
        });
    }, 5000);
}

setInterval(() => {
    fetch('/api/stock').then(res => res.json()).then(inv => {
        document.querySelectorAll('.btn-agregar').forEach(btn => {
            const id = btn.getAttribute('data-product-id');
            const card = btn.closest('.card');
            if (inv[id] === false) { btn.classList.add('d-none'); card.classList.add('opacity-50'); }
            else { btn.classList.remove('d-none'); card.classList.remove('opacity-50'); }
        });
    });
}, 10000);

function toggleDireccion(val) { document.getElementById('c-dir').classList.toggle('d-none', val === 'Sucursal'); }
function toggleTarjeta(show) { document.getElementById('form-tarjeta').classList.toggle('d-none', !show); }

async function validarYEnviar() {
    if (carrito.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Carrito vacío',
            text: 'Agrega al menos un producto antes de continuar.',
            confirmButtonColor: '#d90429'
        });
        return;
    }

    const esTarjeta = document.getElementById('p-tarjeta').checked;
    if (esTarjeta) {
        Swal.fire({ title: 'Procesando...', allowOutsideClick: false, didOpen: () => { Swal.showLoading() } });
        setTimeout(() => {
            Swal.fire({ icon: 'success', title: '¡Transferencia Exitosa!', confirmButtonText: 'Continuar' }).then(enviarBackend);
        }, 2000);
    } else { enviarBackend(); }
}

function enviarBackend() {
    const data = {
        cliente: {
            nombre: document.getElementById('c-nombre').value,
            telefono: document.getElementById('c-tel').value,
            tipo: document.getElementById('c-tipo').value,
            direccion: document.getElementById('c-dir').value,
            metodo_pago: document.querySelector('input[name="pago"]:checked').value
        },
        carrito: carrito
    };
    fetch('/ordenar', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) })
    .then(res => res.json()).then(res => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('checkoutModal'));
        modal.hide();
        document.getElementById('rastreador-container').classList.remove('d-none');
        document.getElementById('track-id').innerText = res.id;
        document.getElementById('progreso-barra').style.width = '30%';
        rastrearPedido(res.id);
        carrito = []; total = 0; actualizarCarritoUI();
    });
}

// Disparador unificado para inicializar el monitor si detecta el badge de cocina
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('db-status-badge')) {
        verificarSaludNodoDatos();
        setInterval(verificarSaludNodoDatos, 2000);
    }
});

