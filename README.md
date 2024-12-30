# Cancheros

Cancheros es una API construida con Flask que sigue el patrón MVC y está diseñada para implementarse en entornos serverless como AWS Lambda o Google Cloud Run. Este proyecto facilita la creación y gestión de recursos para el proyecto Cancheros, permitiendo una arquitectura escalable y eficiente.

## Características

- **Patrón MVC**: Separación clara de modelos, vistas y controladores.
- **Arquitectura Serverless**: Optimizado para entornos sin servidor, reduciendo costos y aumentando la escalabilidad.
- **API RESTful**: Endpoints bien definidos para interactuar con los recursos.
- **Fácil de Escalar**: Compatible con plataformas como AWS Lambda y Google Cloud Run.

## Prerrequisitos

- Python 3.8+
- pip
- Virtualenv (opcional pero recomendado)

## Instalación

1. **Clonar el repositorio**

   ````bash
   git clone https://github.com/tuusuario/cancheros.git
   cd cancheros   ```

   ````

2. **Crear y activar un entorno virtual**

   ````bash
   python3 -m venv venv
   source venv/bin/activate   ```

   ````

3. **Instalar las dependencias**
   ````bash
   pip install -r requirements.txt   ```
   ````

## Configuración del Entorno de Desarrollo

1. Instalar dependencias de desarrollo:

   ```bash
   pip install -r requirements-dev.txt
   ```

   2. Instalar pre-commit hooks:
      ```bash
      pre-commit install
      ```

## Uso

1. **Configurar las variables de entorno**

   Crea un archivo `.env` y añade las configuraciones necesarias.

2. **Ejecutar la aplicación localmente**

   ````bash
   python run.py   ```

   La API estará disponible en `http://localhost:5000`.
   ````

## Despliegue

Este proyecto está diseñado para desplegarse en plataformas serverless como AWS Lambda o Google Cloud Run. Asegúrate de seguir las guías específicas de la plataforma que elijas para configurar correctamente el despliegue.

## Contribución

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para discutir cualquier cambio.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.
