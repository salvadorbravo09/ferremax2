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

    // Validación para asegurar que el valor sea mayor que cero (requisito #5)
    if (isNaN(precioClp) || precioClp <= 0) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor ingrese un precio válido mayor a cero en CLP',
            confirmButtonColor: '#3085d6'
        });
        return;
    }

    // Obtener el tipo de cambio de la API
    fetch('/api/conversion/dolar')
        .then(response => response.json())
        .then(data => {
            const tipoCambio = data.tasa;
            const precioEnUsd = (precioClp / tipoCambio).toLocaleString('en-US', { 
                style: 'currency', 
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });

            document.getElementById(resultadoId).textContent = precioEnUsd;
        })
        .catch(error => {
            console.error('Error al obtener tipo de cambio:', error);
            // Usar valor fijo en caso de error
            const tipoCambio = 950;
            const precioEnUsd = (precioClp / tipoCambio).toLocaleString('en-US', { 
                style: 'currency', 
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });

            document.getElementById(resultadoId).textContent = precioEnUsd + " (usando tasa por defecto)";
        });
}

function venderProducto(codigo, sucursal, cantidadSpanId, inputId) {
    const cantidadInput = document.getElementById(inputId);
    const cantidad = parseInt(cantidadInput.value);
    const stockActual = parseInt(document.getElementById(cantidadSpanId).textContent);

    // Validación para asegurar que el valor sea mayor que cero (requisito #5)
    if (isNaN(cantidad) || cantidad <= 0) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor ingrese una cantidad válida mayor a cero',
            confirmButtonColor: '#3085d6'
        });
        return;
    }

    // Validar en el front que exista la cantidad en stock (requisito #4)
    if (cantidad > stockActual) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: `No hay suficiente stock. Solo hay ${stockActual} unidades disponibles.`,
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

// Configuración de SSE
let eventSource;

function iniciarSSE() {
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource('/api/events');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.tipo === 'stock_bajo') {
            Swal.fire({
                icon: 'warning',
                title: '¡Stock Bajo!',
                text: `El producto ${data.producto} en ${data.sucursal} tiene solo ${data.cantidad} unidades disponibles (menos de 10).`,
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 5000,
                timerProgressBar: true
            });
        } else if (data.tipo === 'stock_actualizado') {
            // Actualizar la cantidad en la interfaz si el producto está visible
            const cantidadElementos = document.querySelectorAll(`[id^="cantidad-${data.producto.replace(/\s+/g, '-')}-"]`);
            cantidadElementos.forEach(el => {
                if (el.closest('li').textContent.includes(data.sucursal)) {
                    el.textContent = data.cantidad;
                    
                    // Si el stock baja a menos de 10, mostrar alerta
                    if (data.cantidad < 10) {
                        Swal.fire({
                            icon: 'warning',
                            title: '¡Stock Bajo!',
                            text: `El producto ${data.producto} en ${data.sucursal} ahora tiene solo ${data.cantidad} unidades disponibles (menos de 10).`,
                            toast: true,
                            position: 'top-end',
                            showConfirmButton: false,
                            timer: 5000,
                            timerProgressBar: true
                        });
                    }
                }
            });
        }
    };

    eventSource.onerror = function(error) {
        console.error('Error en SSE:', error);
        // Intentar reconectar después de 5 segundos
        setTimeout(iniciarSSE, 5000);
    };
}

// Iniciar SSE cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    iniciarSSE();
    
    // Cargar la lista de sucursales para el formulario
    fetch('/api/sucursales')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('productBranch');
            // Limpiar opciones actuales excepto la primera
            while (select.options.length > 1) {
                select.remove(1);
            }
            
            // Agregar las sucursales desde la API
            data.forEach(sucursal => {
                const option = document.createElement('option');
                option.value = sucursal.nombre;
                option.textContent = sucursal.nombre;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error al cargar sucursales:', error);
        });
});

// Manejar la vista previa de la imagen
document.getElementById('productPhoto').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('preview');
            preview.src = e.target.result;
            document.getElementById('imagePreview').style.display = 'block';
        }
        reader.readAsDataURL(file);
    }
});

// Manejar el guardado de nuevo producto
document.getElementById('saveProduct').addEventListener('click', function() {
    const form = document.getElementById('addProductForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Validaciones adicionales (requisito #5)
    const precio = parseFloat(document.getElementById('productPrice').value);
    const cantidad = parseInt(document.getElementById('productQuantity').value);

    if (isNaN(precio) || precio <= 0) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'El precio debe ser mayor que cero',
            confirmButtonColor: '#3085d6'
        });
        return;
    }

    if (isNaN(cantidad) || cantidad <= 0) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'La cantidad debe ser mayor que cero',
            confirmButtonColor: '#3085d6'
        });
        return;
    }

    const formData = new FormData(form);

    fetch('/api/agregar_producto', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.error,
                confirmButtonColor: '#3085d6'
            });
            if (data.errors) {
                Swal.fire({
                    icon: 'error',
                    title: 'Errores de validación',
                    html: data.errors.join('<br>'),
                    confirmButtonColor: '#3085d6'
                });
            }
        } else {
            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: 'Producto agregado correctamente',
                confirmButtonColor: '#3085d6'
            });
            
            // Cerrar el modal y limpiar el formulario
            const modal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
            modal.hide();
            form.reset();
            document.getElementById('imagePreview').style.display = 'none';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Ocurrió un error al agregar el producto',
            confirmButtonColor: '#3085d6'
        });
    });
});
