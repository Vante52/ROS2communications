import rclpy
from rclpy.node import Node
from std_msgs.msg import String, UInt32


class Controller(Node):
    """Contiene la lógica del robot; el ESP32 solo ejecuta sus órdenes."""

    def __init__(self):
        super().__init__("controller")
        #TODO: Cree las interfaces de comunicación que corresponden a este modulo (publicadores y subscriptores)
        
        self.warning_active = False
        self.yellow_on = False
        self.create_timer(0.4, self.blink_yellow)

    def convertir_pulso_a_cm(self, pulso_us):
        #TODO:  Investigue cómo convertir el tiempo en distancia en centimetros
        return

    def sensor_callback(self, message):
        distancia_cm = self.convertir_pulso_a_cm(message.data)
        self.get_logger().info(
            f"Distancia: {distancia_cm:.1f} cm"
        )
        #TODO: Coloque aquí la lógica de qué debe ocurrir en cada distancia con sus comandos, recuerde considerar el self.warning_active para el parpadeo del led amarillo
        #CLUE: Aquí es donde usted publica y se refleja el comportamiento en el hardware

    def blink_yellow(self):
        if not self.warning_active:
            return
        self.yellow_on = not self.yellow_on
        self.publish_leds(False, self.yellow_on, False)

    def publish_servo(self, command):
        #TODO: guarde en la interfaz el dato que quiere enviar y publiquelo
        return

    def publish_leds(self, blue, yellow, red):
        #TODO: guarde en la interfaz el dato que quiere enviar y publiquelo
        return

def main(args=None):
    rclpy.init(args=args)
    node = Controller()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()