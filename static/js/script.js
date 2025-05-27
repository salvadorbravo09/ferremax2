document.getElementById('btnBuscar').addEventListener('click', function () {
    const nombre = document.getElementById('buscar').value.trim();
    
    if (!nombre) {
        document.getElementById('resultado').innerHTML = '<div class="alert alert-warning">Por favor ingrese el nombre de un producto.</div>';
        return;
    }

    fetch(`/api/buscar_producto?nombre=${encodeURIComponent(nombre)}`)
        .then(response => response.json())
        .then(data => {
            let html = '';
            
            if (data.error) {
                html = `<div class="alert alert-danger">${data.error}</div>`;
            } else {
                data.forEach(producto => {
                    html += `
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5 class="card-title">${producto.nombre}</h5>
                            <p class="card-text">
                                <strong>Código:</strong> ${producto.codigo}<br>
                            </p>
                            <ul>`;

                    producto.sucursales.forEach((suc, idx) => {
                        const inputId = `input-${producto.codigo}-${idx}`;
                        html += `
                                <li>
                                    <strong>Sucursal:</strong> ${suc.sucursal} |
                                    <strong>Cantidad:</strong> <span id="cantidad-${producto.codigo}-${idx}">${suc.cantidad}</span> |
                                    <strong>Precio USD:</strong> $${suc.precio.toFixed(2)} |
                                    <strong>Precio (CLP):</strong> $${suc.precio_clp.toLocaleString('es-CL')} |
                                    <input type="number" id="${inputId}" placeholder="Cantidad" min="1" max="${suc.cantidad}" style="width: 70px;">
                                    <button class="btn btn-success btn-sm" 
                                            onclick="venderProducto('${producto.codigo}', '${suc.sucursal}', 'cantidad-${producto.codigo}-${idx}', '${inputId}')">
                                        Vender
                                    </button>
                                </li>`;
                    });
                    
                    html += `
                            </ul>
                        </div>
                    </div>
            
                    <div class="mb-3 p-2 border rounded">
                        <div class="input-group">
                            <input type="text" 
                                    autocomplete="off"
                                   id="tipo-cambio-${producto.codigo}" 
                                   class="form-control form-control-sm" 
                                   placeholder="Tipo de cambio (CLP)"
                                   style="width: 75px;">
                            <button class="btn btn-primary btn-sm" 
                                    onclick="convertirMonedaProducto('${producto.codigo}', ${producto.sucursales[0].precio})">
                                Convertir
                            </button>
                            <span class="input-group-text">
                                Resultado: <span id="resultado-clp-${producto.codigo}"></span>
                            </span>
                        </div>
                    </div>`;
                });
            }
            
            document.getElementById('resultado').innerHTML = html;
        })
        .catch(error => {
            document.getElementById('resultado').innerHTML = `<div class="alert alert-danger">Error al consultar el producto.</div>`;
        });
});

// Función de conversión modificada para trabajar por producto
function convertirMonedaProducto(productoCodigo, precioUsd) {
    const input = document.getElementById(`tipo-cambio-${productoCodigo}`);
    const valorRaw = input.value.trim().replace(',', '.'); // Corrige formato coma-punto
    const tipoCambio = parseFloat(valorRaw);

    // Si el valor ingresado no es válido, usamos 950 como tipo de cambio por defecto
    const cambioFinal = (!isNaN(tipoCambio) && tipoCambio > 0) ? tipoCambio : 950;

    const resultado = precioUsd * cambioFinal;

    document.getElementById(`resultado-clp-${productoCodigo}`).textContent = 
        `$${resultado.toLocaleString('es-CL')} CLP`;
}





function venderProducto(codigo, sucursal, cantidadSpanId, inputId) {
    const cantidadInput = document.getElementById(inputId);
    const cantidad = parseInt(cantidadInput.value);

    if (isNaN(cantidad) || cantidad <= 0) {
        alert('Por favor ingrese una cantidad válida');
        return;
    }

    fetch('/api/vender', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            codigo: codigo, 
            sucursal: sucursal,
            cantidad: cantidad
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById(cantidadSpanId).textContent = data.cantidad_restante;
            cantidadInput.value = '';
        }
    })
    .catch(error => {
        document.getElementById('resultado').innerHTML = `
            <div class="alert alert-danger">
                Error en la venta: ${error.message}
            </div>`;
    });
}