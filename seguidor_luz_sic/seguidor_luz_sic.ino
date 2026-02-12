/*
 * Seguidor de Luz Event-Driven — Metalenguaje SIC
 * ================================================
 * Implementación del sistema Nested Learning con tres contextos anidados:
 *
 *   Reactivo     {C:inmediato, S:ms, P:hardware}
 *       ↕
 *   Adaptativo   {C:patrones, S:segundos, P:estadística}
 *       ↕
 *   Ambiental    {C:entorno, S:minutos, P:estratégica}
 *
 * Paradigma: event-driven (sin delay(), sin frecuencias fijas).
 * Decaimiento temporal basado en millis(), independiente de velocidad de CPU.
 * Los eventos se propagan y cada contexto "resuena" según sus condiciones.
 *
 * Hardware:
 *   - 2x LDR en A0 (izquierda) y A1 (derecha) con pull-down 10kΩ
 *   - 1x Servo SG90 en Pin 9
 *
 * Desarrollado como parte del Metalenguaje SIC — Miguel y Claude.
 */

#include <Servo.h>

// ============================================================
// CONSTANTES
// ============================================================

// Pines
#define PIN_LDR_IZQ    A0
#define PIN_LDR_DER    A1
#define PIN_SERVO      9

// Parámetros iniciales
#define GANANCIA_INICIAL           0.5
#define ZONA_MUERTA_INICIAL        30
#define TAU_DECAIMIENTO            200.0  // constante de tiempo en ms (vida media de la memoria)
#define UMBRAL_ENERGIA_ADAPTATIVA  500.0
#define MUESTRAS_AMBIENTALES       50
#define GANANCIA_MIN               0.1
#define GANANCIA_MAX               2.0
#define ZONA_MUERTA_MIN            10
#define ZONA_MUERTA_MAX            80

// Cola de eventos
#define MAX_EVENTOS 16

// Servo
#define SERVO_MIN   0
#define SERVO_MAX   180
#define SERVO_CENTRO 90

// Monitor serie
#define INTERVALO_MONITOR 500  // ms entre impresiones

// ============================================================
// TIPOS DE EVENTO
// ============================================================

enum TipoEvento {
  CAMBIO_LUZ,
  MOVIMIENTO,
  AJUSTE_PARAM,
  PATRON,
  CAMBIO_AMBIENTE
};

struct Evento {
  TipoEvento tipo;
  float magnitud;
  unsigned long timestamp;
  int extra;  // dato auxiliar según tipo
};

// ============================================================
// COLA CIRCULAR DE EVENTOS (sin malloc)
// ============================================================

Evento cola[MAX_EVENTOS];
int cola_head = 0;
int cola_tail = 0;
int cola_count = 0;

bool hay_eventos() {
  return cola_count > 0;
}

bool encolar(TipoEvento tipo, float magnitud, int extra) {
  if (cola_count >= MAX_EVENTOS) return false;  // cola llena
  cola[cola_tail].tipo = tipo;
  cola[cola_tail].magnitud = magnitud;
  cola[cola_tail].timestamp = millis();
  cola[cola_tail].extra = extra;
  cola_tail = (cola_tail + 1) % MAX_EVENTOS;
  cola_count++;
  return true;
}

Evento desencolar() {
  Evento e = cola[cola_head];
  cola_head = (cola_head + 1) % MAX_EVENTOS;
  cola_count--;
  return e;
}

// ============================================================
// ESTADO DEL SISTEMA
// ============================================================

Servo servo;
float posicion_servo = SERVO_CENTRO;

// --- Contexto Reactivo ---
float ganancia = GANANCIA_INICIAL;
float zona_muerta = ZONA_MUERTA_INICIAL;

// --- Contexto Adaptativo ---
float energia_acumulada = 0.0;
float error_promedio = 0.0;
float movimiento_promedio = 0.0;
int ciclos_adaptativos = 0;
unsigned long ultimo_decaimiento = 0;  // timestamp del último decaimiento

// --- Contexto Ambiental ---
int muestras_ambientales = 0;
int ajustes_realizados = 0;
int direccion_ultimo_ajuste = 0;  // +1 subió ganancia, -1 bajó
int oscilaciones = 0;
float ganancia_min_actual = GANANCIA_MIN;
float ganancia_max_actual = GANANCIA_MAX;
float zona_muerta_min_actual = ZONA_MUERTA_MIN;
float zona_muerta_max_actual = ZONA_MUERTA_MAX;

// --- Monitor ---
unsigned long ultimo_monitor = 0;

// ============================================================
// LECTURA DE SENSORES Y GENERACIÓN DE EVENTOS
// ============================================================

void leer_sensores_generar_eventos() {
  int ldr_izq = analogRead(PIN_LDR_IZQ);
  int ldr_der = analogRead(PIN_LDR_DER);
  int diferencia = ldr_izq - ldr_der;

  // Si la diferencia supera la zona muerta → evento CAMBIO_LUZ
  if (abs(diferencia) > (int)zona_muerta) {
    encolar(CAMBIO_LUZ, (float)diferencia, (ldr_izq + ldr_der) / 2);
  }
}

// ============================================================
// CONTEXTO REACTIVO
// ============================================================

void reactivo_evaluar(Evento e) {
  if (e.tipo != CAMBIO_LUZ) return;

  float error = e.magnitud;

  // Movimiento proporcional: posición += ganancia × error (normalizado)
  float delta = ganancia * (error / 512.0) * 10.0;
  posicion_servo += delta;

  // Limitar a rango válido del servo
  if (posicion_servo < SERVO_MIN) posicion_servo = SERVO_MIN;
  if (posicion_servo > SERVO_MAX) posicion_servo = SERVO_MAX;

  servo.write((int)posicion_servo);

  // Generar evento MOVIMIENTO con la magnitud del delta aplicado
  encolar(MOVIMIENTO, abs(delta), (int)abs(error));
}

// ============================================================
// CONTEXTO ADAPTATIVO
// ============================================================

void adaptativo_evaluar(Evento e) {
  if (e.tipo != CAMBIO_LUZ && e.tipo != MOVIMIENTO) return;

  // Acumular energía (suma de magnitudes — el decaimiento temporal
  // se aplica en aplicar_decaimiento() basado en millis())
  energia_acumulada += abs(e.magnitud);

  // Actualizar promedios móviles ponderados por evento.
  // El peso α del nuevo evento se calcula según el tiempo desde
  // el último evento: α = 1 - exp(-Δt/τ). Si pasa mucho tiempo
  // sin eventos, el próximo evento "pesa más" (reemplaza memoria vieja).
  // Si los eventos llegan rápido, cada uno pesa poco (promedio estable).
  float alpha = 1.0 - exp(-(float)(millis() - e.timestamp) / TAU_DECAIMIENTO);
  alpha = constrain(alpha, 0.02, 0.5);  // límites prácticos

  if (e.tipo == MOVIMIENTO) {
    float mov_normalizado = min(abs(e.magnitud) / 5.0, 1.0);
    movimiento_promedio = movimiento_promedio * (1.0 - alpha)
                          + mov_normalizado * alpha;
  }

  if (e.tipo == CAMBIO_LUZ) {
    float err_normalizado = min(abs(e.magnitud) / 512.0, 1.0);
    error_promedio = error_promedio * (1.0 - alpha)
                     + err_normalizado * alpha;
  }

  ciclos_adaptativos++;

  // ¿Suficiente energía acumulada para evaluar reglas?
  if (energia_acumulada < UMBRAL_ENERGIA_ADAPTATIVA) return;

  // --- Reglas de adaptación ---
  float ganancia_anterior = ganancia;

  // REGLA 1: Mucho movimiento + error alto → sistema nervioso → reducir ganancia
  if (movimiento_promedio > 0.6 && error_promedio > 0.1) {
    ganancia *= 0.85;
  }

  // REGLA 2: Poco movimiento + error alto → sistema lento → aumentar ganancia
  if (movimiento_promedio < 0.2 && error_promedio > 0.2) {
    ganancia *= 1.15;
  }

  // REGLA 3: Mucho movimiento + error bajo → reducir ganancia innecesaria
  if (movimiento_promedio > 0.8 && error_promedio < 0.06) {
    ganancia *= 0.9;
  }

  // REGLA 4: Ajustar zona muerta según error
  if (error_promedio < 0.05) {
    zona_muerta *= 1.05;  // Error bajo → ampliar zona muerta (menos sensible)
  } else if (error_promedio > 0.3) {
    zona_muerta *= 0.95;  // Error alto → reducir zona muerta (más sensible)
  }

  // Aplicar límites
  ganancia = constrain(ganancia, ganancia_min_actual, ganancia_max_actual);
  zona_muerta = constrain(zona_muerta, zona_muerta_min_actual, zona_muerta_max_actual);

  // Resetear energía acumulada
  energia_acumulada = 0.0;
  muestras_ambientales++;

  // Generar evento si hubo cambio significativo
  if (abs(ganancia - ganancia_anterior) > 0.01) {
    int dir = (ganancia > ganancia_anterior) ? 1 : -1;
    encolar(AJUSTE_PARAM, ganancia, dir);
  }
}

// ============================================================
// CONTEXTO AMBIENTAL
// ============================================================

void ambiental_evaluar(Evento e) {
  if (e.tipo != AJUSTE_PARAM) return;

  ajustes_realizados++;

  // Detectar oscilaciones: si la dirección del ajuste cambia
  int dir = e.extra;
  if (dir != 0 && dir != direccion_ultimo_ajuste && direccion_ultimo_ajuste != 0) {
    oscilaciones++;
  }
  direccion_ultimo_ajuste = dir;

  // ¿Suficientes muestras para evaluación ambiental?
  if (muestras_ambientales < MUESTRAS_AMBIENTALES) return;

  // --- Evaluación del rendimiento global ---
  float ratio_oscilacion = (float)oscilaciones / (float)max(ajustes_realizados, 1);

  if (ratio_oscilacion > 0.5) {
    // Adaptación oscila → ampliar rangos (más libertad para encontrar equilibrio)
    ganancia_min_actual *= 0.9;
    ganancia_max_actual *= 1.1;
    zona_muerta_min_actual *= 0.9;
    zona_muerta_max_actual *= 1.1;
    encolar(CAMBIO_AMBIENTE, ratio_oscilacion, 1);  // 1 = ampliar
  } else if (ratio_oscilacion < 0.2 && ajustes_realizados > 5) {
    // Adaptación converge → estrechar rangos (más preciso)
    float rango_g = ganancia_max_actual - ganancia_min_actual;
    ganancia_min_actual += rango_g * 0.05;
    ganancia_max_actual -= rango_g * 0.05;
    float rango_z = zona_muerta_max_actual - zona_muerta_min_actual;
    zona_muerta_min_actual += rango_z * 0.05;
    zona_muerta_max_actual -= rango_z * 0.05;
    encolar(CAMBIO_AMBIENTE, ratio_oscilacion, -1);  // -1 = estrechar
  }

  // Aplicar límites absolutos a los rangos
  ganancia_min_actual = max(ganancia_min_actual, 0.01);
  ganancia_max_actual = min(ganancia_max_actual, 5.0);
  zona_muerta_min_actual = max(zona_muerta_min_actual, 5.0);
  zona_muerta_max_actual = min(zona_muerta_max_actual, 200.0);

  // Resetear contadores ambientales
  muestras_ambientales = 0;
  ajustes_realizados = 0;
  oscilaciones = 0;
}

// ============================================================
// DECAIMIENTO TEMPORAL
// ============================================================

void aplicar_decaimiento() {
  // Decaimiento basado en TIEMPO REAL, no en ciclos de CPU.
  // Esto garantiza comportamiento idéntico en Arduino Uno (16MHz),
  // ESP32 (240MHz) o cualquier otro procesador.
  //
  // Modelo: valor *= exp(-Δt / τ)  — decaimiento exponencial físico
  // donde Δt = tiempo transcurrido, τ = constante de tiempo

  unsigned long ahora = millis();
  unsigned long delta_ms = ahora - ultimo_decaimiento;

  if (delta_ms == 0) return;  // sin tiempo transcurrido, sin decaimiento

  float factor = exp(-(float)delta_ms / TAU_DECAIMIENTO);

  // La energía acumulada decae naturalmente (como un capacitor)
  energia_acumulada *= factor;

  // Los promedios móviles decaen con constante de tiempo más larga
  // (memoria más persistente que la energía instantánea)
  float factor_lento = exp(-(float)delta_ms / (TAU_DECAIMIENTO * 10.0));
  movimiento_promedio *= factor_lento;
  error_promedio *= factor_lento;

  ultimo_decaimiento = ahora;
}

// ============================================================
// MONITOR SERIE (CSV para Serial Plotter)
// ============================================================

void monitor_serie() {
  unsigned long ahora = millis();
  if (ahora - ultimo_monitor < INTERVALO_MONITOR) return;
  ultimo_monitor = ahora;

  // Formato CSV: pos, ganancia×100, zona_muerta, error×1000, mov×1000, energia,
  //              g_min×100, g_max×100
  Serial.print(posicion_servo);
  Serial.print(",");
  Serial.print(ganancia * 100.0);
  Serial.print(",");
  Serial.print(zona_muerta);
  Serial.print(",");
  Serial.print(error_promedio * 1000.0);
  Serial.print(",");
  Serial.print(movimiento_promedio * 1000.0);
  Serial.print(",");
  Serial.print(energia_acumulada);
  Serial.print(",");
  Serial.print(ganancia_min_actual * 100.0);
  Serial.print(",");
  Serial.println(ganancia_max_actual * 100.0);
}

// ============================================================
// SETUP
// ============================================================

void setup() {
  Serial.begin(9600);
  servo.attach(PIN_SERVO);
  servo.write(SERVO_CENTRO);
  posicion_servo = SERVO_CENTRO;
  ultimo_decaimiento = millis();

  // Cabecera CSV
  Serial.println("pos,ganancia_x100,zona_muerta,error_x1000,mov_x1000,energia,gmin_x100,gmax_x100");
}

// ============================================================
// LOOP PRINCIPAL — Event-Driven (sin delay)
// ============================================================

void loop() {
  // 1. Leer sensores → generar eventos si hay cambio significativo
  leer_sensores_generar_eventos();

  // 2. Propagar todos los eventos a los tres contextos
  while (hay_eventos()) {
    Evento e = desencolar();
    reactivo_evaluar(e);
    adaptativo_evaluar(e);
    ambiental_evaluar(e);
  }

  // 3. Decaimiento temporal (memoria que se disipa naturalmente)
  aplicar_decaimiento();

  // 4. Monitor serie para observación (no afecta la lógica)
  monitor_serie();

  // NO hay delay() — el sistema responde a la velocidad real del hardware
}
