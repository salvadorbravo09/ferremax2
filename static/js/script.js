document.getElementById('btnBuscar').addEventListener('click', function () {
    const nombre = document.getElementById('buscar').value.trim();

    if (!nombre) {
        document.getElementById('resultado').innerHTML = '<div class="alert alert-warning">Por favor ingrese el nombre de un producto.</div>';
        return;
    }

    fetch(`/api/buscar_producto?nombre=${encodeURIComponent(nombre)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Respuesta de API:', data); // Para debug

            // Si la API envía {error: "..."} y no array, lo manejamos aquí
            if (data.error) {
                document.getElementById('resultado').innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }

            if (!Array.isArray(data) || data.length === 0) {
                document.getElementById('resultado').innerHTML = `<div class="alert alert-info">No se encontraron productos.</div>`;
                return;
            }

            let html = '';

            data.forEach(producto => {
                html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <h5 class="card-title">${producto.nombre}</h5>
                        <p><strong>Código:</strong> ${producto.codigo}</p>
                        <ul>`;

                producto.sucursales.forEach((suc, idx) => {
                    const inputId = `tipo-cambio-${producto.codigo}-${idx}`;
                    const resultadoId = `resultado-clp-${producto.codigo}-${idx}`;
                    const cantidadSpanId = `cantidad-${producto.codigo}-${idx}`;
                    const inputVentaId = `input-cantidad-${producto.codigo}-${idx}`;

                    html += `
                        <li>
                            <strong>Sucursal:</strong> ${suc.sucursal} |
                            <strong>Cantidad:</strong> <span id="${cantidadSpanId}">${suc.cantidad}</span> |
                            <strong>Precio USD:</strong> $${suc.precio.toFixed(2)}

                            <div class="input-group mt-1" style="max-width: 320px;">
                                <input type="number" step="0.01" min="1" id="${inputId}" class="form-control form-control-sm" placeholder="Precio en CLP">
                                <button class="btn btn-primary btn-sm" onclick="convertirPrecio('${producto.codigo}', ${suc.precio}, '${inputId}', '${resultadoId}')">Convertir a USD</button>
                                <h5 id="${resultadoId}" class="mb-0 ms-2" style="line-height: 1.5;"></h5>
                            </div>

                            <div class="input-group mt-2" style="max-width: 200px;">
                                <input type="number" min="1" max="${suc.cantidad}" id="${inputVentaId}" class="form-control form-control-sm" placeholder="Cantidad a vender">
                                <button class="btn btn-success btn-sm" onclick="venderProducto('${producto.codigo}', '${suc.sucursal}', '${cantidadSpanId}', '${inputVentaId}')">Vender</button>
                            </div>
                        </li>`;
                });

                html += `</ul></div></div>`;
            });

            document.getElementById('resultado').innerHTML = html;
        })
        .catch(error => {
            console.error('Error en fetch:', error);
            document.getElementById('resultado').innerHTML = `<div class="alert alert-danger">Error al consultar el producto.</div>`;
        });
});


function convertirPrecio(codigoProducto, precioUsd, inputId, resultadoId) {
    const input = document.getElementById(inputId);
    const precioClp = parseFloat(input.value);

    if (isNaN(precioClp) || precioClp <= 0) {
        alert('Por favor ingrese un precio válido en CLP');
        return;
    }

    const tipoCambio = 950; // Tipo de cambio fijo
    const precioEnUsd = (precioClp / tipoCambio).toLocaleString('en-US', { 
        style: 'currency', 
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    document.getElementById(resultadoId).textContent = precioEnUsd;
}

function venderProducto(codigo, sucursal, cantidadSpanId, inputId) {
    const cantidadInput = document.getElementById(inputId);
    const cantidad = parseInt(cantidadInput.value);

    if (isNaN(cantidad) || cantidad <= 0) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor ingrese una cantidad válida',
            confirmButtonColor: '#3085d6'
        });
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
            Swal.fire({
                icon: 'error',
                title: 'Error en la venta',
                text: data.error,
                confirmButtonColor: '#3085d6'
            });
        } else {
            Swal.fire({
                icon: 'success',
                title: '¡Venta exitosa!',
                text: `Se vendieron ${cantidad} unidades. Quedan ${data.cantidad_restante} en stock.`,
                confirmButtonColor: '#3085d6'
            });
            document.getElementById(cantidadSpanId).textContent = data.cantidad_restante;
            cantidadInput.value = '';
        }
    })
    .catch(error => {
        console.error('Error en venta:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error en la venta',
            text: error.message,
            confirmButtonColor: '#3085d6'
        });
    });
}
