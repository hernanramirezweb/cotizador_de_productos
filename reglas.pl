:- dynamic producto/2.

% Regla para calcular el costo total de un producto
costo_producto(Nombre, Cantidad, Costo) :- producto(Nombre, PrecioUnitario),
Costo is PrecioUnitario * Cantidad.

% Regla para aplicar descuento si el costo total es mayor a 500.
calcular_descuento(Total, TotalConDescuento) :-
    Total > 500,
    TotalConDescuento is Total * 0.85.
calcular_descuento(Total, Total). % Si no hay descuento, permanece igual.

% Regla para agregar un producto nuevo.
agregar_producto(Nombre, Precio) :-
    \+ producto(Nombre, _), % Verifica que no exista un producto con el mismo nombre.
assertz(producto(Nombre, Precio)). % Agrega el nuevo producto dinámicamente.

