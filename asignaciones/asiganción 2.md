asignación 2 RPA:



\# TAREA — Bot de WhatsApp con Playwright



\## Objetivo



Crear un bot que envíe un mensaje por WhatsApp Web indicando que la tarea fue finalizada y qué patrones de diseño se utilizaron.



\## Requisitos



\### 1. Mensaje a enviar



El bot debe enviar un solo mensaje con este formato (o similar):



Tarea finalizada.

Patrones utilizados: Builder, Page Object Model, Strategy.

\### 2. Persistencia de sesión (IMPORTANTE)



La primera ejecución va a pedir escanear el QR. Las siguientes no deben pedirlo. Para eso hay que guardar y cargar el storage\_state de Playwright:



\- Si existe la sesión guardada → cargarla y saltar QR.

\- Si no existe → mostrar QR, escanear, y al cerrar guardar la sesión.



\### 3. Gestión del proyecto con PDM



El proyecto debe manejarse con PDM:



pdm init

pdm add playwright

pdm add keyring

keyring se usa para la gestión de credenciales, para este bot la usaremos para guardar el número.



\### 4. Ejecución



El proyecto debe incluir un .bat que ejecute el bot sin cerrar la consola al finalizar.



\### 5. Entrega



\- Subir el proyecto a un repositorio público en GitHub.

\- Compartir el link del repo.



\## Criterios de evaluación



\- El bot envía el mensaje correctamente.

\- La sesión se persiste (no pide QR en la 2da ejecución).

\- El proyecto se gestiona con PDM.

\- El .bat funciona.

\- El repo está en GitHub y es accesible.

