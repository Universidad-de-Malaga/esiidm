��    �      �      �      �  V   �  R   �  �   G     	  o   �  U   �  K   O  �   �  L   3  �   �  j     �   �  F       \  D   ^  �   �  �   W  �   D  [   �  m   3  4   �  �   �  <   |  }   �  X   7  +   �  0   �  *   �  .        G     S     b     w     �     �     �     �     �     �     �     �  "   �       ,   5     b     �     �     �     �     �     �     �     �     �  /        1     O     g     o  
   v  
   �  
   �     �     �     �     �     �     �     �     �                (     6     >     K     a     ~  "   �  	   �     �      �     �     �          /     3     @     P     a     �     �     �     �  6   �  @     +   B     n     {     �     �     �  
   �     �     �     �           #   
   3   
   >      I      _      g      l   #   q      �      �      �      �      �   	   !     !     '!     A!     M!     S!     k!     �!  ;   �!     �!     �!     �!  %   �!     "     "     *"     D"     T"     ]"     `"     h"     p"     �"     �"     �"     �"     �"  N   �"     #     #  1   %#  !   W#  	   y#  $   �#  ,   �#     �#     �#     �#  -   $  
   B$     M$     m$     �$  	   �$     �$     �$     �$     �$      %     %     +%  
   =%     H%     Y%     a%     f%     j%     v%  0   �%     �%     �%     �%  	   	&  -   &  &   A&     h&     �&  +   �&  ,   �&  +   �&     '  %   ('     N'     e'     |'     �'  #   �'     �'     �'     �'     	(     (     *(     :(     P(     e(     n(     �(     �(     �(     �(  "   �(  &   )  "   <)  &   _)  �  �)  A   +  4   X+  �   �+  z   B,  {   �,  H   9-  C   �-  �   �-  F   o.  �   �.  �   o/  �   �/  X   �0  �   �0  T   �1  �   2  	  �2  �   �3  g   �4  �   �4  7   5  �   �5  H   h6  �   �6  J   T7  *   �7  <   �7  )   8  E   18     w8     �8     �8     �8     �8     �8     �8     �8     �8     9     9     :9  ,   S9     �9  /   �9  +   �9     �9     �9     :     +:     F:     ^:  +   |:     �:     �:  E   �:      ;     ';     E;     K;  
   Q;     \;     m;     ;  	   �;     �;     �;     �;     �;     �;     <     <  4   )<     ^<     k<     s<     �<  +   �<     �<  -   �<  	   =  	   =  #   $=     H=  $   P=  !   u=     �=     �=     �=     �=  -   �=     >  1   %>     W>     w>  4   �>     �>  &   �>     ?  #   ?  $   3?     X?     ^?     x?      �?     �?     �?     �?     �?     @     @     )@     C@     I@     O@  ,   U@     �@  %   �@  -   �@     �@  '   A     .A  .   :A  ,   iA     �A     �A     �A     �A     �A  D   �A     ?B     FB  !   IB  `   kB  	   �B     �B     �B      C     C      C     #C  !   +C  4   MC  !   �C     �C     �C     �C     �C  d   �C     CD     ^D  =   gD  -   �D  	   �D  5   �D  (   E     <E     RE     fE  4   ~E     �E  3   �E  /   �E  "   &F  
   IF     TF     eF  &   {F  *   �F      �F     �F     G  
    G     +G  
   @G     KG     SG  	   WG  #   aG  @   �G     �G     �G     �G     �G  4   H  =   =H     {H     �H  6   �H  9   �H  /   I     MI  -   RI  H   �I  H   �I  H   J  H   [J  E   �J  :   �J  /   %K  ,   UK     �K     �K  0   �K     �K     �K     L     L  $   3L  !   XL     zL  +   �L  )   �L  1   �L  +   "M  '   NM   
              C for creating a new card, this is the default if absent
               
              D for deleting the card if it belongs to the student
               
        If first_name and last_name are present,
        the person is created in the system if needed.<br>
        If they are not, there MUST exist a person with the provided email.
         
        If there is no HEI, the person is created in the system
        with needed privileges but no associated HEI.
         
        Only one of SHO, PIC, EUC, ERC or OID is required for linking
        the officer to the HEI.
         
        Persons receive an invitation via email for activating the account.
         
        The CSV file MUST (RFC2119) have a minimum set of fields:
         
        The CSV file MUST (RFC2119) have field names as columns on
        the first row.<br />
        Fields MAY (RFC2119) be in any order.
         
        The rows MAY (RFC2119) also contain these optional fields:
         
      An officer is just a person that has special status and is linked to
      a HEI (or more) whose cards and students is authorised to manage.
       
      Persons are created as needed and receive an invitation over email
      requesting consent.
       
      The first officer for a HEI may be loaded as an unlinked person and the link
      is later established when the HEI is created.
       
    The token you used was expired. A new one has been sent.<br>
     
    {0} {1}

    You are accessing {2}, that requires that you authenticate with
    the following token in the next {3} minutes.

    Token: {4}

    You can copy it and paste on the form that has informed you about
    this message.

    Thank you.

     
  Please, enter the token you have received from the system.<br>
   
<h3>Processing of personal information rejected</h3>
Your declination of consent has been registered. Thank you.<br>
Please note that you will not be able to use the system.<br>
 
<h3>Welcome to the European Student Card and Identifier management system</h3>
It is important the you consent that your personal information is processed
in the system before using it.<br>
This is what the system knows about you:<br>
 
Also, the system will create a link to the identification received vía
%(source.description)s but no extra personal information will be stored.
 
Do you agree with the information being stored to allow you access and
manage the system?
 
Do you agree with the information being stored to provide you with an European
Student Card and Identifier?
 
If you want to use a new source for authenticating
 
Please, enter your email address associated with the system, to recieve an
access token.<br>
It usually is the one in which you received a request for consent.<br>
 
Please, select one of the following authentication methods
 
The invitation you have used is expired.<br>
But sending a new one to the email address the system has for you, has failed.
 
The invitation you have used is expired.<br>
You will receive a fresh one you can use.
 
You can authenticate to the system using:
 
You can manage students for the following HEI:
 
You have permission to manage the system
 
that will be sent to the above email address
 Accepted on Access control Access not permitted Access not permitted. Active Administrivia April Attribute name August Authentication log Authentication logs Authentication source Authentication source description. Authentication sources Authentication system for {0} <no-reply@{1}> Bad operation {0} on line {1} Card Card Number Card load batch Card load batches Card load line Card load lines Card not found on line {0} Cards Close session Consent is required for the Student Card System Could not send message to {0} Could register card {0} Country Create Created by Created on Data file: Data has errors December Delete Description ESC production key ESC registered on ESC sandbox key EUC code Email Email token based authentication Empty listing Erasmus Erasmus code European Student Card European Student Card number Expired invitation Export selected cards to CSV file. Extractor Family name Fatal error calling ESC_Router() February Field {0} missing on line {1} Government issued identifier HEI HEI EUC code HEI Erasmus OID HEI Erasmus code HEI PIC code (required for ESC) HEI bulk load HEI country ISO two letter code HEI main web page HEI name HTTP server environment variables based authentication HTTP server environment variables based authentication for Cl@ve HTTP server x509 certificate authentication Has accepted Higher Education Institution Higher Education Institutions How Identification source Identifier Identifier value hash Identifiers Institution name Institution web site Invitation code Invited on Is Invited Is the source active? January July June Link for adding a new autentication Link sent to {0} Load HEIs from CSV Load Officers from CSV Load selected batches Load student cards from CSV Loaded on Main officer's family name Main officer's given name Managed HEI March Message to {0} not sent Missing data on line {0} Modified on Month the term starts on, for expiration date calculations. Name No No information to store No source, extractor is time duration November Number of HEIs Number of authentications Number of cards OID code OK October Officer Officer bulk load Officers PIC code Permissions Person Person that manages a HEI Person {0} in line {1} does not exist. Not enough information to add a person. Person's HEI Persons Please, make sure you select the right delimiter. Problem with {0} in line {1}: {2} Processed Register selected cards again (slow) Regular expression for extracting the value. Responsible officer Responsible person SCHAC Home Organization SCHAC Home Organization (HEI Internet domain) Select HEI Select delimiter your file uses Send invite to selected persons Send link to {0} failed. September Source name Student Number Student cards bulk load Student specific part of ESI Student who owns the card Term start month Test presentation Upload CSV Usage statistics Welcome When Yes You have to Your Internet domain. For ESI Your access token for {0} card management system Your session has been closed. authenticate yourself authentications comma "," contains the student specific part of the ESI email address for the main HEI officer for preprinted backgrounds get cards in PDF government issued identifier for the person government issued identifier for the student if present, value MUST (RFC 2119) be either month nameMay month when term starts (1 through 12) officer's HEI ERC code officer's HEI EUC code officer's HEI OID code officer's HEI PIC code officer's HEI schacHomeOrganization officer's email officer's family name officer's given name request a new one semi-colon ";" student's email student's family name student's given name students to use the system. via the admin panel {0} HEI loaded {0} HEIs loaded {0} already exists in line {1} {0} card added {0} cards added {0} card deleted {0} cards deleted {0} officer loaded {0} officers loaded {0} person added {0} persons added {0} person created {0} persons created Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2024-03-12 00:12+0100
PO-Revision-Date: 2024-03-12 00:20-0015
Last-Translator: V. Giralt <v@uma.es>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
X-Translated-Using: django-rosetta 0.9.8
 
C para crear una nueva tarjeta, que será la opción por defecto 
D para borrar la tarjeta si pertenece al estudiante 
Si están presentes first_name y last_name, la persona se crea en el sistema si es necesario.<br>Si no están, DEBE existir una perosona con la dirección de correo que se indica. 
Si no existe la HEI, la persona es añadida al sistema con los permisos necesarios pero sin asociarse a una institución. 
Sólo se requiere uno de SHO, PIC, EUC, ERC u OID para vincular al responsable con su Institución de Educación Superior. 
Las personas reciben una invitación por correo para activar la cuenta. 
El fichero CSV DEBE (RFC2119) tener un conjunto mínimo de campos: 
El fichero CSV DEBE (RFC2119) contener nombres de campo como encabezado de columnas en la primera fila.<br /> 
Los campos PUEDEN (RFC2119) aparecer en cualquier orden. 
Las filas PUEDEN (RFC2119) contener los siguientes campos opcionales: 
Un responsable del sistema en la HEI es sólo una persona con un estado especial que se vincula a una o varias HEIs, cuyas tarjetas y estudiantes tiene autorización para administrar. 
Las personas son creadas según sea necesario y reciben una invitación mediante correo electrónico solicitando su consentimiento. 
El responsable principal del sistema en la HEI puede cargarse como una persona no enlazada, y enlazarse posteriormente cuandose crea la HEI. 
El código de acceso (token) que usó ha expirado. Se le acaba de enviar uno nuevo.<br> 
{0} {1}
Está accediendo a {2}, que requiere que se identifique con el siguiente token en los próximos {3} minutos.

Código de acceso (Token): {4}

Puede copiar y pegar en el formulario que le ha informado de este mensaje.

Gracias. 
Por favor, introduzca el código de acceso (token) que ha recibido del sistema.<br> 
<h3>Se rechazó el procesado de información personal</h3>
Su rechazo del consentimiento ha sido registrado. Gracias.<br />
Por favor, tenga en cuenta que no podrá usar el sistema.<br />
 
<h3>Bienvenido al sistema de gestión de la Tarjeta e Identificador Europeo de Estudiante </h3>
Es importante que des tu consentimiento para que tu información personal sea procesada por el sistema antes de usarla.<br>
Esto es lo que el sistema conoce de ti:<br>
 
Además, el sistema creará un vínculo con la identificación recibida a través de %(source.description)s sin que ninguna información personal adicional sea almacenada.
 
¿Estás de acuerdo con que la información se almacene para ofrecerte acceso al sistema de gestión?
 
¿Estás de acuerdo con que la información se almacene para poder proporcionar una Tarjeta e Identificador Europeo de Estudiante?
 
Si quiere utilizar una nueva fuente para autenticarse
 
Por favor, introduzca su dirección de correo asociada al sistema, y recibirá un código de acceso.<br>
Habitualmente es el que recibió para solicitarle consentimiento.<br>
 
Por favor, seleccione uno de los siguientes métodos de autenticación
 
La invitación que ha usado ha expirado.<br> Sin embargo, ha habido un problema al enviar una nueva a la dirección de correo electrónico que tiene el sistema.
 
La invitación usada ha expirado.<br>Recibirá una nueva que pueda usar.
 
Puede autenticarse en el sistema usando:
 
Puedes gestionar estudiantes de la siguiente institución:
 
Tiene permiso para gestionar el sistema
 
que será enviada a la dirección de correo que aparece más arriba
 Aceptado en la fecha Control de acceso Acceso denegado Acceso denegado. Activo Información administrativa abril Nombre del atributo agosto Registro de autenticación Registros de autenticación Fuente de autenticación Descripción de la fuente de autenticación. Fuentes de autenticación Sistema de autenticación de {0} <no-reply@{1}> Operación incorrecta {0} en la línea {1}. Tarjeta Número de Tarjeta Lote de carga de tarjetas Lotes de carga de tarjetas Línea de lote de carga Líneas de carga de tarjetas  No se encontró la tarjeta en la línea {0} Tarjetas Cerrar sesión Se requiere consentimiento para el Sistema de Tarjetas de Estudiantes No se puede enviar mensaje a {0} pudo registrar la tarjeta {0} País Crear Creado por Creado con fecha Fichero de datos: Los datos contienen errores diciembre Eliminar Descripción Clave de producción de ESC ESC registrada con fecha Clave de pruebas de ESC Código ECHE Correo electrónico Autenticación basada en códigos de acceso (tokens) Lista vacía Erasmus Código Erasmus Tarjeta Europea de Estudiante Número de la Tarjeta Europea de Estudiante Invitación expirada Exportar tarjetas seleccionadas a fichero CSV Extractor Apellidos Error fatal llamando a ESC_Router() febrero Faltan el campo {0} en la línea {1} Identificador nacional (DNI, NIF) HEI Código ECHE de la HEI OID Erasmus de la HEI Código Erasmus de la HEI Código PIC de la HEI (requerido para la ESC) Carga masiva de HEIs Código ISO de dos letras para el país de la HEI Página web principal de la HEI nombre de la HEI Autenticación basada en códigos de acceso (tokens) Autenticación basada en Cl@ve Autenticación con certificado digital Ha aceptado Institución de Educación Superior Instituciones de Educación Superior Cómo Fuente de identificación Identificador Valor del hash del identificador Identificadores Nombre de la institución Sitio web de la institución Código de invitación Invitado con fecha Ha sido invitado ¿Está la fuente activa? enero julio junio Enlace para añadir una nueva autenticación Enlace enviado a {0} Cargar instituciones (HEIs) desde CSV Cargar responsables institucionales desde CSV Cargar lotes seleccionados Cargar tarjetas de estudiante desde CSV Cargado él Apellido del responsable del sistema en la HEI Nombre del responsable del sistema en la HEI HEI gestionada marzo Mensaje para {0} no enviado Faltan datos en la línea {0} Modificado con fecha Mes de comienzo del curso, para cálculo de la fecha de expiración. Nombre No No hay información que almacenar No usa un atributo origen, el valor del extractor es la duración del código de acceso (token). noviembre Número de HEI Número de autenticaciones Número de tarjetas Código OID OK octubre Responsable del sistema en la HEI Carga masiva de responsables del sistema en las HEIs Responsable del sistema en la HEI Código PIC Permisos Persona Persona que gestiona una HEI La persona {0} en la línea {1} no existe. No hay información suficiente para añadir una persona.  Institución de la persona Personas Por favor, asegúrese de seleccionar el delimitador correcto. Hay un problema con {0} en la línea {1}: {2} Procesado Registrar de nuevo las tarjetas seleccionadas (lento) Expresión regular para extraer el valor Responsable en la HEI Persona responsable SCHAC Home Organization SCHAC Home Organization (dominio internet de la HEI) Selecciona HEI Seleccione el delimitador que utiliza en su fichero Enviar invitación a las personas seleccionadas Falló el envío del enlace a {0}. septiembre Nombre de fuente Número de Estudiante Carga masiva de tarjetas de estudiante Parte específica del estudiante en el ESI Estudiante titular de la tarjeta Mes de comienzo del curso Presentación de prueba Cargar CSV Estadísticas de uso Bienvenido Cuándo Sí Tiene que Su dominio de Internet. Para el ESI Su código de acceso para el sistema de gestión de tarjetas {0} Su sesión ha sido cerrada. autenticarse autenticaciones coma "," contiene la parte específica del estudiante del ESI dirección de correo para el responsable de sistema en la HEI para fondos pre-impresos obtener tarjetas en PDF identificador expedido por el gobierno para la persona identificador expedido por el gobierno para el estudiante si está presente, el valor DEBE (RFC 2119) ser mayo mes en el que comienza el curso (del 1 al 12) Código ERC de la institución HEI del responsable del sistema en la HEI Código EUC de la institución HEI del responsable del sistema en la HEI Código OID de la institución HEI del responsable del sistema en la HEI Código PIC de la institución HEI del responsable del sistema en la HEI schacHomeOrganization de la HEI del responsable del sistema en la HEI dirección de correo del responsable del sistema en la HEI apellidos del responsable del sistema en la HEI nombre del responsable del sistema en la HEI solicite una nueva invitación punto y coma ";" dirección de correo electrónico del estudiante apellidos del estudiante nombre de estudiante estudiantes para usar el sistema. a través del panel de administrador Cargada {0} HEI Cargadas {0} HEIs {0} ya existe en la línea {1}. añadida {0} tarjeta {0} tarjetas añadidas borrada {0} tarjeta {0} tarjetas borradas cargado {0} responsable cargados {0} responsables {0} persona añadida {0} personas añadidas {0} persona creada {0} personas creadas 