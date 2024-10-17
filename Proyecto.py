import json
import requests

# Clase Producto
class Producto:
    def __init__(self, nombre, cantidad, precio):
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    def __str__(self):
        return f"{self.nombre} - {self.cantidad} unidades - {self.precio:.2f}€"

# Clase Carrito
class Carrito:
    def __init__(self):
        self.productos = []

    # Funcion para agregar  productos
    def agregar_producto(self, producto, cantidad):
        if cantidad <= producto.cantidad:
            producto.cantidad -= cantidad # Reducimos el stock disponible
            self.productos.append((producto, cantidad))
            print(f"{producto.nombre} ha sido añadido al carrito.")
        else:
            print(f"No hay suficiente stock de {producto.nombre}. Stock disponible {producto.cantidad}")

    # Funcion para mostrar el carrito de compra
    def mostrar_carrito(self):
        if not self.productos:
            print("El carrito está vacío.")
        else:
            print("Carrito de compras:")
            total = 0
            for producto, cantidad in self.productos:
                subtotal = producto.precio * cantidad
                total += subtotal
                print(f"{producto.nombre} x {cantidad} = {subtotal:.2f}€")
            print(f"Total a pagar: {total:.2f}€")

    def vaciar_carrito(self):
        self.productos = []
        print("El carrito ha sido vaciado.")


# Clase GestorProductos (con el catálogo)
class GestorProductos:
    def __init__(self):
        self.catalogo = []

    # Funcion para mostrar los productos
    def cargar_productos(self, archivo):
        try:
            with open(archivo, 'r') as file:
                productos = json.load(file)
                for producto in productos:
                    nombre = producto['nombre']
                    cantidad = producto['cantidad']
                    precio = producto['precio']
                    self.catalogo.append(Producto(nombre, cantidad, precio))
        except FileNotFoundError:
            print("No se encontró el archivo de productos.")

    # Funcion para mostrar el catalogo
    def mostrar_catalogo(self):
        if not self.catalogo:
            print("No hay productos disponibles.")
        else:
            print("Catálogo de productos:")
            for producto in self.catalogo:
                print(producto)

    # Funcion para buscar el producto
    def buscar_producto(self, nombre_producto):
        for producto in self.catalogo:
            if producto.nombre.lower() == nombre_producto.lower():
                return producto
        return None

    # Funcion para obtener información de medicamentos desde la API de OpenFDA
    def buscar_medicamento_en_api(nombre_medicamento):
        url = f"https://api.fda.gov/drug/label.json?search={nombre_medicamento}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                resultados = data.get('results', [])
                if resultados:
                    for resultado in resultados:
                        print(f"Nombre: {resultado.get('openfda', {}).get('brand_name', 'Desconocido')}")
                        print(f"Propósito: {resultado.get('purpose', ['Desconocido'])[0]}")
                        print(f"Advertencias: {resultado.get('warnings', ['No hay advertencias disponibles'])[0]}")
                        print("\n")
                else:
                    print("No se encontraron resultados.")
            else:
                print("Error en la solicitud:", response.status_code)
        except Exception as e:
            print("Ocurrió un error:", e)

    def filtrar_por_precio(self, precio_maximo):
        productos_filtrados = list(filter(lambda p: p.precio <= precio_maximo, self.catalogo))
        return productos_filtrados


# Función para mostrar el menú principal
def mostrar_menu():
    print("\n--- Farmacia en Línea ---")
    print("1. Ver catálogo de productos")
    print("2. Agregar producto al carrito")
    print("3. Mostrar carrito")
    print("4. Confirmar pedido")
    print("5. Buscar información de medicamentos")
    print("6. Filtrar medicamentos por precio")
    print("7. Salir")


# Funcion principal del programa
def main():
    gestor_productos = GestorProductos()
    carrito = Carrito()

    # Cargar los productos
    gestor_productos.cargar_productos("farmacia.json")

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            gestor_productos.mostrar_catalogo()

        elif opcion == '2':
            nombre_producto = input("Ingrese el nombre del producto: ")
            producto = gestor_productos.buscar_producto(nombre_producto)
            if producto:
                cantidad = int(input(f"Ingrese la cantidad de {producto.nombre}: "))
                if cantidad <= producto.cantidad:
                    carrito.agregar_producto(producto, cantidad)
                else:
                    print("No hay suficiente stock.")
            else:
                print("Producto no encontrado.")

        elif opcion == '3':
            carrito.mostrar_carrito()

        elif opcion == '4':
            carrito.mostrar_carrito()
            confirmar = input("¿Desea confirmar el pedido? (s/n): ")
            if confirmar.lower() == 's':
                with open("pedido.txt", 'w') as f:
                    f.write("Resumen de pedido:\n")
                    for producto, cantidad in carrito.productos:
                        f.write(f"{producto.nombre} x {cantidad} = {producto.precio * cantidad:.2f}€\n")
                    total = sum([producto.precio * cantidad for producto, cantidad in carrito.productos])
                    f.write(f"Total: {total:.2f}€\n")
                print("Pedido confirmado.")
                print("En el archivo pedido.txt obtendras el ticket. Gracias por su compra.")
                carrito.vaciar_carrito()

        elif opcion == '5':
                nombre_medicamento = input("Ingrese el nombre del medicamento: ")
                GestorProductos.buscar_medicamento_en_api(nombre_medicamento)

        elif opcion == '6':
            limite = float(input("¿Qué limite de precio quieres mirar?"))
            productos_baratos = gestor_productos.filtrar_por_precio(limite)

            print(f"Productos con precio menor o igual a {limite}:")
            for producto in productos_baratos:
                print(f"{producto.nombre} - Precio: {producto.precio:.2f}€")

        elif opcion == '7':
            print("Gracias por usar Farmacia en Línea.")
            break
        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    main()
