# Guion de defensa — TP Final SdS (Grupo G01S2)

**Objetivo: ≤ 12 min.** Presentación online: cada uno lee su parte y "hace que presenta".
Sincronizado con `SdS_TPFinal_2026Q1G01S2_Presentacion.pdf` (17 diapositivas).

## Reparto (bloques contiguos, un solo relevo entre bloques)

| Bloque | Diapos | Presenta | Tiempo aprox. |
|---|---|---|---|
| Apertura + contexto | 1–3 | **Nico** | ~2:40 |
| Modelo y motor (lo técnico) | 4–7 | **Ian** | ~2:30 |
| Simulaciones y primeros resultados | 8–11 | **Keo** | ~2:40 |
| Orden, distribuciones, FD, validación, limitaciones (lo difícil) | 12–16 | **Ian** | ~3:20 |
| Conclusiones | 17 | **Nico** | ~0:45 |

> **Ian** lleva el peso técnico (modelo, física fina y validación). **Nico** abre y cierra;
> **Keo** cuenta el setup y los primeros resultados.

**Tips para practicar online:**
- Al pasar de diapositiva, quien recibe arranca con el relevo ya escrito ("Gracias…", "Sigo yo…").
- Ritmo tranquilo (~150 palabras/min). Si van rápido, sobra tiempo para preguntas.
- Los tiempos son guía: crono al practicar y recortá donde se estiren.

---

## 🎬 GUION

### ▶ Diapo 1 — Portada · **NICO** (~20 s)
> Buenas, somos el grupo G01S2. Yo soy Nico Arias, y me acompañan Keo Dubovitsky e Ian Tognetti.
> Nuestro trabajo es el **diagrama fundamental de vehículos dirigidos por vibración**: reproducimos,
> con un autómata celular de Nagel–Schreckenberg con interacción por contacto, las **tendencias** que
> Patterson y Parisi midieron experimentalmente. Arranco yo con el sistema real.

### ▶ Diapo 2 — El sistema real: VDV · **NICO** (~50 s)
> El sistema experimental son robots comerciales, los Hexbug Nano, de 44 por 15 por 18 milímetros.
> Avanzan por la vibración rectificada de unas cerdas asimétricas. Están confinados en un canal
> **circular** de unos 1313 milímetros, así que es un sistema **unidimensional**, y entran hasta 30
> vehículos. Lo interesante, y por eso se eligió este sistema, es que **interactúan solo por contacto**:
> no tienen percepción remota, no "ven" al de adelante para frenar como un auto. Sus velocidades libres
> son heterogéneas, más o menos uniformes entre 90 y 120 milímetros por segundo. Esto **aísla** la parte
> del diagrama fundamental que se debe solo a las colisiones físicas, sin la reducción voluntaria de
> velocidad del tráfico convencional.

### ▶ Diapo 3 — Lo que mide el experimento · **NICO** (~50 s)
> ¿Qué mide el experimento? Cuatro cosas. Uno: la velocidad media se mantiene **casi constante** a
> densidad baja y media. Dos: **cae entre un 25 y un 40 por ciento** al acercarse a la densidad de
> contacto. Tres: importa el **orden** en que se insertan los vehículos, ordenados por su velocidad
> libre —el orden aleatorio queda **acotado** entre el creciente y el decreciente—. Y cuatro: a
> saturación, con los 30 vehículos, las tres configuraciones **convergen**, a una velocidad que además
> es **menor que la del agente más lento**: hay un colapso colectivo. Nuestro objetivo es reproducir
> estas **tendencias** con un modelo de bajo costo. **Le paso a Ian para el modelo.**

---

### ▶ Diapo 4 — Modelo: NaSch con contacto · **IAN** (~50 s)
> Gracias. El modelo es un autómata celular de Nagel–Schreckenberg sobre una **ruta periódica 1D** de L
> celdas. Cada vehículo ocupa ℓ celdas y tiene velocidad entera, de 0 a su máximo. La actualización es
> **sincrónica**, en el orden R1, R3, R2, R4: acelerar, frenar aleatorio, resolver contactos y mover.
> Lo clave —y es una decisión de diseño— es que **frenamos antes de proyectar los contactos**: como el
> frenado solo puede reducir el avance, proyectar después garantiza que **nunca aparezca un
> solapamiento**. Nuestra modificación al modelo es la Regla 2, la de interacción: la hicimos de
> **contacto puro**. El vehículo avanza libre hasta alcanzar al de adelante; si lo alcanzaría, queda
> pegado a contacto, sin solaparse, y **hereda su velocidad**. La fórmula del desplazamiento es esa: el
> mínimo entre lo que quería avanzar y el hueco más lo que avanza el líder —lo que asegura el
> no-solapamiento.

### ▶ Diapo 5 — Dos variantes de la Regla 2 · **IAN** (~40 s)
> Trabajamos con dos variantes de esa Regla 2. La **oficial, la A**, es contacto puro: sin
> anticipación, flujo libre hasta el contacto, y al alcanzar al líder hereda su velocidad. Es la física
> del experimento, que interactúa solo por contacto. La segunda, la **B**, es la clásica de
> Nagel–Schreckenberg de libro, donde la velocidad se limita al hueco. Esta variante B la usamos **solo
> para validar** el motor contra la solución analítica, en régimen homogéneo, con p igual a cero y
> partículas puntuales. Y subrayo algo importante: la variante de contacto puro **no** se valida contra
> la curva triangular clásica, porque son modelos distintos.

### ▶ Diapo 6 — Calibración · **IAN** (~35 s)
> Calibramos la malla a la geometría del experimento. El paso espacial es un cuarto de milímetro; el
> temporal, un veinticuatroavo de segundo —los 24 cuadros por segundo de la cámara—, lo que da un cuanto
> de velocidad de 6 milímetros por segundo. El vehículo mide 176 celdas, o sea 44 milímetros. Y
> elegimos la pista de 5280 celdas, 1320 milímetros, que es **exactamente 30 veces el largo del
> vehículo**. Eso hace que con 30 vehículos la ruta quede **exactamente llena a contacto**, con la
> densidad de contacto de 1 sobre 44 milímetros.

### ▶ Diapo 7 — Implementación del motor · **IAN** (~40 s)
> El motor está en Java. El paso sincrónico se calcula sobre una **instantánea inmutable** de los huecos
> y las velocidades, así que el resultado **no depende del orden** en que se recorren los vehículos. La
> regla de colisión devuelve el desplazamiento y la velocidad heredada, sin mutar el estado. El
> no-solapamiento está garantizado por construcción y se valida en cada inserción. Para el protocolo
> incremental, cuando agregamos 5 vehículos lo hacemos **por empuje**: los demás se corren lo mínimo, lo
> que nos permite llegar a los 30 exactos. Y algo que la cátedra pide respetar: el motor es
> **determinista** dado el identificador de la realización, y emite **solo variables físicas** —posición
> y velocidad—; el color de las animaciones se deriva después. **Keo sigue con las simulaciones.**

---

### ▶ Diapo 8 — Simulaciones y observables · **KEO** (~50 s)
> Gracias Ian. Los **parámetros** que barremos son el número de vehículos, de 5 a 30, y la probabilidad
> de frenado p, de 0 a 0,4. Usamos dos **protocolos**: uno de N fijo, de 10 mil pasos, y el incremental
> cada 180 segundos, que arranca en 5 y suma 5 hasta 30, con los tres órdenes de inserción. Corremos
> **30 realizaciones** por punto. Del lado de los **observables** —y esto es central para la cátedra—
> todos se calculan **después** de la simulación, sobre los archivos de salida, nunca dentro del motor.
> Calculamos la velocidad media, con el error como el **desvío entre realizaciones** —no un promedio de
> promedios—, la densidad individual como la inversa de la distancia al vecino, y las distribuciones y
> el diagrama fundamental. El estacionario lo elegimos **por inspección**.

### ▶ Diapo 9 — Dinámica: baja y alta densidad · **KEO** (~35 s)
> Acá se ve la dinámica en dos extremos, con N fijo. A la izquierda, **N igual a 5**: es flujo libre,
> los vehículos avanzan casi sin interactuar, rápidos. A la derecha, **N igual a 30**: la ruta está
> llena a contacto, forman un anillo rígido. El **color es la velocidad**. Son fotogramas
> representativos; la animación completa se regenera desde el repositorio.

### ▶ Diapo 10 — Estacionario por inspección · **KEO** (~30 s)
> Antes de medir nada, elegimos el corte del **estacionario**. Y lo hacemos **por inspección**, mirando
> la serie temporal de la velocidad media, **no** descartando un porcentaje fijo —que es lo que pide la
> cátedra—. Se ve que, pasado el transitorio, la serie fluctúa alrededor de un valor estable, y de ahí
> en adelante promediamos.

### ▶ Diapo 11 — Velocidad media vs N (N fijo) · **KEO** (~45 s)
> Esta es la curva respuesta–estímulo con N fijo: velocidad media en función de N, una curva por cada p.
> A densidad baja la velocidad se mantiene casi constante, pero acá hay un punto **sutil e importante**:
> esa meseta **no** está en la velocidad libre media, que es 105, sino en la velocidad del vehículo
> **más lento** presente, alrededor de 90 a 95. En una pista de un carril **sin adelantamiento**, todo
> el sistema se agrupa detrás del más lento. Y en N igual a 30 —la ruta exactamente llena, un punto
> **singular**— el descenso depende de p: con p cero cruza a la velocidad del más lento, pero con p
> mayor que cero el frenado aleatorio del cúmulo lo hace caer por debajo. **Le devuelvo a Ian para el
> efecto del orden.**

---

### ▶ Diapo 12 — Efecto del orden de inserción · **IAN** (~50 s)
> Gracias. Este es el resultado análogo a la **Figura 2** del artículo, con el protocolo incremental:
> la velocidad media según el **orden** en que entran los vehículos. El orden **decreciente** —los más
> rápidos primero— da la mayor velocidad; el **creciente** —los más lentos primero— la menor; y el
> **aleatorio** queda acotado en el medio. Eso reproduce la tendencia del experimento. Y las tres
> configuraciones **convergen a saturación**, en torno a 81 milímetros por segundo con p igual a 0,1,
> que ya está por debajo de los 90 del más lento.

### ▶ Diapo 13 — Distribuciones por orden · **IAN** (~45 s)
> Acá están las distribuciones por N activo, análogas a las **Figuras 3 y 4**. A la izquierda, la
> **densidad**: el pico está en la densidad de contacto, 1 sobre 44 milímetros, y se acentúa al
> aumentar N. A la derecha, la **velocidad**. Un detalle fino: mostramos el orden **creciente**, donde
> la distribución de velocidad es **casi independiente de N** —justamente porque el más lento ya está
> presente desde N igual a 5—. En cambio, en el **decreciente**, que no mostramos acá, la distribución
> sí se corre marcadamente hacia abajo al crecer N, porque va entrando gente más lenta.

### ▶ Diapo 14 — Diagrama fundamental por orden · **IAN** (~40 s)
> El **diagrama fundamental** por orden, análogo a la Figura 5D, confirma toda la estructura: velocidad
> instantánea contra densidad. El orden **decreciente** es la curva de arriba, el **creciente** la de
> abajo, y el **aleatorio** queda acotado entre los dos. La línea punteada marca la densidad de
> contacto, que es el **límite**: por el no-solapamiento duro, no hay densidades por encima de eso. Y la
> velocidad decae al acercarse al contacto, como en el experimento.

### ▶ Diapo 15 — Validación del motor · **IAN** (~40 s)
> Antes de las limitaciones, la **validación**. Acá usamos la variante clásica, la B, en su régimen de
> validez: partículas puntuales, velocidad homogénea, p cero y reparto uniforme. En ese caso hay una
> **solución analítica**: el diagrama fundamental **triangular**, Q igual al mínimo entre ρ por vmax y
> 1 menos ρ. El motor la reproduce **a precisión de máquina** —error del orden de 10 a la menos 16— y
> lo tenemos cubierto además con tests automáticos a tolerancia 10 a la menos 9. Repito el punto: esto
> valida **el motor**; el contacto puro **no** se valida contra esta curva, porque da flujo libre hasta
> el contacto.

### ▶ Diapo 16 — Limitaciones y sensibilidad · **IAN** (~50 s)
> Y acá viene lo más **honesto** del trabajo: las limitaciones. Primero: el modelo impone
> no-solapamiento duro, así que **no** reproduce la cola de densidad por encima del contacto que sí ve
> el experimento —por solapamiento y desalineación—. Segundo: el punto N igual a 30 es **singular**,
> ruta exactamente llena, y depende de que fijemos L en 1320; el experimento tiene 1313. Y tercero, lo
> más importante: la caída de la velocidad por debajo del más lento **requiere p mayor que cero**, y su
> mecanismo —el frenado estocástico de un cúmulo rígido— es **distinto** al del experimento. Es más: a p
> mayor o igual a 0,3 el anillo lleno se **congela** casi por completo, con velocidad cercana a cero,
> que ya no corresponde a ningún régimen experimental; por eso el punto físicamente comparable es
> **p igual a 0,1**. En resumen: reproducimos **tendencias**, no el mecanismo punto a punto. **Nico
> cierra con las conclusiones.**

---

### ▶ Diapo 17 — Conclusiones · **NICO** (~45 s)
> Para cerrar. El autómata celular con interacción por contacto **reproduce las tendencias centrales**
> del diagrama fundamental de estos vehículos: velocidad casi plana a baja densidad y caída cerca del
> contacto. El **orden de inserción** modula el diagrama, con el aleatorio acotado entre el creciente y
> el decreciente, igual que en el experimento. Reproducimos el **pico de densidad** en la densidad de
> contacto y el angostamiento de la distribución de velocidad con N. La caída por debajo del más lento
> la obtenemos en el punto singular con p mayor que cero: es la reproducción de una **tendencia**, con
> un mecanismo distinto al experimental. Y la variante clásica **valida el motor** contra la curva
> triangular analítica. **Muchas gracias; quedamos para las preguntas.**

---

## 🛡️ Machete de preguntas típicas del jurado (por si acaso)

- **¿Por qué L = 1320 y no 1313 del paper?** Para que N=30 cierre exacto a contacto (30·ℓ); el 1313 lo
  discutimos como sensibilidad. A L=1313, N=30 no entra (5252 < 5280 celdas).
- **¿Qué valida exactamente la variante B?** El diagrama fundamental triangular analítico
  Q(ρ)=min(ρ·vmax, 1−ρ), en régimen homogéneo ℓ=1, p=0. El contacto puro NO se valida contra esa curva.
- **¿Cómo eligieron el estacionario?** Por inspección de la evolución temporal (no un % fijo); el corte
  queda registrado en `figures/manifiesto.csv`.
- **¿Por qué la meseta está en ~90 y no en 105?** Pista de un carril sin adelantamiento: todo se agrupa
  detrás del más lento, así que la media queda anclada a su velocidad, no a la libre media.
- **¿El error?** Desvío ENTRE realizaciones (ddof=1), no el de todos los cuadros ni SEM.
- **¿Qué NO reproduce el modelo?** La cola de densidad sobre el contacto, la forma de la distribución de
  velocidad (pico en ~90 vs ~65 del experimento) y el mecanismo del colapso (nuestro colapso a p alto es
  un congelamiento artificial del anillo lleno).
