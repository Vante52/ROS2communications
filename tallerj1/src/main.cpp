#include <Arduino.h>
#include <ESP32Servo.h>

//Pines del montaje
const int PIN_SERVO = 2;

const int PIN_TRIG = 5;
const int PIN_ECHO = 17;

const int PIN_LED_AZUL = 18;
const int PIN_LED_ROJO = 4;
const int PIN_LED_AMARILLO = 19;

//Tiempos de lectura para no usar delays bloqueantes
const unsigned long INTERVALO_SENSOR_MS = 100;
const unsigned long TIEMPO_MAXIMO_ECHO_US = 30000;
const unsigned long TIMEOUT_COMANDO_MS = 1500;
const unsigned long INTERVALO_SERVO_MS = 15;

unsigned long ultimaLecturaMs = 0;
unsigned long ultimoComandoMs = 0;
unsigned long ultimoMovimientoServoMs = 0;


// Rangos configurados para el servo
const int ANGULO_MINIMO_COMPLETO = 0;
const int ANGULO_MAXIMO_COMPLETO = 180;
const int ANGULO_MINIMO_MEDIO = 45;
const int ANGULO_MAXIMO_MEDIO = 135;


//Servomotor
Servo servomotor;

//Estados del motor
enum ModoServo {
  SERVO_DETENIDO,
  ROTACION_COMPLETA,
  MEDIA_ROTACION
};

//estado inicial y límites
ModoServo modoServo = SERVO_DETENIDO;
int anguloActual = 90;
int anguloMinimo = 90;
int anguloMaximo = 90;
int direccionServo = 1;


void rotacionCompleta() {
  anguloMinimo = ANGULO_MINIMO_COMPLETO;
  anguloMaximo = ANGULO_MAXIMO_COMPLETO;

  modoServo = ROTACION_COMPLETA;
}

void mediaRotacion() {
  anguloMinimo = ANGULO_MINIMO_MEDIO;
  anguloMaximo = ANGULO_MAXIMO_MEDIO;

  modoServo = MEDIA_ROTACION;
}

void detenerServomotor() {
  // El servo conserva el último ángulo, pero deja de hacer el barrido.
  modoServo = SERVO_DETENIDO;
}

// Hace avanzar el servo un grado cada vez, sin usar delay(). Así el ESP32
// puede seguir atendiendo el sensor y el puerto serial durante el movimiento.
void actualizarServomotor() {
  if (millis() - ultimoMovimientoServoMs < INTERVALO_SERVO_MS) {
    return;
  }
  ultimoMovimientoServoMs = millis();

  anguloActual = anguloActual + direccionServo;

  if (anguloActual >= anguloMaximo) {
    anguloActual = anguloMaximo;
    direccionServo = -1;
  } else if (anguloActual <= anguloMinimo) {
    anguloActual = anguloMinimo;
    direccionServo = 1;
  }

  servomotor.write(anguloActual);
}

// Sensor ultrasonido

// Devuelve el tiempo que tardó el eco
unsigned long leerPulsoUltrasonido() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  // Si no llega eco antes del tiempo máximo, pulseIn devuelve 0.
  return pulseIn(PIN_ECHO, HIGH, TIEMPO_MAXIMO_ECHO_US);
}


void enviarLectura() {
  unsigned long pulsoUs = leerPulsoUltrasonido();
  Serial.print("PULSE_US:");
  Serial.println(pulsoUs);
}

// Leds
void cambiarLeds(bool azul, bool amarillo, bool rojo) {
  digitalWrite(PIN_LED_AZUL, azul ? HIGH : LOW);
  digitalWrite(PIN_LED_AMARILLO, amarillo ? HIGH : LOW);
  digitalWrite(PIN_LED_ROJO, rojo ? HIGH : LOW);
}

//recibe los comandos de ROS2 hacia el motor 
void procesarComandoServo(String comando) {
  if (comando == "SERVO:FULL_ROTATION") {
    rotacionCompleta();
    ultimoComandoMs = millis();
  } else if (comando == "SERVO:HALF_ROTATION") {
    mediaRotacion();
    ultimoComandoMs = millis();
  } else if (comando == "SERVO:STOP") {
    detenerServomotor();
    ultimoComandoMs = millis();
  }
}

//recibe los comandos de ROS2 hacia los leds
void procesarComandoLeds(String comando) {
  // Formato: LEDS:azul,amarillo,rojo. Ejemplo: LEDS:1,0,0
  if (!comando.startsWith("LEDS:") || comando.length() < 10) {
    return;
  }

  bool azul = comando.charAt(5) == '1';
  bool amarillo = comando.charAt(7) == '1';
  bool rojo = comando.charAt(9) == '1';
  cambiarLeds(azul, amarillo, rojo);
}

//Lee lo que llega por comunicación serial (lo que le manda ROS)
void leerComandosSeriales() {
  if (Serial.available() == 0) {
    return;
  }

  String comando = Serial.readStringUntil('\n');
  comando.trim();
  procesarComandoServo(comando);
  procesarComandoLeds(comando);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);

  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_LED_AZUL, OUTPUT);
  pinMode(PIN_LED_AMARILLO, OUTPUT);
  pinMode(PIN_LED_ROJO, OUTPUT);

  servomotor.attach(PIN_SERVO);
  servomotor.write(anguloActual);
  detenerServomotor();
  cambiarLeds(false, false, false);
  ultimoComandoMs = millis();
}

void loop() {
  leerComandosSeriales();
  actualizarServomotor();

  if (millis() - ultimaLecturaMs >= INTERVALO_SENSOR_MS) {
    ultimaLecturaMs = millis();
    enviarLectura();
  }

  // Medida de seguridad: si ROS deja de enviar comandos, el servo deja de
  // recorrer su rango y conserva la última posición alcanzada.
  if (millis() - ultimoComandoMs > TIMEOUT_COMANDO_MS) {
    detenerServomotor();
  }
}
