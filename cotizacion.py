from tkinter import * #librería estándar de Python para crear interfaces gráficas de usuario (GUI)
from tkinter import ttk  # Extensión de tkinter que proporciona widgets estilizados, como Treeview, para crear interfaces de usuario, lLo usamos para mostrar el carrito de compras.
from tkinter import messagebox #módulo de tkinter para mostrar mensajes.
from fpdf import FPDF #Librería para generar archivos PDF.
from pyswip import Prolog #biblioteca para integrar prolog con python

# Inicializar Prolog
prolog = Prolog() # Crear una instancia de Prolog que se utilizará para ejecutar consultas lógicas en Prolog.
prolog.consult("lista_de_productos.pl")  # Cargar la base de conocimiento de productos 


reglas = Prolog() # Crear otra instancia de Prolog para manejar las reglas.
reglas.consult("reglas.pl")  # Cargar la base de conocimiento de reglas



# -------------------------------------------------------------------------
# Obtener productos desde Prolog
# ------------------------------------------------------------------------

productos = {} # Inicializo el diccionario en python que será llenado abajo cuando se obtenga valores de prolog a través del for.

for resultado in prolog.query("producto(Nombre, PrecioUnitario)"): #consulta a prolog usando query.
    
    nombre = resultado["Nombre"].decode("utf-8")  #convierte esos bytes a una cadena de texto en formato UTF-8.
    precio = resultado["PrecioUnitario"]
    productos[f"{nombre} (S/{precio})"] = precio  # se van llenando los datos de producto y precio a al diccionado.
    

# Inicializar carrito y total
carrito = [] # lista vacía, aquí se almaceraán los productos gregados al carrito.
total = 0 # Inicializo el total en 0.





# -------------------------------------------------------------------------
# Función para actualizar el carrito en la interfaz
# -------------------------------------------------------------------------

def actualizar_carrito():
    global total # Esta línea indica que se está utilizando la variable total que se definió fuera de la función, para actualizar su valor.
    total = sum(item['precio'] * item['cantidad'] for item in carrito) # Recorrer cada producto en el carrito (una lista de diccionarios) y multiplica el precio del artículo por su cantidad y lo va
    tree_carrito.delete(*tree_carrito.get_children())  # Limpiar la tabla, y hace que no se duplique los productos agregados al carrito

    for index, item in enumerate(carrito):
        # Insertar producto en el treeview y agregar un botón para eliminarlo
        tree_carrito.insert(
            "", END, values=(
                item['producto'],
                f"S/{item['precio']:.2f}",
                item['cantidad'],
                f"S/{item['precio'] * item['cantidad']:.2f}",
                "Eliminar" # Columna para el botón de liminar
            ),
            iid=index
        )

        # Agregar el botón "Eliminar" en la última columna
        tree_carrito.item(index, tags="eliminar")
        tree_carrito.tag_bind("eliminar", "<ButtonRelease-1>", lambda e, idx=index: eliminar_producto(idx))

    label_total.config(text=f"Total: S/{total:.2f}")

    # Consultar descuento en Prolog al archivo reglas.pl
    descuento_query = list(reglas.query(f"calcular_descuento({total}, TotalConDescuento)"))
    total_con_descuento = descuento_query[0]["TotalConDescuento"]

    # Mostrar o esconder descuento y total final
    if total_con_descuento < total:
        descuento = total - total_con_descuento
        label_descuento.config(
            text=f"Descuento (15%): -S/{descuento:.2f}", fg="green", font=("Arial", 10, "bold"))
        label_descuento.pack()
        label_total_final.config(
            text=f"Total Final: S/{total_con_descuento:.2f}", fg="blue", font=("Arial", 12, "bold"))
        label_total_final.pack()
    else:
        label_descuento.pack_forget()
        label_total_final.pack_forget()



# -------------------------------------------------------------------------
# Función para eliminar producto del carrito
# -------------------------------------------------------------------------

def eliminar_producto(index):
    global carrito
    # Eliminar producto de la lista de carrito
    carrito.pop(index)
    # Actualizar el carrito
    actualizar_carrito()
    
    
        
        
# -------------------------------------------------------------------------
# Función para agregar producto al carrito
# -------------------------------------------------------------------------

def agregar_producto():
    producto_seleccionado = combo_producto.get()
    cantidad = spinbox_cantidad.get()
    if not producto_seleccionado or not cantidad.isdigit():
        messagebox.showerror(
            "Error", "Selecciona un producto y una cantidad válida.")
        return
    cantidad = int(cantidad)
    if cantidad <= 0:
        messagebox.showerror("Error", "La cantidad debe ser mayor a 0.")
        return

    # Obtener precio del producto
    precio = productos[producto_seleccionado]

    carrito.append({"producto": producto_seleccionado.split(" (")[0],
                   "cantidad": cantidad, "precio": precio})
    actualizar_carrito()
    

    
    
# -------------------------------------------------------------------------
# Función para generar cotización en PDF
# -------------------------------------------------------------------------

def generar_cotizacion():
    if not carrito:
        messagebox.showwarning(
            "Carrito vacío", "Agrega productos al carrito antes de generar la cotización.")
        return

    # Consultar descuento en Prolog al archivo reglas.pl
    descuento_query = list(reglas.query(f"calcular_descuento({total}, TotalConDescuento)"))
    total_con_descuento = descuento_query[0]["TotalConDescuento"]
    descuento = total - total_con_descuento if total_con_descuento < total else 0

    # Generar PDF
    pdf = FPDF()
    pdf.add_page()

    # Cabecera estilizada
    pdf.set_fill_color(52, 58, 64)  # Fondo gris oscuro
    pdf.set_text_color(255, 255, 255)  # Texto blanco
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 15, txt="Cotización de Productos", ln=True, align="C", fill=True)
    pdf.ln(10)

    # Encabezados de tabla
    pdf.set_fill_color(230, 230, 230)  # Fondo gris claro
    pdf.set_text_color(0, 0, 0)  # Texto negro
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(60, 10, txt="Producto", border=1, align="C", fill=True)
    pdf.cell(40, 10, txt="Precio (S/)", border=1, align="C", fill=True)
    pdf.cell(40, 10, txt="Cantidad", border=1, align="C", fill=True)
    pdf.cell(40, 10, txt="Total (S/)", border=1, align="C", fill=True)
    pdf.ln(10)

    # Filas de la tabla
    pdf.set_font("Arial", size=11)
    for item in carrito:
        pdf.cell(60, 10, txt=item['producto'], border=1)
        pdf.cell(40, 10, txt=f"S/{item['precio']:.2f}", border=1, align="C")
        pdf.cell(40, 10, txt=str(item['cantidad']), border=1, align="C")
        pdf.cell(40, 10, txt=f"S/{item['precio'] * item['cantidad']:.2f}", border=1, align="C")
        pdf.ln(10)

    # Espaciado antes del resumen
    pdf.ln(10)

    # Resumen
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, txt=f"Total: S/{total:.2f}", ln=True, align="R")
    if descuento > 0:
        pdf.set_text_color(34, 139, 34)  # Verde
        pdf.cell(0, 10, txt=f"Descuento (15%): -S/{descuento:.2f}", ln=True, align="R")
        pdf.set_text_color(0, 0, 139)  # Azul
        pdf.cell(0, 10, txt=f"Total Final: S/{total_con_descuento:.2f}", ln=True, align="R")

    # Guardar PDF
    pdf.output("cotizacion.pdf")

    # Confirmación
    messagebox.showinfo(
        "PDF Generado", "La cotización se ha generado como 'cotizacion.pdf'.")







# -------------------------------------------------------------------------
# Función para agregar un producto a Prolog
# -------------------------------------------------------------------------

def agregar_producto_prolog(nombre, precio):
    if not nombre.strip(): 
     # Validar que el nombre no esté vacío
        messagebox.showerror("Error", "El nombre del producto no puede estar vacío.")
        return
        
    try:
        precio_float = float(precio) # Asegura que precio sea un número flotante
        
        if precio_float < 1: # Validar que el precio sea mayor o igual a 1
            messagebox.showerror("Error", "El precio debe ser mayor o igual a 1.")
            return

        # Convertir nombre y precio al formato de Prolog
        nombre_prolog = f"'{nombre}'"  # Asegura que el nombre se maneje como átomo
        precio_prolog = precio_float  # Usar el valor convertido a float

        # Comando Prolog para agregar el producto
        prolog.assertz(f"producto({nombre_prolog}, {precio_prolog})")  # Agregar el producto directamente

        # Actualizar la lista de productos en Python
        productos[f"{nombre} (S/{precio_float:.2f})"] = precio_float  # Asegura que el precio esté formateado
        combo_producto['values'] = list(productos.keys())  # Actualizar el combo box
        
        nombre_prolog = nombre_prolog.strip("'")  # Asegura de que nombre_prolog no tenga comillas extras  # Elimina comillas simples si las tiene
        precio_prolog = int(precio_prolog) if precio_prolog.is_integer() else precio_prolog

        # Guardar el producto en el archivo lista_de_productos.pl
        with open("lista_de_productos.pl", "a", encoding="utf-8") as archivo:
            archivo.write(f'producto("{nombre_prolog}", {precio_prolog}).\n')

        messagebox.showinfo("Éxito", f"Producto '{nombre}' agregado con éxito.")   # Mensaje de éxito
                
    except ValueError:
        messagebox.showerror("Error", f"El precio '{precio}' no es válido. Debe ser un número.")






# -------------------------------------------------------------------------
# Crear interfaz de usuario
# -------------------------------------------------------------------------

ventana = Tk() #ventana principal del programa
ventana.title("Generador de Cotizaciones") # titulo de una ventana 
ventana.geometry("800x600") # tamaño de la ventana


frame_titulo = Frame(ventana) # contenedor dentro de la ventana
frame_titulo.pack(pady=10) # espacaiado de 10 pixeles arriba y abajo por que tiene el y para el título
label_titulo = Label(frame_titulo, text="Generador de Cotizaciones", font=("Arial", 20, "bold"))          #crea una etiqueta label dentro del frame titulo
label_titulo.pack() #hacer visible el titulo en la interfáz




# -------------------------------------------------------------------------
#Agregar productos a prolog (interfaz)
# -------------------------------------------------------------------------


frame_agregar_producto = Frame(ventana)
frame_agregar_producto.pack(pady=10)

label_nuevo_producto = Label(frame_agregar_producto, text="Nuevo Producto:")
label_nuevo_producto.grid(row=0, column=0, padx=5)

entry_nombre_producto = Entry(frame_agregar_producto, width=30)
entry_nombre_producto.grid(row=0, column=1, padx=5)

label_precio_producto = Label(frame_agregar_producto, text="Precio:")
label_precio_producto.grid(row=0, column=2, padx=5)

entry_precio_producto = Entry(frame_agregar_producto, width=10)
entry_precio_producto.grid(row=0, column=3, padx=5)

btn_agregar_nuevo = Button(frame_agregar_producto, text="Agregar Producto", 
                           command=lambda: agregar_producto_prolog(
                               entry_nombre_producto.get(),
                               entry_precio_producto.get()
                           ))
btn_agregar_nuevo.grid(row=0, column=4, padx=5)

# Fin de interfaz para agregar producto


# -------------------------------------------------------------------------
#Agregar producto al carrito de productos (interfaz)
# -------------------------------------------------------------------------


frame_selector = Frame(ventana)
frame_selector.pack(pady=10)


label_producto = Label(frame_selector, text="Producto:")
label_producto.grid(row=0, column=0, padx=5)

combo_producto = ttk.Combobox(frame_selector, values=list(productos.keys()), width=50)
combo_producto.grid(row=0, column=1, padx=5)

label_cantidad = Label(frame_selector, text="Cantidad:")
label_cantidad.grid(row=0, column=2, padx=5)

spinbox_cantidad = Spinbox(frame_selector, from_=1, to=100)
spinbox_cantidad.grid(row=0, column=3, padx=5)

btn_agregar = Button(frame_selector, text="Agregar al carrito", command=agregar_producto)
btn_agregar.grid(row=0, column=4, padx=5)


# Fin de interfaz de agregar productos al carrito de pedidos




# Agregando interfaz para mostrar la tabla del carrito de productos

frame_carrito = Frame(ventana)
frame_carrito.pack(pady=10)

label_carrito = Label(frame_carrito, text="Carrito de productos", font=("Arial", 12, "bold"))
label_carrito.pack()


#Representación de la información que se mostrará en cada columna (usando Treeview de ttk) dentro el frame_Carrito
tree_carrito = ttk.Treeview(frame_carrito, columns=("Producto", "Precio", "Cantidad", "Total", "Acción"), show="headings", height=15)

# Definir los encabezados de las columnas
tree_carrito.heading("Producto", text="Producto")
tree_carrito.heading("Precio", text="Precio")
tree_carrito.heading("Cantidad", text="Cantidad")
tree_carrito.heading("Total", text="Total")
tree_carrito.heading("Acción", text="Acción")

tree_carrito.column("Producto", width=200)
tree_carrito.column("Precio", width=100, anchor="center")
tree_carrito.column("Cantidad", width=100, anchor="center")
tree_carrito.column("Total", width=100, anchor="center")
tree_carrito.column("Acción", width=50, anchor="center")
tree_carrito.pack()

# Fin de interfaz para mostrar la tabla de carrito de productos


# Incio de interfaz para mostrar el total, descuento, final total y generar cotización en pdf.

label_total = Label(ventana, text="Total: S/0.00", font=("Arial", 12))
label_total.pack()

label_descuento = Label(ventana)
label_total_final = Label(ventana)

btn_cotizar = Button(ventana, text="Generar Cotización en PDF", command=generar_cotizacion)
btn_cotizar.pack(pady=10)

# Fin de interfaz para mostrar el total, descuento, final total y generar cotización en pdf.


ventana.mainloop() # Fin de la ventana
