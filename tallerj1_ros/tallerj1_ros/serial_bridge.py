import serial
from serial.tools import list_ports

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, UInt32
from std_srvs.srv import SetBool, Trigger


class SerialBridge(Node):
    """Traduce líneas seriales a mensajes ROS 2 y viceversa."""

    def __init__(self):
        super().__init__("serial_bridge")

        self.declare_parameter("port", "auto")
        self.declare_parameter("baudrate", 115200)
        requested_port = self.get_parameter("port").value
        baudrate = self.get_parameter("baudrate").value
        port = self.find_serial_port(requested_port)

        self.serial = serial.Serial(port, baudrate, timeout=0.01)
        self.leds = [False, False, False]  # azul, amarillo, rojo
        
        #TODO: Cree las interfaces de comunicación que corresponden a este modulo (publicadores y subscriptores)

        # TODO: Cree las interfaces de los servicios pedidos en el enunciado

        self.create_timer(0.01, self.read_serial)
        self.get_logger().info(f"Puente abierto en {port} a {baudrate} baudios")

    def find_serial_port(self, requested_port):
        """Devuelve el puerto indicado o detecta automáticamente el ESP32."""
        if requested_port != "auto":
            return requested_port

        candidates = []
        for port in list_ports.comports():
            if port.device.startswith(("/dev/ttyUSB", "/dev/ttyACM")):
                candidates.append(port.device)

        if not candidates:
            raise RuntimeError(
                "No se encontró el ESP32. Conéctelo o indique port:=/dev/ttyUSB0"
            )

        candidates.sort()
        return candidates[0]

    def send_line(self, text):
        self.serial.write((text + "\n").encode("utf-8"))

    def read_serial(self):
        while self.serial.in_waiting > 0:
            line = self.serial.readline().decode("utf-8", errors="ignore").strip()
            if not line.startswith("PULSE_US:"):
                continue
            # Publicación de la distancia recibida por platformio   
            try:
                pulse_us = int(line.split(":", 1)[1])
                message = UInt32()
                #TODO: Publique la distancia
            except ValueError:
                self.get_logger().warning(f"Lectura serial inválida: {line}")

    def servo_callback(self, message):
        # el mensaje esperado es "FULL_ROTATION" o "HALF_ROTATION" o "STOP"
        #TODO: Implemente el callback
        return
    def leds_callback(self, message):
        # El mensaje esperado es: "azul,amarillo,rojo", por ejemplo "1,0,0".
        parts = message.data.replace(" ", "").split(",")
        if len(parts) != 3 or any(value not in ("0", "1") for value in parts):
            self.get_logger().warning("Comando de LED no válido")
            return
        self.leds = [value == "1" for value in parts]
        self.send_leds()

    def send_leds(self):
        values = ["1" if enabled else "0" for enabled in self.leds]
        self.send_line("LEDS:" + ",".join(values))

    def servo_service(self, command, response):
        #TODO: Implemente el servicio
        return
    def full_rotation_service(self, request, response):
        #TODO: Implemente el servicio
        return

    def half_rotation_service(self, request, response):
        #TODO: Implemente el servicio
        return
    
    def stop_service(self, request, response):
        #TODO: Implemente el servicio
        return
    def led_service(self, index, enabled, response):
        #TODO: Implemente el servicio
        return
    def blue_service(self, request, response):
        #TODO: Implemente el servicio
        return

    def yellow_service(self, request, response):
        #TODO: Implemente el servicio
        return 

    def red_service(self, request, response):
        #TODO: Implemente el servicio
        return 

    def destroy_node(self):
        if self.serial.is_open:
            try:
                self.send_line("SERVO:STOP")
            except serial.SerialException:
                pass
            self.serial.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
