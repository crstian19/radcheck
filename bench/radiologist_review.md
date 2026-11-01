# RadCheck-Bench-ES v1 — revisión del radiólogo

50 informes del split *test*, estratificados por tipo de ítem. Todos son sintéticos: ningún paciente real.

Marca cada casilla. Si un ítem no es realista o la etiqueta es incorrecta, anota el motivo debajo.

---

## 1. `rcb-0070` — clean_hard

*ecografía · cabeza-cuello · estilo B · 259 palabras · dificultad hard* · negativo difícil: mismo_numero_estructuras_distintas

```text
ECOGRAFÍA DE CABEZA Y CUELLO

TÉCNICA: exploración ecográfica en modo B y Doppler color de región cervical anterior, con transductores lineal de alta frecuencia y convexo según nivel de profundidad.

HALLAZGOS:
- Tiroides: glándula de tamaño y morfología conservados. En lóbulo derecho, nódulo sólido, hipoecoico respecto al parénquima adyacente, de contornos bien definidos y morfología ovalada, de 12 mm en su eje mayor, con vascularización intralesional escasa al Doppler color. En lóbulo izquierdo, nódulo quístico simple de 12 mm, de pared fina, contenido anecoico y refuerzo posterior, sin componente sólido ni septos. Istmo sin alteraciones.
- Glándulas submandibulares: de tamaño normal, ecotextura homogénea, sin lesiones focales ni litiasis visible.
- Glándulas parótidas: simétricas, sin nódulos ni dilatación de conductos.
- Cadenas ganglionares cervicales: se identifican varios ganglios en nivel IIA bilateral y nivel III izquierdo, de morfología ovalada, con hilio graso conservado y cortical fina, con eje corto máximo de 8 mm en nivel IIA derecho. No se observan adenopatías de características sospechosas en los niveles explorados.
- Resto de estructuras: músculos prevertebrales sin alteraciones. Eje vascular carotídeo y yugular permeable, sin placas significativas. Ausencia de colecciones líquidas cervicales.

CONCLUSIÓN:
- Nódulo sólido hipoecoico de 12 mm en lóbulo tiroideo derecho, con rasgos ecográficos indeterminados; se recomienda correlación con PAAF según criterios clínicos.
- Lesión quística simple de 12 mm en lóbulo tiroideo izquierdo, de aspecto benigno.
- Ganglios cervicales reactivos de morfología conservada, sin signos de malignidad en los niveles explorados.
- No se identifican otras alteraciones significativas en las glándulas salivares mayores ni en el compartimento cervical.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 2. `rcb-0089` — negacion

*RX · tórax · estilo A · 105 palabras · dificultad medium*

```text
EXPLORACIÓN: radiografía de tórax en proyección posteroanterior y lateral. HALLAZGOS: campos pulmonares sin condensaciones ni infiltrados. Se identifica derrame pleural bilateral; los senos costofrénicos se hallan libres en ambos lados. Cardiomediastino de contornos normales, con índice cardiotorácico dentro de la normalidad. A nivel de la columna dorsal media se aprecia un aplastamiento vertebral de 8 mm que afecta al cuerpo de D7, con discreta pérdida de altura anterior. Conclusión: no hay signos de derrame en las cavidades pleurales de ningún lado. La silueta cardiovascular no muestra alteraciones. Se objetiva una fractura-aplastamiento del cuerpo vertebral de D7 con reducción de 8 mm de su altura.
```

**Etiqueta:** `negacion`

- fragmento: «Se identifica derrame pleural bilateral»
- contraparte: «no hay signos de derrame en las cavidades pleurales»
- explicación: En hallazgos se afirma la presencia de derrame pleural bilateral, mientras que la conclusión lo niega al indicar que no hay signos de derrame en las cavidades pleurales.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 3. `rcb-0102` — clean_ordinary

*mamografía · mama · estilo B · 278 palabras · dificultad easy*

```text
MAMOGRAFÍA BILATERAL

TÉCNICA: Proyecciones craneocaudal y mediolateral oblicua de ambas mamas. Compresión adecuada. Estudio comparativo con mamografía previa de hace dos años.

HALLAZGOS:
- Mama derecha: nódulo ovalado de 12 mm en unión de cuadrantes superoexternos, de márgenes bien definidos y densidad isodensa respecto al parénquima, sin microcalcificaciones asociadas ni distorsión arquitectónica en su entorno. Aparentemente estable respecto al estudio previo.
- Mama derecha: quiste simple de 8 mm en cuadrante inferior interno, de contornos lisos y contenido homogéneo.
- Mama izquierda: asimetría focal de densidad en cuadrante superoexterno, de 15 mm, sin nódulo dominante ni calcificaciones agrupadas; se recomienda completar estudio con ecografía dirigida.
- Mama izquierda: microcalcificaciones puntiformes dispersas en cuadrante inferior externo, de morfología benigna y distribución difusa.
- Resto del parénquima de patrón fibroglandular heterogéneo, sin otras lesiones focales sospechosas.
- Ganglios axilares bilaterales de aspecto reactivo, sin adenopatías de características patológicas.
- Piel y pezón sin alteraciones significativas.

COMPARACIÓN: Sin cambios significativos respecto a la exploración previa en la mama derecha. La asimetría focal de la mama izquierda no se identificaba claramente en el estudio anterior.

CONCLUSIÓN:
1. Nódulo ovalado de 12 mm en la unión de cuadrantes superoexternos de la mama derecha, de características morfológicas benignas y sin cambios respecto al control previo.
2. Quiste simple de 8 mm en el cuadrante inferior interno derecho, hallazgo incidental sin repercusión.
3. Asimetría focal de 15 mm en el cuadrante superoexterno de la mama izquierda, sin nódulo ni microcalcificaciones agrupadas; se sugiere ecografía dirigida para su caracterización.
4. Microcalcificaciones puntiformes dispersas en el cuadrante inferior externo izquierdo, de patrón benigno.
Se recomienda correlación con ecografía en la mama izquierda y control mamográfico según protocolo.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 4. `rcb-0113` — medida

*ecografía · musculoesquelético · estilo A · 162 palabras · dificultad medium*

```text
EXPLORACIÓN: Ecografía de partes blandas del tobillo derecho.

HALLAZGOS: Tendón de Aquiles de grosor conservado, con ecoestructura fibrilar homogénea y sin signos de tendinosis ni de rotura parcial. En la unión miotendinosa del sóleo, a unos 4 cm de la inserción calcánea, se identifica una formación quística de 8 cm de diámetro máximo, de pared fina y contenido anecoico, compatible con ganglión intratendinoso. El tendón del tibial posterior muestra grosor y ecogenicidad normales, sin líquido peritendinoso. La fascia plantar presenta un engrosamiento de 4,5 mm en su porción proximal, con pérdida de la diferenciación fibrilar habitual. No se observan colecciones líquidas en las vainas tendinosas ni alteraciones del tejido celular subcutáneo adyacente. Los cuerpos musculares explorados conservan su patrón ecográfico normal.

CONCLUSIÓN: Engrosamiento de la fascia plantar proximal derecha de 4,5 mm, hallazgo sugestivo de fascitis plantar. Formación quística de 8 mm en la unión miotendinosa del sóleo, compatible con ganglión intratendinoso. Resto de estructuras tendinosas del tobillo derecho sin alteraciones significativas.
```

**Etiqueta:** `medida`

- fragmento: «identifica una formación quística de 8 cm de»
- contraparte: «Formación quística de 8 mm en la unión»
- explicación: La formación quística se describe en hallazgos con 8 cm de diámetro máximo y en la conclusión con 8 mm, discrepancia de unidades entre ambos apartados.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 5. `rcb-0115` — clean_hard

*ecografía · abdomen-pelvis · estilo C · 340 palabras · dificultad hard* · negativo difícil: laterales_distintos

```text
ECOGRAFÍA ABDOMEN-PELVIS

Se realiza estudio ecográfico abdominal y pélvico en paciente de 47 años, con transductor convexo multifrecuencia, en ayunas y con vejiga parcialmente repleta. Se valora el parénquima hepático, vía biliar, vesícula, páncreas, bazo, riñones, retroperitoneo, así como estructuras pélvicas.

El hígado presenta tamaño conservado, con contorno regular y ecogenicidad homogénea. No se identifican lesiones focales sólidas ni quísticas en el parénquima hepático. La vía biliar intrahepática no está dilatada. El colédoco mide 4 mm, dentro de límites normales. La vesícula biliar es de pared fina, sin litiasis en su interior ni signos de colecistitis. El páncreas se visualiza parcialmente por interposición de gas, sin dilatación del conducto de Wirsung en los segmentos accesibles. El bazo es de tamaño normal, homogéneo, sin lesiones focales.

El riñón derecho mide 108 mm, con grosor cortical conservado y diferenciación corticomedular mantenida; presenta una formación quística simple de 14 mm en el polo inferior, de pared fina y contenido anecoico, sin septos ni calcificaciones. El riñón izquierdo mide 111 mm, con grosor cortical conservado; se identifica una formación quística simple de 22 mm en el tercio medio, de características similares. No se observa dilatación de la vía excretora en ninguno de los dos lados. La aorta abdominal es de calibre normal en el segmento explorado, sin signos de dilatación aneurismática.

En la pelvis, la vejiga presenta pared fina y contenido anecoico, sin ecos móviles en su interior. El útero es de tamaño y morfología normales, con endometrio fino y homogéneo; no se identifican masas anexiales en la exploración transabdominal. El fondo de saco de Douglas está libre. No se detecta líquido libre intraabdominal ni en las gotieras parietocólicas.

IMPRESIÓN DIAGNÓSTICA

Quiste simple cortical de 14 mm en el polo inferior del riñón derecho y quiste simple de 22 mm en el tercio medio del riñón izquierdo, ambos sin criterios ecográficos de complicación. Resto del estudio abdominal y pélvico sin hallazgos significativos: hígado, vía biliar, vesícula, bazo y páncreas accesible dentro de la normalidad, sin dilatación de la vía excretora bilateral ni líquido libre.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 6. `rcb-0120` — clean_ordinary

*TC · columna · estilo D · 205 palabras · dificultad easy*

```text
TC COLUMNA LUMBAR. Técnica: adquisición volumétrica en decúbito supino, cortes axiales de 1 mm con reconstrucciones sagitales y coronales, ventana ósea y de partes blandas. Sin contraste iv. Comparación con estudio previo de hace 14 meses.

HALLAZGOS:
Columna lumbar con alineación conservada en el plano sagital. Discreta rectificación de la lordosis fisiológica.
Cambios degenerativos moderados. Abombamiento discal posterior en L4-L5, de 3 mm, sin compromiso significativo del canal. En L5-S1, protrusión discal central de 4 mm con contacto sobre el saco tecal sin repercusión medular.
Canal raquídeo de amplitud mantenida en los niveles restantes. Agujeros de conjunción libres en L1-L2, L2-L3 y L3-L4.
Articulaciones facetarias con hipertrofia leve bilateral en L5-S1, sin pinzamiento foraminal.
Médula ósea de señal homogénea. No se identifican lesiones líticas ni blásticas. Altura vertebral conservada en todos los cuerpos vertebrales explorados.
Estructuras paravertebrales sin alteraciones destacables. No se observan colecciones ni masas en el espacio epidural.

CONCLUSIÓN:
Protrusión discal central en L5-S1 de 4 mm con contacto sobre el saco tecal, sin signos de compresión. Abombamiento discal posterior en L4-L5 de 3 mm sin repercusión sobre el canal. Hipertrofia facetaria bilateral leve en L5-S1 sin pinzamiento foraminal. Resto de la columna lumbar sin hallazgos significativos. Discreta rectificación de la lordosis lumbar.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 7. `rcb-0129` — clean_hard

*ecografía · abdomen-pelvis · estilo A · 192 palabras · dificultad hard* · negativo difícil: negacion_estructura_distinta

```text
EXPLORACIÓN: Ecografía abdominal-pélvica. HALLAZGOS: Hígado de tamaño y ecogenicidad conservados, sin lesiones focales. Vesícula biliar alitiásica, con pared fina y sin signos de inflamación. Vía biliar intra y extrahepática no dilatada. Páncreas de visualización parcial, sin alteraciones destacables en los segmentos explorados. Bazo homogéneo, de 108 mm de eje mayor. Riñones de morfología y grosor cortical normales, sin dilatación de la vía excretora ni litiasis. No se observan adenopatías retroperitoneales ni mesentéricas de tamaño significativo. Se identifica una adenopatía ilíaca derecha de 11 mm, de morfología ovalada y contornos lisos, hallazgo que puede corresponder a reactividad inespecífica. Útero de tamaño normal, con endometrio fino y ovarios de aspecto ecográfico conservador. No hay líquido libre en el fondo de saco de Douglas. Vejiga con pared regular, bien distendida y sin ecos patológicos en su interior. CONCLUSIÓN: Estudio ecográfico sin alteraciones significativas en el parénquima hepático, la vesícula biliar, el bazo ni los riñones. Destaca únicamente una adenopatía de 11 mm en la fosa ilíaca derecha, sin otras adenopatías retroperitoneales o mesentéricas acompañantes, hallazgo que se recomienda correlacionar con el contexto clínico y valorar seguimiento ecográfico. Aparato genital interno y vejiga sin hallazgos reseñables.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 8. `rcb-0136` — clean_ordinary

*TC · tórax · estilo D · 280 palabras · dificultad easy*

```text
TC TÓRAX. TÉCNICA: adquisición volumétrica sin contraste iv, reconstrucciones axiales de 1 mm y coronales/sagitales. Comparación con TC previa de hace 14 meses.

HALLAZGOS:

Pulmón dcho: nódulo sólido de 8 mm en LSD, lóbulo superior, de márgenes bien definidos, sin calcificación ni cavitación, estable respecto a estudio previo. No otros nódulos significativos en el resto del parénquima dcho.

Pulmón izq: sin masas ni consolidaciones. Leve engrosamiento de septos interlobulillares en LII, base, de predominio subpleural, sin derrame asociado.

Pleura: no neumotórax. Sin derrame pleural bilateral. Engrosamiento pleural apical dcho mínimo, residual, sin cambios.

Mediastino: adenopatías hiliares y mediastínicas no significativas, la mayor de 9 mm en estación 4R, de aspecto reactivo y estable. No adenopatías en estaciones 5, 6 ni 7. Aorta torácica de calibre normal, sin disección. Tronco pulmonar y arterias pulmonares principales sin defectos de repleción.

Corazón: silueta cardiaca de tamaño normal. No calcificaciones coronarias significativas. No derrame pericárdico.

Vía aérea: tráquea centrada. Carina y bronquios principales permeables. No bronquiectasias de predominio central.

Pared torácica: sin lesiones líticas ni blásticas. Partes blandas sin hallazgos.

Abdomen superior incluido: hígado de morfología normal, sin lesiones focales. Vesícula sin litiasis. Bazo y suprarrenales sin alteraciones. Riñones de tamaño y morfología conservados.

CONCLUSIÓN:

1. Nódulo sólido de 8 mm en LSD, sin cambios respecto a estudio previo de hace 14 meses; comportamiento morfológico estable, sin signos de agresividad.

2. Engrosamiento septal interlobulillar leve en LII de predominio subpleural, sin derrame ni consolidación acompañante; hallazgo inespecífico, probablemente de origen fibroso residual.

3. Adenopatía de 9 mm en estación 4R de aspecto reactivo, sin cambios; no adenopatías significativas en otras estaciones.

4. Sin neumotórax ni derrame pleural. Sin masas pulmonares. Resto sin hallazgos relevantes.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 9. `rcb-0139` — clean_hard

*RM · abdomen-pelvis · estilo C · 250 palabras · dificultad hard* · negativo difícil: laterales_distintos

```text
RM ABDOMEN-PELVIS

Técnica: estudio realizado en equipo de 1,5 T, con antena de superficie, adquisición de secuencias potenciadas en T1 y T2 con y sin saturación grasa en planos axial y coronal, y secuencia axial eco de gradiente con saturación grasa tras administración de contraste intravenoso. Se incluye fase de difusión. Se compara con estudio previo de hace once meses.

Hallazgos: hígado de tamaño y contornos normales, sin lesiones focales en el parénquima hepático; la vía biliar intra y extrahepática no está dilatada. Vesícula biliar de pared fina, sin cálculos visibles ni signos de inflamación. Páncreas de morfología y señal conservadas, sin dilatación del conducto pancreático principal. Bazo homogéneo, de dimensiones dentro de la normalidad. Ambos riñones presentan morfología conservada y no muestran hidronefrosis ni lesiones sólidas; la grasa perirrenal es normal. En la columna lumbar se identifica una protrusión discal foraminal izquierda en L3-L4 que contacta con la raíz nerviosa homóloga, sin signos de sufrimiento agudo, y una hernia discal foraminal derecha en L4-L5 que comprime la raíz emergente derecha en ese nivel. El resto de los discos lumbares conserva altura y señal. No se aprecia líquido libre intraabdominal ni colecciones en las regiones declives exploradas. Aparato genital interno sin alteraciones morfológicas destacables en el estudio actual.

IMPRESIÓN DIAGNÓSTICA: Protrusión discal foraminal izquierda en L3-L4, con contacto sobre la raíz nerviosa del mismo lado. Hernia discal foraminal derecha en L4-L5, que comprime la raíz emergente derecha en ese segmento. Resto de la exploración abdominal y pélvica sin hallazgos significativos.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 10. `rcb-0141` — clean_hard

*ecografía · musculoesquelético · estilo A · 73 palabras · dificultad hard* · negativo difícil: negacion_estructura_distinta

```text
EXPLORACIÓN: ecografía de partes blandas del hombro derecho. HALLAZGOS: tendón supraespinoso con engrosamiento hipoecoico de 8 mm en su porción distal, sin rotura completa; bursa subacromiosubdeltoidea con líquido laminar de 3 mm; no se observan adenopatías axilares. Se identifica adenopatía supraclavicular derecha de 12 mm, de morfología ovalada y hilio conservado. CONCLUSIÓN: tendinopatía del supraespinoso sin rotura, con mínima cantidad de líquido bursal subacromiosubdeltoidea. Adenopatía supraclavicular derecha de aspecto reactivo, sin adenopatías axilares.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 11. `rcb-0152` — clean_ordinary

*RM · musculoesquelético · estilo D · 186 palabras · dificultad easy*

```text
RM RODILLA DCHA. ESTUDIO SIN CONTRASTE.

INDICACIÓN: gonalgia dcha de 3 meses de evolución. Antecedente de traumatismo banal.

HALLAZGOS:
Rotura completa del LCA, con retracción de los muñones y edema difuso en la grasa de Hoffa adyacente. Inestabilidad anterior en la exploración dinámica.
Menisco interno: rotura en asa de cubo del cuerno posterior, con fragmento desplazado hacia la escotadura. Menisco externo sin alteraciones significativas.
Cartílago femorotibial interno: fisuración condral de 6 mm en el compartimento central, sin pérdida de espesor completo.
Ligamento colateral medial: engrosamiento y edema periférico de 12 mm de extensión, compatible con esguince de grado II.
Tendón rotuliano íntegro. Aparato extensor sin hallazgos. Escaso derrame articular. No se identifican fracturas ni lesiones óseas focales. Resto de ligamentos y estructuras capsulares sin alteraciones reseñables.

CONCLUSIÓN:
Rotura completa del ligamento cruzado anterior con inestabilidad anterior asociada. Rotura en asa de cubo del cuerno posterior del menisco interno con fragmento desplazado. Esguince de grado II del ligamento colateral medial, con edema de 12 mm. Fisuración condral de 6 mm en el compartimento femorotibial interno. Hallazgos compatibles con lesión ligamentosa y meniscal combinada de la rodilla dcha.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 12. `rcb-0162` — lateralidad

*TC · columna · estilo B · 195 palabras · dificultad hard*

```text
TC DE COLUMNA LUMBAR SIN CONTRASTE

INDICACIÓN: lumbociática derecha de dos meses de evolución.

HALLAZGOS:
- Columna lumbar con alineación conservada. Rectificación de la lordosis fisiológica.
- En el nivel L4-L5 se identifica una hernia discal paracentral derecha de 7 mm de diámetro anteroposterior, que contacta con la raíz descendente derecha de L5 en el receso lateral homónimo.
- Disco L5-S1 con pérdida de señal y abombamiento difuso, sin protrusión focal significativa.
- Cambios degenerativos facetarios en los segmentos L4-L5 y L5-S1, con hipertrofia articular bilateral de predominio derecho.
- Canal raquídeo de amplitud conservada en el resto de niveles. No se observan colecciones epidurales ni signos de compresión medular.
- Cono medular y cono terminal de morfología y señal normales.
- No se identifican fracturas ni lesiones líticas en los cuerpos vertebrales explorados.

CONCLUSIÓN:
1. Hernia discal paracentral derecha en L4-L5 de 7 mm, con contacto sobre la raíz de L5 izquierda en el receso lateral, hallazgo concordante con la clínica referida.
2. Enfermedad discal degenerativa L5-S1 y artropatía facetaria en los dos últimos niveles lumbares, con hipertrofia articular bilateral de mayor expresión en el lado derecho.
3. Resto del estudio sin hallazgos significativos.
```

**Etiqueta:** `lateralidad`

- fragmento: «contacto sobre la raíz de L5 izquierda»
- contraparte: «contacta con la raíz descendente derecha de L5»
- explicación: La raíz de L5 afectada se describe como derecha en los hallazgos y como izquierda en la conclusión.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 13. `rcb-0165` — negacion

*RM · neuro · estilo A · 169 palabras · dificultad hard*

```text
EXPLORACIÓN: RM cerebral sin y con contraste intravenoso. Cortes axiales T1, T2, FLAIR, difusión y secuencias potenciadas en T1 tras contraste, con reconstrucciones sagitales y coronales.

HALLAZGOS: Lesión focal de morfología redondeada en la sustancia blanca periventricular parietooccipital izquierda, de 18 mm de diámetro máximo, hiperintensa en T2 y FLAIR, con realce anular incompleto tras contraste y sin restricción significativa en difusión. Escaso edema vasogénico perilesional. Sistema ventricular de tamaño normal, sin desplazamiento de la línea media. Se identifica captación meníngea patológica. Hiperseñal puntiforme de 4 mm en el centro semioval derecho, inespecífica, sin realce. Estructuras óseas sin alteraciones significativas en el estudio. No hay signos de trombosis venosa en las secuencias realizadas.

CONCLUSIÓN: Lesión parietooccipital izquierda de 18 mm con realce anular incompleto y mínimo edema adyacente, hallazgo que precisa correlación clínica y seguimiento evolutivo. No se observa afectación meníngea realzable ni efecto de masa sobre el sistema ventricular. El foco puntiforme del centro semioval derecho, de 4 mm, carece de traducción patológica clara en este contexto.
```

**Etiqueta:** `negacion`

- fragmento: «Se identifica captación meníngea patológica.»
- contraparte: «No se observa afectación meníngea realzable»
- explicación: En hallazgos se afirma que se identifica captación meníngea patológica, mientras que en la conclusión se niega la afectación meníngea realzable.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 14. `rcb-0169` — clean_hard

*ecografía · musculoesquelético · estilo A · 319 palabras · dificultad hard* · negativo difícil: laterales_distintos

```text
EXPLORACIÓN: Ecografía musculoesquelética de partes blandas de la región aquílea bilateral, con sonda lineal de alta frecuencia (12 MHz), exploración comparativa y estudio en dos planos ortogonales, con maniobras dinámicas de flexoextensión del tobillo. HALLAZGOS: En el tendón de Aquiles derecho se identifica un engrosamiento fusiforme de la porción media, a unos 35 mm de la inserción calcánea, con pérdida de la ecoestructura fibrilar normal y áreas hipoecoicas mal definidas de hasta 9 mm en el eje transversal, sin solución de continuidad completa de las fibras; se acompaña de discretas irregularidades del contorno anterior y de aumento de la vascularización peritendinosa al Doppler color. El tendón de Aquiles izquierdo presenta un foco hipoecoico intrasustancia de 6 mm en el tercio medio, de márgenes mal delimitados, con las fibras adyacentes conservadas y sin signos de rotura ni de bursitis retrocalcánea asociada. En el compartimento muscular posterior profundo del lado derecho, el músculo sóleo muestra una zona de alteración de la ecotextura de 18 x 11 mm, de bordes geográficos, con ecos internos y sin colección líquida, hallazgo que se corresponde con una lesión de tipo fibrilar de bajo grado. La fascia plantar proximal del pie izquierdo muestra un engrosamiento de 4,5 mm en su origen calcáneo, con mínima heterogeneidad ecogénica y sin rotura fascial; en el pie derecho la fascia plantar mide 3 mm y presenta ecoestructura conservada. No se observan colecciones líquidas organizadas, calcificaciones intratendinosas significativas ni signos de tenosinovitis del tibial posterior. El estudio Doppler no muestra flujo intralesional en el foco del tendón izquierdo. CONCLUSIÓN: Tendinopatía crónica del tendón de Aquiles derecho con componente inflamatorio peritendinoso, junto a lesión fibrilar de bajo grado del sóleo ipsilateral. En el lado contrario se objetiva un foco intrasustancia en el tendón de Aquiles izquierdo compatible con tendinopatía focal, así como fascitis plantar proximal izquierda de carácter leve. No se identifican signos de rotura tendinosa completa ni colecciones que requieran drenaje.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 15. `rcb-0172` — clean_ordinary

*mamografía · mama · estilo D · 98 palabras · dificultad easy*

```text
MAMOGRAFÍA BILATERAL. PROYECCIONES CC Y MLO.

HALLAZGOS:
Mama dcha: nódulo espiculado en cuadrante superoexterno, 18 mm, con microcalcificaciones agrupadas asociadas.
Mama izq: distorsión arquitectural focal en unión de cuadrantes superiores, 12 mm.
Resto de parénquima sin alteraciones significativas. Ganglios axilares dchos de aspecto sospechoso, el mayor de 15 mm.

CONCLUSIÓN:
Lesión espiculada de 18 mm en CSE de mama dcha con microcalcificaciones, altamente sugestiva de malignidad. Distorsión arquitectural de 12 mm en unión de cuadrantes superiores de mama izq, a filiar. Adenopatías axilares dchas de 15 mm sospechosas. Se recomienda estudio histológico de ambas lesiones y valoración ganglionar.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 16. `rcb-0179` — clean_ordinary

*RM · neuro · estilo C · 368 palabras · dificultad easy*

```text
RM CEREBRAL Y DE COLUMNA CERVICAL. Estudio realizado en equipo de 1,5 T con antena de cráneo y secuencias potenciadas en T1, T2, FLAIR, difusión y eco de gradiente, así como adquisiciones sagitales en T2 y STIR de columna cervical.

HALLAZGOS

Parénquima encefálico: se identifican varios focos de hiperseñal en secuencias potenciadas en T2 y FLAIR, de morfología ovalada y bordes mal definidos, localizados en la sustancia blanca periventricular y subcortical de ambos hemisferios. El de mayor tamaño se sitúa en la región frontoparietal derecha y mide aproximadamente 8 mm en su eje mayor. No presentan restricción de la difusión ni realce tras la administración de contraste. El resto del parénquima no muestra alteraciones de señal significativas. No se observan lesiones ocupantes de espacio ni signos de efecto masa.

Sistema ventricular: ventrículos laterales de tamaño normal, sin dilatación ni signos de hidrocefalia. Tercer y cuarto ventrículos de morfología conservada. Espacios subaracnoideos de convexidad dentro de límites normales para la edad.

Fosa posterior: cerebelo y troncoencéfalo de morfología y señal normales. No se identifican lesiones en la fosa posterior.

Columna cervical: rectificación de la lordosis cervical fisiológica. Se observa una protrusión discal posterior de base amplia en el nivel C5-C6 que contacta con el saco tecal anterior sin signos claros de compresión medular. En el nivel C6-C7 se aprecia una protrusión discal de 3 mm que no compromete el canal. Los cuerpos vertebrales mantienen altura y señal conservadas. No se identifican lesiones óseas sospechosas ni alteraciones de la médula espinal cervical.

Vascular: sistema arterial intracraneal principal de morfología normal en las secuencias sin contraste. No se identifican aneurismas ni malformaciones vasculares evidentes.

IMPRESIÓN DIAGNÓSTICA

1. Focos múltiples de hiperseñal en sustancia blanca periventricular y subcortical, inespecíficos, compatibles con enfermedad de pequeño vaso o lesiones desmielinizantes de bajo grado; el mayor de ellos, de 8 mm, en la región frontoparietal derecha. Sin signos de actividad inflamatoria aguda.
2. Rectificación de la lordosis cervical con protrusiones discales en C5-C6 y C6-C7, la primera de ellas en contacto con el saco tecal anterior sin compromiso medular.
3. No se observan hallazgos que sugieran hipertensión intracraneal ni lesiones ocupantes de espacio.

Se recomienda correlación clínica y seguimiento evolutivo según criterio del servicio solicitante.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 17. `rcb-0185` — clean_hard

*ecografía · abdomen-pelvis · estilo A · 332 palabras · dificultad hard* · negativo difícil: comparacion_previa

```text
EXPLORACIÓN: Ecografía abdominal-pélvica completa, con transductores convexo de 3,5 MHz y lineal de alta frecuencia para pared abdominal, en ayunas de al menos seis horas. Se revisan hígado, vía biliar, páncreas, bazo, riñones, grandes vasos, retroperitoneo, vejiga y pelvis, con correlación con estudio ecográfico previo aportado por la paciente.

HALLAZGOS: Hígado de tamaño conservado, contorno regular y ecogenicidad homogénea, sin lesiones focales sólidas ni quísticas en los segmentos explorados; no se identifica dilatación de la vía biliar intrahepática. Vesícula biliar distendida, de pared fina, sin cálculos ni lodo en su interior, con colédoco de calibre normal en el segmento visible. Páncreas de morfología y ecotextura conservadas en la porción explorable, sin colecciones peripancreáticas. Bazo homogéneo, de dimensiones dentro de la normalidad, sin lesiones focales. Riñón derecho de tamaño y grosor cortical conservados, sin ectasia pielocalicial ni litiasis, con diferenciación corticomedular mantenida. Riñón izquierdo sin alteraciones significativas, sin dilatación del sistema excretor. Aorta abdominal de calibre normal, sin aneurisma; vena cava inferior permeable. En pelvis, vejiga parcialmente repleta, de pared fina y contenido anecoico, sin cálculos ni masas intraluminales; útero de tamaño normal para la edad, con endometrio fino y ovarios de morfología habitual, sin quistes significativos ni líquido libre en fondo de saco. Como hallazgo relevante, se identifica un nódulo sólido de bordes bien definidos en la vertiente anterior del lóbulo tiroideo izquierdo, incidental en la exploración cervical baja, que previamente media 9 mm y actualmente mide 13 mm, con vascularización central moderada y sin adenopatías cervicales sospechosas en los niveles explorados. No se observan colecciones intraabdominales, adenopatías retroperitoneales de tamaño significativo ni signos de hipertensión portal.

CONCLUSIÓN: Estudio abdominal-pélvico sin alteraciones significativas en hígado, vía biliar, páncreas, bazo, riñones, grandes vasos ni pelvis. Destaca un nódulo sólido en el lóbulo tiroideo izquierdo, incidental, que ha aumentado de tamaño respecto al control previo, pasando de 9 mm a 13 mm en la medición actual, sin adenopatías cervicales asociadas. Se recomienda valoración dirigida de dicho nódulo tiroideo y seguimiento ecográfico según criterios clínicos.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 18. `rcb-0186` — clean_hard

*mamografía · mama · estilo B · 310 palabras · dificultad hard* · negativo difícil: organo_sin_lateralidad

```text
MAMOGRAFÍA BILATERAL

EXPLORACIÓN
Mamografía digital bilateral en dos proyecciones (craneocaudal y mediolateral oblicua). Se completa con ecografía dirigida de la mama derecha y de la axila derecha.

HALLAZGOS
- Mama derecha: en unión de cuadrantes inferiores, a unos 30 mm del pezón, se identifica una opacidad nodular de contornos mal definidos, de aproximadamente 14 mm, con microcalcificaciones agrupadas en su interior. En la ecografía dirigida corresponde a una lesión sólida hipoecoica, irregular, de 13 mm, con sombra acústica posterior. Se realiza punción con aguja gruesa (dos cilindros).
- Mama derecha: nódulo ovalado, bien delimitado, de 9 mm, en cuadrante superoexterno, con aspecto benigno (probable fibroadenoma).
- Axila derecha: adenopatía de 15 mm con pérdida de la diferenciación corticomedular; se practica punción aspirativa con aguja fina.
- Mama izquierda: sin nódulos ni distorsiones de la arquitectura. Microcalcificaciones dispersas de morfología benigna, sin agrupamiento sospechoso.
- Axila izquierda: no se identifican adenopatías significativas.

ESTUDIO DE EXTENSIÓN
Ecografía abdominal dirigida: se visualiza el íleon terminal sin alteraciones parietales ni engrosamiento. El bazo presenta tamaño y ecogenicidad dentro de la normalidad. La aorta abdominal es de calibre normal, sin dilatación aneurismática. El útero muestra morfología conservada, sin colecciones. El páncreas se identifica parcialmente por interposición de gas, sin dilatación del conducto principal. No se observan adenopatías retroperitoneales ni líquido libre.

CONCLUSIÓN
1. Lesión nodular de 14 mm en la unión de cuadrantes inferiores de la mama derecha, con microcalcificaciones agrupadas y correlación ecográfica sospechosa; se ha realizado biopsia con aguja gruesa. Resultado pendiente.
2. Adenopatía axilar derecha de 15 mm con pérdida de la diferenciación corticomedular, estudiada mediante punción aspirativa.
3. Nódulo de 9 mm en el cuadrante superoexterno derecho, de características benignas.
4. Mama izquierda y axila izquierda sin hallazgos sospechosos.
5. Estudio abdominal dirigido sin alteraciones significativas en íleon terminal, bazo, aorta, útero ni páncreas.

Se recomienda correlacionar con los resultados anatomopatológicos.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 19. `rcb-0188` — clean_hard

*TC · neuro · estilo D · 191 palabras · dificultad hard* · negativo difícil: bilateral_asimetrico

```text
TC CRÁNEO SIN CONTRASTE.

TÉCNICA: adquisición volumétrica, cortes axiales de 1 mm, reconstrucciones MPR coronales y sagitales.

HALLAZGOS:
Lesión hipodensa frontopolar izq de 18 x 14 mm, bien delimitada, sin realce tras contraste ni edema perilesional significativo. Compatible con quiste aracnoideo.
Atrofia cortical difusa moderada, con predominio frontotemporal. Surcos de convexidad y cisuras de Silvio prominentes. Ventrículos laterales de tamaño conservado, sin signos de hidrocefalia activa.
Leucoencefalopatía crónica de pequeño vaso: múltiples focos hiperintensos en T2/FLAIR periventriculares y en centros semiovales, bilaterales, con claro predominio dcho (Fazekas 2 dcho, 1 izq).
Antecedente traumático: colección subdural laminar frontoparietal dcha de 5 mm de espesor máximo, sin desplazamiento de la línea media ni efecto compresivo significativo.
Senos paranasales libres. Órbitas sin hallazgos. Estructuras óseas sin lesiones líticas ni fracturas visibles.

CONCLUSIÓN:
1. Colección subdural laminar frontoparietal dcha de escaso grosor, sin repercusión sobre la línea media; control evolutivo recomendado.
2. Quiste aracnoideo frontopolar izq, estable por sus características.
3. Cambios de leucoencefalopatía de pequeño vaso, asimétricos, más acentuados en el hemisferio dcho.
4. Atrofia cortical difusa de predominio frontotemporal, acorde con la edad del paciente.

Sin signos de sangrado intraparenquimatoso ni de herniación.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 20. `rcb-0189` — clean_ordinary

*TC · abdomen-pelvis · estilo A · 78 palabras · dificultad easy*

```text
EXPLORACIÓN: TC abdomen-pelvis con contraste intravenoso. HALLAZGOS: Hígado de morfología normal con lesión hipodensa de 18 mm en segmento VI, compatible con quiste simple. Vesícula biliar sin cálculos. Páncreas y bazo sin alteraciones. Ambos riñones de tamaño y morfología conservados, sin dilatación de la vía excretora. Aorta abdominal de calibre normal. No se identifican adenopatías retroperitoneales ni pélvicas significativas. CONCLUSIÓN: Lesión quística hepática de 18 mm en segmento VI, de aspecto benigno. Resto del estudio sin hallazgos relevantes.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 21. `rcb-0190` — clean_ordinary

*TC · columna · estilo B · 201 palabras · dificultad easy*

```text
TC DE COLUMNA LUMBAR SIN CONTRASTE

TÉCNICA: Adquisición volumétrica en decúbito supino, reconstrucciones sagitales y axiales en ventana ósea y de partes blandas. Sin administración de contraste intravenoso.

HALLAZGOS:
- Discreta pérdida de altura del cuerpo vertebral de L1, con acuñamiento anterior de aproximadamente 4 mm y corticales íntegras; no se identifica línea de fractura aguda ni edema medular en la ventana de partes blandas.
- Hernia discal posterocentral en L4-L5 de 6 mm de diámetro máximo, que contacta con la cara anterior del saco tecal sin comprimirlo de forma significativa.
- Cambios degenerativos facetarios en los niveles L4-L5 y L5-S1, con esclerosis subcondral y mínimos osteofitos marginales.
- Canal raquídeo de calibre conservado en el resto de los niveles explorados; cono medular en situación y morfología normales.
- No se observan lesiones líticas ni blásticas en los cuerpos vertebrales ni en los pedículos. Tejidos paravertebrales sin alteraciones significativas.

CONCLUSIÓN:
Acuñamiento anterior leve del cuerpo vertebral de L1, de 4 mm, sin signos de fractura aguda en el estudio actual. Hernia discal posterocentral en L4-L5 de 6 mm, sin compromiso significativo del saco tecal. Enfermedad degenerativa facetaria en los dos niveles lumbares inferiores. No hay hallazgos sugestivos de lesión ósea secundaria.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 22. `rcb-0194` — lateralidad

*RM · musculoesquelético · estilo B · 192 palabras · dificultad medium*

```text
RM MUSCULOESQUELÉTICO — RODILLA IZQUIERDA

TÉCNICA: Cortes sagitales, coronales y axiales potenciados en T1, DP con saturación grasa y T2 con saturación grasa. Secuencia eco de gradiente en el plano sagital.

HALLAZGOS:
- Menisco interno: rotura horizontal en el cuerpo posterior, de 12 mm de extensión, con línea de rotura que alcanza la cara articular inferior. No se identifica fragmento desplazado.
- Menisco externo: morfología y señal conservadas.
- Cartílago femorotibial interno: pérdida focal de espesor en la vertiente central del cóndilo femoral, de grado intermedio, con algún signo de fisuración superficial.
- Ligamento cruzado anterior: íntegro, con señal homogénea y trayecto normal. Ligamento cruzado posterior sin alteraciones.
- Derrame articular: lámina líquida de 6 mm en el receso suprarrotuliano.
- Partes blandas: discreto edema perimeniscal en relación con la rotura meniscal descrita. Tendón rotuliano y cuádriceps sin cambios significativos.

CONCLUSIÓN:
1. Rotura horizontal del cuerpo posterior del menisco interno de la rodilla derecha, con extensión de 12 mm y sin fragmento desplazado, acompañada de edema perimeniscal.
2. Condropatía focal de grado intermedio en el compartimento femorotibial interno.
3. Derrame articular moderado.
4. Resto de estructuras ligamentosas y meniscales sin hallazgos relevantes.
```

**Etiqueta:** `lateralidad`

- fragmento: «posterior del menisco interno de la rodilla derecha»
- contraparte: «RM MUSCULOESQUELÉTICO — RODILLA IZQUIERDA»
- explicación: El título del estudio indica rodilla izquierda, mientras que la conclusión refiere la rotura meniscal en la rodilla derecha.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 23. `rcb-0197` — clean_ordinary

*ecografía · musculoesquelético · estilo A · 102 palabras · dificultad easy*

```text
EXPLORACIÓN: Ecografía de partes blandas del hombro derecho.

HALLAZGOS: Tendón supraespinoso con engrosamiento fusiforme y áreas de hipoecogenicidad intrasustancia en su tercio distal, sin rotura transtendinosa completa; se objetiva un foco de rotura parcial de 6 mm en la vertiente articular. Bursa subacromiosubdeltoidea con líquido laminar de 2 mm. Tendón largo del bíceps de aspecto conservado. No se identifican colecciones líquidas organizadas ni calcificaciones intratendinosas.

CONCLUSIÓN: Rotura parcial de 6 mm en la vertiente articular del supraespinoso derecho sobre tendinopatía con engrosamiento del tercio distal, junto con mínimo derrame bursal subacromiosubdeltoideo de 2 mm. Sin signos de rotura completa ni colecciones significativas.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 24. `rcb-0208` — clean_ordinary

*RM · musculoesquelético · estilo D · 64 palabras · dificultad easy*

```text
RM RODILLA DCHA.

HALLAZGOS:
Rotura longitudinal del cuerno posterior del menisco interno, de 12 mm, con extensión a la unión capsular. Leve derrame articular. Quiste poplíteo de 18 mm. LCA íntegro. Cartílago rotuliano con fisura superficial focal.

CONCLUSIÓN:
Rotura del cuerno posterior del menisco interno dcho de 12 mm. Quiste poplíteo de 18 mm. Derrame articular leve y fisura condral rotuliana focal. LCA conservado.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 25. `rcb-0210` — negacion

*ecografía · cabeza-cuello · estilo B · 162 palabras · dificultad hard*

```text
ECOGRAFÍA DE CABEZA Y CUELLO

HALLAZGOS:
- Tiroides: glándula de tamaño y ecogenicidad conservados. Nódulo sólido en el lóbulo derecho de 14 mm, hipoecoico, de márgenes regulares y sin microcalcificaciones. No se identifica nódulo en el lóbulo izquierdo.
- Región cervical derecha: adenopatía laterocervical derecha nivel II de 12 mm, de morfología ovalada, con hilio graso conservado y vascularización central.
- Región cervical izquierda: no se observan adenopatías de tamaño significativo en niveles II-IV izquierdos.
- Glándulas submandibulares: de tamaño y ecotextura normales, sin cálculos ni dilatación ductal.
- Glándula parótida derecha: aumento difuso de la ecogenicidad sin lesión focal dominante; parótida izquierda sin alteraciones.

CONCLUSIÓN:
1. Nódulo sólido de 14 mm en el lóbulo tiroideo derecho, sin signos ecográficos de agresividad; se sugiere control evolutivo.
2. Adenopatía de 12 mm en el nivel II derecho, con características ecográficas de benignidad.
3. Hay adenopatías significativas en el lado cervical izquierdo.
4. Cambios difusos en la glándula parótida derecha, sin lesión focal.
```

**Etiqueta:** `negacion`

- fragmento: «Hay adenopatías significativas en el lado cervical izquierdo.»
- contraparte: «no se observan adenopatías de tamaño significativo»
- explicación: En los hallazgos se niegan adenopatías significativas en la región cervical izquierda, mientras que la conclusión las afirma.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 26. `rcb-0214` — negacion

*mamografía · mama · estilo B · 121 palabras · dificultad easy*

```text
MAMOGRAFÍA BILATERAL

HALLAZGOS:
- Mama derecha: nódulo ovalado de 12 mm en unión de cuadrantes superiores, con bordes bien definidos y densidad igual a la grasa circundante.
- Mama derecha: sin microcalcificaciones sospechosas ni distorsión de la arquitectura.
- Mama izquierda: no se identifica nódulo de 12 mm ni masa dominante en unión de cuadrantes superiores.
- Mama izquierda: leve asimetría de densidad glandular en cuadrante inferointerno, sin traducción focal.
- Axilas: sin adenopatías de aspecto patológico.

CONCLUSIÓN:
En la mama derecha se observa una formación nodular de 12 mm en la unión de los cuadrantes superiores, de características benignas. En la mama izquierda hay lesión nodular de 12 mm en esa misma localización. Resto sin hallazgos mamográficos de sospecha.
```

**Etiqueta:** `negacion`

- fragmento: «mama izquierda hay lesión nodular»
- contraparte: «no se identifica nódulo de 12 mm»
- explicación: En los hallazgos se niega la existencia de nódulo de 12 mm en la mama izquierda, mientras que en la conclusión se afirma que hay lesión nodular de 12 mm en esa misma localización.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 27. `rcb-0231` — clean_hard

*TC · abdomen-pelvis · estilo C · 124 palabras · dificultad hard* · negativo difícil: negacion_estructura_distinta

```text
TC ABDOMEN-PELVIS

Se realiza estudio dirigido tras administración de contraste intravenoso. El hígado presenta morfología conservada, con una lesión hipodensa de 18 mm en el segmento VI, de contornos bien definidos, sin realce significativo en fase portal. No se observan adenopatías en cadenas ilíacas ni retroperitoneales. Se identifica adenopatía mesentérica de 14 mm, de morfología redondeada. El páncreas y la vesícula biliar no muestran alteraciones reseñables. Ambos riñones presentan tamaño y grosor cortical normales, sin dilatación de la vía excretora. No hay líquido libre intraabdominal. Vejiga de paredes finas.

IMPRESIÓN DIAGNÓSTICA
Lesión focal hepática de 18 mm en segmento VI, sugestiva de benignidad, a correlacionar con estudios previos. Adenopatía mesentérica de 14 mm, sin adenopatías en territorio ilíaco ni retroperitoneal. Resto sin hallazgos relevantes.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 28. `rcb-0242` — lateralidad

*mamografía · mama · estilo B · 263 palabras · dificultad medium*

```text
MAMOGRAFÍA BILATERAL. PROYECCIONES CC Y OML.

INDICACIÓN: cribado poblacional. Paciente de 58 años, asintomática.

CALIDAD TÉCNICA: posicionamiento y compresión adecuados en las cuatro proyecciones. Densidad mamaria tipo B (ACR).

HALLAZGOS:
- Mama derecha: nódulo de contornos bien definidos, ovalado, en unión de cuadrantes superoexternos, a 32 mm de la piel, de 11 mm de diámetro máximo. Sin microcalcificaciones asociadas.
- Mama derecha: dos calcificaciones grupales redondeadas, de morfología benigna, en cuadrante inferointerno, sin pleomorfismo ni distribución ductal, de 2 mm de extensión conjunta.
- Mama izquierda: nódulo de 9 mm en cuadrante superoexterno, parcialmente ocupado por grasa, compatible con fibroadenoma en involución. Sin cambios respecto a estudio previo de hace dos años.
- Mama izquierda: distorsión arquitectural focal en cuadrante inferocentral, de 8 mm, sin centro denso ni espiculación, estable en controles.
- Axilas: ganglios linfáticos de morfología habitual, con centro graso conservado, en ambas regiones axilares. No se identifican adenopatías sospechosas.
- Piel y pezón sin alteraciones radiológicas significativas.

COMPARACIÓN: estudio de hace 24 meses, sin modificaciones en los hallazgos descritos.

CONCLUSIÓN:
1. Nódulo de 11 mm en la mama izquierda, en la unión de cuadrantes superoexternos, de características radiológicas benignas (BI-RADS 2).
2. Calcificaciones benignas grupales en cuadrante inferointerno derecho, sin criterios de malignidad (BI-RADS 2).
3. Nódulo de 9 mm en cuadrante superoexterno izquierdo y distorsión arquitectural focal de 8 mm en cuadrante inferocentral izquierdo, ambas estables y de apariencia benigna (BI-RADS 2).
4. No se observan hallazgos sospechosos en ninguna de las dos mamas ni en las regiones axilares.

Se recomienda control mamográfico en el programa de cribado habitual.
```

**Etiqueta:** `lateralidad`

- fragmento: «Nódulo de 11 mm en la mama izquierda»
- contraparte: «Mama derecha: nódulo de contornos bien definidos»
- explicación: El nódulo de 11 mm se localiza en la mama derecha en los hallazgos, pero en la conclusión se atribuye a la mama izquierda.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 29. `rcb-0245` — lateralidad

*TC · abdomen-pelvis · estilo A · 327 palabras · dificultad medium*

```text
TÉCNICA: TC de abdomen y pelvis con contraste intravenoso, adquisición helicoidal en fase portal, cortes de 3 mm con reconstrucciones multiplanares. Se compara con estudio previo de hace 14 meses.

HALLAZGOS: El hígado presenta morfología y tamaño conservados, sin lesiones focales de captación anómala en el parénquima. La vesícula biliar está distendida, con pared de grosor normal y sin cálculos radiopacos en su interior. El páncreas muestra una glándula de morfología habitual, sin dilatación del conducto pancreático principal. El bazo es homogéneo y de dimensiones dentro de la normalidad. Ambas glándulas suprarrenales son de morfología y grosor normales. Los riñones presentan tamaño y contorno conservados, sin hidronefrosis ni litiasis de densidad cálcica. El uréter derecho, visualizado hasta su desembocadura, no muestra dilatación.

En el riñón derecho, en el seno renal, se identifica una formación quística de pared fina y contenido homogéneo, de 18 mm de diámetro máximo, sin realce tras la administración de contraste, hallazgo ya presente en el estudio previo y sin cambios significativos en el intervalo. No se observan otras lesiones focales renales.

Aorta abdominal de calibre normal, sin aneurisma ni signos de disección; calcificaciones parietales ateromatosas moderadas en la bifurcación ilíaca. Vena cava inferior permeable. No se identifican adenopatías retroperitoneales de tamaño significativo. El plano muscular y la pared abdominal no muestran alteraciones relevantes.

En la pelvis, la vejiga está distendida, con paredes finas y regulares. El útero presenta tamaño y morfología dentro de la normalidad, sin colecciones líquidas en el fondo de saco de Douglas. No se identifican lesiones óseas líticas ni blásticas en el esqueleto visualizado; cambios degenerativos leves en la charnela lumbosacra. Escaso líquido libre en la pared cólica derecha, sin traducción clínica aparente. No se observa dilatación de asas intestinales ni signos de obstrucción.

CONCLUSIÓN: Quiste simple de 18 mm en el seno renal del riñón izquierdo, sin modificaciones respecto al estudio comparativo y de características benignas. Resto de la exploración abdominal y pélvica sin hallazgos significativos. Ateromatosis ilíaca moderada.
```

**Etiqueta:** `lateralidad`

- fragmento: «riñón derecho, en el seno renal»
- contraparte: «seno renal del riñón izquierdo»
- explicación: En los hallazgos se describe la formación quística en el riñón derecho, mientras que la conclusión la sitúa en el riñón izquierdo.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 30. `rcb-0253` — medida

*ecografía · musculoesquelético · estilo A · 285 palabras · dificultad easy*

```text
EXPLORACIÓN: Ecografía de partes blandas del hombro derecho, con transductores lineal de alta frecuencia y convexa para planos profundos. Estudio comparativo con el lado contralateral. Paciente de 47 años.

HALLAZGOS: Tendón supraespinoso de grosor conservado, con ecogenicidad y patrón fibrilar normales en el vientre muscular y en la porción distal; no se identifican zonas de hipoecogenicidad intratendinosa ni signos de rotura parcial o completa. En la vertiente lateral del troquíter, la bursa subacromiosubdeltoidea se encuentra distendida por líquido anecoico, con pared sinovial fina, en una extensión craneocaudal de 6 mm y longitudinal de 24 cm, sin tabiques internos ni ecos en su interior; el hallazgo se reproduce con la abducción activa y no muestra señal Doppler color en la pared. El tendón del bíceps en la corredera bicipital presenta morfología y ecogenicidad normales, sin líquido peritendinoso. La articulación acromioclavicular muestra un espacio conservado, sin osteofitos significativos ni hipertrofia sinovial. El tendón subescapular y el infraespinoso se exploran sin alteraciones estructurales. El músculo deltoides mantiene un patrón fibrilar homogéneo, sin colecciones intramusculares ni cambios de ecogenicidad. No se observan calcificaciones en la porción insertional de los tendones del manguito rotador. El estudio Doppler no demuestra hiperemia en las estructuras periarticulares exploradas. La movilidad pasiva del hombro durante la exploración no provoca desplazamiento anómalo del tendón largo del bíceps. No hay adenopatías en las fosas supraclavicular ni axilar del lado derecho. No se identifican alteraciones en la cortical ósea accesible del húmero proximal.

CONCLUSIÓN: Bursitis subacromiosubdeltoidea derecha de carácter simple, con una extensión longitudinal de 24 mm, sin signos de sinovitis proliferativa ni de afectación del manguito rotador. Tendinopatía del supraespinoso no evidenciada. Resto de estructuras periarticulares del hombro derecho sin hallazgos significativos en la exploración ecográfica.
```

**Etiqueta:** `medida`

- fragmento: «6 mm y longitudinal de 24 cm»
- contraparte: «extensión longitudinal de 24 mm, sin signos»
- explicación: La medida longitudinal de la bursa aparece como 24 mm en los hallazgos y como 24 cm en la conclusión, con unidad distinta para la misma cifra.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 31. `rcb-0272` — lateralidad

*TC · neuro · estilo D · 191 palabras · dificultad medium*

```text
TC CRÁNEO SIN CONTRASTE. NEURO.

TÉCNICA: adquisición helicoidal volumétrica, cortes axiales de 1 mm con reconstrucciones coronales y sagitales. Sin administración de contraste iv. Comparación con estudio previo de hace 14 meses.

HALLAZGOS:
Parénquima cerebral sin lesiones focales intraaxiales. Surcos y cisternas de amplitud conservada para la edad. Sistema ventricular de morfología y tamaño normales; no se identifica hidrocefalia.
Lesión hipodensa de 12 mm en la sustancia blanca subcortical frontal izq, de márgenes mal definidos, sin captación tras contraste ni efecto de masa significativo sobre el ventrículo lateral adyacente.
Línea media centrada. No se observan colecciones extraaxiales ni signos de herniación.
Cisternas perimesencefálicas libres. Troncoencéfalo y cerebelo sin alteraciones morfológicas.
Senos paranasales neumatizados, sin ocupación de senos maxilares ni celdillas etmoidales. Mastoides bien neumatizadas de forma bilateral.
Estructuras óseas de la bóveda y base craneal sin fracturas ni lesiones líticas visibles.

IMPRESIÓN DIAGNÓSTICA:
1. Lesión hipodensa subcortical frontal dcho de 12 mm, sin realce ni efecto de masa, sugestiva de leucoencefalopatía de pequeño vaso; sin cambios significativos respecto al estudio previo.
2. Resto del parénquima cerebral sin hallazgos relevantes.
3. No se identifican signos de sangrado intracraneal ni de hipertensión intracraneal.
```

**Etiqueta:** `lateralidad`

- fragmento: «Lesión hipodensa subcortical frontal dcho de 12 mm»
- contraparte: «sustancia blanca subcortical frontal izq, de márgenes mal definidos»
- explicación: La lesión se describe en los hallazgos como subcortical frontal izquierda y en la conclusión se cambia a derecha, generando una discordancia de lateralidad entre ambos apartados.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 32. `rcb-0278` — clean_ordinary

*RM · musculoesquelético · estilo B · 168 palabras · dificultad easy*

```text
RM MUSCULOESQUELÉTICO. RODILLA DERECHA

TÉCNICA: Cortes sagitales potenciados en T1 y DP con saturación grasa, y coronales en T2, sin contraste intravenoso.

HALLAZGOS:
- Lesión focal de señal intermedia en DP con saturación grasa en el cuerno posterior del menisco interno, de 8 mm, sin extensión a la superficie articular.
- Rotura parcial del ligamento cruzado anterior, con alteración de señal intrasustancia y continuidad fibrilar conservada.
- Derrame articular de moderada cuantía, con distensión del fondo de saco suprarrotuliano.
- Quiste parameniscal de 12 mm en relación con el cuerpo del menisco externo.
- Cartílago femorotibial interno con irregularidad leve, sin pérdida de espesor significativa.
- Estructuras ligamentosas colaterales y aparato extensor sin alteraciones reseñables.

CONCLUSIÓN:
1. Rotura parcial del ligamento cruzado anterior, sin discontinuidad completa del mismo.
2. Lesión focal de 8 mm en el cuerno posterior del menisco interno, sin signos de rotura completa.
3. Derrame articular moderado y quiste parameniscal de 12 mm adyacente al menisco externo.
4. Cambios degenerativos leves del compartimento femorotibial interno.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 33. `rcb-0279` — clean_hard

*RM · abdomen-pelvis · estilo C · 160 palabras · dificultad hard* · negativo difícil: negacion_estructura_distinta

```text
RM ABDOMEN-PELVIS

Estudio realizado en planos axial y coronal, con secuencias potenciadas en T1, T2 y T1 tras administración de contraste intravenoso.

El hígado presenta contornos lobulados con múltiples lesiones nodulares de hasta 28 mm en el segmento VI, compatibles con metástasis. La vesícula biliar no muestra alteraciones significativas. El páncreas y el bazo presentan morfología y señal conservadas. Ambos riñones muestran realce homogéneo, sin hidronefrosis. No se observan adenopatías en las cadenas ilíacas ni en los territorios retroperitoneales. Se identifica una adenopatía en la región supraclavicular izquierda de 14 mm de eje corto. Llama la atención una lesión quística de 32 mm en el ovario derecho, de aspecto benigno. No hay líquido libre en la cavidad peritoneal.

IMPRESIÓN DIAGNÓSTICA

Lesiones hepáticas múltiples sugestivas de metástasis, con un nódulo dominante de 28 mm en el segmento VI. Adenopatía supraclavicular izquierda de 14 mm. Ausencia de adenopatías en cadenas ilíacas y retroperitoneales. Lesión quística ovárica derecha de 32 mm, probablemente benigna.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 34. `rcb-0293` — clean_hard

*RM · abdomen-pelvis · estilo A · 222 palabras · dificultad hard* · negativo difícil: comparacion_previa

```text
EXPLORACIÓN: RM abdomen-pelvis, estudio con contraste intravenoso y secuencias potenciadas en T1, T2 y difusión. Se dispone de estudio previo para comparación.

HALLAZGOS: Hígado de morfología y tamaño conservados. En el lóbulo hepático derecho, segmento VIII, se identifica una lesión nodular de bordes bien definidos, hiperintensa en T2 y con realce arterial, que mide 18 mm en su eje mayor; en el estudio previo de hace diez meses la misma lesión presentaba un tamaño de 15 mm, apreciándose por tanto un crecimiento discreto. No se observan otras lesiones focales hepáticas. Vesícula biliar sin litiasis ni signos de inflamación. Vía biliar intra y extrahepática de calibre normal. Páncreas, bazo y glándulas suprarrenales sin alteraciones morfológicas significativas. Ambos riñones de tamaño y morfología normales, sin dilatación de la vía excretora ni lesiones focales. En la pelvis, útero de características normales para la edad, sin engrosamiento endometrial ni colecciones anexiales. No se identifican adenopatías retroperitoneales ni pélvicas de tamaño significativo. Escaso líquido libre en fondo de saco, de aspecto fisiológico. Estructuras óseas sin lesiones líticas ni blásticas evidentes.

CONCLUSIÓN: Lesión focal hepática en el segmento VIII de 18 mm, con realce arterial, que ha aumentado de tamaño respecto al control previo, donde medía 15 mm; hallazgo que condiciona seguimiento y correlación. Resto del estudio sin alteraciones relevantes en parénquima hepático, vía biliar, retroperitoneo ni pelvis.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 35. `rcb-0294` — negacion

*ecografía · cabeza-cuello · estilo B · 288 palabras · dificultad hard*

```text
ECOGRAFÍA DE CABEZA Y CUELLO

TÉCNICA: Exploración realizada con transductor lineal multifrecuencia (7-12 MHz) en modo B y Doppler color. Se estudian región cervical anterior y laterales, glándulas submandibulares, parótidas, tiroides y cadenas ganglionares. Se compara con estudio previo de hace 14 meses.

HALLAZGOS:
- Tiroides de tamaño y morfología conservados, con parénquima homogéneo y ecogenicidad normal. Lóbulo derecho de 44 x 17 x 15 mm; lóbulo izquierdo de 42 x 16 x 14 mm; istmo de 3 mm. No se identifican nódulos sólidos ni quísticos en ninguno de los lóbulos.
- En lóbulo tiroideo derecho, no obstante, se aprecia una formación nodular de 9 mm, hipoecoica, de márgenes mal definidos y morfología más alta que ancha, con vascularización intralesional escasa al Doppler color. No presenta microcalcificaciones. No se acompaña de adenopatías regionales sospechosas.
- Glándula submandibular derecha de 28 x 14 mm, de ecoestructura homogénea, sin cálculos ni dilatación ductal. Submandibular izquierda de 26 x 13 mm, sin alteraciones significativas.
- Parótida derecha de 38 x 18 mm y parótida izquierda de 36 x 17 mm, con ecogenicidad grasa normal y sin lesiones focales. No se observan ectasias ductales.
- Cadenas ganglionares yugulares internas y espinales: se identifican ganglios reactivos bilaterales de hasta 8 mm de eje corto, con hilio graso conservado y morfología ovalada. No hay adenopatías de aspecto patológico.
- Estructuras vasculares cervicales permeables, sin trombosis ni placas significativas en carótidas comunes.

CONCLUSIÓN:
Se documenta un nódulo sólido de 9 mm en el lóbulo tiroideo derecho, hipoecoico y con márgenes mal definidos, hallazgo que condiciona seguimiento ecográfico y valoración dirigida. El resto de la glándula tiroides, las glándulas salivales mayores y las cadenas ganglionares cervicales muestran alteraciones reseñables; los ganglios identificados presentan características reactivas.
```

**Etiqueta:** `negacion`

- fragmento: «cadenas ganglionares cervicales muestran alteraciones reseñables»
- contraparte: «sin lesiones focales»
- explicación: En los hallazgos se describe la parótida sin lesiones focales y glándulas salivales sin alteraciones, mientras que en la conclusión se afirma que las glándulas salivales mayores muestran alteraciones reseñables.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 36. `rcb-0305` — clean_hard

*RM · neuro · estilo A · 127 palabras · dificultad hard* · negativo difícil: comparacion_previa

```text
EXPLORACIÓN: RM cerebral con contraste. Comparación con estudio previo de hace 14 meses.

HALLAZGOS: Se identifica una lesión focal de señal hiperintensa en T2/FLAIR en la sustancia blanca periventricular parietal izquierda, de morfología ovoidea y bordes mal definidos, que mide 18 mm en su eje mayor; en el estudio previo medía 12 mm. No presenta realce tras la administración de contraste. Escaso componente de edema vasogénico perilesional. Resto del parénquima cerebral sin lesiones focales significativas. Sistema ventricular de tamaño normal, sin desplazamiento de la línea media. No se observan colecciones extraaxiales.

CONCLUSIÓN: Lesión desmielinizante periventricular parietal izquierda sin realce, que ha aumentado de tamaño respecto al control (de 12 a 18 mm), hallazgo que puede corresponder a progresión de enfermedad desmielinizante. Resto del estudio sin alteraciones reseñables.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 37. `rcb-0307` — lateralidad

*RM · abdomen-pelvis · estilo C · 129 palabras · dificultad easy*

```text
RM ABDOMEN-PELVIS

Se realiza estudio de RM abdominal y pélvico. El hígado presenta un quiste simple de 18 mm en el segmento VI, sin otras lesiones focales. La vesícula biliar no muestra cálculos ni signos de inflamación. El páncreas es de morfología y señal normales. En la fosa ilíaca izquierda se identifica un apéndice de 7 mm de diámetro, sin grasa periapendicular infiltrada. Ambos riñones son de tamaño y señal conservados, sin dilatación de la vía excretora. No se observan adenopatías retroperitoneales ni pélvicas de tamaño significativo. El útero presenta un aspecto normal y los anejos no muestran masas.

IMPRESIÓN DIAGNÓSTICA
Quiste hepático simple de 18 mm en el segmento VI. Apéndice de 7 mm en la fosa ilíaca derecha sin signos inflamatorios. Resto del estudio sin hallazgos relevantes.
```

**Etiqueta:** `lateralidad`

- fragmento: «fosa ilíaca izquierda se identifica»
- contraparte: «Apéndice de 7 mm en la fosa ilíaca derecha»
- explicación: El apéndice se sitúa en la fosa ilíaca derecha en la conclusión, pero en los hallazgos se cambia a fosa ilíaca izquierda.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 38. `rcb-0309` — medida

*ecografía · musculoesquelético · estilo A · 309 palabras · dificultad hard*

```text
EXPLORACIÓN: Ecografía del tendón de Aquiles derecho y de la región aquílea, con sonda lineal de alta frecuencia (12-18 MHz), en decúbito prono y con el pie en ligera flexión dorsal pasiva. Se completa con estudio comparativo del lado contralateral y con maniobras dinámicas de dorsiflexión y flexión plantar.

HALLAZGOS: En el tercio distal del tendón de Aquiles derecho, a unos 35 mm de su inserción calcánea, se identifica un engrosamiento fusiforme de contornos mal definidos que alcanza 11 cm de eje anteroposterior máximo, frente a los 5 mm del tendón contralateral en el mismo nivel. La ecogenicidad está disminuida de forma difusa en esa porción, con pérdida de la arquitectura fibrilar normal y sin solución de continuidad completa de las fibras. A la compresión con el transductor el tendón conserva cierta consistencia, sin colapso. No se observa colección líquida peritendinosa significativa ni calcificaciones intratendinosas. El tendón proximal y la unión miotendinosa muestran grosor y ecopatrón conservados. La grasa de Kager mantiene su aspecto habitual, sin edema adyacente. La cortical posterior del calcáneo es regular, sin entesofitos de gran tamaño en la inserción distal; únicamente se aprecia un discreto remodelado óseo de 3 mm en el borde posterosuperior. La bursa retrocalcánea no está distendida. El nervio sural y los vasos peritendinosos no presentan alteraciones en el plano de estudio. En el lado izquierdo, el tendón de Aquiles es de grosor y ecoestructura normales, sin signos de tendinopatía. La valoración dinámica no muestra pinzamiento del tendón sobre el calcáneo ni luxación de los tendones peroneos. No hay datos de rotura parcial ni complete.

CONCLUSIÓN: Tendinopatía aquílea derecha de tipo degenerativo en el tercio distal, con engrosamiento focal de 11 mm de eje anteroposterior máximo y pérdida de la trama fibrilar habitual, sin rotura ni colección peritendinosa asociada. El tendón contralateral y la inserción calcánea presentan hallazgos dentro de la normalidad.
```

**Etiqueta:** `medida`

- fragmento: «mal definidos que alcanza 11 cm de eje»
- contraparte: «engrosamiento focal de 11 mm de eje anteroposterior»
- explicación: En hallazgos se describe el engrosamiento con 11 cm de eje anteroposterior máximo, mientras que la conclusión lo cifra en 11 mm, con discrepancia de unidades entre ambos extremos del informe.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 39. `rcb-0316` — clean_ordinary

*TC · columna · estilo D · 82 palabras · dificultad easy*

```text
TC COLUMNA LUMBAR.

HALLAZGOS:
Protrusión discal post dcha L4-L5 de 4 mm, sin contacto radicular. Hernia extruida post izq L5-S1 de 8 mm, en contacto con raíz S1 izq. Cambios degenerativos facetarios L4-L5 y L5-S1. Canal óseo lumbar de amplitud conservada. Sin signos de fractura ni lesión ósea lítica.

CONCLUSIÓN:
Hernia extruida L5-S1 post izq de 8 mm con contacto sobre raíz S1 izq. Protrusión L4-L5 post dcha de 4 mm sin compromiso radicular. Artropatía facetaria en los dos últimos niveles lumbares.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 40. `rcb-0324` — negacion

*TC · cabeza-cuello · estilo D · 168 palabras · dificultad hard*

```text
TC CABEZA-CUELLO. TÉCNICA: adquisición helicoidal sin y con contraste iv, cortes de 1 mm, reconstrucciones multiplanares.

HALLAZGOS: Lesión lítica de 18 mm en ángulo mandibular izq, con bordes esclerosos y afectación de la cortical lingual; ausencia de reacción perióstica. Masa laterocervical izq de 26 mm, nivel IIA, hipodensa y con realce periférico irregular, en íntima relación con vena yugular interna izq, que se halla comprimida sin signos de trombosis. Adenopatías subcentimétricas en nivel IB dcho, sin criterios de sospecha. No se identifica captación patológica en la nasofaringe ni en la orofaringe. Glándulas submaxilares y parótidas de morfología y densidad conservadas. Escaleras y musculatura infrahioidea sin alteraciones. Senos maxilares y celdillas etmoidales libres.

IMPRESIÓN DIAGNÓSTICA: 1) Lesión ósea mandibular izq de 18 mm, de aspecto agresivo local, pendiente de correlación anatomopatológica. 2) Adenopatía necrótica nivel IIA izq de 26 mm que comprime la yugular interna homónima; no se objetiva trombosis venosa. 3) Hay adenopatías sospechosas en el nivel IB contralateral. 4) Sin hallazgos significativos en vía aerodigestiva superior.
```

**Etiqueta:** `negacion`

- fragmento: «3) Hay adenopatías sospechosas en el nivel IB»
- contraparte: «Adenopatías subcentimétricas en nivel IB dcho, sin criterios de sospecha»
- explicación: En hallazgos se describen adenopatías subcentimétricas en nivel IB derecho sin criterios de sospecha, mientras que en la conclusión se afirma que hay adenopatías sospechosas en el nivel IB contralateral, negación que se invierte respecto al original.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 41. `rcb-0325` — negacion

*ecografía · abdomen-pelvis · estilo A · 97 palabras · dificultad easy*

```text
EXPLORACIÓN: ecografía abdominal y pélvica. HALLAZGOS: hígado de tamaño normal, sin lesiones focales. Vesícula biliar de pared fina, sin cálculos en su interior. Riñón derecho de 105 mm, sin dilatación de la vía excretora; se observa litiasis en el riñón derecho. Riñón izquierdo de 108 mm, sin alteraciones. Bazo homogéneo, de 112 mm. Vejiga bien repleta, de pared regular. No se identifica líquido libre en pelvis. CONCLUSIÓN: estudio ecográfico sin hallazgos significativos. Destaca únicamente la ausencia de litiasis en el riñón derecho, con riñones de morfología y tamaño conservados y sin dilatación de la vía excretora.
```

**Etiqueta:** `negacion`

- fragmento: «se observa litiasis en el riñón derecho.»
- contraparte: «ausencia de litiasis en el riñón derecho»
- explicación: En los hallazgos se afirma que se observa litiasis en el riñón derecho, mientras que en la conclusión se mantiene la ausencia de litiasis en el riñón derecho.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 42. `rcb-0327` — medida

*RX · tórax · estilo C · 113 palabras · dificultad hard*

```text
RADIOLOGÍA DE TÓRAX

Proyección posteroanterior y lateral. Silueta cardiaca de tamaño normal, con índice cardiotorácico dentro de límites. En el lóbulo superior derecho se identifica una opacidad nodular de bordes mal definidos, de aproximadamente 8 mm de diámetro máximo, que condiciona un signo de la silueta positivo sobre el contorno mediastínico derecho. El resto del parénquima pulmonar no muestra consolidaciones ni derrame pleural. Ángulos costofrénicos libres. Hilios de morfología conservada. Estructuras óseas sin alteraciones reseñables.

IMPRESIÓN DIAGNÓSTICA
Nódulo de unos 18 mm en el lóbulo superior derecho, con contorno mal definido y contacto mediastínico, hallazgo que precisa caracterización mediante tomografía computarizada. No se observan otros infiltrados, derrame pleural ni signos de afectación ósea.
```

**Etiqueta:** `medida`

- fragmento: «mal definidos, de aproximadamente 8 mm de diámetro»
- contraparte: «Nódulo de unos 18 mm en el lóbulo superior derecho»
- explicación: En hallazgos se describe la opacidad nodular de aproximadamente 8 mm de diámetro, mientras que en la conclusión se recoge un nódulo de unos 18 mm.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 43. `rcb-0335` — lateralidad

*RM · abdomen-pelvis · estilo C · 247 palabras · dificultad medium*

```text
RM ABDOMEN-PELVIS

Estudio de resonancia magnética del abdomen y la pelvis en paciente de 58 años, sin datos identificativos disponibles para este informe. Se realiza estudio multiplanar con secuencias potenciadas en T1, T2 y T2 con saturación grasa, tras la administración de contraste intravenoso y adquisición en fases arterial, portal y tardía.

El hígado presenta morfología y tamaño conservados, sin lesiones focales de carácter significativo en los segmentos explorados. La vesícula biliar se identifica distendida y sin cálculos en su interior; no se aprecia dilatación de la vía biliar intra ni extrahepática. El páncreas muestra una morfología normal, sin colecciones peripancreáticas. El bazo es de tamaño homogéneo y sin alteraciones focales. Los riñones presentan un parénquima de grosor conservado, sin dilatación de los sistemas pielocaliciales. Se visualiza un quiste simple en el riñón derecho, de 22 mm, de contenido homogéneo y pared fina, sin realce tras el contraste.

En la pelvis se identifica un útero de características normales para la edad, sin engrosamientos endometriales ni colecciones en el fondo de saco. Los ovarios no presentan formaciones quísticas de gran tamaño. No se observan adenopatías iliacas ni inguinales significativas. La vejiga muestra pared fina y contenido homogéneo.

IMPRESIÓN DIAGNÓSTICA

Estudio sin signos de enfermedad infiltrativa abdominal ni de adenopatías de tamaño patológico. El hallazgo más relevante corresponde a una formación quística simple de 22 mm en el riñón izquierdo, de aspecto benigno, que conviene correlacionar con estudios previos si los hubiera. Resto de la exploración sin alteraciones significativas.
```

**Etiqueta:** `lateralidad`

- fragmento: «quiste simple en el riñón derecho, de 22»
- contraparte: «en el riñón izquierdo, de aspecto benigno»
- explicación: El quiste renal se describe en el riñón izquierdo en los hallazgos (tras el cambio, derecho) y en el riñón izquierdo en la conclusión, con lateralidades distintas.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 44. `rcb-0351` — medida

*ecografía · musculoesquelético · estilo C · 123 palabras · dificultad hard*

```text
Ecografía musculoesquelética de hombro derecho. Se explora el tendón supraespinoso, que muestra un engrosamiento fusiforme de morfología conservada, con una zona de heterogeneidad interna en su porción distal de 9 mm de eje mayor, sin retracción de las fibras ni pérdida de continuidad completa. El tendón infraespinoso y el subescapular presentan ecoestructura y grosor normales. La bursa subacromiosubdeltoidea no está distendida. En la articulación acromioclavicular se identifica un discreto pinzamiento del espacio articular con mínima hipertrofia capsular, sin derrame. No se observan calcificaciones intratendinosas ni alteraciones del perfil cortical de la tuberosidad mayor.

IMPRESIÓN DIAGNÓSTICA: Tendinopatía del supraespinoso con foco de heterogeneidad distal de 8 mm, sin rotura completa. Cambios degenerativos leves en la articulación acromioclavicular. Resto de estructuras exploradas sin alteraciones significativas.
```

**Etiqueta:** `medida`

- fragmento: «interna en su porción distal de 9 mm»
- contraparte: «foco de heterogeneidad distal de 8 mm»
- explicación: La medida del foco de heterogeneidad distal se consigna como 8 mm en los hallazgos y como 9 mm en la conclusión, con errata de dígito.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 45. `rcb-0361` — medida

*RM · neuro · estilo A · 105 palabras · dificultad easy*

```text
EXPLORACIÓN: RM cerebral sin contraste. HALLAZGOS: Estudio de RM cerebral que incluye secuencias potenciadas en T1, T2, FLAIR y difusión. Se identifica una lesión hiperintensa en FLAIR y T2 en la sustancia blanca periventricular izquierda, de morfología ovoidea y 12 cm de eje mayor, sin restricción de la difusión ni captación tras contraste. No se observan otras lesiones supratentoriales ni infratentoriales. Ventrículos de tamaño y morfología normales, con surcos corticales conservados para la edad. No hay signos de sangrado ni colecciones extraaxiales. CONCLUSIÓN: Lesión desmielinizante inespecífica de 12 mm en la sustancia blanca periventricular izquierda, sin signos de actividad. Resto del estudio sin hallazgos relevantes.
```

**Etiqueta:** `medida`

- fragmento: «morfología ovoidea y 12 cm de eje»
- contraparte: «de 12 mm en la sustancia blanca»
- explicación: La medida de la lesión aparece como 12 mm en los hallazgos y como 12 cm en la conclusión, en frases contiguas dentro de los hallazgos.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 46. `rcb-0364` — negacion

*ecografía · cabeza-cuello · estilo D · 164 palabras · dificultad easy*

```text
ECOGRAFÍA DE CUELLO

HALLAZGOS:
Tiroides de tamaño normal, morfología homogénea, sin nódulos ni áreas de fibrosis. Glándula tiroides sin alteraciones ecográficas significativas.
No se identifican adenopatías patológicas en las cadenas yugulocarotídeas ni en el espacio submandibular. No hay adenopatías de aspecto sospechoso en los niveles II, III, IV y VI.
En región submandibular dcha, se observa una imagen quística de 8 mm, de pared fina, sin vascularización interna, compatible con quiste de retención. No se aprecia componente sólido ni calcificaciones en su interior.
Glándulas submandibulares de tamaño y ecogenicidad conservados, sin dilatación de los conductos excretores. La glándula parótida dcha presenta ecogenicidad homogénea, sin lesiones focales. Parótida izq sin hallazgos reseñables.
Vascularización carotídea y yugular simétrica, sin trombosis ni estenosis significativas. No se observan placas de ateroma en los ejes carotídeos.

CONCLUSIÓN:
Quiste de retención submandibular dcho de 8 mm, sin signos de complicación. Tiroides y glándulas salivales mayores sin alteraciones ecográficas. Presencia de adenopatías cervicales patológicas. Estudio vascular cervical dentro de la normalidad.
```

**Etiqueta:** `negacion`

- fragmento: «Presencia de adenopatías cervicales patológicas.»
- contraparte: «No se identifican adenopatías patológicas»
- explicación: La conclusión afirma adenopatías cervicales patológicas mientras los hallazgos indican que no se identifican adenopatías patológicas.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 47. `rcb-0365` — lateralidad

*ecografía · musculoesquelético · estilo A · 130 palabras · dificultad medium*

```text
EXPLORACIÓN: Ecografía de partes blandas del tobillo derecho. HALLAZGOS: En la cara lateral del tobillo izquierdo, sobre el ligamento peroneoastragalino anterior, se identifica una colección líquida de 14 x 6 mm, de morfología fusiforme y contenido anecoico, sin señal Doppler en su interior. El tendón peroneo corto presenta un engrosamiento fusiforme de 9 mm de eje anteroposterior, con pérdida de su patrón fibrilar habitual y mínima vascularización peritendinosa. El tendón peroneo largo es de aspecto conservado. No se observan calcificaciones ni fragmentos óseos en el seno del líquido peritendinoso. CONCLUSIÓN: Colección líquida de 14 x 6 mm en la vertiente lateral del tobillo derecho, en relación con el ligamento peroneoastragalino anterior, junto con tendinopatía del peroneo corto con engrosamiento de 9 mm. Los hallazgos sugieren un componente inflamatorio peritendinoso asociado.
```

**Etiqueta:** `lateralidad`

- fragmento: «cara lateral del tobillo izquierdo, sobre»
- contraparte: «vertiente lateral del tobillo derecho»
- explicación: La colección líquida se sitúa en la cara lateral del tobillo izquierdo en los hallazgos, mientras que la conclusión la refiere al tobillo derecho.

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 48. `rcb-0372` — clean_hard

*TC · columna · estilo D · 199 palabras · dificultad hard* · negativo difícil: organo_sin_lateralidad

```text
TC COLUMNA LUMBAR. 

TÉCNICA: cortes axiales de 1,25 mm con reconstrucciones sagitales y coronales. Sin CIV. 

HALLAZGOS: 

Columna lumbar con pérdida de altura discal L4-L5 y L5-S1, esta última con deshidratación del disco. Protusión discal central L4-L5 de 4 mm que contacta con cara anterior del saco tecal sin comprimirlo. Hernia foraminal izq L5-S1 de 6 mm que oblitera el foramen izq y contacta con raíz L5 izq. Canal medular libre en el resto de niveles. 

Cambios degenerativos facetarios en L4-L5 y L5-S1 bilaterales, más acusados en lado dcho. Hipertrofia de ligamentos amarillos en L4-L5. 

Cuerpos vertebrales con altura conservada. No fracturas ni lesiones líticas. 

Estructuras vecinas: aorta abdominal de calibre normal, sin dilatación aneurismática. Bazo de tamaño y morfología conservados. Páncreas sin alteraciones morfológicas. Asas de íleon en fosa ilíaca dcha sin engrosamiento parietal ni dilatación. Útero de morfología normal, sin colecciones en fondo de saco. 

CONCLUSIÓN: 

1. Discopatía degenerativa L4-L5 y L5-S1 con protusión central L4-L5 sin repercusión sobre saco tecal. 
2. Hernia foraminal izq L5-S1 con contacto sobre raíz L5 izq; correlacionar con clínica radicular. 
3. Artropatía facetaria L4-L5 y L5-S1, predominante en lado dcho. 
4. Sin hallazgos significativos en aorta, bazo, páncreas, íleon ni útero.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 49. `rcb-0387` — clean_ordinary

*RM · columna · estilo C · 245 palabras · dificultad easy*

```text
RM DE COLUMNA LUMBAR

Se realiza estudio de resonancia magnética de la columna lumbar en paciente de 47 años, sin contraste intravenoso, con cortes sagitales y axiales potenciados en T1 y T2.

Alineación vertebral conservada, con lordosis fisiológica mantenida. No se observan escalones ni listesis significativas.

En el plano discal L4-L5 se identifica una hernia discal central paramedial derecha de 9 mm de extensión craneocaudal, que contacta con la raíz descendente derecha en el receso lateral sin desplazarla de forma evidente. El disco L5-S1 muestra una protrusión difusa de 4 mm sin compromiso foraminal significativo. En el nivel L3-L4 el disco aparece deshidratado, sin abombamiento relevante.

El canal raquídeo presenta un diámetro anteroposterior conservado en los niveles superiores. En L4-L5 se aprecia una estenosis foraminal derecha moderada en relación con la hernia descrita, con reducción del agujero de conjunción de ese lado. Los agujeros foraminales izquierdos se mantienen permeables en todos los niveles explorados.

Los cuerpos vertebrales presentan altura y señal medular normales, sin fracturas ni lesiones focales sospechosas. No hay signos de inflamación en las articulaciones interapofisarias ni en los ligamentos longitudinales. La médula ósea no muestra alteraciones de señal destacables.

Las estructuras paravertebrales visualizadas no presentan hallazgos reseñables.

IMPRESIÓN DIAGNÓSTICA

Hernia discal central paramedial derecha en L4-L5, de 9 mm, que condiciona una estenosis foraminal derecha moderada en ese nivel. Protrusión discal difusa en L5-S1 de 4 mm, sin repercusión foraminal significativa. Disco L3-L4 deshidratado sin abombamiento. Resto del estudio sin alteraciones relevantes.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---

## 50. `rcb-0392` — clean_ordinary

*ecografía · cabeza-cuello · estilo D · 308 palabras · dificultad easy*

```text
ECOGRAFÍA DE CABEZA Y CUELLO

TÉCNICA: sonda lineal multifrecuencia 7-15 MHz. Exploración en modo B y Doppler color. Estudio de glándulas submaxilares, parótidas, tiroides, cadenas laterocervicales y región supraclavicular. Sin contraste. Comparación con estudio previo de hace 14 meses.

HALLAZGOS:

Tiroides de tamaño y morfología conservados. Lóbulo dcho de 42 x 15 x 13 mm. Lóbulo izq de 38 x 14 x 12 mm. Istmo de 3 mm. Parénquima homogéneo, sin nódulos dominantes. Vascularización intraparenquimatosa normal al Doppler color.

Nódulo sólido en lóbulo tiroideo izq, tercio medio, de 9 x 7 mm, hipoecoico, de márgenes bien definidos, sin microcalcificaciones ni flujo intralesional significativo. Sin crecimiento respecto al estudio previo (9 x 6 mm).

Glándula submaxilar dcha de 28 x 16 mm, ecotextura homogénea, sin cálculos ni dilatación ductal. Submaxilar izq de 26 x 15 mm, sin alteraciones.

Parótida dcha de 44 x 22 mm y parótida izq de 42 x 21 mm, de ecogenicidad normal, sin lesiones focales ni quistes. Conductos de Stenon no dilatados.

Cadenas laterocervicales: adenopatías reactivas bilaterales en niveles IIA, de hasta 11 mm de eje corto, con hilio graso conservado y morfología ovalada. No se identifican adenopatías de características sospechosas en niveles III, IV, V ni VI. Región supraclavicular libre.

Estructuras vasculares: carótidas comunes y bulbos sin placas significativas, con flujo conservado. Venas yugulares internas permeables, sin trombosis.

Glándulas salivales menores y espacio parafaríngeo sin hallazgos. Musculatura cervical y tejido celular subcutáneo sin alteraciones. No se observan colecciones líquidas ni trayectos fistulosos.

CONCLUSIÓN:

1. Nódulo sólido hipoecoico de 9 x 7 mm en lóbulo tiroideo izq, estable en el tiempo, sin signos ecográficos de sospecha. Seguimiento ecográfico recomendado.

2. Adenopatías reactivas bilaterales en nivel IIA de hasta 11 mm de eje corto, con hilio conservado, de aspecto benigno.

3. Tiroides, glándulas submaxilares y parótidas sin otras alteraciones focales. Estudio vascular cervical sin hallazgos significativos.
```

**Etiqueta:** sin incoherencias (informe limpio)

- [ ] realista
- [ ] el error es verificable solo con el texto
- [ ] etiqueta correcta

Notas: 

---
