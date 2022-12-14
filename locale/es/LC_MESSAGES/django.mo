??    ?      ?      l      l  V   m  R   ?  q        ?  o   	  U   y  K   ?  ?     L   ?  ?      j   ?  ?     F   ?    ?  D   ?  ?   #  ?   ?  ?   ?  [   W  m   ?  4   !  ?   V  <   ?  }   9  X   ?  +     0   <  *   m  .   ?     ?     ?     ?     ?               "     (     7     >  "   T     w  ,   ?     ?     ?     ?     ?            /        I     g  
   o  
   z     ?     ?     ?     ?     ?     ?     ?     ?      ?               $     :     W  	   j     t      ?     ?     ?     ?     ?     ?               3     A     a     s     |     ?     ?     ?  
   ?     ?     ?               -  
   =  
   H     S     i     q     v  #   {     ?     ?     ?     ?     ?     ?          (  ;   4     p     u     x  %   ?     ?     ?     ?     ?     ?     ?     ?     ?     ?            N   ,     {     ?  1   ?  ,   ?     ?            -   .  
   \     g     ?     ?  	   ?     ?     ?     ?     ?           4   
   E      P      X      \      h   0   ?      ?      ?   -   ?   &   !     @!  +   Q!  ,   }!  +   ?!     ?!  %   ?!     "     ""     9"     P"  #   g"     ?"     ?"     ?"     ?"     ?"     ?"     ?"     #     &#     :#     Y#     x#  "   ?#  )   ?#  &   ?#  "   $  &   .$  ?  U$  A   ?%  4   8&  ^   m&  ?   ?&  {   d'  H   ?'  C   )(  ?   m(  F   )  ?   O)  ?   ?)  ?   v*  D   ?*  ?   C+  @   ,  ?   \,    -  ?    .  g   ?.  ?   6/  7   ?/  ?   ?/  H   ?0  ?   ?0  N   ?1  +   ?1  <    2  )   =2  E   g2     ?2     ?2     ?2     ?2     ?2     ?2     3     3     23     93  ,   R3     3  /   ?3  +   ?3     ?3     ?3  +   4     <4     E4  E   T4      ?4     ?4     ?4     ?4     ?4  	    5     
5     5     35     L5     d5     p5     ?5     ?5     ?5     ?5  (   ?5     6  	   6  	   !6  #   +6     O6  %   W6  !   }6     ?6     ?6     ?6  -   ?6     7  %   '7     M7     m7     ~7  #   ?7  $   ?7     ?7     ?7      ?7     8     ,8     F8     c8     z8     ?8     ?8     ?8     ?8     ?8  ,   ?8     ?8  $   9  "   19     T9     c9     i9     ?9     ?9  J   ?9     :     
:  !   :  K   /:     {:     ?:     ?:     ?:     ?:     ?:     ?:     ?:     ?:     ?:     ?:  d   ;     q;     ?;  =   ?;  (   ?;     ?;     <     *<  4   B<     w<  3   ?<  /   ?<  !   ?<  
   =     =     %=  (   ;=  *   d=     ?=     ?=  
   ?=  
   ?=     ?=  	   ?=      ?=  @   >     O>     k>  4   x>  >   ?>     ?>  6   ?  9   ;?  /   u?     ??  -   ??  2   ??  2   @  2   >@  2   q@  1   ?@  &   ?@     ?@     A     2A  0   QA     ?A     ?A     ?A  $   ?A  "   ?A     B  +   .B  )   ZB  6   ?B  1   ?B  +   ?B  '   C   
              C for creating a new card, this is the default if absent
               
              D for deleting the card if it belongs to the student
               
        If first_name and last_name are present,
        the person is created in the system if needed.
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
 Accepted on Access control Access not permitted Access not permitted. Active Administrivia April Attribute name August Authentication source Authentication source description. Authentication sources Authentication system for {0} <no-reply@{1}> Bad operation {0} on line {1} Card Card Number Card not found on line {0} Cards Close session Consent is required for the Student Card System Could not send message to {0} Country Created on Data file: Data has errors December Description ESC production key ESC registered on ESC sandbox key EUC code Email Email token based authentication Erasmus Erasmus code European Student Card European Student Card number Expired invitation Extractor Family name Fatal error calling ESC_Router() February Field {0} missing on line {1} Government issued identifier HEI EUC code HEI Erasmus OID HEI Erasmus code HEI PIC code (required for ESC) HEI bulk load HEI country ISO two letter code HEI main web page HEI name Has accepted Higher Education Institution Higher Education Institutions Identification source Identifier Identifier value hash Identifiers Institution name Institution web site Invitation code Invited on Is Invited Is the source active? January July June Link for adding a new autentication Link sent to {0} Main officer's family name Main officer's given name Managed HEI March Message to {0} not sent Missing data on line {0} Modified on Month the term starts on, for expiration date calculations. Name No No information to store No source, extractor is time duration November OID code OK October Officer Officer bulk load Officers PIC code Permissions Person Person that manages a HEI Person {0} in line {1} does not exist. Not enough information to add a person. Person's HEI Persons Please, make sure you select the right delimiter. Regular expression for extracting the value. Responsible officer Responsible person SCHAC Home Organization SCHAC Home Organization (HEI Internet domain) Select HEI Select delimiter your file uses Send invite to selected persons Send link to {0} failed. September Source name Student Number Student cards bulk load Student specific part of ESI Student who owns the card Term start month Upload CSV Welcome Yes You have to Your Internet domain. For ESI Your access token for {0} card management system Your session has been closed. authenticate yourself contains the student specific part of the ESI email address for the main HEI officer get cards in PDF government issued identifier for the person government issued identifier for the student if present, value MUST (RFC 2119) be either month nameMay month when term starts (1 through 12) officer's HEI ERC code officer's HEI EUC code officer's HEI OID code officer's HEI PIC code officer's HEI schacHomeOrganization officer's email officer's family name officer's given name request a new one student's email student's family name student's given name to use the system. via the admin panel {0} HEI loaded {0} HEIs loaded {0} already exists in line {1} {0} card added {0} cards added {0} card deleted {0} cards deleted {0} not saved. Existing data in line {1}. {0} officer loaded {0} officers loaded {0} person added {0} persons added {0} person created {0} persons created Project-Id-Version: PACKAGE VERSION
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2021-11-13 12:46+0100
PO-Revision-Date: 2021-11-13 13:04-0015
Last-Translator: Victoriano Giralt <victoriano@uma.es>
Language-Team: LANGUAGE <LL@li.org>
Language: 
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Plural-Forms: nplurals=2; plural=(n != 1);
X-Translated-Using: django-rosetta 0.9.7
 
C para crear una nueva tarjeta, que será la opción por defecto 
D para borrar la tarjeta si pertenece al estudiante 
Si están presentes first_name y last_name, la persona se crea en el sistema si es necesario. 
Si no existe Institución de Educación Superior, la persona es añadida al sistema con los permisos necesarios pero sin asociarse a una institución. 
Sólo se requiere uno de SHO, PIC, EUC, ERC o OID para vincular al responsable con su Institución de Educación Superior. 
Las personas reciben una invitación por correo para activar la cuenta. 
El fichero CSV DEBE (RFC2119) tener un conjunto mínimo de campos: 
El fichero CSV DEBE (RFC2119) contener nombres de campo como columnas en la primera fila.<br /> 
Los campos PUEDEN (RFC2119) aparecer en cualquier orden. 
Las filas PUEDEN (RFC2119) contener los siguientes campos opcionales: 
Un representante es sólo una persona con un estado especial que se vincula a una o varias HEIs, cuyas tarjetas y estudiantes tiene autorización para administrar. 
Las personas son creadas según sea necesario y reciben una invitación mediante correo electrónico solicitando consentimiento. 
El representante principal de una HEI puede cargarse como una persona no enlazada, y enlazarse posteriormente cuando la HEI es creada. 
El token que usó ha expirado. Se le acaba de enviar uno nuevo.<br> 
{0} {1}
Está accediendo a {2}, que requiere que se identifique con el siguiente token en los próximos {3} minutos.

Token: {4}

Puede copiar y pegar en el formulario que le ha informado de este mensaje.

Gracias. 
Por favor, introduzca el token que ha recibido del sistema.<br> 
<h3>Se rechazó el procesado de información personal</h3>
Su rechazo del consentimiento ha sido registrado. Gracias.<br />
Por favor, tenga en cuenta que no podrá usar el sistema.<br />
 
<h3>Bienvenido al sistema de gestión de la Tarjeta e Identificador de Estudiante Europeo</h3>
Es importante que des consentimiento para que tu información personal sea procesada por el sistema antes de usarla.<br>
Esto es lo que el sistema conoce de ti:<br>
 
Además, el sistema creará un vínculo con la identificación recibida a través de %(source.description)s sin que ninguna información personal adicional sea almacenada.
 
¿Estás de acuerdo con que la información se almacene para ofrecerle acceso al sistema de gestión?
 
¿Estás de acuerdo con que la información se almacene para poder proporcionar una Tarjeta e Identificador de Estudiante Europeo?
 
Si quiere utilizar una nueva fuente para autenticarse
 
Por favor, introduzca su dirección de correo asociada al sistema, y recibirá un código de acceso.<br>
Habitualmente es el que recibió para solicitarle consentimiento.<br>
 
Por favor, seleccione uno de los siguientes métodos de autenticación
 
La invitación que ha usado está expirada.<br> Sin embargo, enviar una nueva a la dirección de correo electrónico que tiene el sistema ha fallado.
 
La invitación usada está expirada.<br>Recibirás una nueva que pueda usar.
 
Puede identificarse en el sistema usando:
 
Puedes gestionar estudiantes de la siguiente institución:
 
Tiene permiso para gestionar el sistema
 
que será enviada a la dirección de correo que aparece más arriba
 Aceptado en la fecha Control de acceso Acceso denegado Acceso denegado. Activo Información administrativa abril Nombre del atributo agosto Fuente de autenticación Descripción de la fuente de autenticación. Fuentes de autenticación Sistema de autenticación de {0} <no-reply@{1}> Operación incorrecta {0} en la línea {1}. Tarjeta Número de Tarjeta No se encontró la tarjeta en la línea {0} Tarjetas Cerrar sesión Se requiere consentimiento para el Sistema de Tarjetas de Estudiantes No se puedo enviar mensaje a {0} País Creado con fecha Fichero de datos: Los datos contienen errores Diciembre Descripción Clave de producción de ESC ESC registrada con fecha Clave de pruebas de ESC Código EUC Correo electrónico Autenticación basada en tokens Erasmus Código Erasmus Carnet de Estudiante Europeo Número de Tarjeta de Estudiante Europeo Invitación expirada Extractor Apellidos Error fatal llamando a ESC_Router() febrero Faltan el campo {0 } en la línea {1} Identificador nacional (DNI, NIF) Código EUC de la HEI OID Erasmus de la HEI Código Erasmus de la HEI Código PIC de la HEI (requerido para la ESC) Carga masiva de HEI Código ISO de dos letras para la HEI Página web principal de la HEI nombre de la HEI Ha aceptado Institución de Educación Superior Instituciones de Educación Superior Fuente de identificación Identificador Valor del hash del identificador Identificadores Nombre de la institución Sitio web de la institución Código de invitación Invitado con fecha Ha sido invitado ¿Está la fuente activa? enero julio junio Enlace para añadir una nueva autenticación Enlace enviado a {0} Apellido del representante principal Nombre del representante principal HEI gestionada marzo Mensaje para {0} no enviada Faltan datos en la línea {0} Modificado con fecha Mes en el que comienza el curso, para cálculo de la fecha de expiración. Nombre No No hay información que almacenar No usa un atributo origen,el valor del extractor es la duración del token. november Código OID OK octubre Responsable Carga masiva de representantes Responsable Código PIC Permisos Persona Persona que gestiona una HEI La persona {0} en la línea {1} no existe. No hay información suficiente para añadir una persona.  Institución de la persona Personas Por favor, asegúrese de seleccionar el delimitador correcto. Expresión regular para extraer el valor Representante responsable Persona responsable SCHAC Home Organization SCHAC Home ORganization (dominio internet de la HEI) Selecciona HEI Seleccione el delimitador que utiliza en su fichero Enviar invitación a las personas seleccionadas Falló el envío de enlace a {0}. septiembre Nombre fuente Número de Estudiante Carga en lotes de tarjetas de estudiante Parte específica del estudiante en el ESI Estudiante que tiene la tarjeta Mes de comienzo del curso Cargar CSV Bienvenido Sí Tiene que Su dominio de Internet. Para ESI Su código de acceso para el sistema de gestión de tarjetas {0} Su sesión ha sido cerrada. autenticarse contiene la parte específica del estudiante del ESI dirección de correo para el representante principal de la HEI obtener tarjetas en PDF identificador expedido por el gobierno para la persona identificador expedido por el gobierno para el estudiante si está presente, el valor DEBE (RFC 2119) ser mayo mes en el que comienza el curso (del 1 al 12) Código ERC de la institución HEI del responsable Código EUC de la institución HEI del responsable Código OID de la institución HEI del responsable Código PIC de la institución HEI del responsable schacHomeOrganization de la HEI del representante dirección de correo del representante apellidos del representante nombre del representante solicite una nueva invitación dirección de correo electrónico del estudiante apellidos del estudiante nombre de estudiante para usar el sistema. a través del panel de administrador Cargada HEI {0} Cargadas HEIs {0}  {0} ya existe en la línea {1}. añadida {0} tarjeta {0} tarjetas añadidas borrada {0} tarjeta {0} tarjetas borradas no se salvó {0}. Ya existían datos en la línea {1}. cargado {0} responsable cargados {0} responsables {0} persona añadida {0} personas añadidas {0} persona creada {0} personas creadas 